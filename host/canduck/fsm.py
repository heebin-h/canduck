"""행동 FSM.

상태 정의/전이는 docs/architecture.md 의 FSM 섹션과 동기화.
"""
import asyncio
import time
from enum import Enum

import structlog

from .config import settings

log = structlog.get_logger(__name__)


class State(str, Enum):
    IDLE = "idle"
    LISTENING = "listening"
    HEADACHE = "headache"
    HAPPY = "happy"
    SLEEPY = "sleepy"
    SLEEP = "sleep"
    SURPRISED = "surprised"
    WALKING = "walking"
    ERROR = "error"


class Event(str, Enum):
    BUILD_FAIL = "build_fail"
    BUILD_PASS = "build_pass"
    GIT_MERGE = "git_merge"
    NOTIFICATION = "notification"
    WAKE_WORD = "wake_word"
    TAP = "tap"
    TOUCH_HEAD = "touch_head"
    TOUCH_BACK = "touch_back"
    SHAKE = "shake"
    POSE_DONE = "pose_done"
    COMM_FAIL = "comm_fail"
    VBAT_CRITICAL = "vbat_critical"
    IDLE_TIMEOUT = "idle_timeout"


class FSM:
    """단순 transition 테이블 기반.

    실제 모션/표정 트리거는 daemon이 fsm.on_enter 콜백을 통해 수행.
    """

    def __init__(self) -> None:
        self.state: State = State.IDLE
        self.last_transition: float = time.monotonic()
        self._on_enter: dict[State, list] = {s: [] for s in State}

    def on_enter(self, state: State, handler) -> None:
        self._on_enter[state].append(handler)

    async def handle(self, event: Event, payload: dict | None = None) -> None:
        """이벤트 → 다음 상태 결정."""
        cur = self.state
        next_state = self._transition(cur, event)
        if next_state is None or next_state == cur:
            return
        log.info("fsm_transition", from_=cur.value, to=next_state.value, event=event.value)
        self.state = next_state
        self.last_transition = time.monotonic()
        for handler in self._on_enter[next_state]:
            try:
                await handler(payload or {})
            except Exception:
                log.exception("fsm_on_enter_failed", state=next_state.value)

    def _transition(self, cur: State, event: Event) -> State | None:
        # 최우선 (어디서든 우회)
        if event == Event.COMM_FAIL or event == Event.VBAT_CRITICAL:
            return State.ERROR

        # error 상태에서는 회복 이벤트 없음 — 외부 리셋 필요
        if cur == State.ERROR:
            return None

        # sleep 상태: wake-word만 깨움
        if cur == State.SLEEP:
            if event == Event.WAKE_WORD or event == Event.TAP or event == Event.SHAKE:
                return State.LISTENING
            return None

        # 우선순위 기반 전이
        if event == Event.BUILD_FAIL:
            return State.HEADACHE
        if event == Event.GIT_MERGE or event == Event.BUILD_PASS:
            return State.HAPPY
        if event == Event.TAP or event == Event.SHAKE:
            return State.HEADACHE
        if event == Event.TOUCH_HEAD:
            return State.SLEEPY
        if event == Event.TOUCH_BACK:
            return State.HAPPY
        if event == Event.WAKE_WORD:
            return State.LISTENING
        if event == Event.NOTIFICATION:
            return State.SURPRISED
        if event == Event.IDLE_TIMEOUT:
            if cur == State.IDLE:
                return State.SLEEPY
            if cur == State.SLEEPY:
                return State.SLEEP
            return None
        if event == Event.POSE_DONE:
            # 일시 상태에서는 idle로 복귀
            if cur in (State.HEADACHE, State.HAPPY, State.SURPRISED, State.LISTENING):
                return State.IDLE
            return None
        return None

    async def idle_timer_loop(self) -> None:
        """idle/sleepy 진입 후 일정 시간 경과 시 IDLE_TIMEOUT 이벤트 self-emit."""
        while True:
            await asyncio.sleep(5)
            elapsed = time.monotonic() - self.last_transition
            if self.state == State.IDLE and elapsed > settings.idle_to_sleepy_sec:
                await self.handle(Event.IDLE_TIMEOUT)
            elif self.state == State.SLEEPY and elapsed > settings.sleepy_to_sleep_sec:
                await self.handle(Event.IDLE_TIMEOUT)
