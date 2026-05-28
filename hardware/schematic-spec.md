# PCB Schematic 설계 사양서

> KiCad 8.x 기준. 본인이 schematic 그릴 때 보고 작업할 가이드.
> 4-layer board: Top(signal) / GND / PWR / Bottom(signal).

## 보드 분할

| 보드 | 크기 (예상) | 역할 |
|---|---|---|
| **Board A — Power Distribution** | 50 × 60 mm | 배터리 입력, 보호, 5V/6V/3V3 생성, 전류 모니터, 충전 단자 |
| **Board B — RPi5 HAT (I/O)** | 65 × 56 mm (RPi5 HAT 표준) | RPi5 40핀 연결, ESP32-S3 온보드, PCA9685, MPR121, IMU, I2S 오디오, LCD 커넥터, 확장 헤더 |

두 보드는 6핀 JST-XH 케이블로 연결: `[5V, 6V, 3V3, GND, GND, I2C_SDA/SCL → INA219 통신]` (INA219 두 개는 Board A 측에 실장).

## Reference Designator 컨벤션

| 접두 | 용도 |
|---|---|
| U | IC, 모듈 |
| Q | 트랜지스터/MOSFET |
| D | 다이오드, LED |
| R | 저항 |
| C | 캐패시터 |
| L | 인덕터 |
| F | 퓨즈, 폴리스위치 |
| J | 커넥터, 핀헤더 |
| TP | 테스트 포인트 |
| SW | 스위치 |
| M | 모터 (외부 부품) |

Board A는 A1, B는 B1부터 시작. 예: `U_A1`은 Power 보드 IC1, `U_B1`은 HAT IC1. (KiCad에서 Symbol Properties → Reference Prefix 설정으로 강제.)

## 네트 명명 규칙

- 전원: `VBAT`, `+5V`, `+6V_SERVO`, `+3V3`, `GND`
- I2C: `I2C_MAIN_SDA`, `I2C_MAIN_SCL` (RPi 메인), `I2C_SRV_SDA`, `I2C_SRV_SCL` (서보 보드)
- UART (RPi ↔ ESP32-S3): `RPI_TX`, `RPI_RX` (RPi 관점), 보드에서는 `MCU_RX`, `MCU_TX`
- SPI (LCD): `SPI_SCK`, `SPI_MOSI`, `LCD_CS`, `LCD_DC`, `LCD_RST`, `LCD_BL`
- I2S (마이크): `I2S_BCLK`, `I2S_WS`, `I2S_DIN`
- 인터럽트: `MPU_INT`, `MPR_IRQ`

---

## Board A — Power Distribution

### 블록 다이어그램

```
J_A1 (XT60 배터리 입력)
   │
   ├─ F_A1 (10A 폴리스위치)
   ├─ SW_A1 (전원 토글 스위치, SPDT)
   │
   ├─ Q_A1 (P-MOSFET 역접속 보호, IRLML6402)
   │
   ├─ Bulk Cap (C_A1: 470μF / 25V 알루미늄 전해)
   │
   ├──► U_A1 (5V Buck, Pololu D24V50F5 모듈) ──┬─► +5V
   │                                            └─ INA219 #1 (U_A3, addr 0x40)
   │
   ├──► U_A2 (6V Buck, Pololu D24V60F6 모듈) ──┬─► +6V_SERVO
   │                                            ├─ 캐패시터 뱅크 (C_A2~C_A5: 470μF ×4)
   │                                            └─ INA219 #2 (U_A4, addr 0x41)
   │
   ├──► U_A5 (3V3 LDO, AMS1117-3.3) ──► +3V3
   │
   ├─ Battery monitor: R_A1(20K) / R_A2(10K) 분압 → J_A2 (Board B로)
   │
   ├─ J_A3 (충전 입력: XT60 또는 별도 충전 잭, 발란스 단자 포함)
   │
   └─ J_A4 (Board B로 출력: +5V, +6V_SERVO, +3V3, GND ×2, I2C_SDA, I2C_SCL, VBAT_SENSE)
```

### 핵심 부품 핀맵

#### U_A1 — Pololu D24V50F5 (5V Buck 모듈)
- VIN: VBAT (보호 회로 후)
- GND: GND
- VOUT: +5V
- EN: VIN (풀업) 또는 GPIO 제어용 헤더 (선택)
- 별도 디커플링 캡: VIN에 100μF, VOUT에 47μF + 100nF

#### U_A3, U_A4 — INA219 ×2

| 핀 | U_A3 (5V 레일) | U_A4 (6V_SERVO 레일) |
|---|---|---|
| VS+ | Shunt 고전압 측 | Shunt 고전압 측 |
| VS- | Shunt 저전압 측 → 부하 | Shunt 저전압 측 → 부하 |
| GND | GND | GND |
| VCC | +5V (또는 +3V3) | +5V |
| SDA | I2C_SDA → J_A4 | I2C_SDA → J_A4 |
| SCL | I2C_SCL → J_A4 | I2C_SCL → J_A4 |
| A0, A1 | 둘 다 GND (addr=0x40) | A0=VCC, A1=GND (addr=0x41) |

션트 저항: R_A3 = 0.01Ω 1% 1W (5V 레일), R_A4 = 0.01Ω 1% 1W (6V 레일). 최대 측정 전류 = 0.32V / 0.01 = 32A 이론치, 실용 8A 범위.

#### Q_A1 — IRLML6402 (P-channel MOSFET, 역접속 보호)
- Source: VBAT(+) 인입 측
- Drain: 후단 부하 측 (Q_A1_OUT 네트)
- Gate: 분압 R_A5(10K)와 R_A6(100K)로 VBAT에서 GND 사이. Vgs ≈ -Vbatt × (10K/110K) ≈ -0.67V (불충분!)
- **수정**: Gate는 단순히 GND로 직결. 정상 결선 시 Vgs = -Vbatt → 도통. 단, Vbatt 인가 전에 음전압이 잠시 걸릴 수 있어 R_A5 (100K) Gate-Source 보호 저항 + Zener D_A1 (10V) Vgs 클램프 추가.

```
VBAT(+) ─┬─ S(Q_A1) ─ D(Q_A1) ─ Q_A1_OUT
         │              
         R_A5 (100K, S-G)
         │
         G(Q_A1) ─── D_A1 (Zener 10V to S) + 직결 GND
```

### 테스트 포인트 (브링업 디버깅용)

- TP_A1: VBAT
- TP_A2: Q_A1_OUT (보호 통과 후)
- TP_A3: +5V
- TP_A4: +6V_SERVO
- TP_A5: +3V3
- TP_A6: GND
- TP_A7: I2C_SDA
- TP_A8: I2C_SCL

---

## Board B — RPi5 HAT

### 블록 다이어그램

```
J_B1 (RPi5 40핀 헤더, 패스스루)
   │
   ├─ I2C (GPIO2/3) ──► I2C_MUX (U_B1, TCA9548A) ──┬─► I2C_CH0: MPU6050 (U_B2)
   │                                                ├─► I2C_CH1: MPR121 (U_B3)
   │                                                ├─► I2C_CH2: PCA9685 (U_B4)
   │                                                ├─► I2C_CH3: 확장 헤더 J_B5
   │                                                └─► I2C_CH4-7: 예비
   │
   ├─ UART (GPIO14/15) ──► ESP32-S3 (U_B5)
   │                          │
   │                          ├─ USB-UART (CH340N, U_B6) ── J_B2 (USB-C, 펌웨어 플래시)
   │                          ├─ Boot 버튼 (SW_B1), Reset 버튼 (SW_B2)
   │                          ├─ I2C_SRV ──► PCA9685 V+ 제어 (별도 I2C 채널, 또는 메인 공유)
   │                          ├─ GPIO ──► PCA9685 OE# (출력 enable)
   │                          ├─ ADC ──► VBAT_SENSE (Board A에서)
   │                          └─ GPIO ──► MOTOR_DRIVER (TB6612FNG) AIN1/AIN2/BIN1/BIN2/PWMA/PWMB
   │
   ├─ SPI (GPIO10/11, CE0) ──► LCD 커넥터 J_B3 (Waveshare 1.28" Round)
   │                              핀: VCC(3V3), GND, SCK, MOSI, CS, DC, RST, BL
   │
   ├─ I2S (GPIO18/19/20/21) ──► INMP441 마이크 커넥터 J_B4
   │
   ├─ Audio out (GPIO13 PWM 또는 RPi5 헤드폰잭 사용) ──► PAM8403 (U_B7) ──► 스피커 J_B6
   │
   ├─ PCA9685 (U_B4)
   │     │ V+: +6V_SERVO (Board A에서)
   │     │ VCC: +3V3 (로직)
   │     │ I2C addr 0x40 (TCA9548A 통해 격리됨)
   │     │ OE#: ESP32 GPIO 제어
   │     └─ PWM 0~15 ──► J_B7~J_B16 (서보 커넥터 ×10, 3핀 JST-PH)
   │
   ├─ TB6612FNG (U_B8) ──► J_B17, J_B18 (N20 모터 ×2, 2핀 JST-PH)
   │     │ VM: +6V_SERVO
   │     └ VCC: +5V (로직)
   │
   ├─ 전원 입력 J_B19 (Board A에서: +5V, +6V_SERVO, +3V3, GND, I2C, VBAT_SENSE)
   │
   └─ 확장 헤더:
       - J_B20: I2C_CH3 + 3V3 + GND (센서 확장)
       - J_B21: UART2 + 3V3 + GND (서브 모듈)
       - J_B22: GPIO 8핀 + 3V3 + 5V + GND (범용)
```

### RPi5 40핀 사용 핀맵

| RPi5 핀 | GPIO | 용도 |
|---|---|---|
| 1, 17 | 3V3 | (HAT는 자체 3V3 사용, 풀업만) |
| 2, 4 | 5V | HAT 내부에서는 미사용, Board A에서 별도 +5V 인가 |
| 6, 9, 14, 20, 25, 30, 34, 39 | GND | |
| 3 | GPIO2 (I2C_SDA) | TCA9548A SDA |
| 5 | GPIO3 (I2C_SCL) | TCA9548A SCL |
| 8 | GPIO14 (UART_TX) | ESP32 RX |
| 10 | GPIO15 (UART_RX) | ESP32 TX |
| 11 | GPIO17 | LCD_RST |
| 13 | GPIO27 | LCD_DC |
| 15 | GPIO22 | LCD_BL (PWM 가능) |
| 19 | GPIO10 (SPI_MOSI) | LCD MOSI |
| 21 | GPIO9 (SPI_MISO) | (LCD 미사용, 확장 헤더로) |
| 23 | GPIO11 (SPI_SCLK) | LCD SCK |
| 24 | GPIO8 (SPI_CE0) | LCD_CS |
| 26 | GPIO7 | 확장 (예비 CS) |
| 12 | GPIO18 (I2S_CLK) | INMP441 BCLK |
| 35 | GPIO19 (I2S_FS) | INMP441 WS |
| 38 | GPIO20 (I2S_DIN) | INMP441 DOUT |
| 40 | GPIO21 (I2S_DOUT) | (마이크는 IN만 사용) |
| 16 | GPIO23 | ESP32 RESET (RPi가 ESP32 리셋 가능) |
| 18 | GPIO24 | ESP32 BOOT 모드 (펌웨어 OTA 시) |
| 7 | GPIO4 | 사용자 버튼 (선택, 두피 정전식 외 물리버튼) |
| 22, 29, 31, 32, 33, 36, 37 | GPIO 예비 | 확장 헤더로 노출 |

### ESP32-S3 핀 사용

| ESP32-S3 핀 | 용도 |
|---|---|
| TXD0 (GPIO43) | RPi RX |
| RXD0 (GPIO44) | RPi TX |
| GPIO4 | PCA9685 OE# |
| GPIO5, 6 | I2C_SRV SDA/SCL (PCA9685 직접 제어 라인, TCA9548A 거치지 않음) |
| GPIO7~12 | TB6612FNG (AIN1, AIN2, PWMA, BIN1, BIN2, PWMB) |
| GPIO1 (ADC1_CH0) | VBAT_SENSE |
| GPIO2 (ADC1_CH1) | 예비 ADC |
| GPIO13~21 | 확장 헤더로 노출 |
| GPIO0 (BOOT) | SW_B1 + 풀업 |
| EN | SW_B2 + 풀업 |
| USB D+/D- (GPIO19, 20) | CH340N으로 → USB-C J_B2 |

> ESP32-S3 자체 USB native도 있지만 CH340N 경유로 단순화 (RPi에서 보드 인식 안정성↑). 펌웨어 OTA는 W3 이후 RPi → ESP32 UART OTA 구현 시 USB 불필요.

### LCD 커넥터 J_B3 핀맵

| 핀 | 신호 | 비고 |
|---|---|---|
| 1 | +3V3 | LCD 전원 |
| 2 | GND | |
| 3 | SCK | RPi GPIO11 |
| 4 | MOSI | RPi GPIO10 |
| 5 | CS | RPi GPIO8 |
| 6 | DC | RPi GPIO27 |
| 7 | RST | RPi GPIO17 |
| 8 | BL | RPi GPIO22 (PWM 백라이트) |

JST-PH 1.25mm 8핀, 또는 FFC 8핀. Waveshare 기본 모듈 핀 순서와 맞춰 라벨링.

### 디커플링 캡

| 위치 | 캡 |
|---|---|
| 모든 IC VCC 핀 | 100nF 0603 (≤ 5mm 거리) |
| TCA9548A, MPR121, INA219 | + 4.7μF 0805 (전원 안정화) |
| ESP32-S3 VDD | 100nF + 10μF + 22μF (datasheet 권장) |
| PCA9685 V+ (6V 레일) | 220μF 1개 (인근 인입부) |
| RPi5 5V 인입부 | 470μF + 100nF |
| LCD 커넥터 인근 | 10μF + 100nF |

### 그라운드 처리

- L2 layer 전체 GND plane
- 6V_SERVO 레일과 5V_MAIN 레일은 L3 (PWR plane)에서 분리, single-point bridge로 합류 (Board A의 star point)
- Board B에서는 두 레일이 분리된 채로 들어오고, GND는 통합 plane으로 받음
- 서보 PWM 라인 routing은 신호 그라운드 인접 트레이스로 짝지어 ground-coupled
- I2C 라인은 별도 trace, 풀업 저항(4.7K) Board B 측 1쌍만 (TCA9548A 입력 측)

### Layer Stackup (4-layer)

| Layer | 용도 |
|---|---|
| L1 (Top) | Signal — 디지털 신호, IC 배치 |
| L2 | GND plane (solid) |
| L3 | PWR plane — 5V/6V/3V3 분리 영역 |
| L4 (Bottom) | Signal — 보조 신호, 서보 커넥터 측 trace |

### 트레이스 폭

| 신호 | 폭 (4-layer 1oz Cu, 20°C 상승) |
|---|---|
| +6V_SERVO (전원 backbone) | 2.0 mm |
| +5V_MAIN (RPi backbone) | 2.5 mm (5A 견딤) |
| +3V3 | 0.5 mm |
| GND (return path) | plane 사용 |
| 서보 PWM 신호 | 0.2 mm |
| I2C, SPI, UART | 0.15~0.2 mm |
| LCD SPI (속도 ↑) | 0.2 mm, 임피던스 ~50Ω 목표 (4-layer 0.2mm trace, 0.2mm dielectric에 가까움) |

## KiCad 워크플로우

1. **Symbol 라이브러리**: 기본 라이브러리 + [SnapEDA](https://www.snapeda.com/), [Ultra Librarian](https://www.ultralibrarian.com/), 또는 직접 그리기. ESP32-S3, PCA9685, MPR121, INA219, TB6612FNG, IRLML6402는 모두 공개 라이브러리 있음.
2. **Footprint**: 손납땜 우선이면 0805, 자신 있으면 0603. IC는 SOIC/TSSOP 우선, QFN은 핫에어 필수.
3. **schematic 작성 → ERC pass → PCB 시작 → DRC pass → Gerber export → JLCPCB 업로드**.
4. **JLCPCB 설정**:
   - 4 layer, 1.6mm 두께, 1oz Cu
   - HASL (lead-free) 또는 ENIG (rework 자주 한다면 ENIG 추천, +5K)
   - Silkscreen White
   - 5장 발주
   - **Stencil 포함 발주** (SMT 부품 페이스트 도포용, 약 5K)

## v1 → v2 리비전 백로그

PCB는 한 번 발주하면 2주 묶임. 첫 리비전에 모든 걸 완벽하게 넣지 말고, 다음은 의도적으로 v2로 미룸:

- USB-PD 패스스루 충전
- Hailo-8L M.2 HAT 통합 (별도 적층으로 처리)
- 무선 충전 코일 직결 풋프린트
- 카메라 CSI 보조 커넥터
- 정식 soft-start 회로 (v1은 NTC로 단순화)

## 체크리스트 (발주 전 본인이 확인)

- [ ] 모든 IC에 디커플링 캡 100nF 인접 배치됨
- [ ] 전원 레일 trace 폭 계산 완료 (Saturn PCB Toolkit 추천)
- [ ] I2C 풀업 저항 (4.7K) 1쌍만 (멀티 풀업 금지)
- [ ] 서보 커넥터 극성 통일 (PWM-V-G 순서 또는 G-V-PWM, 서보 매뉴얼 확인)
- [ ] ESP32-S3 BOOT/RESET 풀업 + 캡 (datasheet 권장값)
- [ ] RPi5 40핀 헤더 키-pin (9번) 차단되어 있는지
- [ ] 모든 커넥터에 silkscreen 라벨 (J 번호 + 핀 1 표시)
- [ ] 테스트 포인트 8개 이상 (전원/통신 노드)
- [ ] DRC 0 errors, ERC 0 errors
- [ ] 3D 뷰에서 부품 충돌/간섭 없음
- [ ] BOM export → JLCPCB Parts 일치 확인
