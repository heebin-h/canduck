# canduck firmware

ESP32-S3 펌웨어. PlatformIO + Arduino framework.

## 빌드 / 플래시

```sh
# PlatformIO CLI 사용
pio run                      # 빌드
pio run -t upload            # 플래시 (USB-C 연결)
pio device monitor           # 시리얼 모니터 (115200)
```

또는 VSCode에서 PlatformIO 확장 사용.

## 디렉토리

```
firmware/
├── platformio.ini
├── include/
│   ├── pins.h          # GPIO/PCA9685 채널 매핑
│   ├── comm.h          # UART 프로토콜
│   ├── servo_ctrl.h    # 서보 제어 + easing
│   └── poses.h         # 포즈 시퀀스
└── src/
    ├── main.cpp        # setup/loop, 10ms 틱
    ├── comm.cpp        # UART 파서/이벤트
    ├── servo_ctrl.cpp  # PCA9685 래퍼
    └── poses.cpp       # 포즈 키프레임 테이블
```

## 현재 구현 상태 (W3 시작 시점)

- [x] UART 프로토콜 골격 (HEAD, POSE, STOP, ENABLE, PING)
- [x] PCA9685 서보 제어 + easeInOutCubic 보간
- [x] 포즈 시퀀스 5종 (idle, headache, shake, happy, sleep)
- [x] 배터리 ADC 모니터링 (1Hz)
- [ ] MPU6050 IMU 폴링 + 탭/흔들기 감지 (W4)
- [ ] MPR121 정전식 터치 (W4)
- [ ] TB6612FNG 휠 모터 PWM (W8)
- [ ] UART OTA 업데이트 (v2)

## 테스트 시나리오 (시리얼 모니터)

```
< BOOT 0.1.0           # ESP32 부팅 시 자동
> PING                 # ↩
< PONG                 # ↩
> ENABLE 1             # 서보 출력 활성
< ACK ENABLE
> POSE idle
< ACK POSE
< DONE idle            # 모든 서보 중립 완료 후
> POSE headache
< ACK POSE
< DONE headache        # ~5.5초 후
> POSE invalid
< ERR 5 invalid
```
