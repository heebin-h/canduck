# canduck host daemon

RPi 4 위에서 동작하는 Python 데몬. UART로 ESP32-S3와, MQTT로 macOS 에이전트와 통신.
표정은 tkinter 창으로 표시 (LCD 탈락, 2026-07-12 — `docs/reports/W0-T02e-order-final.md`).

## 설치 (RPi 4)

```sh
# 시스템 의존성
sudo apt update
sudo apt install -y python3-venv python3-pip python3-tk mosquitto i2c-tools

# 인터페이스 활성화 (raspi-config 또는 /boot/firmware/config.txt)
#   - I2C on (INA219 텔레메트리)
#   - UART on (/dev/ttyAMA0, console 비활성)
# (SPI/I2S 불필요 — LCD·I2S 마이크 탈락, 오디오/영상은 USB 3-in-1 카메라)

# 코드 배치
sudo mkdir -p /opt/canduck
sudo chown $USER:$USER /opt/canduck
cp -r host/ /opt/canduck/

# venv + 의존성
cd /opt/canduck
python3 -m venv .venv
.venv/bin/pip install -e .[voice]

# 환경변수
sudo mkdir -p /etc/canduck
sudo cp systemd/canduck.env.example /etc/canduck/canduck.env
sudo nano /etc/canduck/canduck.env

# 사용자 그룹
sudo usermod -a -G dialout,gpio,spi,i2c $USER

# systemd 등록
sudo cp systemd/canduck.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now canduck
journalctl -u canduck -f
```

## 디렉토리

```
host/
├── pyproject.toml
├── canduck/
│   ├── daemon.py          # 메인 진입점 (canduck-daemon)
│   ├── config.py          # pydantic-settings
│   ├── fsm.py             # 행동 FSM
│   ├── face.py            # 표정 도메인 (Expression + PIL 렌더)
│   ├── display_tk.py      # tkinter 표시 백엔드 (전용 스레드 + Queue)
│   ├── gpio.py            # RPi GPIO (ESP32 리셋/부트, 사용자 버튼) — 비 RPi는 mock
│   ├── uart_smoke.py      # UART 프로토콜 스모크 테스트 (canduck-smoke)
│   ├── uart_client.py     # ESP32 통신
│   ├── mqtt_client.py     # macOS 이벤트 수신
│   ├── voice.py           # Porcupine wake-word
│   └── telemetry.py       # INA219 + VBAT 모니터
└── systemd/
    ├── canduck.service
    └── canduck.env.example
```

## 현재 구현 상태 (W3 시작 시점)

- [x] 골격 작성, 모든 모듈 import 가능 (실 HW 없이 dev 환경에서)
- [x] 표정 표시 tkinter 백엔드 (`display_tk.py`) + GPIO 모듈 (`gpio.py`)
- [x] UART 스모크 테스트 CLI (`canduck-smoke --check`)
- [ ] 표정 PNG 자산 (`assets/face/*.png`) — W3
- [ ] INA219 calibration + 실측 — W4
- [ ] 깜빡임/idle sway 애니메이션 — W3
- [ ] 음성 응답음 WAV 자산 — W6
- [ ] macOS 측 canduck-agent (별도 레포 또는 디렉토리) — W6

## 개발 환경 (macOS 또는 RPi)

> 노트북에서 `canduck-daemon` 완주는 **DevKit을 USB로 연결해야** 가능 (UART 연결 실패 시 기동 중단).
> UART 없이는 `canduck-smoke`(DevKit 직결 테스트)나 개별 모듈 단위로 확인.

```sh
cd host
python -m venv .venv
.venv/bin/pip install -e .[dev]

# 코드 정리
.venv/bin/ruff check canduck/
.venv/bin/ruff format canduck/

# 테스트 (HW mock 필요, W5 이후)
.venv/bin/pytest
```

## 트러블슈팅

- **UART 안 잡힘**: `/boot/firmware/config.txt`에 `enable_uart=1`, 콘솔 비활성 (`raspi-config` → Interface → Serial → No console / Yes hardware).
- **tkinter 창 안 뜸**: `sudo apt install python3-tk`. SSH 세션이면 DISPLAY 없음 — 데몬은 표시 없이 정상 동작.
- **MQTT 연결 실패**: `sudo systemctl status mosquitto`. listener는 `localhost` 한정 권장 (LAN 노출 시 ACL 설정).
- **systemd가 venv 못 찾음**: ExecStart 경로 `/opt/canduck/.venv/bin/canduck-daemon` 정확한지 확인.
