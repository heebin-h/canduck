# Skill — Firmware Test Loop (PlatformIO build → flash → serial log → 분석)

> 대상: `firmware/` (ESP32-S3-WROOM-1, PlatformIO + Arduino framework).
> 현재 구현 상태는 `firmware/README.md` 참고 (UART 프로토콜, PCA9685 서보 제어, 포즈 5종, 배터리 ADC 구현됨. IMU/터치/휠모터는 W4/W8 예정).

## 0. 사전 조건

- PlatformIO CLI 설치 (heebin, W3 진입 전) — `pip install platformio` 또는 VSCode 확장
- USB-C로 ESP32-S3 (dev board 또는 HAT 실장본) 연결 (heebin, 물리 접속 담당)

## 1. 빌드

```sh
cd firmware
pio run                    # 전체 빌드
pio run -v                 # verbose (에러 진단 시)
pio run -t clean           # 클린 빌드 필요 시
```

- 빌드 에러 시 `firmware/platformio.ini` 보드 정의/라이브러리 버전 먼저 확인
- Claude가 코드 수정 후에는 항상 `pio run`으로 컴파일 통과 확인까지가 "완료"

## 2. 플래시

```sh
pio run -t upload          # USB-C 연결 상태에서
```

- heebin이 물리적으로 USB-C 연결 및 보드 전원 상태 확인 (담당 분리: 코드는 Claude, 플래시 실행은 heebin — CLAUDE.md § 4)
- 플래시 실패 시: 보드 BOOT 버튼(SW_B1)/RESET(SW_B2) 조합, 포트 권한(`dialout` 그룹) 확인

## 3. 시리얼 모니터 (검증)

```sh
pio device monitor          # 기본 115200 baud
```

### 기본 스모크 테스트 시퀀스 (firmware/README.md 기준)

```
< BOOT 0.1.0           # 부팅 시 자동 출력 — 버전 확인
> PING
< PONG                 # 통신 확인
> ENABLE 1
< ACK ENABLE           # 서보 출력 활성화 확인
> POSE idle
< ACK POSE
< DONE idle            # 모든 서보 중립 완료
> POSE headache
< ACK POSE
< DONE headache        # ~5.5초 후 (poses.cpp 키프레임 타이밍 검증)
> POSE invalid
< ERR 5 invalid        # 에러 핸들링 확인
```

- 각 포즈(`idle`, `headache`, `shake`, `happy`, `sleep`) 전환마다 `ACK` → `DONE` 순서, 타이밍이 `firmware/src/poses.cpp` 키프레임 테이블과 일치하는지 확인
- 배터리 ADC 로그 (1Hz) — 전압값이 실측 멀티미터와 ±0.1V 이내인지 (드리프트 있으면 `pins.h` ADC 보정 계수 재확인)

## 4. 로그 캡처 → 분석 루프

- `pio device monitor` 출력을 파일로 저장해 heebin이 전달: `pio device monitor | tee /tmp/canduck-serial-$(date +%Y%m%d-%H%M).log`
- Claude는 전달받은 로그에서:
  - [ ] 예상 시퀀스(ACK/DONE 순서) 이탈 여부
  - [ ] 타이밍 오차 (키프레임 대비 실측 ms)
  - [ ] 에러 코드 발생 빈도/조건
  - [ ] 예외적 리셋/크래시 로그 (watchdog reset 등)
- 이슈 발견 시 `firmware/src/*.cpp` 수정 → 다시 1번(빌드)부터 루프

## 5. W4 이후 추가 테스트 항목 (구현되는 대로 추가)

- **MPU6050 (W4)**: 탭/흔들기 감지 임계값 튜닝 — 로그로 가속도 raw 값 출력 후 임계치 조정, `<TAP`/`<SHAKE` 이벤트 오탐/미탐 체크
- **MPR121 (W4)**: 터치 채널별 반응성, `<TOUCH` 이벤트 디바운스 확인
- **TB6612FNG 휠 모터 (W8)**: PWM duty별 실제 회전 속도, 정지/역전 응답 지연
- **UART OTA (v2, 아직 미착수)**: 해당 없음

## 6. 회귀 체크리스트 (매 기능 추가 후)

- [ ] `pio run` 빌드 통과
- [ ] `PING`/`PONG` 기본 통신 확인
- [ ] 기존 포즈 5종 전부 재검증 (새 기능이 서보 제어 타이밍에 간섭 없는지)
- [ ] 배터리 ADC 로그 정상 출력
- [ ] 에러 케이스(`invalid` 포즈 등) 여전히 `ERR` 응답

## 7. 산출물

- 시리얼 로그 파일 (`/tmp/canduck-serial-*.log`, 분석 후 필요 시 `docs/logs/` 로 보존 여부 결정)
- 발견된 이슈 → `docs/reports/W{n}-T{m}-{slug}.md` 에 기록 (CLAUDE.md § 2 포맷)
