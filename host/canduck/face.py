"""표정 도메인 — Expression 정의 + PIL 렌더링.

표시 백엔드는 분리됨: v1은 tkinter 창 (`display_tk.TkFaceDisplay`).
(LCD는 2026-07-12 품목 심사에서 탈락 — GC9A01/pygame/spidev 경로 제거.)

자산 PNG가 assets/face/{expr}.png 에 있으면 사용, 없으면 절차적 폴백(도트 LCD 스타일).
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


# ── 절차적 폴백: 도트 LCD 스타일 ─────────────────────────────────────────
# 레퍼런스: i-mode 이모지(1999, 12×12 도트), 다마고치(1996, 32×16 도트 LCD), 싸이월드 픽셀 미니미.
# 20×20 논리 도트 그리드에 ASCII 스프라이트를 찍고, 도트 사이 틈 + 오프셋 그림자로 매트릭스 LCD 질감.
# 스프라이트 문자: '.' 꺼짐, '#' 잉크, 'w' 하이라이트, 'o' 코랄, 'b' 블루, 'y' 별.
_GRID = 20

_DAY = {
    "bg": (244, 239, 230), "off": (239, 233, 222), "shadow": (214, 205, 190),
    "#": (43, 43, 58), "w": (255, 255, 255), "o": (255, 111, 97), "b": (90, 169, 230), "y": (255, 200, 87),
}
_NIGHT = {
    "bg": (43, 43, 58), "off": (48, 48, 64), "shadow": (28, 28, 40),
    "#": (244, 239, 230), "w": (255, 255, 255), "o": (214, 104, 100), "b": (90, 169, 230), "y": (255, 214, 120),
}

# 스프라이트 (행 문자열 목록)
_EYE = [".##.", "#w##", "####", "####", ".##."]
_EYE_CLOSED = ["#..#", ".##."]          # ‿
_EYE_ARCH = [".##.", "#..#"]            # ^
_EYE_LID = ["####", "####", ".##."]     # 반쯤 감김
_EYE_X = ["#.#", ".#.", "#.#"]
_BLUSH = [".ooo", "ooo."]               # 비스듬한 볼터치
_M_CAT = ["#.##.#", ".#..#."]           # ω
_M_SMILE = ["#..#", ".##."]
_M_OPEN = ["######", "#oooo#", ".####."]
_M_O = [".##.", "#..#", "#..#", ".##."]
_M_DOT = ["##", "##"]
_M_WAVE = [".##..##.", "#..##..#"]
_M_FLAT = ["####"]
_HEART = ["oo.oo", "ooooo", ".ooo.", "..o.."]
_HEART_S = ["o.o", "ooo", ".o."]
_PLUS = [".o.", "ooo", ".o."]
_DROP = [".b.", "bbb", "bbb"]
_SHOCK = ["#.", ".#"]
_TICK = ["#", "#"]
_Z_S = ["###", ".#.", "###"]
_Z_L = ["####", "..#.", ".#..", "####"]
_EXCL = ["##", "##", "##", "##", "..", "##"]
_QUES = [".##.", "#..#", "..#.", ".#..", "....", ".#.."]
_STAR = ["y"]

_L, _R = 4, 12  # 4폭 눈 슬롯 좌측 x (좌우 대칭: 19 - 7 = 12)
_CHEEKS = [(_BLUSH, 1, 11), (_BLUSH, 15, 11)]

_FACES: dict[Expression, list] = {
    Expression.IDLE: [(_EYE, _L, 6), (_EYE, _R, 6), *_CHEEKS, (_M_CAT, 7, 12)],
    Expression.BLINK: [(_EYE_CLOSED, _L, 8), (_EYE_CLOSED, _R, 8), *_CHEEKS, (_M_CAT, 7, 12)],
    Expression.HAPPY: [(_EYE_ARCH, _L, 7), (_EYE_ARCH, _R, 7), *_CHEEKS, (_M_OPEN, 7, 12),
                       (_HEART, 14, 1), (_HEART_S, 2, 3)],
    Expression.SLEEPY: [(_EYE_LID, _L, 8), (_EYE_LID, _R, 8), *_CHEEKS, (_M_DOT, 9, 13), (_Z_S, 15, 3)],
    Expression.SLEEP: [(_EYE_CLOSED, _L, 8), (_EYE_CLOSED, _R, 8), *_CHEEKS, (["##"], 9, 13),
                       (_Z_S, 12, 4), (_Z_L, 15, 1),
                       (_STAR, 2, 3), (_STAR, 5, 1), (_STAR, 17, 16), (_STAR, 2, 16)],
    Expression.HEADACHE: [(_EYE_X, 5, 7), (_EYE_X, 12, 7), (_M_WAVE, 6, 12), (_DROP, 15, 2)],
    Expression.SURPRISED: [(_EYE, _L, 6), (_EYE, _R, 6), *_CHEEKS, (_M_O, 8, 12),
                           (_SHOCK, 2, 3), (_SHOCK, 16, 3, True), (_TICK, 5, 1), (_TICK, 14, 1)],
    Expression.ATTENTIVE: [(_EYE, _L, 5), (_EYE, _R, 5), *_CHEEKS, (_M_SMILE, 8, 12), (_PLUS, 15, 2)],
    Expression.ERROR: [(_EXCL, 5, 5), (_QUES, _R, 5), (_M_FLAT, 8, 13)],
}


def _compose(stamps: list) -> list[list[str]]:
    grid = [["."] * _GRID for _ in range(_GRID)]
    for stamp in stamps:
        sprite, x, y = stamp[:3]
        mirror = len(stamp) > 3 and stamp[3]
        for j, row in enumerate(sprite):
            for i, ch in enumerate(row[::-1] if mirror else row):
                if ch != ".":
                    grid[y + j][x + i] = ch
    return grid


def _draw_fallback(expr: Expression, size: tuple[int, int]) -> Image.Image:
    """자산 파일 없을 때 절차적 표정 — 도트 LCD 스타일 (sleep은 반전 팔레트).

    assets/face/{expr}.png 를 두면 그쪽이 우선.
    """
    w, h = size
    cell = max(2, min(w, h) // _GRID)
    ox, oy = (w - cell * _GRID) // 2, (h - cell * _GRID) // 2
    pal = _NIGHT if expr == Expression.SLEEP else _DAY
    grid = _compose(_FACES.get(expr, _FACES[Expression.IDLE]))
    img = Image.new("RGB", size, pal["bg"])
    d = ImageDraw.Draw(img)
    gap = max(1, cell // 5)   # 도트 사이 틈 — 매트릭스 LCD 질감
    shadow = max(1, cell // 5)

    def dot(gx: int, gy: int, color: tuple, off: int = 0) -> None:
        x0, y0 = ox + gx * cell + off, oy + gy * cell + off
        d.rectangle((x0, y0, x0 + cell - gap - 1, y0 + cell - gap - 1), fill=color)

    for gy in range(_GRID):
        for gx in range(_GRID):
            dot(gx, gy, pal["off"])
    lit = [(gx, gy, ch) for gy, row in enumerate(grid) for gx, ch in enumerate(row) if ch != "."]
    for gx, gy, _ in lit:
        dot(gx, gy, pal["shadow"], shadow)
    for gx, gy, ch in lit:
        dot(gx, gy, pal[ch])
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
