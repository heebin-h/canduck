"""LCD(240×240 둥근) 표정 렌더러.

W3 시점 — Pygame로 SDL 화면에 렌더 후, SPI 드라이버로 전송하는 구조.
실제 LCD 드라이버는 GC9A01 (Waveshare 1.28") — spidev로 직접 제어.
"""
from enum import Enum
from pathlib import Path

import pygame
import structlog
from PIL import Image, ImageDraw

from .config import settings

log = structlog.get_logger(__name__)

ASSETS_DIR = Path(__file__).resolve().parent.parent.parent / "assets" / "face"


class Expression(str, Enum):
    IDLE = "idle"
    BLINK = "blink"
    HAPPY = "happy"
    SLEEPY = "sleepy"
    SLEEP = "sleep"
    HEADACHE = "headache"
    SURPRISED = "surprised"
    ATTENTIVE = "attentive"
    ERROR = "error"


class Face:
    """표정 렌더는 두 단계.

    1) Pillow로 비트맵 합성 (240×240 RGB565 호환)
    2) GC9A01 LCD 드라이버로 SPI 송신
    """

    def __init__(self) -> None:
        self._current: Expression = Expression.IDLE
        self._frame: Image.Image | None = None
        self._lcd = None  # GC9A01 드라이버 인스턴스 (W3에 구현)

    def init_hardware(self) -> None:
        """SPI/GPIO 초기화. 실 RPi에서만 호출."""
        try:
            from .lcd_gc9a01 import GC9A01  # W3에 작성 예정
            self._lcd = GC9A01(
                spi_bus=settings.lcd_spi_bus,
                spi_dev=settings.lcd_spi_dev,
                gpio_dc=settings.lcd_gpio_dc,
                gpio_rst=settings.lcd_gpio_rst,
                gpio_bl=settings.lcd_gpio_bl,
            )
            self._lcd.init()
        except ImportError:
            log.warning("lcd_driver_missing_using_pygame_only")

    def set_expression(self, expr: Expression) -> None:
        if expr == self._current:
            return
        log.info("face_expression", expr=expr.value)
        self._current = expr
        self._render()
        self._present()

    def tick(self) -> None:
        """짧은 애니메이션(깜빡임 등) 진행. 30Hz로 호출."""
        # TODO: 깜빡임 키프레임, idle sway 등 W3에 추가
        pass

    def _render(self) -> None:
        """현재 표정의 비트맵 생성. 자산 파일이 있으면 로드, 없으면 그림."""
        asset_path = ASSETS_DIR / f"{self._current.value}.png"
        if asset_path.exists():
            self._frame = Image.open(asset_path).convert("RGB").resize(
                (settings.lcd_width, settings.lcd_height)
            )
            return
        # 폴백: 코드로 그리기
        self._frame = self._draw_fallback(self._current)

    def _draw_fallback(self, expr: Expression) -> Image.Image:
        """자산 파일 없을 때 절차적 표정.

        W3에 실제 표정 디자인을 PNG로 그려서 assets/face/ 에 두면 자동으로 사용됨.
        """
        img = Image.new("RGB", (settings.lcd_width, settings.lcd_height), (255, 220, 80))
        d = ImageDraw.Draw(img)
        w, h = settings.lcd_width, settings.lcd_height
        cx, cy = w // 2, h // 2

        # 표정별 단순 placeholder
        if expr == Expression.HEADACHE:
            # X자 눈
            for dx, sign in ((-50, 1), (50, -1)):
                d.line((cx + dx - 15, cy - 15, cx + dx + 15, cy + 15), fill=(60, 60, 60), width=4)
                d.line((cx + dx - 15, cy + 15, cx + dx + 15, cy - 15), fill=(60, 60, 60), width=4)
            d.arc((cx - 25, cy + 25, cx + 25, cy + 55), 0, 180, fill=(80, 40, 40), width=4)
        elif expr == Expression.HAPPY:
            d.arc((cx - 70, cy - 30, cx - 30, cy + 10), 200, 340, fill=(60, 60, 60), width=5)
            d.arc((cx + 30, cy - 30, cx + 70, cy + 10), 200, 340, fill=(60, 60, 60), width=5)
            d.arc((cx - 30, cy + 10, cx + 30, cy + 50), 0, 180, fill=(80, 40, 40), width=4)
        elif expr == Expression.SLEEPY or expr == Expression.SLEEP:
            d.line((cx - 60, cy, cx - 30, cy), fill=(60, 60, 60), width=4)
            d.line((cx + 30, cy, cx + 60, cy), fill=(60, 60, 60), width=4)
        else:  # idle/blink/attentive/surprised/error
            d.ellipse((cx - 60, cy - 15, cx - 30, cy + 15), fill=(60, 60, 60))
            d.ellipse((cx + 30, cy - 15, cx + 60, cy + 15), fill=(60, 60, 60))
        return img

    def _present(self) -> None:
        if self._frame is None:
            return
        if self._lcd is not None:
            self._lcd.show(self._frame)
        else:
            log.debug("face_lcd_not_initialized")
