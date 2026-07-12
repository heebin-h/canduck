# 12주 로드맵

> 시작일: TBD. 각 주차는 평일 저녁 + 주말 중심으로 산정.

## 마일스톤 요약

```
W0 ──► W2:   schematic + PCB 발주 + Blender 학습 시작 (병행)
W3 ──► W5:   dev board로 펌웨어/호스트 골격 + PCB 브링업
W6 ──► W9:   인터랙션 (음성/PC 연동) + 팔 + 두통포즈
W10 ─► W12:  보행 + 외형 마감 + 통합 시연
```

## 주차별 작업

### W0 — 셋업 (1주)

**목표**: 발주 완료, 개발 환경 가동, Blender 학습 착수.

- [ ] 부품 1차 발주 (랩 도구 + RPi5 + dev board + 센서 모듈)
- [ ] RPi 5 OS(Bookworm 64-bit) 설치, SSH/VNC 활성, hostname=`canduck`
- [ ] `mosquitto` 설치, 1883 LAN 한정 listener 설정
- [ ] macOS에 KiCad 8.x 설치 + 한국어 부품 라이브러리 추가
- [ ] PlatformIO + VSCode 확장 설치
- [ ] Python 3.12 venv, paho-mqtt, pyserial-asyncio, pygame, smbus2 의존성 확인
- [ ] git remote (private) 셋업 또는 로컬 git만
- [ ] Blender 학습 시작: 인터페이스 + sculpt + retopo 워크플로우 (Blender Guru, Grant Abbitt 일반 강좌)

**산출물**: 개발 환경 동작 확인, 부품 도착 트래킹 시트.

**게이트**: 발주 리스트 본인이 마지막으로 검토 → OK 후 결제.

---

### W1 — Schematic 설계 (1주)

**목표**: Board A + Board B schematic 완성, ERC pass.

- [ ] KiCad 새 프로젝트 `canduck-power` (Board A)
  - [ ] 배터리 입력, 보호회로, 5V/6V/3V3 Buck/LDO 배치
  - [ ] INA219 ×2 + 션트 저항 배치
  - [ ] 충전 단자, 테스트 포인트, 출력 커넥터
  - [ ] ERC clean
- [ ] KiCad 새 프로젝트 `canduck-hat` (Board B)
  - [ ] RPi5 40핀 헤더 심볼 (`Raspberry_Pi_2_3` 호환 또는 직접 제작)
  - [ ] ESP32-S3 모듈 + CH340N + USB-C
  - [ ] PCA9685, MPR121, MPU6050, TCA9548A, PAM8403, TB6612FNG 배치
  - [ ] 서보 커넥터 ×10, 모터 커넥터 ×2, LCD 커넥터, 마이크 커넥터, 스피커 커넥터
  - [ ] 확장 헤더 (I2C, UART, GPIO)
  - [ ] ERC clean

**산출물**: 두 schematic의 PDF export.

**게이트**: 본인이 schematic을 출력해서 종이로 한 번 더 추적 — 잘못된 핀 연결, 빠진 풀업, 디커플링 캡 누락 등.

---

### W2 — PCB Layout + 발주 (1주)

**목표**: 두 보드 layout 완성, DRC pass, JLCPCB 발주.

- [ ] Board A layout
  - [ ] 4-layer stackup 설정 (Top / GND / PWR / Bottom)
  - [ ] Buck 모듈 배치, 입출력 캡 배치
  - [ ] 션트 저항 → INA219 kelvin connection
  - [ ] 트레이스 폭 (전원 2~2.5mm)
  - [ ] DRC clean
- [ ] Board B layout
  - [ ] RPi5 헤더 핀맵 핀 1 정확히
  - [ ] ESP32-S3 모듈 안테나 영역 클리어런스 (no copper under antenna)
  - [ ] 서보 커넥터를 보드 가장자리에 배치 (배선 정리)
  - [ ] LCD 커넥터 위치 (외형 본체 내 LCD 위치와 맞물림 고려)
  - [ ] DRC clean
- [ ] Gerber + drill + BOM + Pick&Place export
- [ ] JLCPCB 업로드, 5장 발주, **stencil 동봉**
- [ ] AliExpress SMT 부품 잔여분 발주 (캡, 저항, 커넥터, IC)

**산출물**: 발주 완료. 추정 도착 W4 중반.

**게이트**: ⚠️ **발주 전 본인이 schematic + layout 24시간 텀 두고 재검토**. 발주하면 2주 묶임.

---

### W3 — LCD 얼굴 + 펌웨어 골격 (dev board) (1주)

**목표**: dev board(RPi5 + ESP32 DevKit + 노출 배선)로 LCD 얼굴 표정 6종 + UART 프로토콜 골격 동작.

- [ ] RPi5에 Waveshare LCD 연결 (점퍼로), `face.py` 표정 9종 렌더 확인
- [ ] systemd `canduck-face.service` 부팅 시 자동 실행
- [ ] ESP32 dev board + PCA9685 점퍼 연결, 서보 1~2개로 PWM 동작 확인
- [ ] UART 프로토콜 `>HEAD`, `>PING`, `<ACK`, `<PONG` 구현
- [ ] `host/canduck/uart_client.py` asyncio 래퍼 + 라인 파서
- [ ] `host/canduck/face.py` Pygame 또는 PIL 렌더 + LCD SPI 드라이버
- [ ] `host/canduck/fsm.py` 기본 상태 머신 (idle/listening/error)
- [ ] `daemon.py` 메인 이벤트 루프, 표정 + UART 통합

**산출물**: dev board에서 표정 변하고 머리 1축이 움직이는 데모.

---

### W4 — 머리 모션 + 인터랙션 1 (dev board) + PCB 입고 (1주)

**목표**: 머리 2축 부드러운 보간, IMU/터치 인터랙션, PCB 도착 후 brought-up 시작.

- [ ] ESP32 측: SG90 ×2 PCA9685로 yaw+pitch 제어, easeInOutCubic 보간
- [ ] `>POSE idle`, `>POSE shake` (좌우 흔들기) 구현
- [ ] MPU6050 폴링 + 탭/흔들기 감지 (가속도 적분 임계값)
- [ ] MPR121 임시 모듈로 정전식 터치 2채널 테스트
- [ ] `<TAP`, `<TOUCH`, `<SHAKE` 이벤트 RPi 보고
- [ ] FSM: tap → headache 시퀀스, touch → sleepy
- [ ] **PCB 도착** (~W4 중반)
  - [ ] Board A 부품 실장 (전원 IC, INA219, 보호회로) — 단계별 brought-up
  - [ ] 1단계: 입력 인가 전에 short 체크 (멀티미터)
  - [ ] 2단계: 가변 PSU로 9V 인가 (전류 제한 100mA), 5V/6V/3V3 출력 확인
  - [ ] 3단계: 부하 점진적 인가 (10K → 1K → 100Ω)
  - [ ] 4단계: INA219 I2C 통신 (Bus Pirate 또는 임시 ESP32로)

**산출물**: 머리 두드림 → 두통 모션 통합 데모, Board A 단독 동작 확인.

**게이트**: Board A에 결함 발견 시 → rev2 즉시 결정 (JLCPCB 재발주 2주 추가).

---

### W5 — Board B 브링업 + dev board 코드 이식 (1주)

**목표**: HAT 보드 실장, RPi5에 장착, ESP32-S3 펌웨어 플래시 통과.

- [ ] Board B 부품 실장 (수동 SMT, 핫에어로 IC)
- [ ] RPi5에 HAT 장착 전 — 다시 short/저항 체크
- [ ] HAT 단독 5V/3V3 공급 → I2C 디바이스 스캔 (RPi5 `i2cdetect`)
- [ ] ESP32-S3 USB-C로 PlatformIO 첫 플래시
- [ ] dev board용 코드를 HAT에 그대로 이식, 동작 확인
- [ ] 서보 ×10 모두 PCA9685 통해 sweep 테스트
- [ ] 모터 드라이버 + N20 휠 회전 확인
- [ ] Board A → Board B 케이블 연결, 통합 전원 테스트

**산출물**: HAT + RPi5 + Board A 통합 동작.

**게이트**: HAT에 결함 발견 시 → 패치 와이어로 우회 가능한지 평가, 아니면 rev2.

---

### W6 — 음성 + PC 연동 (1주)

**목표**: wake-word 응답, macOS 이벤트가 캔덕에 반영됨.

- [ ] INMP441 I2S 마이크 연결, `arecord`로 raw 캡처 확인
- [ ] Picovoice Porcupine 계정 + 무료 wake-word 등록 ("hey canduck" 또는 한글)
- [ ] `host/canduck/voice.py` pvporcupine 통합, wake-word 감지 시 FSM 트리거
- [ ] PAM8403 + 스피커로 응답음 (WAV) 재생, `sounddevice`
- [ ] `mqtt_client.py` paho-mqtt async 통합
- [ ] macOS `canduck-agent` Python 스크립트
  - [ ] xcodebuild/cargo/npm exit code 감지 (shell wrapper 또는 git hook)
  - [ ] git post-merge / post-receive hook
  - [ ] launchd plist
- [ ] 통합 시나리오: 빌드 실패 → 두통포즈, 머리 흔들기 5초

**산출물**: PC에서 빌드 실패 → 캔덕 두통 반응 데모.

---

### W7 — 팔 + 두통포즈 (1주)

**목표**: 팔 4서보 추가, 두통포즈 시퀀스(양손이 머리 옆으로) 동기화.

- [ ] 임시 외형(폼보드/박스) 위에 팔 서보 4개 가조립
- [ ] 어깨 yaw/pitch + 팔꿈치 pitch 각도 캘리브레이션
- [ ] `firmware/src/poses.cpp`에 `headache` 시퀀스 정의
  - [ ] t=0~500ms: 양 팔 어깨까지 들기
  - [ ] t=500~1000ms: 양 손 머리 옆으로
  - [ ] t=1000~5000ms: 머리 격렬 흔들기, 팔은 고정
  - [ ] t=5000~5500ms: 천천히 팔 내림
- [ ] 표정 동기: t=0에 LCD `headache` 전환, t=5500에 `idle`
- [ ] 서보 토크 부족 확인 → 필요 시 MG996R 메탈기어 교체 (예비예산)

**산출물**: 두통포즈 풀 시퀀스 동영상.

---

### W8 — 보행 메커니즘 (1주)

**목표**: 보행 방식 결정 + 기구 가조립.

- [ ] 옵션 평가:
  - A. 캠워커 (4-bar linkage) — 1 모터로 다리 2개 교차 운동
  - B. 휠 +다리 스윙 — 휠은 추진, 다리는 연출
  - C. 옴니휠 4개 (메카넘) — 자유 이동, 다리 외관은 고정
- [ ] 본체 무게 중심 측정, 휠/베이스 배치 결정
- [ ] ToF VL53L0X 하단 부착, 책상 모서리 감지 임계 캘리브레이션
- [ ] `firmware/motor.cpp` PWM duty + 가속 ramp

**산출물**: 평평한 책상 위 직진/회전 동작.

**게이트**: 보행 기구가 1주 안에 안정화 안 되면 → W9를 폴리싱에 사용, 보행은 v2로.

---

### W9 — 보행 알고리즘 + 자율 배회 (1주)

**목표**: FSM `walking` 상태, 30분마다 자율 배회, 모서리 감지 시 정지.

- [ ] FSM `walking` 진입/탈출 조건
- [ ] 경로: 직진 5초 → 정지 → 회전 90° → 직진 (boundary 따라)
- [ ] ToF로 모서리 감지 → 즉시 정지 + 놀란 표정
- [ ] 배터리 < 70% 시 walking 비활성 (전력 절약)
- [ ] 통합 부하 테스트: 1시간 연속 운영, 전류/전압 로깅
- [ ] 발열 체크 (서모 카메라 또는 비접촉 온도계)

**산출물**: 1시간 자율 운영 로그, 자율 배회 영상.

---

### W10 — 외형 통합 + 슬라이싱/출력 (1주)

**목표**: Blender 모델링 완료, STL → 슬라이싱 → 외주 출력 발주.

- [ ] Blender로 본체 외형 완성 (W0부터 병행 학습한 결과물)
  - [ ] 내부 캐비티 — PCB, 배터리, 서보 위치 모두 들어가는지 측정 후 모델
  - [ ] 머리 분리 (서보 마운트 포함)
  - [ ] 팔 분리 (어깨/팔꿈치 관절 마운트)
  - [ ] 다리 분리 (스윙 서보 마운트, 휠 마운트)
  - [ ] 얼굴 LCD 안착 베젤
  - [ ] 정전식 터치 패드 위치 (정수리, 등)
  - [ ] 케이블 통과 홀
- [ ] STL export, Bambu Studio 또는 PrusaSlicer로 슬라이싱
- [ ] 출력 외주 발주 (PLA 권장, 본체는 0.2mm 레이어)
- [ ] 출력 대기 (~1주)

**산출물**: 슬라이싱 g-code 또는 외주 발주 영수증.

---

### W11 — 조립 + 케이블링 (1주)

**목표**: 출력물 도착, 전자부품 통합 조립, 케이블 정리.

- [ ] 인쇄물 후처리 (서포트 제거, 사포)
- [ ] 도색 (선택, 자가 도색 or PLA 컬러 그대로)
- [ ] 서보 마운트 확인, 출력물 끼움새 조정 (드릴/줄로 미세 조정)
- [ ] PCB + 배터리 본체 내부 안착, 양면테이프 + 케이블 타이로 고정
- [ ] 모든 서보 케이블 → PCA9685 커넥터 매핑 (라벨링)
- [ ] LCD 안착, 백라이트 빛샘 차단 (검정 펠트 또는 EVA폼)
- [ ] 마이크 위치 (입 근처 또는 정수리), 스피커 위치 (배 또는 등)
- [ ] 정전식 터치 패드 부착 (구리테이프 + MPR121 케이블)
- [ ] 마지막 통합 점검 후 시동

**산출물**: 외형까지 완성된 캔덕.

---

### W12 — 마감 + 시연 + v2 백로그 (1주)

**목표**: 안정성 검증, 시연 영상 (비공개), v2 백로그 정리.

- [ ] 24시간 연속 운영 burn-in (충전 연결한 채로)
- [ ] FSM 시나리오 전부 트리거 테스트
  - [ ] wake-word → listening
  - [ ] tap → headache
  - [ ] 빌드 실패 → headache
  - [ ] git merge → happy
  - [ ] 정수리 쓰다듬 → sleepy
  - [ ] 600초 idle → sleep
  - [ ] 자율 배회 → 모서리 회피
- [ ] systemd 자동 복구 검증 (process kill → 재시작)
- [ ] 로그 로테이션 (`/var/log/canduck/`, logrotate)
- [ ] 시연 영상 촬영 (비공개 보관)
- [ ] **v2 백로그 정리**:
  - [ ] 카메라 + 얼굴 추적
  - [ ] 로컬 LLM 응답
  - [ ] BME280 환경센서
  - [ ] M.2 HAT + AI 가속기
  - [ ] PCB rev2 (USB-PD 패스스루 + soft-start 정식)
  - [ ] 액세서리 자석 인식

**산출물**: 작동하는 캔덕, v2.md.

---

## 리스크 매트릭스

| 리스크 | 확률 | 영향 | 완화 |
|---|---|---|---|
| PCB rev1 결함 → 재발주 | 중 | +2주 | W2 전 24시간 텀 검토, 패치 와이어 우회 시도 |
| 서보 토크 부족 | 중 | +비용 5만원 | W7에 메탈기어로 교체, 예비예산 |
| Blender 학습 지연 | 고 | +1~2주 | W10 시점에 미완이면 외주 모델링 발주(추가 10~20만원) |
| 보행 기구 1주 안에 미해결 | 중 | 보행 v2 | W8 게이트에서 즉시 결정, 폴리싱에 시간 재배분 |
| 배터리 운영 시간 부족 | 중 | UX 저하 | 데스크탑 상시 충전 운영, 배터리는 백업 |
| ESP32 펌웨어 OTA 실패 | 저 | USB-C로 폴백 | HAT에 USB-C 항상 노출 |
| RPi5 발열 throttle | 저 | 응답 지연 | 액티브 쿨러 필수, ambient 30°C 이하 유지 |
| 자가 SMT 실수 (IC 손상) | 중 | 부품 재구매 | 같은 IC 2~3개씩 발주, 핫에어 리워크 연습 |

## 롤백 경로

- **W2 발주 후 PCB 결함 발견** → JLCPCB는 발주 24시간 내 hold 요청 가능. 그 이후엔 rev2 발주.
- **W5 brought-up 실패** → dev board 구성으로 W6~W8 진행, PCB는 W9~W10에 rev2로 도전.
- **W8 보행 미해결** → 보행 v2로 미루고 W9~W10을 폴리싱/외형 통합 가속에 사용. 12주 데드라인 유지.
- **W10 Blender 미완** → 외주 모델링 즉시 발주 (Fiverr "stylized 3D character chibi" 카테고리, 10~20만원, 보통 1주). 일정 13~14주로 연장.

## 일일 체크리스트 템플릿

각 주말에 본인이 5분 자가 점검:

```
[ ] 이번 주 산출물 완성도 (0~100%)
[ ] 예산 누계 (vs. 견적)
[ ] 다음 주 의존성 (부품 도착, 외주 대기 등)
[ ] 발견된 새 리스크
[ ] 사기 (1~5)
```
