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
import logging
import signal
import sys

import structlog

from .config import settings
from .display_tk import TkFaceDisplay
from .face import Expression, Face
from .gpio import GpioManager
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
        self.face = Face(display=TkFaceDisplay() if settings.enable_face else None)
        self.gpio = GpioManager()
        self.uart = UartClient()
        self.mqtt = MqttClient()
        self.telemetry = Telemetry()
        self.voice = VoiceManager(on_wake=self._on_wake)
        self._stop_evt = asyncio.Event()
        self._loop: asyncio.AbstractEventLoop | None = None
        self._tasks: list[asyncio.Task] = []  # 참조 유지 — 안 하면 GC로 태스크가 사라질 수 있음
        self._stopping = False
        self.exit_code = 0  # 0이 아니면 systemd Restart=on-failure가 재기동

    async def start(self) -> None:
        self._loop = asyncio.get_running_loop()
        self._wire_fsm()
        self.face.start()
        self.gpio.start(on_button=self._on_button)
        self.telemetry.init()
        self.uart.add_handler(self._on_uart_event)
        self.uart.set_disconnect_handler(self._on_uart_disconnect)
        await self.uart.connect()
        await self.uart.send("ENABLE", 1)
        self.mqtt.add_handler(self._on_mqtt_message)
        self.mqtt.connect()
        await self.voice.start()
        # 백그라운드 태스크
        self._tasks.append(asyncio.create_task(self.fsm.idle_timer_loop(), name="fsm-idle-timer"))
        self._tasks.append(asyncio.create_task(self.telemetry.poll_loop(), name="telemetry"))
        # 부팅 시 idle 자세. (기존 fsm.handle(POSE_DONE)은 초기 상태가 IDLE이라 전이 없음 → no-op이었음)
        await self.uart.send("POSE", STATE_TO_POSE[State.IDLE])

    async def stop(self) -> None:
        if self._stopping:  # SIGTERM 중복·UART 단절 경로가 겹쳐도 1회만
            return
        self._stopping = True
        log.info("daemon_stopping")
        for task in self._tasks:
            task.cancel()
        try:
            await self.uart.send("STOP")
            await self.uart.send("ENABLE", 0)
        except Exception as exc:  # UART 미연결/장애여도 종료는 계속
            log.warning("uart_shutdown_send_failed", error=str(exc))
        try:
            await self.uart.close()
        except Exception as exc:
            log.warning("uart_close_failed", error=str(exc))
        self.mqtt.close()
        await self.voice.stop()
        self.gpio.close()
        self.face.stop()
        self._stop_evt.set()

    async def wait(self) -> None:
        await self._stop_evt.wait()

    def _wire_fsm(self) -> None:
        for state, expr in STATE_TO_EXPRESSION.items():
            self.fsm.on_enter(state, self._make_enter_handler(state, expr))
        self.fsm.on_enter(State.ERROR, self._on_enter_error)

    async def _on_enter_error(self, payload: dict) -> None:
        # architecture.md: error = 모션 중단. 배터리 critical에서 서보 토크 유지 시 과방전.
        await self.uart.send("STOP")
        await self.uart.send("ENABLE", 0)

    async def _on_uart_disconnect(self) -> None:
        await self.fsm.handle(Event.COMM_FAIL)
        self.exit_code = 1
        # reader 태스크 안에서 호출됨 — stop()이 그 태스크를 cancel하므로 await하지 않고 분리
        asyncio.create_task(self.stop(), name="stop-on-uart-eof")

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
                # ERROR(배터리 critical 등)에서 ESP32가 brown-out 리셋되면 재활성화하지 않음
                if self.fsm.state != State.ERROR:
                    await self.uart.send("ENABLE", 1)
            case "DONE":
                # "< DONE POSE <name>". 현재 상태의 포즈가 아닌 DONE(전이 직전 포즈의 늦은 완료)은
                # 무시 — 안 그러면 새 상태가 포즈 시작 직후 idle로 튕긴다.
                done_pose = event.args[1] if len(event.args) > 1 and event.args[0] == "POSE" else None
                if done_pose != STATE_TO_POSE.get(self.fsm.state):
                    log.info("stale_done_ignored", pose=done_pose, state=self.fsm.state.value)
                    return
                await self.fsm.handle(Event.POSE_DONE, {"pose": done_pose})
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

    def _dispatch_threadsafe(self, event: Event) -> None:
        # voice/gpio 콜백은 별도 스레드에서 호출됨 — start()에서 캡처한 루프 사용
        # (스레드에서 asyncio.get_event_loop()는 3.12+에서 RuntimeError)
        if self._loop is None:
            return
        asyncio.run_coroutine_threadsafe(self.fsm.handle(event), self._loop)

    def _on_wake(self) -> None:
        self._dispatch_threadsafe(Event.WAKE_WORD)

    def _on_button(self) -> None:
        # 물리 버튼 = wake-word와 동일 취급 (schematic-spec GPIO4 사용자 버튼)
        self._dispatch_threadsafe(Event.WAKE_WORD)


def _setup_logging() -> None:
    structlog.configure(
        wrapper_class=structlog.make_filtering_bound_logger(
            logging.getLevelName(settings.log_level)
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
    return app.exit_code


def main() -> int:
    try:
        return asyncio.run(_amain())
    except KeyboardInterrupt:
        return 0


if __name__ == "__main__":
    sys.exit(main())
