# PR — W0-T02n: 펌웨어 첫 빌드 수정 + 코드 리뷰 반영 + stale 문서 정합화 + 후속 리뷰 반영

- **Branch**: `w0/t02n-poses-include-fix` → `main`
- **Date**: 2026-11-09
- **Base**: `main` (`ec86be2`, PR #5 머지)
- **규모**: 커밋 목록은 `git log origin/main..HEAD` (2026-11-09 7개 + 2026-11-10 후속)

## What
1. **펌웨어 첫 빌드 실패 수정** — PR #5의 코드 초안은 빌드한 적이 없었고, 처음 `pio run`을 돌리자 `poses.cpp`에서 컴파일 에러가 났다. include 1줄로 수정.
2. **전체 코드 리뷰 지적 반영** — 펌웨어(서보 점프·입력 검증·DONE 포맷)와 호스트(FSM이 한 번도 전이하지 못하던 버그, 고착 상태, ERROR 안전, UART 단절).
3. **stale 문서 정합화 + 현황 점검 기록** — 2026-07-12 확정 사항(RPi4·LCD 탈락·JLC 어셈블리)과 실제 프로토콜을 문서에 반영. 3.5개월 정체 후 재진입 시점의 현황 보고서.
4. **후속 리뷰 반영 (2026-11-10)** — 2번의 UART 단절 수정이 실제 장치 분리 경로에서는 동작하지 않던 문제, headache/happy 고착, 표정 창 기본 비활성 결정.

## Files
**firmware**
- `src/poses.cpp` — `#include "pins.h"` 추가, DONE을 `POSE <name>` 포맷으로
- `src/servo_ctrl.cpp` — 현재 보간 위치에서 출발, STOP 시 상태 리셋, ARM/LEG 범위 검사
- `src/comm.cpp` — `strtol` 엄격 파싱, 라인 오버플로 시 `\n`까지 폐기

**host**
- `canduck/fsm.py` — structlog `event=` 충돌 수정, surprised/listening 타이머 복귀, headache/happy DONE 미수신 타임아웃
- `canduck/daemon.py` — 늦은 DONE 무시, ERROR 시 STOP+ENABLE 0, ERROR 중 BOOT 재활성화 금지, UART 단절 → exit 1(stop 태스크 참조 보관), 부팅 idle 포즈
- `canduck/uart_client.py` — EOF + 장치 분리 예외(SerialException) 감지 → disconnect 콜백. 64KiB 초과 라인(ValueError)은 계속
- `canduck/config.py` — `surprised_sec`, `listening_sec`, `pose_done_timeout_sec`(15초), `enable_face` 기본 False
- `canduck/face.py`, `canduck/display_tk.py` — 절차적 폴백을 도트 LCD 스타일로, 자산 PNG·창 확대 NEAREST (창은 기본 off)

**docs / hardware**
- `docs/architecture.md`, `docs/roadmap.md`, `hardware/parts.md`, `README.md`, `host/README.md`, `firmware/README.md`, `host/systemd/canduck.env.example`, `host/pyproject.toml` — stale 정합화 + 후속 리뷰 반영
- `docs/reports/W0-T02m-status.md` (new) — 현황 점검 + §6 빌드 검증 + §7 코드 리뷰 결과
- `docs/pr/w0-t02d-handoff-update_2026-11-09-merge-comment.md` (new) — PR #5 머지 전 정리 comment 원본
- `docs/pr/w0-t02n-poses-include-fix_2026-11-09.md` (new) — 이 PR 본문
- `docs/logs/session-2026-11-09.md`, `docs/logs/session-2026-11-10.md` (new) — 세션 로그

## 원인 / 결함 설명

### 1. 펌웨어 빌드 실패
```
src/poses.cpp:27:10: error: 'CH_HEAD_YAW' was not declared in this scope
... (CH_HEAD_PITCH / CH_ARM_* / CH_LEG_* 동일, 27~94행)
*** [.pio/build/esp32-s3-devkit/src/poses.cpp.o] Error 1
```
`CH_*`는 `include/pins.h`에 정의돼 있다. 그런데 `poses.cpp`가 include하는 `poses.h`·`servo_ctrl.h`·`comm.h`는 `<Arduino.h>`만 포함한다. 다른 TU는 `pins.h`를 직접 include하거나(`main`/`motor`/`servo_ctrl`) `vbat.h`를 통해 받는다(`comm`).

### 2. 호스트 FSM 전이 불가 (가장 큰 결함)
`fsm.py`의 `log.info("fsm_transition", ..., event=event.value)`에서 `event`는 structlog bound logger의 첫 위치 인자 이름이다. 그래서 매번 `TypeError: ... got multiple values for argument 'event'`가 났고, `self.state` 대입 전이라 **어떤 이벤트로도 상태가 바뀌지 않았다**. 호출 측 예외 처리(uart handler)가 이 에러를 삼켜 로그에만 남았다. kwarg를 `trigger`로 바꿨다.

### 3. 그 외
| 영역 | 결함 | 수정 |
|---|---|---|
| fw servo | 새 명령이 직전 *target*에서 출발한다. STOP은 출력만 0으로 하고 상태는 남긴다 → STOP 후 첫 명령, 또는 보간 중 새 포즈 시작 시 서보가 순간 점프 | 현재 보간 위치에서 출발, STOP 시 채널 상태 리셋 |
| fw comm | `atoi`가 비숫자는 0으로 통과시키고, int16 랩어라운드(예: 65566 → 30)로 범위 검사를 통과한다. ARM/LEG는 범위 검사 없이 clamp 후 ACK | `strtol` 엄격 파싱 → ParseError, ARM/LEG도 OutOfRange |
| fw comm | 오버플로 라인의 꼬리가 새 라인으로 처리되고, 127바이트마다 ERR이 반복된다 | `\n`까지 폐기 |
| fw poses | DONE 포맷 `< DONE idle` ≠ 명세 `< DONE POSE idle` | 명세대로 |
| host fsm | surprised/listening은 포즈가 없어 DONE이 오지 않는다 → 다음 외부 이벤트까지 고착 | 1초/5초 타이머로 idle 복귀 (env 설정) |
| host daemon | 전이 직전 포즈의 늦은 DONE이 새 상태를 바로 idle로 되돌린다 | 현재 상태 포즈가 아닌 DONE은 무시 |
| host daemon | ERROR(배터리 critical)에서 서보 토크가 유지된다. brown-out 리셋 후 BOOT에 ENABLE 1을 재전송한다 | ERROR 진입 시 STOP+ENABLE 0, ERROR 중엔 재활성화 안 함 |
| host uart | EOF 시 50ms sleep 빈 루프를 영구 반복한다. 실제 장치 분리는 EOF가 아니라 `SerialException`으로 오는데(pyserial-asyncio가 reader에 set_exception → 이후 readline이 같은 예외를 영구 재발생), 이 경로는 0.5초마다 로그만 찍고 재시도한다. 어느 쪽이든 장애가 드러나지 않는다 | EOF·읽기 예외 모두 COMM_FAIL → stop → exit 1 → systemd `Restart=on-failure`가 재기동. 예외 경로는 후속 리뷰에서 추가 (`a791541`) |
| host fsm | headache/happy는 DONE에만 의존한다. 포즈 중 ESP32 brown-out 리셋(BOOT 핸들러는 ENABLE만 재전송)이나 DONE 유실 시 다음 외부 이벤트까지 고착 | `CANDUCK_POSE_DONE_TIMEOUT_SEC`(15초) 후 idle 강제 복귀 |
| host daemon | 부팅 idle 진입(`handle(POSE_DONE)`)이 IDLE→IDLE이라 no-op | `POSE idle` 직접 전송 |

## Notes — 결정사항 / 트레이드오프
- **include는 헤더가 아니라 `.cpp`에** — `poses.h` 공개 인터페이스는 `CH_*`를 쓰지 않는다. 다른 TU와 같은 패턴이다.
- **UART 단절은 프로세스 내 재연결 대신 exit 1** — ERROR 상태에는 회복 경로가 없도록 설계돼 있다. systemd unit이 이미 `Restart=on-failure`/`RestartSec=3`이라 재기동이 곧 재연결이다. 코드가 가장 적게 바뀐다.
- **STOP은 여전히 즉시 중립(0°)으로 스냅** — 기존 명세 그대로다. 상태 불일치만 고쳤다.
- **문서 정합화는 확정 사항만** — Board B I2S·앰프·LCD/마이크/스피커 커넥터 삭제는 "W1 결정"으로 표기만 했다. `parts.md` 금액은 바꾸지 않았다(배치 1 표만 기존 체크리스트 합계 ~249K로 맞춤). roadmap 시작일은 TBD 유지.
- **운용 UART(`/dev/ttyAMA0`)는 EOF가 나지 않는다** — GPIO UART라 ESP32 전원 단절·행에도 조용해질 뿐이다. EOF/예외 감지는 USB 시리얼(개발 구성)에서만 동작한다. ESP32 무응답 감지(PING 감시)는 W3로 미룸 — `architecture.md` v1 구현 차이에 명시.
- **표정 창 기본 비활성** — v1 감정 표현은 본체 서보 포즈로 한다. 코드는 유지하고 `CANDUCK_ENABLE_FACE` 기본값만 false. 절차적 폴백은 도트 LCD 스타일(i-mode 이모지·다마고치 LCD 레퍼런스)로 교체했다.
- **env 예시 주석은 별도 줄** — systemd `EnvironmentFile`은 인라인 주석을 지원하지 않아 `false  # ...`가 값으로 들어가 bool 파싱이 실패한다.
- **명세 대비 미구현(이번 PR 범위 밖)**: sleep의 ENABLE 0, headache cooldown, 모션 중 이벤트 큐잉, MQTT alert/`canduck/state` 발행, walking. → `architecture.md` FSM 절에 "v1 구현 차이"로 명시.

## 검증 상태
- 펌웨어: `~/.platformio/penv/bin/pio run` (esp32-s3-devkit) **SUCCESS**, RAM 6.1% (20,008B) · Flash 9.5% (316,545B).
  - ⚠️ PATH의 전역 `pio`(Python 3.14 framework)는 `ModuleNotFoundError: intelhex`로 bootloader 단계에서 실패한다. 환경 문제라 이 PR과 무관하다. penv의 pio를 쓸 것.
- 호스트: 가짜 UART로 FSM/daemon 핸들러 시나리오 **11/11 PASS**. 시나리오: surprised/listening 타이머 복귀, 늦은 DONE 무시, VBAT critical → ERROR + STOP/ENABLE 0, ERROR 중 BOOT 무시, UART EOF → exit 1, stop 중복. `py_compile` OK.
  - ⚠️ 이 시나리오의 "UART EOF → exit 1"은 `b""` EOF만 재현했고, 실제 장치 분리 경로(`SerialException`)를 놓쳤다. 후속 리뷰에서 발견·수정.
- 호스트 (후속 리뷰): StreamReader 시뮬레이션 — `SerialException`/EOF/64KiB 초과 라인 3경로에서 disconnect 핸들러 1회 호출·루프 종료 확인. pyserial-asyncio `_read_ready` 소스로 `_close(exc=e)` 확인. FSM — DONE 없는 headache → 타임아웃 idle, DONE 정상 경로, ERROR 유지 확인. `enable_face` 기본 False·env 파싱 확인. 표정 9종 렌더 육안 확인.
- **미실행**: DevKit 실기 업로드·`canduck-smoke --check` (실물 필요), RPi4 실배포, USB 분리 시 실제 exit 1·systemd 재기동, RPi4 표정 창 실표시.

## Merge 후 남는 것
- **heebin** — 배치 1 결제 여부 확인 → `parts.md` 체크리스트 반영, 벤치 PSU 보유 확인, KiCad 9 설치, roadmap 시작일 재지정.
- **W1 설계 미결** — J_A4 6→8핀, Board B I2S·앰프·J_B3/B4/B6 삭제 (보고서 §3).
- **DevKit 실기** — `pio run -t upload` → `canduck-smoke --dev /dev/ttyUSB0 --check`. 데몬 실행 중 USB 분리 → `uart_read_failed` 후 exit 1·재기동 확인.
- **RPi 배포 시** — 기존 `/etc/canduck/canduck.env`에 `CANDUCK_ENABLE_FACE=true`가 남아 있으면 창이 계속 켜진다. `grep ENABLE_FACE /etc/canduck/canduck.env`.
- **W3** — PING 감시(주기 송신 + 무응답 N초 → COMM_FAIL)로 운용 구성의 ESP32 무응답 감지.
- 그 다음 W1 착수: `w1/t03-pcb-schematic`.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
