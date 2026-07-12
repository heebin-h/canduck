"""canduck 메인 데몬.

systemd 서비스로 실행. asyncio 이벤트 루프로:
- UART (ESP32 명령/이벤트)
- MQTT (macOS 에이전트 이벤트)
- FSM (행동 상태)
- Face (LCD 렌더)
- Voice (wake-word)
- Telemetry (전력 모니터)
를 통합.
"""
import asyncio
import signal
import sys

import structlog

from .config import settings
from .face import Expression, Face
from .fsm import FSM, Event, State
from .mqtt_client import MqttClient, MqttMessage
from .telemetry import Telemetry
from .uart_client import UartClient, UartEvent
from .voice import VoiceManager

log = structlog.get_logger(__name__)


STATE_TO_POSE = {
    State.IDLE: "idle",
    State.HEADACHE: "headache",
    State.HAPPY: "happy",
    State.SLEEP: "sleep",
    State.SLEEPY: "idle",
}

STATE_TO_EXPRESSION = {
    State.IDLE: Expression.IDLE,
    State.LISTENING: Expression.ATTENTIVE,
    State.HEADACHE: Expression.HEADACHE,
    State.HAPPY: Expression.HAPPY,
    State.SLEEPY: Expression.SLEEPY,
    State.SLEEP: Expression.SLEEP,
    State.SURPRISED: Expression.SURPRISED,
    State.WALKING: Expression.ATTENTIVE,
    State.ERROR: Expression.ERROR,
}


class CanduckApp:
    def __init__(self) -> None:
        self.fsm = FSM()
        self.face = Face()
        self.uart = UartClient()
        self.mqtt = MqttClient()
        self.telemetry = Telemetry()
        self.voice = VoiceManager(on_wake=self._on_wake)
        self._stop_evt = asyncio.Event()

    async def start(self) -> None:
        self._wire_fsm()
        self.face.init_hardware()
        self.telemetry.init()
        await self.uart.connect()
        self.uart.add_handler(self._on_uart_event)
        await self.uart.send("ENABLE", 1)
        self.mqtt.add_handler(self._on_mqtt_message)
        self.mqtt.connect()
        await self.voice.start()
        # 백그라운드 태스크
        asyncio.create_task(self.fsm.idle_timer_loop(), name="fsm-idle-timer")
        asyncio.create_task(self.telemetry.poll_loop(), name="telemetry")
        # 부팅 시 idle 진입
        await self.fsm.handle(Event.POSE_DONE)

    async def stop(self) -> None:
        log.info("daemon_stopping")
        await self.uart.send("ENABLE", 0)
        await self.uart.close()
        self.mqtt.close()
        await self.voice.stop()
        self._stop_evt.set()

    async def wait(self) -> None:
        await self._stop_evt.wait()

    def _wire_fsm(self) -> None:
        for state, expr in STATE_TO_EXPRESSION.items():
            self.fsm.on_enter(state, self._make_enter_handler(state, expr))

    def _make_enter_handler(self, state: State, expr: Expression):
        async def handler(payload: dict) -> None:
            self.face.set_expression(expr)
            pose = STATE_TO_POSE.get(state)
            if pose:
                await self.uart.send("POSE", pose)
        return handler

    async def _on_uart_event(self, event: UartEvent) -> None:
        match event.kind:
            case "BOOT":
                log.info("esp32_booted", args=event.args)
                await self.uart.send("ENABLE", 1)
            case "DONE":
                await self.fsm.handle(Event.POSE_DONE, {"pose": event.args})
            case "TAP":
                intensity = int(event.args[1]) if len(event.args) > 1 else 0
                if intensity > 1200:
                    await self.fsm.handle(Event.TAP, {"intensity": intensity})
            case "SHAKE":
                await self.fsm.handle(Event.SHAKE)
            case "TOUCH":
                ch = int(event.args[0]) if event.args else -1
                state = event.args[1] == "1" if len(event.args) > 1 else False
                if not state:
                    return
                if ch == 0:
                    await self.fsm.handle(Event.TOUCH_HEAD)
                elif ch == 1:
                    await self.fsm.handle(Event.TOUCH_BACK)
            case "VBAT":
                mv = int(event.args[0]) if event.args else 0
                self.telemetry.update_vbat(mv)
                if self.telemetry.is_critical():
                    await self.fsm.handle(Event.VBAT_CRITICAL)
            case "ERR":
                log.warning("esp32_error", args=event.args)

    async def _on_mqtt_message(self, msg: MqttMessage) -> None:
        topic = msg.topic
        payload = msg.payload
        if topic.endswith("/build"):
            if payload.get("status") == "fail":
                await self.fsm.handle(Event.BUILD_FAIL, payload)
            elif payload.get("status") == "pass":
                await self.fsm.handle(Event.BUILD_PASS, payload)
        elif topic.endswith("/git"):
            if payload.get("action") == "merge":
                await self.fsm.handle(Event.GIT_MERGE, payload)
        elif topic.endswith("/notification"):
            await self.fsm.handle(Event.NOTIFICATION, payload)
        elif topic.startswith("canduck/cmd/pose"):
            pose = payload.get("pose")
            if pose:
                await self.uart.send("POSE", pose)

    def _on_wake(self) -> None:
        # voice 스레드에서 호출되므로 run_coroutine_threadsafe 사용
        loop = asyncio.get_event_loop()
        asyncio.run_coroutine_threadsafe(self.fsm.handle(Event.WAKE_WORD), loop)


def _setup_logging() -> None:
    structlog.configure(
        wrapper_class=structlog.make_filtering_bound_logger(
            __import__("logging").getLevelName(settings.log_level)
        ),
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ],
    )


async def _amain() -> int:
    _setup_logging()
    app = CanduckApp()
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda: asyncio.create_task(app.stop()))
    await app.start()
    await app.wait()
    return 0


def main() -> int:
    try:
        return asyncio.run(_amain())
    except KeyboardInterrupt:
        return 0


if __name__ == "__main__":
    sys.exit(main())
