"""ESP32 펌웨어 UART 프로토콜 스모크 테스트.

PCB 없이 DevKit만으로 지금 바로 사용:
  DevKit을 USB로 꽂으면 UART0(GPIO43/44)이 온보드 USB 브릿지로 나오므로
  /dev/ttyUSB0 (또는 macOS /dev/cu.usbserial-*) 에 그대로 붙는다.
  HAT 실장 후에는 --dev /dev/ttyAMA0 으로 동일하게 사용.

사용:
  canduck-smoke --dev /dev/ttyUSB0 --check   # 자동 검증 (CI성 self-check)
  canduck-smoke --dev /dev/ttyUSB0           # 대화형 REPL (>HEAD 20 -10 300 등 직접 입력)

의존성: pyserial (pyserial-asyncio 설치 시 함께 들어옴).
"""
import argparse
import sys
import threading
import time

import serial

RESET_BANNER_WAIT_S = 2.5  # DTR 리셋 후 BOOT 배너 대기


class SmokeSession:
    def __init__(self, dev: str, baud: int) -> None:
        self.ser = serial.Serial(dev, baud, timeout=0.1)
        self.events: list[list[str]] = []
        self._lock = threading.Lock()
        self._stop = threading.Event()
        self._reader = threading.Thread(target=self._read_loop, daemon=True)
        self._reader.start()

    def _read_loop(self) -> None:
        buf = b""
        while not self._stop.is_set():
            try:
                chunk = self.ser.read(64)
            except serial.SerialException:
                break
            if not chunk:
                continue
            buf += chunk
            while b"\n" in buf:
                raw, buf = buf.split(b"\n", 1)
                line = raw.decode("ascii", errors="replace").strip()
                if not line:
                    continue
                print(f"  RX: {line}")
                if line.startswith("<"):
                    parts = line[1:].strip().split()
                    if parts:
                        with self._lock:
                            self.events.append(parts)

    def send(self, cmd_line: str) -> None:
        line = cmd_line if cmd_line.startswith(">") else ">" + cmd_line
        print(f"  TX: {line}")
        self.ser.write((line + "\n").encode("ascii"))

    def wait_event(self, kind: str, timeout_s: float = 3.0) -> list[str] | None:
        """kind와 일치하는 첫 이벤트를 consume해서 반환. 못 받으면 None."""
        deadline = time.monotonic() + timeout_s
        while time.monotonic() < deadline:
            with self._lock:
                for i, ev in enumerate(self.events):
                    if ev[0] == kind:
                        return self.events.pop(i)
            time.sleep(0.02)
        return None

    def flush(self) -> None:
        """수신된 이벤트 큐 비우기 (부팅 배너/dry-run ERR 제거용)."""
        with self._lock:
            self.events.clear()

    def close(self) -> None:
        self._stop.set()
        self.ser.close()


def run_check(s: SmokeSession) -> int:
    """프로토콜 왕복 self-check. 실패 항목이 있으면 exit code 1."""
    time.sleep(RESET_BANNER_WAIT_S)  # 포트 오픈 시 DTR 리셋 → BOOT 배너
    failures: list[str] = []

    def expect(desc: str, ok: bool) -> None:
        print(f"{'PASS' if ok else 'FAIL'}: {desc}")
        if not ok:
            failures.append(desc)

    # BOOT 배너는 포트 오픈 타이밍에 따라 놓칠 수 있어 정보성으로만 표시
    print(f"INFO: BOOT 배너 {'수신' if s.wait_event('BOOT', 1.0) else '미수신 (포트 오픈 전에 지나갔을 수 있음)'}")
    s.flush()  # 부팅 시 dry-run ERR 등 잔여 이벤트 제거 — 이후 검증 오염 방지

    s.send("PING")
    expect("PING → PONG", s.wait_event("PONG") is not None)

    s.send("ENABLE 1")
    expect("ENABLE → ACK", s.wait_event("ACK") is not None)

    s.send("HEAD 20 -10 300")
    expect("HEAD → ACK", s.wait_event("ACK") is not None)

    s.send("ARM L 30 40 300")
    expect("ARM → ACK", s.wait_event("ACK") is not None)

    s.send("LEG R 15 200")
    expect("LEG → ACK", s.wait_event("ACK") is not None)

    s.send("MOTOR 100 -100")
    expect("MOTOR → ACK", s.wait_event("ACK") is not None)

    s.send("MOTOR 999 0")
    expect("MOTOR 범위 초과 → ERR", s.wait_event("ERR") is not None)

    s.send("POSE happy")
    expect("POSE → ACK", s.wait_event("ACK") is not None)
    expect("POSE happy → DONE (시퀀스 완주)", s.wait_event("DONE", 5.0) is not None)

    s.send("POSE nope")
    expect("미정의 POSE → ERR", s.wait_event("ERR") is not None)

    s.send("QUERY vbat")
    expect("QUERY vbat → VBAT", s.wait_event("VBAT") is not None)

    s.send("STOP")
    expect("STOP → ACK", s.wait_event("ACK") is not None)

    s.send("ENABLE 0")
    expect("ENABLE 0 → ACK", s.wait_event("ACK") is not None)

    print(f"\n{'모두 통과' if not failures else f'{len(failures)}건 실패'}")
    return 0 if not failures else 1


def run_repl(s: SmokeSession) -> int:
    print("대화형 모드. 명령 입력 (예: HEAD 20 -10 300 / POSE headache / quit)")
    try:
        while True:
            line = input("> ").strip()
            if not line:
                continue
            if line in ("quit", "exit", "q"):
                return 0
            s.send(line)
            time.sleep(0.3)  # 응답 출력 여유
    except (EOFError, KeyboardInterrupt):
        return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dev", default="/dev/ttyUSB0", help="시리얼 장치 (기본 /dev/ttyUSB0)")
    ap.add_argument("--baud", type=int, default=115200)
    ap.add_argument("--check", action="store_true", help="자동 self-check 실행 후 종료")
    args = ap.parse_args()

    try:
        s = SmokeSession(args.dev, args.baud)
    except serial.SerialException as exc:
        print(f"시리얼 오픈 실패: {exc}", file=sys.stderr)
        print("장치 확인: ls /dev/ttyUSB* /dev/ttyACM* /dev/cu.usbserial-* 2>/dev/null", file=sys.stderr)
        return 2

    try:
        return run_check(s) if args.check else run_repl(s)
    finally:
        s.close()


if __name__ == "__main__":
    sys.exit(main())
