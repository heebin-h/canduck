## 머지 전 정리 (2026-11-09 현황 점검)

### 요약
Phase 1 소싱 확정과 W1 진입 전 펌웨어/호스트 코드 초안을 담은 PR입니다. 마지막 커밋(07-20) 뒤로 약 3.5개월 동안 변경이 없었고, origin/main(`0894494`) 대비 충돌 없이 머지할 수 있습니다(`refs/pull/5/merge` 생성 확인).

- 규모: 18 commits · 30 files · +1565 / −390 (본문의 "17 commits · 28 files · +1428"은 마지막 docs 커밋 반영 전 수치)
- 소싱: 배치 1 ~249K / 배치 2(W2 JLC) ~155K 확정. **결제 기록은 없음**(`hardware/parts.md` 체크리스트가 모두 ☐)
- 코드: 펌웨어 UART 명령 9종, 서보 보간, PCA9685 dry-run, 모터, 포즈 5종, vbat / 호스트 daemon·FSM·tkinter 표정·GPIO·smoke CLI

### ⚠️ 본문 "검증 상태" 정정 — 펌웨어 빌드 실패
본문에는 "펌웨어 실제 빌드 미실행"으로 적혀 있습니다. 11-09에 처음 빌드해 본 결과는 **실패**입니다.

```
src/poses.cpp:27: error: 'CH_HEAD_YAW' was not declared in this scope
... (CH_HEAD_PITCH / CH_LEG_L_SWING / CH_LEG_R_SWING 등 동일)
*** [.pio/build/esp32-s3-devkit/src/poses.cpp.o] Error 1
```

- **원인**: `poses.cpp`가 include하는 `poses.h`·`servo_ctrl.h`·`comm.h`는 `<Arduino.h>`만 포함합니다. 그래서 `pins.h`의 `CH_*` 매크로가 보이지 않습니다. 다른 TU는 `pins.h`를 직접 include하거나 `vbat.h`를 통해 받기 때문에 문제가 없습니다.
- **수정안 검증**: 소스는 그대로 두고 `-include include/pins.h` 플래그만 넣어 재빌드하면 **SUCCESS**(error/warning 0, RAM 6.1% · Flash 9.5%)가 나옵니다. 이 외의 컴파일 에러는 없습니다.
- **처리**: 이 PR은 이 상태로 머지하고, 수정은 후속 브랜치 `w0/t02n-poses-include-fix`에서 합니다(`#include "pins.h"` 1줄 + `pio run` 재검증 + 현황 보고서 `docs/reports/W0-T02m-status.md`).

### 머지 후 남는 것
| 구분 | 항목 |
|---|---|
| 코드 | `poses.cpp` include 수정 (위 후속 브랜치) |
| 문서 stale | `docs/architecture.md`(RPi5·LCD·Pygame), `docs/roadmap.md`(RPi5·stencil·핫에어), `host/systemd/canduck.env.example`(`CANDUCK_LCD_*`), `host/pyproject.toml` description, `hardware/parts.md` 구버전 배치 표(~435K) |
| W1 설계 미결 | J_A4 6핀→8핀, Board B I2S·앰프·J_B3/B4/B6 삭제, 벤치 PSU 보유 확인(유일한 7.4V 급전원) |
| heebin | 배치 1 결제 여부 확인 → 체크리스트 반영 / KiCad 9 설치 / roadmap 시작일 재지정 |
| 미검증 | 호스트는 `py_compile`까지만 확인. UART self-check(`canduck-smoke --check`)는 DevKit 실물이 필요 |
