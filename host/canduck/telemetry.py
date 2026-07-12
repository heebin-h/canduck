"""INA219 ×2 폴링, 배터리 모니터링.

I2C 주소: 0x40 (5V 레일), 0x41 (6V 서보 레일).
"""
import asyncio
from dataclasses import dataclass

import structlog

from .config import settings

log = structlog.get_logger(__name__)

INA219_ADDRESSES = {"rail_5v": 0x40, "rail_6v": 0x41}


@dataclass(slots=True)
class PowerSample:
    rail_5v_mv: int = 0
    rail_5v_ma: int = 0
    rail_6v_mv: int = 0
    rail_6v_ma: int = 0
    vbat_mv: int = 0   # ESP32에서 UART로 보고된 값


class Telemetry:
    def __init__(self) -> None:
        self._bus = None
        self._latest = PowerSample()

    def init(self) -> None:
        try:
            from smbus2 import SMBus
            self._bus = SMBus(1)
        except (ImportError, FileNotFoundError):
            log.warning("i2c_bus_unavailable")

    async def poll_loop(self) -> None:
        period = 1.0 / settings.telemetry_poll_hz
        while True:
            try:
                self._poll()
            except Exception:
                log.exception("telemetry_poll_failed")
            await asyncio.sleep(period)

    def _poll(self) -> None:
        if self._bus is None:
            return
        # 실제 INA219 calibration/read는 datasheet 참조하여 W4 brought-up 시 구현.
        # TODO: 션트 0.01Ω 기준 calibration 레지스터 셋, shunt voltage 읽고 전류 환산.
        pass

    @property
    def latest(self) -> PowerSample:
        return self._latest

    def update_vbat(self, mv: int) -> None:
        self._latest.vbat_mv = mv

    def is_critical(self) -> bool:
        return 0 < self._latest.vbat_mv < settings.vbat_critical_mv

    def is_warn(self) -> bool:
        return 0 < self._latest.vbat_mv < settings.vbat_warn_mv
