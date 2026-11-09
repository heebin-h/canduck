"""표정 도메인 — Expression 정의 + PIL 렌더링.

표시 백엔드는 분리됨: v1은 tkinter 창 (`display_tk.TkFaceDisplay`).
(LCD는 2026-07-12 품목 심사에서 탈락 — GC9A01/pygame/spidev 경로 제거.)

자산 PNG가 assets/face/{expr}.png 에 있으면 사용, 없으면 절차적 폴백(Y2K 파스텔 스타일).
"""
import math
from enum import Enum
from pathlib import Path

import structlog
from PIL import Image, ImageDraw, ImageFont

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


# ── 절차적 폴백: Y2K 파스텔 스타일 ─────────────────────────────────────────
# 좌표는 240×240 기준·중심 원점(-120~120). _SS배 캔버스에 그린 뒤 LANCZOS 축소(안티앨리어싱).
_SS = 4
_INK = (82, 54, 104, 255)            # 딥 플럼 — 순흑 대신 부드러운 윤곽
_INK_NIGHT = (255, 243, 250, 255)    # sleep(밤 배경)용 크림
_WHITE = (255, 255, 255, 255)
_BLUSH = (255, 138, 176, 105)
_TONGUE = (255, 150, 172, 255)
_SWEAT = (150, 205, 255, 235)
_HEART = (255, 118, 164, 235)
_CHROME_DOTS = ((255, 158, 196, 255), (255, 214, 120, 255), (140, 220, 196, 255))

# (위, 아래) 세로 그라데이션
_BG_DEFAULT = ((255, 221, 236), (212, 226, 255))
_BG = {
    Expression.HAPPY: ((255, 236, 205), (255, 204, 228)),
    Expression.SLEEPY: ((240, 228, 255), (204, 214, 248)),
    Expression.SLEEP: ((150, 144, 214), (82, 88, 158)),
    Expression.HEADACHE: ((255, 228, 214), (236, 214, 255)),
    Expression.ERROR: ((236, 234, 244), (206, 204, 224)),
}

_EYE_X = 40  # 좌우 눈 중심 x (±)


class _Pen:
    """240 기준 중심좌표 → 슈퍼샘플 캔버스 픽셀 변환 + 자주 쓰는 도형."""

    def __init__(self, draw: ImageDraw.ImageDraw, k: float, cx: float, cy: float) -> None:
        self.d, self.k, self.cx, self.cy = draw, k, cx, cy

    def xy(self, x: float, y: float) -> tuple[float, float]:
        return (self.cx + x * self.k, self.cy + y * self.k)

    def box(self, x0: float, y0: float, x1: float, y1: float) -> tuple[float, float, float, float]:
        return (*self.xy(x0, y0), *self.xy(x1, y1))

    def w(self, v: float) -> int:
        return max(1, round(v * self.k))

    def circle(self, x: float, y: float, r: float, fill) -> None:
        self.d.ellipse(self.box(x - r, y - r, x + r, y + r), fill=fill)

    def line(self, pts: list[tuple[float, float]], width: float, fill) -> None:
        """둥근 끝(round cap) 폴리라인."""
        self.d.line([self.xy(*p) for p in pts], fill=fill, width=self.w(width), joint="curve")
        for p in (pts[0], pts[-1]):
            self.circle(*p, width / 2, fill)

    def arc(self, x: float, y: float, rx: float, ry: float, a0: float, a1: float, width: float, fill) -> None:
        """둥근 끝 타원 호. 각도는 PIL 규약(3시 방향 0°, 시계방향)."""
        self.d.arc(self.box(x - rx, y - ry, x + rx, y + ry), a0, a1, fill=fill, width=self.w(width))
        # PIL은 stroke를 bbox 안쪽으로 그림 → cap은 (반지름 - width/2) 위치
        for a in (a0, a1):
            t = math.radians(a)
            self.circle(x + (rx - width / 2) * math.cos(t), y + (ry - width / 2) * math.sin(t), width / 2, fill)


def _gradient(size: tuple[int, int], top: tuple, bottom: tuple) -> Image.Image:
    mask = Image.linear_gradient("L").resize(size)  # 위 0 → 아래 255
    return Image.composite(Image.new("RGB", size, bottom), Image.new("RGB", size, top), mask)


def _sparkle(p: _Pen, x: float, y: float, r: float, fill=_WHITE) -> None:
    """4각 반짝이 ✦."""
    i = r * 0.28
    pts = [(x, y - r), (x + i, y - i), (x + r, y), (x + i, y + i),
           (x, y + r), (x - i, y + i), (x - r, y), (x - i, y - i)]
    p.d.polygon([p.xy(*pt) for pt in pts], fill=fill)


def _heart(p: _Pen, x: float, y: float, r: float, fill=_HEART) -> None:
    p.circle(x - r * 0.5, y - r * 0.2, r * 0.56, fill)
    p.circle(x + r * 0.5, y - r * 0.2, r * 0.56, fill)
    p.d.polygon([p.xy(x - r * 1.04, y + r * 0.02), p.xy(x + r * 1.04, y + r * 0.02), p.xy(x, y + r * 1.1)], fill=fill)


def _glossy_eye(p: _Pen, x: float, y: float, rx: float, ry: float) -> None:
    """광택 하이라이트 2점이 들어간 동그란 눈."""
    p.d.ellipse(p.box(x - rx, y - ry, x + rx, y + ry), fill=_INK)
    p.circle(x - rx * 0.3, y - ry * 0.36, rx * 0.4, _WHITE)
    p.circle(x + rx * 0.36, y + ry * 0.4, rx * 0.17, _WHITE)


def _blush(p: _Pen, fill=_BLUSH) -> None:
    for sx in (-1, 1):
        p.d.ellipse(p.box(sx * 64 - 13, 16 - 7, sx * 64 + 13, 16 + 7), fill=fill)


def _cat_mouth(p: _Pen, y: float = 28, ink=_INK) -> None:
    """ω 입."""
    p.arc(-6, y, 6, 5, 0, 180, 3, ink)
    p.arc(6, y, 6, 5, 0, 180, 3, ink)


def _chrome(p: _Pen, night: bool) -> None:
    """2000년대 초 OS 창 느낌의 얇은 둥근 테두리 + 좌상단 3색 점."""
    edge = (255, 255, 255, 90 if night else 150)
    p.d.rounded_rectangle(p.box(-110, -110, 110, 110), radius=round(28 * p.k), outline=edge, width=p.w(2.5))
    for i, c in enumerate(_CHROME_DOTS):
        p.circle(-92 + i * 10, -97, 3.2, c)


def _face_idle(p: _Pen) -> None:
    for sx in (-1, 1):
        _glossy_eye(p, sx * _EYE_X, -6, 13, 16)
    _blush(p)
    _cat_mouth(p)
    _sparkle(p, 80, -72, 10)
    _sparkle(p, 96, -50, 4.5)
    _sparkle(p, -84, 66, 6)


def _face_blink(p: _Pen) -> None:
    for sx in (-1, 1):
        p.arc(sx * _EYE_X, -12, 13, 9, 20, 160, 4, _INK)
    _blush(p)
    _cat_mouth(p)
    _sparkle(p, 80, -72, 10)
    _sparkle(p, 96, -50, 4.5)
    _sparkle(p, -84, 66, 6)


def _face_happy(p: _Pen) -> None:
    for sx in (-1, 1):
        p.arc(sx * _EYE_X, -2, 14, 12, 200, 340, 4.5, _INK)  # ^ ^
    _blush(p, (255, 128, 168, 140))
    p.d.chord(p.box(-15, 20, 15, 46), 0, 180, fill=_INK)
    p.d.chord(p.box(-9, 30, 9, 44), 0, 180, fill=_TONGUE)
    _heart(p, 80, -64, 9)
    _heart(p, -86, -56, 6)
    _sparkle(p, 92, 42, 5)
    _sparkle(p, -92, 54, 7)


def _face_sleepy(p: _Pen) -> None:
    for sx in (-1, 1):
        x = sx * _EYE_X
        p.d.ellipse(p.box(x - 13, -16, x + 13, 12), fill=_INK)
        # 무거운 눈꺼풀: 가운데가 살짝 처진 곡선 위쪽을 지움(투명 덮어쓰기).
        # 일자는 시큰둥, 바깥 기울임은 울상으로 읽혀서 대칭 곡선으로.
        lid = [(x + dx, -1 + 3 * (1 - (dx / 16) ** 2)) for dx in range(-16, 17, 2)]
        p.d.polygon([p.xy(x - 16, -30), p.xy(x + 16, -30)] + [p.xy(*pt) for pt in reversed(lid)], fill=(0, 0, 0, 0))
        p.line(lid, 3.5, _INK)
        p.circle(x - 4, 6, 2.4, _WHITE)
    _blush(p, (255, 138, 176, 70))
    p.d.ellipse(p.box(-5, 26, 5, 38), outline=_INK, width=p.w(3))  # 하품
    _sparkle(p, 84, -70, 6, (255, 255, 255, 200))


def _face_sleep(p: _Pen) -> None:
    for sx in (-1, 1):
        p.arc(sx * _EYE_X, -10, 13, 8, 20, 160, 4, _INK_NIGHT)
    _blush(p, (255, 138, 176, 60))
    p.d.ellipse(p.box(-4, 28, 4, 36), outline=_INK_NIGHT, width=p.w(2.5))
    for x, y, s in ((58, -56, 9), (76, -82, 14)):  # z Z
        p.line([(x, y), (x + s, y), (x, y + s), (x + s, y + s)], s * 0.2, _INK_NIGHT)
    for x, y, r in ((-86, -70, 6), (-70, -86, 3), (92, 36, 4), (-90, 60, 5)):
        _sparkle(p, x, y, r, (255, 246, 214, 210))


def _face_headache(p: _Pen) -> None:
    for sx in (-1, 1):
        x, y, r = sx * _EYE_X, -6, 10
        p.line([(x - r, y - r), (x + r, y + r)], 4.5, _INK)
        p.line([(x - r, y + r), (x + r, y - r)], 4.5, _INK)
    wave = [(x, 34 + 3.5 * math.sin(x / 16 * 2 * math.pi)) for x in range(-16, 17, 2)]
    p.line(wave, 3.5, _INK)
    p.circle(74, -56, 7, _SWEAT)  # 땀방울
    p.d.polygon([p.xy(74 - 6.6, -58), p.xy(74 + 6.6, -58), p.xy(74, -73)], fill=_SWEAT)
    p.circle(71.5, -57.5, 2, _WHITE)
    _blush(p, (255, 138, 176, 70))


def _face_surprised(p: _Pen) -> None:
    for sx in (-1, 1):
        _glossy_eye(p, sx * _EYE_X, -8, 16, 20)
    _blush(p)
    p.d.ellipse(p.box(-7, 24, 7, 40), outline=_INK, width=p.w(3.5))  # o
    for sx in (-1, 1):  # 놀람 선
        p.line([(sx * 70, -62), (sx * 78, -74)], 3, _INK)
        p.line([(sx * 58, -70), (sx * 62, -84)], 3, _INK)
    _sparkle(p, 92, 40, 6)


def _face_attentive(p: _Pen) -> None:
    for sx in (-1, 1):
        _glossy_eye(p, sx * _EYE_X, -12, 14, 18)  # 살짝 위를 봄
    _blush(p)
    p.arc(0, 22, 9, 7, 20, 160, 3.5, _INK)
    _sparkle(p, 84, -74, 9)
    _sparkle(p, -80, -66, 5)


def _face_error(p: _Pen) -> None:
    # 왼눈 "!"
    p.d.rounded_rectangle(p.box(-44, -28, -36, -2), radius=round(4 * p.k), fill=_INK)
    p.circle(-40, 7, 4.5, _INK)
    # 오른눈 "?"
    p.arc(_EYE_X, -18, 10, 10, 180, 450, 4, _INK)
    p.line([(_EYE_X, -11), (_EYE_X, -3)], 4, _INK)
    p.circle(_EYE_X, 7, 4.5, _INK)
    p.line([(-8, 34), (8, 34)], 3, _INK)
    # 하단 작은 라벨
    p.d.rounded_rectangle(p.box(-30, 58, 30, 78), radius=round(10 * p.k), fill=(255, 255, 255, 180))
    try:
        font = ImageFont.load_default(size=round(11 * p.k))
    except TypeError:  # Pillow < 10.1: size 인자 없음
        font = ImageFont.load_default()
    p.d.text(p.xy(0, 68), "oops!", fill=_INK, font=font, anchor="mm")


_FACES = {
    Expression.IDLE: _face_idle,
    Expression.BLINK: _face_blink,
    Expression.HAPPY: _face_happy,
    Expression.SLEEPY: _face_sleepy,
    Expression.SLEEP: _face_sleep,
    Expression.HEADACHE: _face_headache,
    Expression.SURPRISED: _face_surprised,
    Expression.ATTENTIVE: _face_attentive,
    Expression.ERROR: _face_error,
}


def _draw_fallback(expr: Expression, size: tuple[int, int]) -> Image.Image:
    """자산 파일 없을 때 절차적 표정 (Y2K 파스텔: 그라데이션 배경·광택 눈·볼터치·반짝이).

    assets/face/{expr}.png 를 두면 그쪽이 우선.
    """
    w, h = size
    cw, ch = w * _SS, h * _SS
    top, bottom = _BG.get(expr, _BG_DEFAULT)
    base = _gradient((cw, ch), top, bottom).convert("RGBA")
    layer = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    p = _Pen(ImageDraw.Draw(layer), _SS * min(w, h) / 240, cw / 2, ch / 2)
    _chrome(p, night=expr == Expression.SLEEP)
    _FACES.get(expr, _face_idle)(p)
    out = Image.alpha_composite(base, layer).convert("RGB")
    return out.resize((w, h), Image.Resampling.LANCZOS)


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
