"""마이크 wake-word + 응답 음원.

Porcupine 무료 티어 사용. CANDUCK_PORCUPINE_ACCESS_KEY 환경변수 필요.
W6에 본격 구현.
"""
import asyncio
from collections.abc import Callable
from pathlib import Path

import structlog

from .config import settings

log = structlog.get_logger(__name__)


class VoiceManager:
    def __init__(self, on_wake: Callable[[], None]) -> None:
        self._on_wake = on_wake
        self._task: asyncio.Task | None = None

    async def start(self) -> None:
        if not settings.enable_voice:
            log.info("voice_disabled")
            return
        if not settings.porcupine_access_key:
            log.warning("voice_no_access_key")
            return
        self._task = asyncio.create_task(self._run(), name="voice-wake")

    async def stop(self) -> None:
        if self._task:
            self._task.cancel()

    async def _run(self) -> None:
        try:
            import pvporcupine
            import sounddevice as sd
        except ImportError:
            log.error("voice_deps_missing", hint="pip install pvporcupine sounddevice")
            return

        keyword_path = settings.wake_word_path or None
        try:
            porcupine = pvporcupine.create(
                access_key=settings.porcupine_access_key,
                keyword_paths=[keyword_path] if keyword_path else None,
                keywords=["porcupine"] if not keyword_path else None,
            )
        except Exception:
            log.exception("porcupine_init_failed")
            return

        log.info("voice_wake_listening", frame_length=porcupine.frame_length)
        try:
            stream = sd.RawInputStream(
                samplerate=porcupine.sample_rate,
                blocksize=porcupine.frame_length,
                dtype="int16",
                channels=1,
            )
            stream.start()
            while True:
                pcm, _ = stream.read(porcupine.frame_length)
                idx = porcupine.process(pcm)
                if idx >= 0:
                    log.info("voice_wake_detected")
                    self._on_wake()
                await asyncio.sleep(0)
        finally:
            porcupine.delete()


async def play_wav(path: Path) -> None:
    """간단 WAV 재생. PAM8403 + 스피커로."""
    try:
        import sounddevice as sd
        import soundfile as sf
    except ImportError:
        log.warning("audio_deps_missing")
        return
    data, sr = sf.read(str(path), dtype="float32")
    sd.play(data, sr)
    sd.wait()
