# PR — W0-T02n: poses.cpp pins.h include 누락 수정 + 현황 점검 보고서

- **Branch**: `w0/t02n-poses-include-fix` → `main`
- **Date**: 2026-11-09
- **Base**: `main` (`ec86be2`, PR #5 머지)
- **규모**: 2 commits · 5 files

## What
1. **펌웨어 첫 빌드 실패 수정** — PR #5의 코드 초안은 빌드한 적이 없었고, 처음 `pio run`을 돌리자 `poses.cpp`에서 컴파일 에러가 났다. include 1줄로 수정.
2. **현황 점검 기록** — 3.5개월 정체 후 재진입 시점의 현황 스냅샷·발견 사항·Next actions 보고서와 PR #5 머지 전 정리 comment.

## Files
- `firmware/src/poses.cpp` — `#include "pins.h"` 추가 (+1)
- `docs/reports/W0-T02m-status.md` (new) — 2026-11-09 현황 점검 + §6 빌드 검증 결과
- `docs/pr/w0-t02d-handoff-update_2026-11-09-merge-comment.md` (new) — PR #5 머지 전 정리 comment 원본
- `docs/pr/w0-t02n-poses-include-fix_2026-11-09.md` (new) — 이 PR 본문
- `docs/logs/session-2026-11-09.md` (new) — 세션 로그

## 원인
수정 전 에러:
```
src/poses.cpp:27:10: error: 'CH_HEAD_YAW' was not declared in this scope
... (CH_HEAD_PITCH / CH_ARM_* / CH_LEG_* 동일, 27~94행)
*** [.pio/build/esp32-s3-devkit/src/poses.cpp.o] Error 1
```
`CH_*` 채널 매크로는 `include/pins.h`에 정의돼 있다. 그런데 `poses.cpp`가 include하는 `poses.h`·`servo_ctrl.h`·`comm.h`는 `<Arduino.h>`만 포함한다. 다른 TU(`main`/`motor`/`servo_ctrl`)는 `pins.h`를 직접 include하고, `comm.cpp`는 `vbat.h`를 통해 받기 때문에 문제가 없었다.

## Notes — 결정사항 / 트레이드오프
- **헤더가 아니라 `.cpp`에 include** — `poses.h`의 공개 인터페이스는 `CH_*`를 쓰지 않는다. 사용처인 `poses.cpp`에서 직접 include하는 것이 다른 TU들과 같은 패턴이고, 헤더 의존도 늘리지 않는다.
- **다른 숨은 에러 없음 확인** — 수정 전에 소스는 그대로 두고 `-include include/pins.h` 플래그로 빌드해 보니 SUCCESS였다. 이 에러 하나가 다른 에러를 가리고 있지 않았다.

## 검증 상태
- `pio run -t clean` → `pio run` (esp32-s3-devkit): **SUCCESS**, error/warning 0. RAM 6.1% (20,008B) · Flash 9.5% (316,153B).
- **DevKit 실기 업로드·UART self-check는 미실행** — 실물이 필요하다. `pio run -t upload` → `canduck-smoke --dev /dev/ttyUSB0 --check`.
- 호스트 코드는 이 PR에서 변경 없음 (기존 `py_compile`까지만 검증된 상태).

## Merge 후 남는 것
- **문서 stale 정합화** (보고서 §3) — `docs/architecture.md`, `docs/roadmap.md`, `host/systemd/canduck.env.example`, `host/pyproject.toml` description, `hardware/parts.md` 구버전 배치 표.
- **W1 설계 미결** — J_A4 6→8핀, Board B I2S·앰프·J_B3/B4/B6 삭제 (보고서 §3)
- **heebin** — 배치 1 결제 여부 확인 → `parts.md` 체크리스트 반영, 벤치 PSU 보유 확인, KiCad 9 설치, roadmap 시작일 재지정.
- 그 다음 W1 착수: `w1/t03-pcb-schematic`.
