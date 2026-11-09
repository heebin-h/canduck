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
        self._on_disconnect: Callable[[], Awaitable[None]] | None = None

    def add_handler(self, handler: EventHandler) -> None:
        self._handlers.append(handler)

    def set_disconnect_handler(self, handler: Callable[[], Awaitable[None]]) -> None:
        """EOF(장치 분리 등) 시 1회 호출. 재연결은 하지 않음 — 호출 측이 결정."""
        self._on_disconnect = handler

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

    async def _notify_disconnect(self) -> None:
        if self._on_disconnect:
            try:
                await self._on_disconnect()
            except Exception:
                log.exception("uart_disconnect_handler_failed")

    async def _read_loop(self) -> None:
        assert self._reader is not None
        while True:
            try:
                raw = await self._reader.readline()
            except (asyncio.CancelledError, GeneratorExit):
                raise
            except ValueError as exc:
                # 64KiB 초과 라인(LimitOverrun) — StreamReader가 버퍼를 비웠으므로 복구 가능
                log.warning("uart_line_too_long", error=str(exc))
                continue
            except Exception as exc:
                # 장치 분리 시 pyserial-asyncio는 reader에 SerialException을 set_exception →
                # 이후 readline()이 같은 예외를 영구히 재발생. 재시도는 무한 로그 루프뿐이므로 EOF와 동일 처리.
                log.error("uart_read_failed", device=settings.uart_device, error=str(exc))
                await self._notify_disconnect()
                return
            if not raw:
                # readline()이 b""면 EOF(포트 닫힘) — sleep 후 재시도하면 빈 루프만 돌고 장애가 묻힌다.
                log.error("uart_eof", device=settings.uart_device)
                await self._notify_disconnect()
                return
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
