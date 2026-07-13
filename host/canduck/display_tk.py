"""tkinter 표정 표시 백엔드.

LCD 탈락(2026-07-12 품목 심사)으로 v1 표정 표시는 tkinter 창으로 대체.
- Tk는 전용 스레드에서 mainloop 실행, 프레임은 thread-safe Queue로 전달.
- headless(SSH, DISPLAY 없음)면 경고만 남기고 no-op — 데몬은 정상 동작.

RPi OS에는 `sudo apt install python3-tk` 필요 (데스크탑 이미지엔 기본 포함).
"""
import queue
import threading

import structlog
from PIL import Image

from .config import settings

log = structlog.get_logger(__name__)

_POLL_MS = 33  # ~30fps


class TkFaceDisplay:
    def __init__(self) -> None:
        self._frames: queue.Queue[Image.Image | None] = queue.Queue(maxsize=4)
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        self._thread = threading.Thread(target=self._run, name="face-tk", daemon=True)
        self._thread.start()

    def show(self, frame: Image.Image) -> None:
        try:
            self._frames.put_nowait(frame)
        except queue.Full:
            # 표시가 밀리면 오래된 프레임은 버림 (최신 표정 우선)
            try:
                self._frames.get_nowait()
                self._frames.put_nowait(frame)
            except queue.Empty:
                pass

    def stop(self) -> None:
        if self._thread and self._thread.is_alive():
            self._frames.put(None)  # 종료 sentinel
            self._thread.join(timeout=2.0)

    def _run(self) -> None:
        import sys
        if sys.platform == "darwin":
            # macOS AppKit은 NSWindow 생성을 메인 스레드로 강제 — 워커 스레드 Tk는
            # NSInternalInconsistencyException으로 프로세스가 통째로 죽음 (실측).
            # ponytail: darwin은 표시 생략. macOS 개발 표시가 필요해지면 Tk 서브프로세스 뷰어로.
            log.warning("tk_darwin_unsupported", hint="RPi/Linux에서만 표정 창 표시")
            return
        try:
            import tkinter as tk
            from PIL import ImageTk
        except ImportError:
            log.warning("tk_unavailable", hint="sudo apt install python3-tk")
            return

        try:
            root = tk.Tk()
        except tk.TclError as exc:  # DISPLAY 없음 등
            log.warning("tk_no_display", error=str(exc))
            return

        w = settings.face_width * settings.face_scale
        h = settings.face_height * settings.face_scale
        root.title("canduck")
        root.geometry(f"{w}x{h}")
        root.resizable(False, False)
        label = tk.Label(root, bd=0)
        label.pack(fill="both", expand=True)
        photo_ref: list = [None]  # PhotoImage GC 방지 참조 홀더

        def poll() -> None:
            try:
                frame = self._frames.get_nowait()
            except queue.Empty:
                root.after(_POLL_MS, poll)
                return
            if frame is None:
                root.destroy()
                return
            img = frame.resize((w, h), Image.NEAREST)
            photo = ImageTk.PhotoImage(img)
            photo_ref[0] = photo
            label.configure(image=photo)
            root.after(_POLL_MS, poll)

        root.after(_POLL_MS, poll)
        # 사용자가 창을 닫아도 데몬은 계속 — 표시만 사라짐
        root.protocol("WM_DELETE_WINDOW", root.destroy)
        try:
            root.mainloop()
        finally:
            log.info("tk_display_closed")
