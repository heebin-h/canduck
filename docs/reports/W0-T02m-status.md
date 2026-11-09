# W0-T02m — Project Status Check (2026-11-09)

- **Date**: 2026-11-09
- **Owner**: Claude (점검) + heebin (판단)
- **Status**: completed — §1~5는 점검 시점(00:50) 스냅샷. include 수정은 §6 하단에서 적용·검증됨
- **Phase**: Phase 1 (Sourcing) 확정 + 코드 초안 완료, **W1 미진입**

---

## 1. What happened

- 세션 재진입 후 추적 파일 71개 전수 통독 (.md 40개 개별 + firmware/host 코드 + hook/설정).
- 결론: Phase 0(Infra)·Phase 1(소싱 확정)·W0 코드 초안까지 완료. W1(KiCad schematic) 미진입. **마지막 작업 2026-07-20 이후 약 3.5개월 정체.**

## 2. 현황 스냅샷

| 영역 | 상태 | 근거 |
|---|---|---|
| Git | `w0/t02d-handoff-update`(17커밋) → **PR #5 open, 미머지**. origin/main = PR #4 (`0894494`) | HTTPS `git ls-remote`: `refs/pull/5/head` = `09d5930` = 로컬 HEAD, `refs/pull/5/merge` 존재 (점검 시점 기준. 이후 `ec86be2`로 머지됨) |
| BOM | 확정 — 배치 1 ~249K (A 97K + 모터 52K + 3-in-1 카메라 ~100K), 배치 2(W2 JLC) ~155K | `hardware/parts.md` 총계 |
| 결제·입고 | **기록상 미결제** — 체크리스트 ☐ 전부 비어있음 | `hardware/parts.md` 발주 실행 체크리스트 |
| 하드웨어 설계 | 사양서만 존재, KiCad 프로젝트 없음 | `hardware/schematic-spec.md`, `hardware/power-budget.md` |
| 펌웨어 | UART 명령 9종·서보 보간·PCA9685 dry-run·모터·포즈 5종·vbat 구현. IMU/터치는 W4 | `firmware/src/*.cpp` |
| 호스트 | daemon/FSM/tkinter 표정/GPIO/smoke CLI 구현. INA219 폴링은 stub(W4) | `host/canduck/telemetry.py:47-52` |
| 검증 | host `py_compile`만 통과. **펌웨어 빌드 이력 0회** | `docs/pr/w0-t02d-handoff-update_2026-07-12.md` "검증 상태" |

## 3. 발견 사항

| 심각도 | 항목 | 내용 | 조치 |
|---|---|---|---|
| 높음 | 펌웨어 컴파일 에러(→ §6에서 확정) | `firmware/src/poses.cpp:27~` 이 `CH_HEAD_YAW` 등 `pins.h` 매크로를 쓰지만 `pins.h` 미include. include 체인(`poses.h`/`servo_ctrl.h`/`comm.h`)도 `<Arduino.h>`만 포함 | `#include "pins.h"` 1줄 추가 — **적용·clean build SUCCESS (§6)** |
| 중간 | 문서 stale | `docs/architecture.md`(RPi5·LCD·Pygame), `docs/roadmap.md`(RPi5·stencil·핫에어 수동 실장), `host/systemd/canduck.env.example`(`CANDUCK_LCD_*`), `host/pyproject.toml` description("RPi 5"), `hardware/parts.md` 발주 배치 표(~435K 구버전 잔존) | 미적용 — 정합화 필요 |
| 중간 | W1 설계 미결 | J_A4 6핀→8핀 정정, Board B I2S·앰프·J_B3/B4/B6 삭제, 벤치 PSU 보유 확인(유일한 7.4V 급전원) | `docs/handoff/next-session.md` §1.4 |
| 낮음 | 미추적 이미지 3개 | 루트 `800.jpeg`, `ff1060939b9bc96f5be5cb21bd85bbe7.jpg`, `moncolle_ex_s24035.jpg` — CLAUDE.md §3 IP 경계로 Claude 미열람 | 레포 비대상이면 `.gitignore` 또는 이동 |

## 4. Next actions

### heebin (W1 진입 조건)
1. PR #5 머지
2. 배치 1 결제 여부 확인 — 7월 이후 진행됐으면 `hardware/parts.md` 체크리스트 반영
3. 벤치 PSU 보유 확인
4. KiCad 9 설치
5. `docs/roadmap.md` 시작일 재지정 (4개월 공백)

### Claude (PR #5 머지 후, 승인 시)
1. ~~새 브랜치에서 `poses.cpp` include 수정~~ — 완료 (`w0/t02n-poses-include-fix`)
2. §3 stale 문서 정합화
3. W1 진입 — `w1/t03-pcb-schematic`

## 5. Context notes

- 확인 못 한 것: `.omc/state` 내용, 결제·장비 보유 여부(레포에 기록 없음), 펌웨어 실제 빌드 결과.
- sandbox는 SSH fetch 불가 — remote 상태는 HTTPS `ls-remote`로 확인 (`docs/handoff/next-session.md` §4).

## 6. 추가 확인 (2026-11-09, 같은 세션 후속)

| 항목 | 결과 | 근거 |
|---|---|---|
| remote 변화 | 없음 — origin/main=`0894494`, PR #5 head=`09d5930`(=로컬 HEAD), `refs/pull/5/merge` 존재 → 여전히 open·미머지 | HTTPS `git ls-remote` |
| 펌웨어 첫 빌드 | **FAILED** — `src/poses.cpp:27~94` `'CH_HEAD_YAW'/'CH_HEAD_PITCH'/'CH_LEG_*' was not declared in this scope`. §3 "예상"이 확정됨 | `pio run` (esp32-s3-devkit, 490s, 툴체인 첫 설치 포함) |
| 수정안 검증 | 소스 무수정, `PLATFORMIO_BUILD_FLAGS="-include include/pins.h"`로 재빌드 → **SUCCESS**, error/warning 0. RAM 6.1%(20,008B), Flash 9.5%(316,153B) | `pio run` 재실행 |
| `.omc/state` | 7/13·7/19 세션 HUD/에러 캐시만 존재. 진행 중 모드·handoff 없음 | `.omc/state/sessions/*` |

→ 펌웨어 블로커는 `poses.cpp`에 `#include "pins.h"` 1줄로 해소됨이 빌드로 검증됨. 그 외 TU(comm/main/motor/servo_ctrl)는 원래 빌드에서도 컴파일 성공.

**적용 (PR #5 머지 `ec86be2` 후)**: `w0/t02n-poses-include-fix`에서 `firmware/src/poses.cpp`에 `#include "pins.h"` 추가 → `pio run -t clean` 후 `pio run` **SUCCESS**, error/warning 0, RAM 6.1% · Flash 9.5% (주입 플래그 없이 검증).
