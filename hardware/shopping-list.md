# 발주 실행 리스트 (배치 1)

> 작성: 2026-07-12 (BOM 최소화 확정 반영 — 근거는 `parts.md` "발주 확정" 섹션)
> 가격은 2026-07 한국 시장 **추정치** — 결제 시점 실가로 갱신할 것.
> 링크는 **판매처 검색 링크** (직접 상품 링크는 재고/판매자 변동으로 금방 깨져서 검색 링크로 고정. Pololu만 공식 페이지).
> 체크박스는 결제 완료 시 체크.

## A. 쿠팡 / 국내 (1~3일 도착)

| ✓ | 품목 | 설명 | 수량 | 추정가 | 링크 |
|---|---|---|---|---|---|
| ☐ | RPi4 방열판+팬 | 보유 RPi4 발열 관리. 상시 운영(wake-word 대기)이라 팬 포함 권장 | 1 | 8,000 | [쿠팡 검색](https://www.coupang.com/np/search?q=라즈베리파이4+방열판+팬) |
| ☐ | RPi 공식급 PSU 5.1V/3A USB-C | 개발 중 RPi4 전원. 일반 폰충전기는 전압강하로 저전압 경고 뜸 — 3A 명시 제품 | 1 | 12,000 | [쿠팡 검색](https://www.coupang.com/np/search?q=라즈베리파이4+전원+어댑터+5.1V+3A) — **보유 시 생략** |
| ☐ | microSD 64GB (A2) | RPi4 OS 디스크. A2 등급이 랜덤 IO 빠름 | 1 | 12,000 | [쿠팡 검색](https://www.coupang.com/np/search?q=샌디스크+microSD+64GB+A2) |
| ☐ | ESP32-S3 DevKitC-1 (N16R8) | PCB 도착 전(W3~W4) 펌웨어 개발용 개발보드 | 1 | 12,000 | [디바이스마트 검색](https://www.devicemart.co.kr/goods/search?keyword=ESP32-S3-DevKitC) |
| ☐ | Pololu D24V50F5 | 5V/5A 벅 컨버터 모듈 — 7.4V 입력을 RPi용 5V로. Board A에 헤더 실장 | 1 | 15,000 | [Pololu 공식](https://www.pololu.com/search?query=D24V50F5) · [디바이스마트 검색](https://www.devicemart.co.kr/goods/search?keyword=D24V50F5) |
| ☐ | Pololu D24V60F6 | 6V/6A 벅 컨버터 모듈 — 서보/모터 레일 전원 | 1 | 18,000 | [Pololu 공식](https://www.pololu.com/search?query=D24V60F6) · [디바이스마트 검색](https://www.devicemart.co.kr/goods/search?keyword=D24V60F6) |
| ☐ | XT60 커넥터 (수/암 세트) | 전원 인입 커넥터 + 벤치 PSU 급전 케이블 제작용 | 1세트 | 5,000 | [쿠팡 검색](https://www.coupang.com/np/search?q=XT60+커넥터) |

**A 소계: ~82,000** (PSU 보유 시 70,000)

> Pololu 모듈 국내 재고 없으면: Pololu 직구(배송 1~2주, 배송비 ~2만 — 두 개 묶으면 감내) 또는 AliExpress 동급 5A/6A 벅 모듈로 대체 가능. 대체 시 출력 리플 스펙 확인.

## B. AliExpress (1~3주 — **이번 주 결제 필수**, W4 크리티컬 패스)

| ✓ | 품목 | 설명 | 수량 | 추정가 | 링크 |
|---|---|---|---|---|---|
| ☐ | SG90 서보 | 머리 yaw/pitch 구동 (소형 9g 서보) | 2 | 4,000 | [Ali 검색](https://www.aliexpress.com/w/wholesale-SG90-servo.html) |
| ☐ | MG90S 서보 | 팔 4축 + 다리 스윙 2축 (메탈기어, SG90보다 토크↑) | 6 | 21,000 | [Ali 검색](https://www.aliexpress.com/w/wholesale-MG90S-servo.html) |
| ☐ | N20 기어드 모터 6V 100RPM | 휠 구동용 초소형 DC 기어드 모터 | 2 | 12,000 | [Ali 검색](https://www.aliexpress.com/w/wholesale-N20-gear-motor-6V-100RPM.html) |
| ☐ | 고무 휠 Φ40~50mm (N20 축용) | 구동 휠. N20 3mm D축 호환 확인 | 1쌍 | 5,000 | [Ali 검색](https://www.aliexpress.com/w/wholesale-N20-wheel-43mm.html) |
| ☐ | Waveshare 1.28" Round LCD (GC9A01) | 얼굴 디스플레이 (240×240 원형, SPI) | 1 | 25,000 | [Ali 검색](https://www.aliexpress.com/w/wholesale-GC9A01-1.28-round-LCD.html) — 국내 급하면 [디바이스마트](https://www.devicemart.co.kr/goods/search?keyword=GC9A01) |
| ☐ | INMP441 I2S 마이크 모듈 | wake-word 음성 입력 (디지털 I2S, 노이즈 적음) | 1 | 5,000 | [Ali 검색](https://www.aliexpress.com/w/wholesale-INMP441.html) |
| ☐ | 스피커 8Ω 0.5W 28mm | 응답 음원 출력 (PAM8403 앰프는 PCB 실장) | 1 | 3,000 | [Ali 검색](https://www.aliexpress.com/w/wholesale-speaker-8ohm-0.5W-28mm.html) |
| ☐ | 듀폰 와이어 + JST-XH/PH 커넥터 키트 | 서보×10·모터·LCD·마이크·스피커 배선 (압착 단자 포함 키트) | 1식 | 15,000 | [Ali 검색](https://www.aliexpress.com/w/wholesale-JST-XH-connector-kit.html) |
| ☐ | M2/M3 나사·너트·스페이서 세트 | PCB 마운트 + 기구 조립 | 1식 | 8,000 | [Ali 검색](https://www.aliexpress.com/w/wholesale-M2-M3-screw-standoff-kit.html) |
| ☐ | VHB 양면테이프 + 케이블 타이 | 기구 고정/케이블 정리 | 1식 | 3,000 | [쿠팡 검색](https://www.coupang.com/np/search?q=3M+VHB+양면테이프) |
| ☐ | 마스터 전원 토글 스위치 | 전원 인입 차단 스위치 | 1 | 2,000 | [Ali 검색](https://www.aliexpress.com/w/wholesale-toggle-switch-10A.html) |

**B 소계: ~103,000**

## C. 랩 도구 최소 셋 (쿠팡/Ali 혼합 — **보유분 체크 후 차감**)

| ✓ | 품목 | 설명 | 추정가 | 링크 |
|---|---|---|---|---|
| ☐ | Pinecil V2 (또는 T12 스테이션) | 인두. 전량 JLC 어셈블리라 남는 납땜은 스루홀/커넥터/수리뿐 — 휴대형이면 충분 | 40,000 | [Ali 검색](https://www.aliexpress.com/w/wholesale-Pinecil-V2.html) |
| ☐ | 솔더 0.5mm rosin core (소형 릴) | 유연 납. 무연은 초심자 난이도↑라 유연 권장 | 10,000 | [쿠팡 검색](https://www.coupang.com/np/search?q=실납+0.5mm+주석) |
| ☐ | 플럭스 펜 | 납땜 품질/수리용 | 8,000 | [쿠팡 검색](https://www.coupang.com/np/search?q=플럭스+펜) |
| ☐ | 솔더윅 + 솔더서커 | 납 제거 (실수 복구) | 5,000 | [쿠팡 검색](https://www.coupang.com/np/search?q=솔더윅+솔더서커) |
| ☐ | ESD 핀셋 (직/곡) | 소형 부품 취급 | 10,000 | [Ali 검색](https://www.aliexpress.com/w/wholesale-ESD-tweezers-set.html) |
| ☐ | 헬핑핸드 (저가) | 납땜 시 보드/와이어 고정 | 10,000 | [쿠팡 검색](https://www.coupang.com/np/search?q=헬핑핸드+납땜) |
| ☐ | 멀티미터 Aneng AN8008 | 전압/도통/전류 측정 — 브링업 필수 1순위 | 30,000 | [Ali 검색](https://www.aliexpress.com/w/wholesale-ANENG-AN8008.html) |
| ☐ | 로직 애널라이저 8ch (Saleae 호환) | I2C/SPI/UART 신호 디버깅 (PulseView 사용) | 20,000 | [Ali 검색](https://www.aliexpress.com/w/wholesale-logic-analyzer-8ch-24MHz.html) |
| ☐ | 가변 벤치 PSU (30V/5A급) | 브링업 급전 + 전류 제한(단락 보호). **배터리 보류의 전제 장비** | 40,000 | [쿠팡 검색](https://www.coupang.com/np/search?q=DC+파워서플라이+30V+5A) |
| ☐ | 헤드밴드 루페 5x/10x | 납땜부/실장 검수 | 15,000 | [쿠팡 검색](https://www.coupang.com/np/search?q=헤드밴드+루페) |
| ☐ | 와이어 스트리퍼 (저가) | 배선 작업 | 10,000 | [쿠팡 검색](https://www.coupang.com/np/search?q=와이어+스트리퍼) |
| ☐ | 압착 펜치 IWISS SN-28B | 듀폰/JST 커넥터 압착 — 커넥터 키트와 세트로 필수 | 25,000 | [쿠팡 검색](https://www.coupang.com/np/search?q=IWISS+SN-28B) |
| ☐ | 정밀 니퍼 Hakko CHP-170 | 리드/타이 컷팅 | 12,000 | [쿠팡 검색](https://www.coupang.com/np/search?q=Hakko+CHP-170) |
| ☐ | 정밀 드라이버 세트 (저가) | M2/M3 + 소형 나사 | 10,000 | [쿠팡 검색](https://www.coupang.com/np/search?q=정밀드라이버+세트) |
| ☐ | ESD 손목 스트랩 | 정전기 보호 (IC 취급 시) | 5,000 | [쿠팡 검색](https://www.coupang.com/np/search?q=정전기+방지+손목+스트랩) |

**C 소계: ~250,000** (보유분만큼 차감)

## D. 배치 2 — W2에 발주 (지금 아님)

| 품목 | 설명 | 추정가 | 링크 |
|---|---|---|---|
| PCB fab 2종 + 전 부품 SMT 어셈블리 | Board A(전원)/Board B(HAT) 4-layer 5장씩 + 실장 부품 전체(ESP32-S3, PCA9685, MPR121, MPU6050, TCA9548A, CH340N, PAM8403, TB6612, INA219×2, 션트, 보호회로, R/C, 커넥터) + 어셈블리 수수료 | ~155,000 | [JLCPCB](https://jlcpcb.com) — layout 완성 + 24h 텀 재검토 후 |

## E. 보류 (트리거 발생 시 구매)

| 품목 | 추정가 | 트리거 |
|---|---|---|
| 2S 5000mAh 리포(BMS 내장) + iMAX B6 충전기 | 65,000 | 이동 운용(전원선 없이 들고 다님) 필요해질 때 |
| VL53L0X ToF 거리센서 | 8,000 | W8 보행 단계에서 모서리 감지 채택 시 |
| 3D 외형 외주 출력 | 100,000~150,000 | W10 모델링 완료 후 |
| 오실로스코프 (FNIRSI 1014D급) | 150,000 | 전원 리플/아날로그 디버깅에 막힐 때 |
| 핫에어 스테이션 + 페이스트 | 112,000 | SMT 리워크가 실제로 생길 때 |

## 총계

| 배치 | 금액 |
|---|---|
| 배치 1 (A+B+C, 지금) | **~435,000** (PSU 보유 시 -12K, 랩 도구 보유분 추가 차감) |
| 배치 2 (W2) | ~155,000 |
| **코어 합계** | **~590,000** |
| 보류 (전부 트리거 시) | +435,000~485,000 |
