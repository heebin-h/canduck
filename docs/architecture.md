# 시스템 아키텍처

## 전체 구조

```
┌──────────────────────────────────────────────────────────────────┐
│  macOS (heebiny)                                                 │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  canduck-agent (launchd 서비스)                          │    │
│  │  ├─ build watcher (xcode/swift/cargo/npm hooks)         │    │
│  │  ├─ git hook listener (PR merge, build fail)            │    │
│  │  ├─ slack mention listener (선택)                        │    │
│  │  └─ macOS notification listener                         │    │
│  │                                                          │    │
│  │  ──── MQTT publish ────────────────────────────────────  │    │
│  └─────────────────────────────────────────────────────────┘    │
└────────────────────┬─────────────────────────────────────────────┘
                     │ Wi-Fi
                     │ MQTT (mosquitto broker, RPi에서 호스팅)
                     │ topic: canduck/event/*
                     ▼
┌──────────────────────────────────────────────────────────────────┐
│  RPi 5 8GB (canduck.local)                                       │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  canduck-daemon (systemd 서비스, Python)                  │    │
│  │  ├─ mqtt_client.py    — MQTT 구독, 이벤트 → FSM         │    │
│  │  ├─ fsm.py            — 행동 상태 머신                   │    │
│  │  ├─ uart_client.py    — ESP32-S3 통신 (모션 명령)        │    │
│  │  ├─ face.py           — LCD 표정 렌더 (Pygame 또는 PIL)  │    │
│  │  ├─ voice.py          — Porcupine wake-word, 응답 음원   │    │
│  │  ├─ telemetry.py      — INA219 폴링, 배터리 모니터       │    │
│  │  └─ daemon.py         — 메인 이벤트 루프                 │    │
│  │                                                          │    │
│  │  ──── UART (115200) ──────────────────────────────────  │    │
│  └─────────────────────────────────────────────────────────┘    │
└────────────────────┬─────────────────────────────────────────────┘
                     │ UART /dev/ttyAMA0
                     ▼
┌──────────────────────────────────────────────────────────────────┐
│  ESP32-S3 (HAT 온보드, Board B)                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  firmware (PlatformIO, Arduino framework 또는 ESP-IDF)   │    │
│  │  ├─ comm.cpp          — UART 프로토콜 파서               │    │
│  │  ├─ servo_ctrl.cpp    — PCA9685 래퍼, easing 보간        │    │
│  │  ├─ motor.cpp         — TB6612FNG, 휠 PWM 제어           │    │
│  │  ├─ imu.cpp           — MPU6050 폴링, 탭/흔들기 감지     │    │
│  │  ├─ touch.cpp         — MPR121 폴링 (HAT의 I2C 통해)     │    │
│  │  ├─ poses.cpp         — 사전 정의 포즈 시퀀스             │    │
│  │  └─ main.cpp          — 메인 루프 (10ms 틱)              │    │
│  │                                                          │    │
│  │  ──── I2C / PWM ──────────────────────────────────────  │    │
│  └─────────────────────────────────────────────────────────┘    │
│        │                                                          │
│        ├─► PCA9685 ─► Servo ×10 (머리/팔/다리)                   │
│        ├─► TB6612FNG ─► N20 모터 ×2 (휠)                         │
│        ├─► MPU6050 (I2C, 인터럽트는 RPi로 보고)                  │
│        └─► VBAT_SENSE ADC                                        │
└──────────────────────────────────────────────────────────────────┘
```

## 책임 분리

| 컴포넌트 | 책임 |
|---|---|
| macOS 에이전트 | 외부 이벤트 → MQTT publish. 캔덕 상태 모름. |
| RPi 데몬 | 이벤트 해석, FSM 운영, 렌더링, 음성, 텔레메트리. |
| ESP32-S3 | 실시간 액추에이터 제어, 센서 폴링. **시퀀스 자체는 모름** — 단순 명령 실행. |

> 핵심 원칙: **ESP32는 dumb actuator**, **RPi는 brain**. ESP32에 행동 로직 넣지 말 것. 펌웨어 업데이트 빈도 최소화.

## UART 프로토콜 (RPi ↔ ESP32-S3)

### 물리 계층

- 115200 8N1
- RPi `/dev/ttyAMA0` ↔ ESP32 UART0 (GPIO43/44)
- 양방향 ASCII 라인 기반 (디버깅 친화)
- 줄바꿈 `\n` 종결

### 프레임 포맷

```
<DIRECTION><CMD> <ARG1> <ARG2> ... \n
```

- `>` 접두: RPi → ESP32 (명령)
- `<` 접두: ESP32 → RPi (응답/이벤트)

### 명령 (RPi → ESP32)

| 명령 | 인자 | 의미 |
|---|---|---|
| `>HEAD` | `yaw pitch duration_ms` | 머리 자세, 부드러운 보간 |
| `>ARM` | `side(L/R) shoulder elbow duration_ms` | 팔 자세 |
| `>LEG` | `side(L/R) angle duration_ms` | 다리 스윙 |
| `>MOTOR` | `left right` (-255~255) | 휠 PWM, 부호=방향 |
| `>POSE` | `name` | 사전 정의 포즈 (`idle`, `headache`, `wave`, `sleep`) |
| `>STOP` | (없음) | 모든 액추에이터 즉시 중립 |
| `>ENABLE` | `0/1` | PCA9685 OE# (서보 토크 on/off) |
| `>PING` | (없음) | keepalive |
| `>QUERY` | `imu/touch/vbat` | 1회 폴링 응답 요청 |

### 응답/이벤트 (ESP32 → RPi)

| 이벤트 | 인자 | 의미 |
|---|---|---|
| `<ACK` | `<원명령>` | 명령 수신 완료 |
| `<DONE` | `<원명령>` | 모션 완료 |
| `<ERR` | `code msg` | 에러 (잘못된 인자, 서보 응답 없음 등) |
| `<TAP` | `axis intensity` | IMU 탭 감지 |
| `<SHAKE` | `intensity` | IMU 흔들기 감지 |
| `<TOUCH` | `channel state` | MPR121 채널 변화 |
| `<VBAT` | `mV` | 배터리 전압 |
| `<PONG` | (없음) | PING 응답 |
| `<BOOT` | `version` | ESP32 부팅 (firmware 버전 보고) |

### 예시 세션

```
< BOOT v0.1.0
> PING
< PONG
> ENABLE 1
< ACK ENABLE 1
> POSE idle
< ACK POSE idle
< DONE POSE idle
< TAP z 1450
> POSE headache
< ACK POSE headache
< DONE POSE headache
> QUERY vbat
< VBAT 7320
```

### 에러 코드

| 코드 | 의미 |
|---|---|
| 1 | 명령 파싱 실패 |
| 2 | 인자 범위 초과 |
| 3 | I2C 통신 실패 (PCA9685 응답 없음) |
| 4 | 모션 중 새 명령 거부 (현재 진행 중) |
| 5 | 미정의 포즈 이름 |

## MQTT 토픽 (macOS ↔ RPi)

브로커: RPi에서 mosquitto 호스팅, 포트 1883 (LAN 한정)

| 토픽 | 페이로드 (JSON) | 발행자 | 의미 |
|---|---|---|---|
| `canduck/event/build` | `{"status": "fail|pass", "project": "x"}` | macOS | 빌드 결과 |
| `canduck/event/git` | `{"action": "merge|push", "repo": "x", "branch": "main"}` | macOS | git 이벤트 |
| `canduck/event/notification` | `{"app": "Slack", "title": "...", "body": "..."}` | macOS | 시스템 알림 |
| `canduck/event/idle` | `{"idle_sec": 300}` | macOS | 사용자 idle 보고 |
| `canduck/cmd/pose` | `{"pose": "headache"}` | (수동 테스트) | RPi가 즉시 실행 |
| `canduck/state` | `{"fsm": "idle", "vbat_mv": 7400, ...}` | RPi | 1Hz 텔레메트리 |
| `canduck/telemetry/power` | `{"rail_5v_ma": 1200, "rail_6v_ma": 400}` | RPi | 전력 텔레메트리 |

## FSM (RPi daemon/fsm.py)

### 상태

| 상태 | 진입 조건 | 동작 |
|---|---|---|
| `idle` | 기본 | 표정 idle + 가벼운 머리 sway. 5초마다 깜빡임. |
| `listening` | wake-word 감지 | 머리 들기, 표정 attentive, 5초 후 idle 복귀 |
| `headache` | TAP 강도↑ 또는 build_fail 이벤트 | 두통 표정 + 머리 양옆 격렬 흔들기 5초 |
| `happy` | git merge 성공, 칭찬 음성 | 점프 모션(다리 스윙) + happy 표정 |
| `sleepy` | idle 600초+ | sleepy 표정 → sleep (LCD off + 서보 비활성) |
| `sleep` | sleepy 60초 후 | LCD off, ENABLE 0, MQTT만 listening |
| `surprised` | TAP 약함, 알림 등 | 1초 surprised → idle |
| `walking` | 사용자 트리거 또는 30분마다 자동 배회 | 휠 + 다리 스윙, ToF로 모서리 감지 |
| `error` | 통신 실패 5초 지속, 배터리 critical | error 표정, 모션 중단, MQTT alert |

### 전이 다이어그램

```
                ┌──────────────────────────┐
                ▼                          │
    ┌──► idle ◄─────────┐              error
    │     │ │            │                ▲
    │     │ │ wake       │ end-of-pose    │
    │     │ │ word       │                │ comm fail
    │     │ ▼            │                │
    │   listening ──┐    │                │
    │               │    │                │
    │     │ tap     │    │                │
    │     │ build_  │    │                │
    │     │ fail    │    │                │
    │     ▼         │    │                │
    │  headache ────┤    │                │
    │               │    │                │
    │     git merge │    │                │
    │     ▼         │    │                │
    │   happy ──────┤    │                │
    │               ▼    │                │
    │            (cooldown)               │
    │               │                     │
    │ idle 600s     │                     │
    │ ▼             │                     │
    sleepy → sleep ─┘                     │
       ▲              wake event          │
       └──────────────────────────────────┘
```

### 우선순위 규칙

- `error` > 모든 상태
- `headache` > `happy` > 일반 알림 (같은 이벤트 동시 발생 시 더 강한 감정 우선)
- `sleep` 중에는 wake-word만 깨움. PC 알림은 무시.
- 모션이 진행 중이면 새 이벤트는 큐에 쌓이고, `<DONE` 받으면 다음 처리.

## 표정 (LCD)

`face.py`가 240×240 둥근 LCD에 렌더. **모든 표정은 LCD 화면 안에서만 표현 — 외형 본체 디자인과 독립**.

| 표정 ID | 화면 구성 |
|---|---|
| `idle` | 기본 눈/입, 가끔 깜빡임 애니메이션 |
| `blink` | 눈 깜빡임 키프레임 (3프레임) |
| `happy` | ^_^ 곡선 눈, 입꼬리 위 |
| `sleepy` | 눈 반쯤 감음 |
| `sleep` | -_- 일자 눈, 코고는 입 (간헐적 zZ) |
| `headache` | 눈 X자 또는 비뚤어진 눈, 입 d자 |
| `surprised` | 눈 동그랗게 커짐 (스케일 키프레임) |
| `attentive` | 눈 살짝 위로, 동공 살짝 확장 |
| `error` | !? 표정, 작은 텍스트 표시 |

렌더는 Pygame 또는 직접 LCD 드라이버 + PIL로 비트맵 합성. 60fps 목표는 아니고 **30fps + 키프레임** 충분.

## 데이터 흐름 예시: "빌드 실패 → 두통"

1. macOS xcodebuild → exit code != 0
2. `canduck-agent` (launchd) build watcher가 감지 → MQTT publish:
   ```
   topic: canduck/event/build
   payload: {"status": "fail", "project": "canduck-host"}
   ```
3. RPi `mqtt_client.py` 수신 → 큐에 enqueue
4. `daemon.py` 메인 루프가 큐 pop → `fsm.handle_event(build_fail)`
5. FSM 전이: 현재 idle → headache
6. `face.set_expression("headache")` (LCD 즉시 표정 변경)
7. `uart_client.send("POSE headache")`
8. ESP32 ACK → 두통 시퀀스 실행 (머리 격렬 흔들기 5초)
9. ESP32 DONE 보고 → FSM 전이: headache → idle (cooldown 10초)
10. cooldown 후 idle 표정 복귀

전체 latency 목표: macOS 이벤트 → 캔덕 반응 < 500ms

## 디렉토리 → 모듈 매핑

| 디렉토리 | 모듈 |
|---|---|
| `host/canduck/daemon.py` | 메인 진입점, asyncio 이벤트 루프 |
| `host/canduck/mqtt_client.py` | paho-mqtt async client |
| `host/canduck/uart_client.py` | pyserial-asyncio 래퍼 |
| `host/canduck/fsm.py` | transitions 라이브러리 또는 직접 구현 |
| `host/canduck/face.py` | LCD 드라이버 + 표정 렌더 |
| `host/canduck/voice.py` | sounddevice + pvporcupine wake-word |
| `host/canduck/telemetry.py` | smbus2로 INA219 폴링 |
| `host/canduck/config.py` | pydantic-settings 환경 변수 로딩 |
| `host/systemd/canduck.service` | systemd unit 파일 |
| `firmware/src/main.cpp` | setup() / loop(), 10ms 틱 |
| `firmware/src/comm.cpp` | UART 라인 파서 + 디스패처 |
| `firmware/src/servo_ctrl.cpp` | PCA9685 + 보간(easing) 엔진 |
| `firmware/src/poses.cpp` | 포즈 시퀀스 테이블 |

## 확장 포인트 (향후)

| 확장 | 인터페이스 | 비고 |
|---|---|---|
| 카메라 (얼굴 인식) | RPi5 CSI | OpenCV + mediapipe. 새 FSM 상태 `tracking` 추가. |
| LLM 응답 | RPi5 로컬 (Phi/Gemma 3B 양자화) 또는 클라우드 API | 새 모듈 `host/canduck/llm.py` |
| 환경센서 | I2C 확장 헤더 J_B20 (BME280) | `host/canduck/env.py`, MQTT topic `canduck/env/*` |
| AI 가속기 | M.2 HAT + Hailo-8L | mediapipe 가속 또는 audio classifier |
| 액세서리 인식 (모자/안경) | 정전식 추가 채널 또는 NFC | `host/canduck/accessory.py` |
| 음성 합성 응답 | 로컬 TTS (Piper) 또는 ElevenLabs | `voice.py` 확장 |
| 멀티 캔덕 페어링 | MQTT broker로 자연스럽게 | 토픽 `canduck/<id>/*` 네임스페이스 |
