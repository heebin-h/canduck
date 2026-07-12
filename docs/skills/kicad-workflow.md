# Skill — KiCad Workflow (Schematic → PCB → DRC → Gerber → JLCPCB)

> 대상: Board A (canduck-power, 50×60mm), Board B (canduck-hat, 65×56mm RPi5 HAT).
> KiCad 9.x 기준. 세부 부품 배치·핀맵은 `hardware/schematic-spec.md` 참고.
> heebin 담당(로컬 KiCad 설치·실행)과 Claude 담당(설계 리뷰·체크리스트·export 스크립트)을 구분.

## 0. 사전 조건

- [ ] KiCad 9.x 설치, 한국어/커스텀 부품 라이브러리 추가 (heebin, W1 진입 전)
- [ ] `hardware/schematic-spec.md`, `hardware/power-budget.md`, `hardware/parts.md` 최신 확인

## 1. 프로젝트 생성

```
canduck-power/   (Board A)
canduck-hat/     (Board B)
```

- 새 KiCad 프로젝트 2개, 4-layer stackup: Top(signal) / GND(plane) / PWR(plane) / Bottom(signal)
- Reference prefix 규칙: `hardware/schematic-spec.md` § Reference Designator 표 그대로 (U/Q/D/R/C/L/F/J/TP/SW/M), Board A = `A1`부터, Board B = `B1`부터

## 2. Schematic

1. 심볼 배치 — schematic-spec.md 블록 다이어그램 순서대로 (전원 입력 → 보호 → buck → 부하, 또는 RPi 헤더 → mux → 주변 IC)
2. 네트 이름 규칙 적용: `VBAT`, `+5V`, `+6V_SERVO`, `+3V3`, `GND`, `I2C_MAIN_SDA/SCL`, `RPI_TX/RX`, `SPI_SCK/MOSI`, `LCD_CS/DC/RST/BL`, `I2S_BCLK/WS/DIN`, `MPU_INT`, `MPR_IRQ`
3. 디커플링 캡 — 모든 IC VCC 핀에 100nF, 전원 모듈 입출력에 스펙대로 (예: U_A1 VIN 100μF / VOUT 47μF+100nF)
4. 테스트포인트 배치 — schematic-spec.md TP_A1~A8 (Board A), Board B 쪽도 동일 원칙 (전원 레일 + 주요 신호선)
5. **ERC clean** 확인 (Inspect → Electrical Rules Checker) — warning 0, error 0까지

### Claude 체크리스트 (schematic review)
- [ ] 모든 IC 핀 데이터시트 대조 (VCC/GND/방향 반전 없는지)
- [ ] 풀업 저항 누락 확인 (I2C SDA/SCL, 인터럽트 라인)
- [ ] Q_A1 게이트 보호 저항/제너 다이오드 반영 (schematic-spec.md 수정사항 — 단순 GND 직결 아님)
- [ ] INA219 A0/A1 주소 핀 설정 확인 (0x40 / 0x41 충돌 없음)
- [ ] 커넥터 극성/핀 순서 (특히 J_A4 Board A→B 케이블, RPi5 40핀 J_B1)

### heebin 체크리스트 (종이 출력 재검토, W1 게이트)
- [ ] schematic PDF 출력 → 손으로 넷 추적
- [ ] 빠진 디커플링 캡, 잘못된 핀 연결 확인

## 3. PCB Layout

1. Footprint 할당 — 안 맞으면 KiCad 라이브러리 검색 또는 직접 제작 (특히 ESP32-S3-WROOM-1 모듈, RPi5 40핀 헤더, Waveshare LCD 커넥터)
2. Board outline: Board A 50×60mm / Board B 65×56mm (RPi5 HAT 표준 마운트홀 위치 정확히 — 4-mounting-hole 표준 좌표)
3. Stackup 배치: Top/Bottom = signal, 내층 2장 = GND/PWR plane
4. 배치 순서: 전원부 먼저 (buck 모듈, 캡 뱅크) → 커넥터를 보드 가장자리로 → 나머지 로직
5. 트레이스 폭:
   - 전원 (VBAT, +5V, +6V_SERVO): 2~2.5mm 이상 (power-budget.md 전류 기준 — 6V 레일 5A 상시 + 7A peak)
   - 서보 헤더 GND는 두껍게, 케이블 타이 정리 고려해 보드 가장자리 배치
   - 신호선: 표준 6~8mil
6. INA219 shunt kelvin connection 정확히 (4-wire 감지, 션트 저항 양단에서 직접 tap)
7. ESP32-S3 안테나 영역 — 밑에 copper pour 금지, 클리어런스 확보
8. **DRC clean** 확인 — clearance/annular ring/net 미연결 0

### Claude 체크리스트 (layout review)
- [ ] RPi5 40핀 헤더 pin 1 방향 재확인 (역삽입 방지 실크 표시)
- [ ] 전원 plane 분할 확인 (GND/PWR plane에 슬릿/아일랜드 없는지)
- [ ] 서보 커넥터 10개 + 모터 커넥터 2개 배치가 실제 케이블 라우팅과 충돌 없는지 (3D 뷰로 확인)
- [ ] 열원(buck 모듈) 근처 캡/IC 열 마진

## 4. Export

```
Gerber (File → Fabrication Outputs → Gerbers)
  - 레이어: F.Cu, In1.Cu, In2.Cu, B.Cu, F/B.SilkS, F/B.Mask, Edge.Cuts
Drill file (Excellon, PTH+NPTH 분리 또는 병합 — JLCPCB 기본값 확인)
BOM (Tools → Generate BOM, CSV, JLCPCB 포맷 필드 매핑: Comment/Designator/Footprint/LCSC Part#)
Pick & Place (Fabrication Outputs → Component Placement, JLCPCB SMT 이용 시)
```

- Gerber/drill을 zip으로 묶어 JLCPCB gerber viewer로 최종 육안 검토 (레이어 순서, outline 닫혀있는지)

## 5. JLCPCB 발주

1. Gerber zip 업로드 → 자동 레이어/치수 인식 확인
2. 사양: 4-layer, HASL(lead-free 권장), 5장, **stencil 동봉 체크**
3. SMT 조립 이용 시: BOM + CPL 업로드, JLCPCB Parts Library 우선 매칭 부품으로 BOM 정리해두면 비용↓ (`hardware/parts.md` 대체품 옵션 참고)
4. AliExpress로 SMT 잔여 수동 부품 (캡/저항/커넥터/IC) 별도 발주

### ⚠️ 발주 게이트 (roadmap.md W2)
- 발주 전 **24시간 텀 두고 schematic + layout 재검토** — 발주 후 hold 요청은 24시간 내에만 가능
- Board A 결함 발견 시 → rev2 즉시 결정 여부 (재발주 시 +2주)

## 6. Brought-up 순서 (부품 실장 후, roadmap.md W4/W5 참고)

1. 실장 전 short 체크 (멀티미터, 전원 레일 간)
2. 가변 PSU로 저전류 제한(100mA) 인가 → 출력 전압 확인
3. 부하 점진 인가 (10K → 1K → 100Ω)
4. I2C 디바이스 스캔 (`i2cdetect`) — 주소 충돌/미인식 확인
5. 결함 시 → 패치 와이어 우회 가능성 평가, 안 되면 rev2

## 7. 산출물 체크리스트

- [ ] Schematic PDF export (Board A, Board B)
- [ ] Gerber + drill + BOM + CPL zip
- [ ] JLCPCB 주문 확인 메일/영수증
- [ ] `hardware/` 폴더에 최종 스냅샷 (선택: PDF만이라도 버전관리)
