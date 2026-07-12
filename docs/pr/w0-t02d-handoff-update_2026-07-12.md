# PR — Phase 1 Sourcing 확정: 핸드오프 갱신 + BOM 최종 + 보고서 4종

- **Branch**: `w0/t02d-handoff-update` → `main`
- **Date**: 2026-07-12
- **Base**: `main` (`0894494`)

## What
Phase 0 마무리 문서 + BOM 발주 확정 전 과정(4차 심사)을 하나의 PR로 정리.

1. **핸드오프 전면 갱신** (`docs/handoff/next-session.md`) — 상태 스냅샷, loose end, W1 진입 계획·설계 제약, 복붙 프롬프트.
2. **BOM 최종 확정** (`hardware/parts.md`) — 심사 이력 순서대로:
   - RPi5 → **보유 RPi4** (전원 설계 무변경, HAT 호환 — `docs/reports/W0-T02e-order-final.md`)
   - **전량 JLCPCB SMT 어셈블리** (핫에어 장비군 삭제, W1 부품은 JLC Parts Library 제약)
   - 배터리·스코프 등 보류 (트리거 명시), 랩 도구 → 멀티미터만
   - 품목 심사(turn-15): LCD·마이크·스피커 탈락 → **3-in-1 USB 카메라 대체**, 모터 재선정
   - **최종 배치 1 ~249K** (A 확정 97K + 모터 52K + 카메라 ~100K), 배치 2(W2 JLC) ~155K 이하
3. **보고서 4종** (`docs/reports/`) — W0-T02e(발주 확정+전 문서 대조 검증 7건), W0-T02f(장비별 구매 사유), W0-T02g(모터 선정: MG90S×10 통일 + N20 100RPM, 스펙·출처 포함).
4. **README 정정** — RPi4/전량 어셈블리/배터리 보류 반영.

## Files
- `hardware/`: parts.md(최종 BOM+발주 체크리스트), power-budget.md(RPi4 노트)
- `docs/reports/`: W0-T02e-order-final.md, W0-T02f-equipment-rationale.md, W0-T02g-motor-selection.md (모두 new)
- `docs/handoff/next-session.md`, `README.md`, `docs/logs/session-2026-07-12.md` (turn-6~16)

## Notes
- W1 설계 파급: Board B에서 I2S·오디오 앰프·J_B3/B4/B6 삭제 검토, J_A4 6핀→8핀 정정, W2 스텐실 발주 불필요.
- 미결: v1 표정(face.py) 표시 수단(LCD 탈락), 벤치 PSU 보유 확인(유일한 7.4V 급전원), roadmap 재캘린더링.

## Merge 후 heebin 액션
1. parts.md 체크리스트로 배치 1 결제 (~249K, Ali 항목 이번 주 내)
2. KiCad 9 설치 → 다음 세션 W1 (`w1/t03-pcb-schematic`) 착수
