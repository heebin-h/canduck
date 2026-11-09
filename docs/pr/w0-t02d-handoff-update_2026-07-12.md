# PR — W0-T02: Phase 1 소싱 확정 + 펌웨어/호스트 코드 초안 (UART 프로토콜 브링업)

- **Branch**: `w0/t02d-handoff-update` → `main`
- **Date**: 2026-07-20 (소싱 확정 2026-07-12 → 코드 브링업 2026-07-19~20)
- **Base**: `main` (`0894494`, PR #4 머지)
- **규모**: 17 commits · 28 files · +1428 / −390

## What
두 갈래를 한 브랜치에 정리:
1. **Phase 1 소싱 확정** — BOM 4차 심사 → 발주 체크리스트 + 근거 보고서 3종 + 핸드오프 갱신.
2. **W1 진입 전 코드 초안** — ESP32 펌웨어와 RPi 호스트의 **UART 프로토콜 왕복 골격**. PCB·센서 실물 없이 DevKit 단독(dry-run)으로 프로토콜/보간 로직을 지금 검증 가능.

## Files

### 펌웨어 (`firmware/`, ESP32 / PlatformIO)
- `src/comm.cpp` — 라인 파서 + 명령 dispatch 9종: `PING/HEAD/ARM/LEG/MOTOR/QUERY/POSE/STOP/ENABLE`, `< ACK/DONE/ERR/VBAT/BOOT` 이벤트 송신
- `src/servo_ctrl.cpp` — PCA9685 16ch, easeInOutCubic 보간(10ms tick), OE# 게이팅, **PCA 미장착 시 dry-run**
- `src/motor.cpp` (+`motor.h`) — TB6612 N20×2, LEDC 20kHz PWM, ±255
- `src/poses.cpp` — 5종 사전 포즈 시퀀스 플레이어(idle/headache/shake/happy/sleep), 완주 시 `DONE`
- `include/vbat.h` — ADC eFuse 캘리브레이션(`analogReadMilliVolts`×3, 20K/10K 분압)
- `src/main.cpp` — setup/loop, 10ms 서보 tick + 1s vbat 텔레메트리

### 호스트 (`host/`, RPi / asyncio)
- `canduck/daemon.py` — 메인 데몬. FSM·Face·UART·MQTT·GPIO·Telemetry·Voice 통합, systemd 진입점, SIGINT/TERM 안전 종료(STOP→ENABLE 0)
- `canduck/display_tk.py` (new) — tkinter 표정 백엔드(전용 스레드 + Queue), headless/darwin 가드
- `canduck/face.py` — Expression 도메인 + PIL 렌더(자산 PNG 우선, 없으면 절차적 폴백)
- `canduck/gpio.py` (new) — RPi GPIO: ESP32 RESET(23)/BOOT(24)/사용자 버튼(4), 비-RPi mock 강등
- `canduck/uart_smoke.py` (new) — 브링업 CLI: `--check`(self-check 13항목, CI성) + 대화형 REPL
- `canduck/config.py` — pydantic-settings, `/etc/canduck/canduck.env` + `CANDUCK_*` 환경변수

### 하드웨어 (`hardware/`)
- `parts.md` — 최종 BOM + 발주 체크리스트(배치 1 ~249K / 배치 2 ~155K)
- `power-budget.md` — RPi4 노트

### 문서 (`docs/`, `README.md`)
- `reports/` — W0-T02e(발주 확정+대조검증 7건), W0-T02f(장비별 구매 사유), W0-T02g(모터 선정: MG90S×10 통일 + N20 100RPM)
- `handoff/next-session.md` — 상태 스냅샷·loose end·W1 계획, `README.md`, 세션 로그(07-12/07-13)

## Notes — 결정사항 / 트레이드오프
- **LCD 탈락**(품목 심사) → v1 표정은 **tkinter 창**으로 대체. GC9A01/pygame/spidev 경로 제거.
- **RPi5 → 보유 RPi4** — 전원 설계 무변경, HAT 호환.
- **전량 JLCPCB SMT 어셈블리** — 핫에어 장비군 삭제, W1 부품은 JLC Parts Library 제약. 배터리·스코프 보류(트리거 명시).
- **dry-run 설계** — PCA9685 부재 시 I2C 쓰기만 생략, ACK/DONE 흐름은 동일. DevKit만으로 프로토콜 테스트.
- **펌웨어=dumb actuator** — 행동 FSM은 RPi 측, ESP32는 명령 실행 + 센서 이벤트 보고만.
- **ponytail 리뷰 반영**(T02l) — 호출처 0 죽은 코드 제거(`poses_active`·`CmdResult::Busy`·`esp32_reset`·`Face.tick`). W3/W4 forward-decl(`emit_event_tap/shake/touch`·`esp32_enter_bootloader`)은 근거와 함께 유지.

## 검증 상태
- 호스트 3파일 `py_compile OK`, 제거 심볼 잔존 참조 0.
- **펌웨어 실제 빌드 미실행** — 로컬에 PlatformIO 툴체인 없음(미확인). heebin `pio run` 필요.
- **UART self-check는 DevKit 실물 필요** — `canduck-smoke --dev /dev/ttyUSB0 --check`.

## W1 설계 파급 (미결)
- Board B: I2S·오디오 앰프·J_B3/B4/B6 삭제 검토, J_A4 6핀→8핀 정정, W2 스텐실 불필요.
- v1 표정 표시 최종 수단(tkinter 확정이나 실기기 확인 필요), 벤치 PSU 보유 확인(유일한 7.4V 급전원), roadmap 재캘린더링.
- IMU/touch(W4)·INA219 전력측정(W4)·blink 애니메이션(W3)·OTA 부트로더(W3+)는 stub/forward-decl 상태.

## Merge 후 heebin 액션
1. `parts.md` 체크리스트로 배치 1 결제 (~249K, Ali 항목 이번 주 내)
2. ESP32 DevKit USB 연결 → `pio run -t upload` → `canduck-smoke --dev /dev/ttyUSB0 --check`로 프로토콜 왕복 확인
3. KiCad 9 설치 → 다음 세션 W1 (`w1/t03-pcb-schematic`) 착수
