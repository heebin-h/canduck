# canduck host daemon

RPi 5 위에서 동작하는 Python 데몬. UART로 ESP32-S3와, MQTT로 macOS 에이전트와 통신.

## 설치 (RPi 5)

```sh
# 시스템 의존성
sudo apt update
sudo apt install -y python3-venv python3-pip mosquitto i2c-tools

# 인터페이스 활성화 (raspi-config 또는 /boot/firmware/config.txt)
#   - SPI on
#   - I2C on
#   - I2S on (마이크용 dtoverlay)
#   - UART on (/dev/ttyAMA0, console 비활성)

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
│   ├── face.py            # LCD 렌더
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
- [ ] LCD GC9A01 SPI 드라이버 (`lcd_gc9a01.py`) — W3
- [ ] 표정 PNG 자산 (`assets/face/*.png`) — W3
- [ ] INA219 calibration + 실측 — W4
- [ ] 깜빡임/idle sway 애니메이션 — W3
- [ ] 음성 응답음 WAV 자산 — W6
- [ ] macOS 측 canduck-agent (별도 레포 또는 디렉토리) — W6

## 개발 환경 (macOS 또는 RPi)

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
- **SPI permission denied**: `usermod -a -G spi $USER` + 재로그인. 또는 `/etc/udev/rules.d/` 룰 추가.
- **MQTT 연결 실패**: `sudo systemctl status mosquitto`. listener는 `localhost` 한정 권장 (LAN 노출 시 ACL 설정).
- **systemd가 venv 못 찾음**: ExecStart 경로 `/opt/canduck/.venv/bin/canduck-daemon` 정확한지 확인.
