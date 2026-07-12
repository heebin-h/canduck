# W0-T02g — 모터 선정 보고서 (서보 + 휠 구동, 스펙·가격 비교)

> 2026-07-12. heebin 지시("모터 적당한 걸로 다시 찾아서 스펙·구매가 포함 재보고")에 따른 재조사.
> 축별 요구조건은 `docs/architecture.md`(모션 종류)·`hardware/power-budget.md`(전류 예산)·`hardware/schematic-spec.md`(PCA9685 PWM 16ch + TB6612FNG 2ch)에서 도출.

---

## 1. 뭘 움직여야 하나 (요구조건)

| 축 | 수량 | 동작 | 요구 토크·특성 |
|---|---|---|---|
| 머리 yaw/pitch | 2 | idle sway, 두통포즈 격렬 흔들기, listening 머리 들기 | 부하 가벼움(머리 = LCD 삭제로 더 가벼워짐). 반복 왕복이 많아 **기어 내구**가 토크보다 중요 |
| 팔 (어깨×2, 팔꿈치×2) | 4 | 두통포즈(양손 머리 옆), wave | 팔 링크 관성 → 스톨 순간 발생. **메탈 기어 필수**, 2kg·cm급 |
| 다리 스윙 | 2 | happy 점프, 보행 연출 | 몸체 일부 하중 순간 부담. 메탈 기어, 2kg·cm급 |
| 휠 구동 | 2 | 30분마다 자율 배회 (책상 위 저속) | 연속 회전(서보 불가 영역). 탁상 로봇 적정 속도 0.1~0.2m/s |

전원 제약: 6V 레일 5A 정상/7A peak (power-budget.md) — 마이크로 서보 10개 체급(개당 stall ~0.7A)을 전제로 설계된 레일이므로 **표준 사이즈 서보(MG996R급, stall 1.4A+)로 올라가면 전원 설계가 깨진다.** 후보는 마이크로(9g~14g) 체급으로 한정.

## 2. 서보 후보 비교

| 후보 | 기어 | 스톨 토크 | 속도 | 무게 | 개당 추정가 | 판정 |
|---|---|---|---|---|---|---|
| SG90 (원안-머리) | **플라스틱** | 1.8kg·cm @4.8V | 0.1s/60° | 9g | ~2,000 | ❌ 탈락 — 두통포즈처럼 빠른 왕복이 잦은 축에서 플라 기어는 마모가 먼저 옴. 500원 아끼자고 기어 갈리면 분해 재조립 |
| **MG90S (권장)** | 메탈 | 1.8kg·cm @4.8V / **2.2kg·cm @6.6V** | 0.1s/60° | 13.4g | ~3,500 (해외가 $4.95) | ✅ **전 축 채택** — 6V 레일에서 2.2kg·cm, 크기는 SG90과 동일(마운트 호환), 가장 흔해서 파손 시 재조달 즉시 |
| MG92B | 메탈(강화) | **3.1kg·cm @4.8V / 3.5 @6.6V** | 0.1s/60° | 13.8g | ~7,000 (해외가 $7.95) | 🔶 옵션 — 어깨 2축만 업그레이드용 예비 선택지. W7 팔 작업에서 MG90S 토크 부족이 실측되면 그때 2개만 구매 (+7K), 크기 동일해서 무개조 교체 가능 |
| EMAX ES08MA II | 메탈 | 2.0kg·cm | 0.1s/60° | 12g | ~5,000 | ❌ — MG90S 대비 이점 없이 단가만 높음 |
| Feetech 버스 서보 (STS/SCS) | 메탈 | 3~15kg·cm | - | - | 12,000+ | ❌ — 위치 피드백은 매력적이나 UART 데이지체인 방식이라 **PCA9685 PWM 전제인 Board B 설계 전체를 뒤집어야 함**. v1 기각 |

**→ 권장: MG90S × 8 (전 축 통일) + 예비 2 = 10개, ~35,000원.**
단일 SKU 통일의 이점: 어느 축이 죽어도 예비로 즉시 교체, 벌크 단가↓, 포즈 튜닝 시 축별 특성 편차 없음. 머리를 SG90으로 아끼는 원안(개당 -1.5K)은 기어 마모 리스크 대비 실익 3천원이라 폐기.

## 3. 휠 구동 후보 비교

| 후보 | 방식 | 스펙 | 개당 추정가 | 판정 |
|---|---|---|---|---|
| **N20 6V 100RPM (권장, 원안 유지)** | 기어드 DC + TB6612FNG 제어 | 10×12mm 기어박스, 3mm D축, 무부하 25~45mA, 스톨 토크 ~1.5kg·cm급(60RPM 기준 실측치, 100RPM은 소폭 낮음) | ~6,000 | ✅ — 탁상 로봇 적정 속도 근거: 30~40mm 휠 기준 **50~100RPM이 0.1~0.2m/s 스위트 스팟** (아래 출처). Φ40 휠 × 100RPM ≈ 0.21m/s로 상한 딱 맞음 |
| N20 6V 30~60RPM | 〃 | 토크↑ 속도↓ | ~6,000 | 🔶 — 카펫/무거운 본체로 판명되면 W8에서 교체 고려 (같은 풋프린트라 무개조 스왑). 책상 위 배회엔 100RPM이 적정 |
| N20 + 엔코더 | 폐루프 속도제어 | +엔코더 2상 | ~9,000 | ❌ — v1 보행은 개루프 + IMU/ToF 보조로 충분 (roadmap W9). 배선 4가닥 추가·펌웨어 복잡도만 늘어남 |
| FS90R (연속회전 서보) | PCA9685 직접 구동 | 1.3kg·cm급 | ~5,000 | ❌ — TB6612FNG 삭제 가능한 매력이 있으나 속도 제어 정밀도가 낮고(중립점 드리프트), 후진 포함 PWM 캘리브레이션 필요. TB6612는 이미 Board B 설계에 포함돼 있어 절감 효과 없음 |
| TT 모터 (노란 기어박스) | 기어드 DC | 크기 65mm급 | ~2,000 | ❌ — 본체 크기 대비 과대. 탁상 로봇에 부적합 |

**→ 권장: N20 6V 100RPM × 2 (~12,000) + Φ40~43mm 고무 휠 1쌍 (N20 3mm D축 호환, ~5,000).**

## 4. 권장 구매 리스트 (모터류 총 ~52,000)

| 결제 | 입고 | 품목 | 수량 | 추정가 | 링크 |
|---|---|---|---|---|---|
| ☐ | ☐ | MG90S 메탈기어 서보 | 10 (8 + 예비 2) | 35,000 | [Ali 검색](https://www.aliexpress.com/w/wholesale-MG90S-servo.html) · [디바이스마트 검색](https://www.devicemart.co.kr/goods/search?keyword=MG90S) |
| ☐ | ☐ | N20 6V 100RPM 기어드 모터 | 2 | 12,000 | [Ali 검색](https://www.aliexpress.com/w/wholesale-N20-gear-motor-6V-100RPM.html) |
| ☐ | ☐ | 고무 휠 Φ40~43 (N20 3mm D축) | 1쌍 | 5,000 | [Ali 검색](https://www.aliexpress.com/w/wholesale-N20-wheel-43mm.html) |

- 원안 대비 변화: SG90 폐지 → 전 축 MG90S 통일(+예비 2), 휠 모터는 원안 100RPM 유지(근거 보강됨). 총액 42K → 52K (+10K는 예비 2개와 SG90→MG90S 격상분).
- W7(팔)에서 토크 부족 실측 시: 어깨 2축만 MG92B 교체 (+14K, 무개조).
- W8(보행)에서 견인력 부족 실측 시: N20 60RPM으로 스왑 (+12K, 무개조).

## 5. 출처

- [ServoDatabase — TowerPro MG90/MG90S 스펙](https://servodatabase.com/servo/towerpro/mg90)
- [ProtoSupplies — MG90S 상세 ($4.95, 13.4g, 2.2kg·cm@6.6V)](https://protosupplies.com/product/servo-motor-micro-mg90s/)
- [Smart Prototyping — MG92B ($7.95, 3.1kg·cm)](https://www.smart-prototyping.com/MG90S-9g-metal-gear-digital-servo.html)
- [Waveshare — MG90S 제품 페이지](https://www.waveshare.com/mg90s-servo.htm)
- [espboards.dev — ESP32 호환 서보 비교](https://www.espboards.dev/blog/most-popular-esp32-servos/)
- [Zbotic — N20 스펙·RPM 옵션 가이드 (50~100RPM = 30~40mm 휠 스위트 스팟)](https://zbotic.in/n20-micro-gear-motor-specs-rpm-options-best-projects/)
- [BC Robotics — N20 6V 60RPM (1.5kg·cm)](https://bc-robotics.com/shop/n20-micro-gear-motor-6v-60rpm/) · [300RPM 변형](https://bc-robotics.com/shop/n20-micro-gear-motor-6v-300rpm/)
- [RobotShop — N20 + 고무휠 세트](https://www.robotshop.com/products/6v-n20-micro-gear-motor-w-rubber-wheel-1-pair)
