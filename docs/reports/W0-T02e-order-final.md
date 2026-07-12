# W0-T02e — BOM 발주 확정 (RPi4 전환 + 최소화 + 발주 실행 리스트)

> 2026-07-12, turn 8~12. 브랜치 `w0/t02d-handoff-update` (커밋 W0-T02e~h + 구조 정정).
> Phase 1 (Sourcing) 진입 산출물 — `hardware/parts.md` 최종 확정.

## What happened

- 핸드오프 재진입 후 이번 세션 주제로 **BOM 발주 논의** 선택 → 4단계에 걸쳐 확정:
  1. (turn-8) 발주 3배치 분리 + 실장 방식/다이어트 1차 결정
  2. (turn-9) **장비 RPi5 → 보유 RPi4로 변경** + 설계 영향 정리 + Pololu 벅 모듈 채택
  3. (turn-10) **전면 최소화** — 전량 JLC 어셈블리, 배터리·스코프 등 보류, 랩 도구 최소 셋
  4. (turn-11~12) 품목별 설명·가격·구매 링크 체크리스트를 `parts.md` 내 "발주 실행 체크리스트" 섹션으로 정리
- 총 예산: 최초 1,363K → **코어 ~590K** (배치 1 ~435K + 배치 2 ~155K, 보류 항목 별도)

## Decisions

| 결정 | 내용 | 근거 |
|---|---|---|
| RPi4 (보유분) 고정 | RPi5 구매 취소. 쿨링·PSU만 RPi4용 교체 | 전원 설계 무변경(peak 3A<5A, 마진↑), HAT 40핀/마운트홀/외형 호환. v1 부하(Porcupine+FSM+MQTT)에 충분. v2 로컬 LLM은 클라우드 경로 |
| 전량 JLCPCB SMT 어셈블리 | 혼합 실장(turn-8) 폐기. Board A+B 실장 부품 전부 W2 JLC 통합 발주 | 핫에어/페이스트/현미경 불필요(-112K+), 실장 실패 리스크 제거 > 어셈블리 수수료 증가(+3~5만 추정). **제약: W1 schematic 부품은 JLC Parts Library(Basic 우선) 재고에 맞출 것** |
| 벅 컨버터 = Pololu 모듈 | D24V50F5(5V) + D24V60F6(6V), 스루홀 헤더 실장 | power-budget.md rev1 권고 그대로 |
| 배터리+충전기 보류 (-65K) | v1 브링업/운영은 벤치 PSU 7.4V 급전 | 데스크탑 상시 운영이 목표(power-budget.md 권장 운용). 이동 운용 필요 시 구매 |
| 랩 도구 최소 셋 250K | 인두(Pinecil급)/멀티미터/로직애널라이저/저가 가변 PSU/루페/수공구. 스코프(-150K)·연기팬·ESD매트 보류 | 보류 항목마다 재구매 트리거를 parts.md에 명시 |
| dev board용 브레이크아웃 모듈 스킵 | W3는 LCD+UART까지만, IMU/터치/서보는 PCB 입고(W4 중반) 후 | heebin 선택 (turn-8) |
| ToF(VL53L0X) 보류 | W8 보행 단계에서 채택 결정 시 구매 | 원래 선택 항목 |

## Files

- `hardware/parts.md` — 최종 확정본: RPi4 반영, Pololu 모듈, 실장 방식(전량 JLC), 랩 도구 최소 셋, 보류/트리거 표, 총합 재계산, **발주 실행 체크리스트**(품목별 설명·추정가·구매 링크·결제/입고 체크박스, 판매처 검색 링크 방식)
- `hardware/power-budget.md` — RPi4 전환 노트 (부하표는 RPi5 기준 보수치 유지)
- `docs/handoff/next-session.md` — loose end 갱신 + W1 JLC 부품 제약 추가
- `docs/logs/session-2026-07-12.md` — turn-8~12
- (정정) `hardware/shopping-list.md` 는 bom-sourcing.md §7 산출물 구조에 없어 생성 취소 → parts.md 내 섹션으로 병합

## Next actions

- **heebin**: ① `w0/t02d-handoff-update` push + PR(→main) merge ② parts.md 체크리스트로 배치 1 결제 (~435K, **Ali 항목이 W4 크리티컬 패스 — 이번 주 내**) ③ 보유 장비(멀티미터/인두/PSU 등) 있으면 체크리스트에서 차감 ④ KiCad 9 설치
- **Claude (다음 세션)**: W1 진입 — `w1/t03-pcb-schematic` 분기, schematic 설계 시 JLC Parts Library 재고 부품 우선 선정, 입고 시작되면 parts.md 체크리스트 "입고" 열로 트래킹

## Context notes

- 발주 결제·입고 확인은 heebin 영역 (CLAUDE.md §4) — Claude는 리스트 확정까지만.
- 가격은 전부 2026-07 추정치. 결제 시 실가로 parts.md 갱신 권장 (bom-sourcing.md §3).
- 구매 링크는 직접 상품 링크 대신 판매처 검색 링크 (링크 rot 방지). Pololu만 공식 페이지.
- parts.md의 카테고리별 항목 표(단가)와 총합/체크리스트 사이에 소액 불일치 있음 — 항목 표는 2026-05 추정 원본 유지, 유효 수치는 총합 표와 체크리스트 기준.
