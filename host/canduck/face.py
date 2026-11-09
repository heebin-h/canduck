"""표정 도메인 — Expression 정의 + PIL 렌더링.

표시 백엔드는 분리됨: v1은 tkinter 창 (`display_tk.TkFaceDisplay`).
(LCD는 2026-07-12 품목 심사에서 탈락 — GC9A01/pygame/spidev 경로 제거.)

자산 PNG가 assets/face/{expr}.png 에 있으면 사용, 없으면 절차적 폴백.
"""
from enum import Enum
from pathlib import Path

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


def render_expression(expr: Expression) -> Image.Image:
    """현재 표정의 비트맵 생성. 자산 파일이 있으면 로드, 없으면 그림."""
    asset_path = ASSETS_DIR / f"{expr.value}.png"
    size = (settings.face_width, settings.face_height)
    if asset_path.exists():
        return Image.open(asset_path).convert("RGB").resize(size)
    return _draw_fallback(expr, size)


def _draw_fallback(expr: Expression, size: tuple[int, int]) -> Image.Image:
    """자산 파일 없을 때 절차적 표정.

    W3에 실제 표정 디자인을 PNG로 그려서 assets/face/ 에 두면 자동으로 사용됨.
    """
    img = Image.new("RGB", size, (255, 220, 80))
    d = ImageDraw.Draw(img)
    w, h = size
    cx, cy = w // 2, h // 2

    if expr == Expression.HEADACHE:
        # X자 눈
        for dx in (-50, 50):
            d.line((cx + dx - 15, cy - 15, cx + dx + 15, cy + 15), fill=(60, 60, 60), width=4)
            d.line((cx + dx - 15, cy + 15, cx + dx + 15, cy - 15), fill=(60, 60, 60), width=4)
        d.arc((cx - 25, cy + 25, cx + 25, cy + 55), 0, 180, fill=(80, 40, 40), width=4)
    elif expr == Expression.HAPPY:
        d.arc((cx - 70, cy - 30, cx - 30, cy + 10), 200, 340, fill=(60, 60, 60), width=5)
        d.arc((cx + 30, cy - 30, cx + 70, cy + 10), 200, 340, fill=(60, 60, 60), width=5)
        d.arc((cx - 30, cy + 10, cx + 30, cy + 50), 0, 180, fill=(80, 40, 40), width=4)
    elif expr in (Expression.SLEEPY, Expression.SLEEP):
        d.line((cx - 60, cy, cx - 30, cy), fill=(60, 60, 60), width=4)
        d.line((cx + 30, cy, cx + 60, cy), fill=(60, 60, 60), width=4)
    else:  # idle/blink/attentive/surprised/error
        d.ellipse((cx - 60, cy - 15, cx - 30, cy + 15), fill=(60, 60, 60))
        d.ellipse((cx + 30, cy - 15, cx + 60, cy + 15), fill=(60, 60, 60))
    return img


class Face:
    """표정 상태 관리 + 렌더 → 표시 백엔드 전달."""

    def __init__(self, display=None) -> None:
        self._current: Expression = Expression.IDLE
        self._display = display

    def start(self) -> None:
        if self._display is not None:
            self._display.start()
        self.set_expression(Expression.IDLE, force=True)

    def stop(self) -> None:
        if self._display is not None:
            self._display.stop()

    def set_expression(self, expr: Expression, force: bool = False) -> None:
        if expr == self._current and not force:
            return
        log.info("face_expression", expr=expr.value)
        self._current = expr
        if self._display is not None:
            self._display.show(render_expression(expr))
