# PR — 핸드오프 갱신 + 세션 로그 + BOM 발주 확정

- **Branch**: `w0/t02d-handoff-update` → `main`
- **Date**: 2026-07-12
- **Base**: `main` (`0894494`)
- **Commits**: 4 — 세션 로그 turn-6/7/8, 핸드오프 전면 갱신, BOM 발주 확정

## What
Phase 0 마무리 문서 묶음 + 다음 세션(BOM 발주 논의) 결과까지 하나의 PR로 정리.

1. **핸드오프 갱신** (`docs/handoff/next-session.md`): 2026-05-25 시점에 멈춰있던 파일을 전면 재작성 — main 단일 트렁크 정책, PR #1~#4 머지 현황, loose end, W1 진입 계획, 복붙 재진입 프롬프트, sandbox 제약 노트.
2. **세션 로그** (`docs/logs/session-2026-07-12.md`): turn-6(Phase 0 완료 확인) / turn-7(핸드오프 갱신) / turn-8(BOM 발주 논의) append. 기존 `w0/t02c-session-log-sync` 브랜치는 이 브랜치로 rebase 통합됨(별도 PR 불필요).
3. **BOM 발주 확정** (`hardware/parts.md`): 2026-07-12 발주 논의 결과 반영.
   - RPi5 8GB→4GB (-30K), USB 현미경 제외·루페 유지 (-100K) → 합계 1,363K → **1,233K**
   - **실장 방식 = 혼합**: Board A(파워)만 JLCPCB SMT 어셈블리(부품은 W2 PCB 발주 시 JLC Parts Library 통합 발주), Board B(HAT)는 직접 실장
   - **발주 3배치 분리**: ①지금(W0~W1, lead time 역산) ②W2(PCB fab + Board A JLC 부품) ③보류(3D 외형 W10, VL53L0X W8)
   - dev board용 브레이크아웃 모듈 3종은 스킵 확정 — W3는 LCD+UART까지만

## Files
- `docs/handoff/next-session.md` — 전면 재작성 + BOM loose end를 "결제만 남음"으로 갱신
- `docs/logs/session-2026-07-12.md` — turn-6/7/8 append
- `hardware/parts.md` — U1(4GB)/현미경 행, 총합, "발주 확정 (2026-07-12)" 섹션

## Merge 후 heebin 액션
1. 배치 1 결제 (이번 주 내 — AliExpress 1~3주 lead time이라 늦으면 W4 모션 작업 밀림)
2. KiCad 9 설치 → 되면 다음 세션에서 W1 (`w1/t03-pcb-schematic`) 착수
