# Skill — BOM / Sourcing Workflow (부품 비교 · 데이터시트 분석 · 가격 추적 · 발주)

> 대상: `hardware/parts.md` (BOM + 랩 도구, 2026-05 기준 한국 시장 추정가).
> W0-T02 (parts.md 재검토)와 W1 진입 전 발주 확정에 사용.

## 1. 부품 비교 프로세스

새 부품 추가/대체 검토 시:

1. **후보 리스트업** — 동급 대체품 최소 2~3개 (예: PCA9685 vs TLC59711, INA219 vs INA226)
2. **데이터시트 대조표** 작성:

   | 항목 | 후보 A | 후보 B |
   |---|---|---|
   | 전기적 스펙 (전압/전류/정확도) | | |
   | 패키지 (SOIC/TSSOP/QFN 등, 손땜 난이도) | | |
   | 인터페이스 (I2C 주소 범위, SPI 등) | | |
   | 재고/조달성 (LCSC/JLCPCB Parts Library 매칭 여부) | | |
   | 가격 (단가 × 수량) | | |

3. **JLCPCB Parts Library 우선 매칭** 여부 확인 — SMT 조립 이용 시 라이브러리 부품이면 조립비 절감 (`kicad-workflow.md` § 5 참고)
4. 결론 + 근거를 `hardware/parts.md` 또는 별도 비교 메모에 기록

## 2. 데이터시트 분석 체크리스트

부품 채택 전 확인:

- [ ] 절대 최대 정격 (Vmax, Imax, 온도 범위) — 프로젝트 전원 스펙(`hardware/power-budget.md`) 대비 여유 있는지
- [ ] 패키지/풋프린트 KiCad 라이브러리 존재 여부 (없으면 직접 제작 필요 — 시간 비용 고려)
- [ ] I2C 주소 겹침 여부 (TCA9548A mux 채널 배정과 연동, `hardware/schematic-spec.md` 참고)
- [ ] 참조 회로(application circuit) 있는지 — 없으면 설계 리스크↑
- [ ] 단종/재고 위험 (특히 AliExpress 소싱 IC — 정품 여부 확인)

## 3. 가격 추적

- `hardware/parts.md` 총합표 형식 유지 (카테고리별 소계 + 합계)
- 가격 변동 큰 항목 (배터리, PCB, 3D 출력 외주) — 발주 직전 재확인 권장
- 대체품/다이어트 옵션은 `parts.md` § 대체품 섹션에 계속 누적 (예산 초과 시 참고)

## 4. 구매처 라우팅 (parts.md 기준)

| 구매처 | 용도 |
|---|---|
| 디바이스마트 / 엘레파츠 | 국내, 빠름, 약간 비쌈 |
| AliExpress | ESP32-S3 모듈, 서보, 센서 IC — 1~3주 lead time |
| JLCPCB | PCB + SMT 부품 조립 (Parts Library 우선) |
| 쿠팡 | 배터리, 인두, 케이블 등 빠른 배송 필요 항목 |
| Mouser 등 | 정확한 datasheet 매칭 필요한 IC (INA219, PCA9685 등) |

- AliExpress 소싱 부품은 발주 시점에 lead time(1~3주)을 W1/W2 일정에 역산해서 반영

## 5. 발주 워크플로우

1. `hardware/parts.md` 최종본 확정 (W0-T02 산출물)
2. heebin 결제·발주 (Claude는 발주 실행 안 함 — CLAUDE.md § 4 "부품 선정은 Claude, 발주/입고 확인은 heebin")
3. 발주 리스트는 heebin이 최종 검토 후 결제 (roadmap.md W0 게이트)
4. 입고 트래킹 시트 (도착 예정일 vs 실제, lead time이 긴 AliExpress 품목 우선 추적)
5. 입고 후 실물 vs 데이터시트 대조 (특히 IC 마킹, 패키지 핀 순서)

## 6. parts.md 재검토 (W0-T02) 시 점검 항목

- [ ] 빠진 부품 있는지 (커넥터, 나사류, 소모품 등 흔히 누락되는 항목)
- [ ] 대체품 옵션 최신 시세 반영
- [ ] 데이터시트 링크 추가 (핵심 IC: PCA9685, MPR121, MPU6050, INA219, TCA9548A, PAM8403)
- [ ] BOM 총합 vs 예산 재확인 (현재 추정 646,000원 시스템 소계 + 717,000원 랩 도구, `parts.md` § 총합)
- [ ] JLCPCB SMT 조립 이용 시 BOM 필드(LCSC Part#) 매핑 준비

## 7. 산출물

- 갱신된 `hardware/parts.md`
- (선택) 부품 비교 근거 메모 — 대체 판단이 복잡한 경우 `docs/reports/W0-T02-parts-review.md`로 별도 기록
