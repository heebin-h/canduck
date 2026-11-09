"""RPi GPIO 제어 — schematic-spec.md RPi 핀맵 기준.

- GPIO23: ESP32 RESET (EN) — active low, 평시 High
- GPIO24: ESP32 BOOT (GPIO0) — 평시 High, Low + 리셋 = 다운로드 모드
- GPIO4 : 사용자 버튼 (풀업, 눌림 = Low)

gpiozero 기반 (RPi OS 기본 탑재). RPi가 아니거나 초기화 실패 시
mock 모드로 강등 — 로그만 남기고 데몬은 정상 동작 (노트북 개발용).
"""
import time
from collections.abc import Callable

import structlog

from .config import settings

log = structlog.get_logger(__name__)

_RESET_PULSE_S = 0.1


class GpioManager:
    def __init__(self) -> None:
        self._reset = None   # gpiozero.DigitalOutputDevice
        self._boot = None
        self._button = None  # gpiozero.Button
        self.mock = True

    def start(self, on_button: Callable[[], None] | None = None) -> None:
        if not settings.enable_gpio:
            log.info("gpio_disabled")
            return
        try:
            from gpiozero import Button, DigitalOutputDevice
        except ImportError:
            log.warning("gpio_mock", reason="gpiozero not installed")
            return
        try:
            # active_high=False: on() = Low. initial off = High(정상 동작 상태).
            self._reset = DigitalOutputDevice(
                settings.gpio_esp32_reset, active_high=False, initial_value=False
            )
            self._boot = DigitalOutputDevice(
                settings.gpio_esp32_boot, active_high=False, initial_value=False
            )
            self._button = Button(settings.gpio_user_button, pull_up=True, bounce_time=0.05)
            if on_button:
                self._button.when_pressed = on_button
            self.mock = False
            log.info(
                "gpio_ready",
                reset=settings.gpio_esp32_reset,
                boot=settings.gpio_esp32_boot,
                button=settings.gpio_user_button,
            )
        except Exception as exc:  # 핀 팩토리 없음(비 RPi) 등
            log.warning("gpio_mock", reason=str(exc))
            self._reset = self._boot = self._button = None

    def esp32_enter_bootloader(self) -> None:
        """BOOT Low 상태로 리셋 → UART 다운로드 모드 (W3+ OTA/플래시용)."""
        if self._reset is None or self._boot is None:
            log.info("gpio_mock_esp32_bootloader")
            return
        self._boot.on()    # BOOT Low
        time.sleep(0.05)
        self._reset.on()
        time.sleep(_RESET_PULSE_S)
        self._reset.off()
        time.sleep(0.1)
        self._boot.off()   # BOOT 복귀
        log.info("esp32_bootloader_entered")

    def close(self) -> None:
        for dev in (self._reset, self._boot, self._button):
            if dev is not None:
                try:
                    dev.close()
                except Exception:
                    pass
        self._reset = self._boot = self._button = None
