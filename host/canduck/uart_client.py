"""ESP32-S3 펌웨어와 UART 라인 프로토콜로 통신.

명세: docs/architecture.md 의 UART 프로토콜 섹션.
"""
import asyncio
from collections.abc import Awaitable, Callable
from dataclasses import dataclass

import serial_asyncio
import structlog

from .config import settings

log = structlog.get_logger(__name__)

EventHandler = Callable[["UartEvent"], Awaitable[None]]


@dataclass(slots=True)
class UartEvent:
    kind: str           # "ACK", "DONE", "ERR", "TAP", "SHAKE", "TOUCH", "VBAT", "BOOT", "PONG"
    args: list[str]


class UartClient:
    def __init__(self) -> None:
        self._reader: asyncio.StreamReader | None = None
        self._writer: asyncio.StreamWriter | None = None
        self._handlers: list[EventHandler] = []
        self._read_task: asyncio.Task | None = None

    def add_handler(self, handler: EventHandler) -> None:
        self._handlers.append(handler)

    async def connect(self) -> None:
        self._reader, self._writer = await serial_asyncio.open_serial_connection(
            url=settings.uart_device, baudrate=settings.uart_baud
        )
        log.info("uart_connected", device=settings.uart_device, baud=settings.uart_baud)
        self._read_task = asyncio.create_task(self._read_loop(), name="uart-reader")

    async def close(self) -> None:
        if self._read_task:
            self._read_task.cancel()
        if self._writer:
            self._writer.close()
            await self._writer.wait_closed()

    async def send(self, cmd: str, *args: object) -> None:
        if not self._writer:
            raise RuntimeError("uart not connected")
        line = ">" + " ".join([cmd, *(str(a) for a in args)]) + "\n"
        self._writer.write(line.encode("ascii"))
        await self._writer.drain()
        log.debug("uart_tx", line=line.strip())

    async def _read_loop(self) -> None:
        assert self._reader is not None
        while True:
            try:
                raw = await self._reader.readline()
            except (asyncio.CancelledError, GeneratorExit):
                raise
            except Exception as exc:
                log.exception("uart_read_error", error=str(exc))
                await asyncio.sleep(0.5)
                continue
            if not raw:
                await asyncio.sleep(0.05)
                continue
            try:
                line = raw.decode("ascii", errors="replace").strip()
            except Exception:
                continue
            if not line.startswith("<"):
                continue
            parts = line[1:].strip().split()
            if not parts:
                continue
            event = UartEvent(kind=parts[0], args=parts[1:])
            log.debug("uart_rx", kind=event.kind, args=event.args)
            for handler in self._handlers:
                try:
                    await handler(event)
                except Exception:
                    log.exception("uart_handler_failed", kind=event.kind)
