# PR — W0-T02: parts.md 재검토

- **Branch**: `w0/t02-parts-review` → `main`
- **Date**: 2026-07-12
- **Base / Compare**: base=`main` (`e8c0f9e`) ← compare=`w0/t02-parts-review` (`caccd42`)
- **Commits**: 1 — `caccd42`
- **Diff**: 1 file, `hardware/parts.md` (+27/-6)

## What
`hardware/parts.md`를 `hardware/schematic-spec.md`, `hardware/power-budget.md`와 대조해 재검토. 누락 부품 7종 발견해 추가, 핵심 IC 6종 데이터시트 공식 링크 추가, 총합표 재계산. 시스템 소계(646,000원)는 변동 없음 — 기존 "PCB SMT 부품" 뭉텅이 예산에서 개별 항목으로 재배분.

## Files
- `hardware/parts.md`:
  - 핵심 IC/모듈: INA219용 정밀 션트저항(R_A3/R_A4, 0.01Ω 1% 1W) + CH340N(USB-UART 브릿지) 추가, 6종 IC 데이터시트 공식 링크 섹션 신설
  - 전원: 폴리스위치(F_A1, power-budget.md 토폴로지에 있었으나 BOM 누락), 제너다이오드(D_A1, schematic-spec.md Q1 게이트 보호 수정사항), NTC 서미스터(v1 soft-start 단순화안) 추가
  - PCB: SMT 부품 뭉텅이 예산 50,000→44,800원 (이동분 반영)
  - 배선/기구: USB-C 플래싱 커넥터(J_B2), Boot/Reset 택트버튼×2 추가, 기존 커넥터 항목에 서보/모터/LCD/마이크/스피커 포함 명시
  - 총합표: 핵심IC 30,000→32,500 / 전원 80,000→81,200 / PCB+SMT 115,000→109,800 / 배선기구 28,000→29,500 (시스템 소계 646,000 동일)

## Notes
- 데이터시트 링크는 웹서치로 제조사 공식 PDF/제품페이지 확인 후 반영 (NXP/TI/TDK-InvenSense/Diodes 공식 도메인 우선).
- 이 브랜치는 `main`에서 분기 — `w0/t00d-main-trunk-policy`와 **형제 브랜치** (서로 다른 파일만 건드려 충돌 없음). 두 PR 순서 무관하게 머지 가능.
- 남은 W0-T00c 미해결 항목(BOM 최종 confirm + 발주 결제)은 이 PR 머지 후 heebin 판단.
