# Skill — Host Deploy Loop (Python 패키징 → systemd → RPi5 배포 → journalctl)

> 대상: `host/canduck/` (RPi5 위 Python 데몬, UART로 ESP32-S3와, MQTT로 macOS 에이전트와 통신).
> 현재 구현 상태는 `host/README.md` 참고 (골격 완성, LCD 드라이버·표정 자산·INA219 calibration은 W3/W4 예정).

## 0. 사전 조건

- RPi5 SSH 셋업 완료 (heebin, W3 진입 전) — Bookworm 64-bit, hostname `canduck`
- 인터페이스 활성화: SPI/I2C/I2S/UART on (`raspi-config` 또는 `/boot/firmware/config.txt`)
- `mosquitto`, `i2c-tools` 설치 확인

## 1. 코드 수정 (Claude, 로컬/macOS)

```sh
cd host
python -m venv .venv
.venv/bin/pip install -e .[dev]

.venv/bin/ruff check canduck/
.venv/bin/ruff format canduck/
.venv/bin/pytest              # HW mock 필요, W5 이후 의미 있어짐
```

- 모듈 구조: `daemon.py`(진입점) / `config.py`(pydantic-settings) / `fsm.py` / `face.py` / `uart_client.py` / `mqtt_client.py` / `voice.py` / `telemetry.py`
- 수정 후 로컬에서 import 가능 여부 최소 확인 (`python -c "import canduck"` 등, 실 HW 없이)

## 2. RPi5로 배포

```sh
# 최초 1회 (heebin)
sudo mkdir -p /opt/canduck && sudo chown $USER:$USER /opt/canduck
cp -r host/ /opt/canduck/
cd /opt/canduck
python3 -m venv .venv
.venv/bin/pip install -e .[voice]

sudo mkdir -p /etc/canduck
sudo cp systemd/canduck.env.example /etc/canduck/canduck.env
sudo nano /etc/canduck/canduck.env      # 환경변수 채우기

sudo usermod -a -G dialout,gpio,spi,i2c $USER

sudo cp systemd/canduck.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now canduck
```

```sh
# 이후 코드 갱신 시 (반복 루프)
rsync -av --exclude='.venv' host/ pi@canduck.local:/opt/canduck/host/
ssh pi@canduck.local "cd /opt/canduck && .venv/bin/pip install -e .[voice] && sudo systemctl restart canduck"
```

- 담당 분리: 코드 변경(Claude) → rsync/ssh 실행 및 systemd 재기동은 heebin이 RPi 접속해서 수행 (CLAUDE.md § 4 — "RPi 배포, journalctl 전달"은 heebin 몫)

## 3. 로그 확인 (journalctl)

```sh
journalctl -u canduck -f              # 실시간
journalctl -u canduck --since "10 min ago"
journalctl -u canduck -p err          # 에러만
```

- heebin이 로그를 캡처해서 전달 (`journalctl -u canduck --since ... > /tmp/canduck-host.log`)
- Claude는 전달받은 로그에서:
  - [ ] 부팅 시퀀스 정상 (모든 모듈 import/초기화 성공)
  - [ ] UART 연결 성공 (`uart_client.py` ↔ ESP32 `PING`/`PONG` 왕복)
  - [ ] MQTT 연결 상태 (`mosquitto` 로컬 리스너 확인)
  - [ ] FSM 상태 전이 로그 (예상 이벤트 → 예상 상태 변경)
  - [ ] 크래시/재시작 여부 (systemd auto-restart 트리거 원인)

## 4. 트러블슈팅 체크리스트 (host/README.md 기준)

| 증상 | 확인 사항 |
|---|---|
| UART 안 잡힘 | `/boot/firmware/config.txt`에 `enable_uart=1`, 콘솔 비활성 (`raspi-config` → Serial → No console / Yes hardware) |
| SPI permission denied | `usermod -a -G spi $USER` + 재로그인, 또는 udev 룰 |
| MQTT 연결 실패 | `systemctl status mosquitto`, listener `localhost` 한정 확인 |
| systemd venv 못 찾음 | `ExecStart` 경로 `/opt/canduck/.venv/bin/canduck-daemon` 정확한지 |

## 5. W3~W5 구현 대기 항목 (완료되는 대로 이 루프에 편입)

- [ ] LCD GC9A01 SPI 드라이버 (`lcd_gc9a01.py`) — W3
- [ ] 표정 PNG 자산 (`assets/face/*.png`) — W3
- [ ] 깜빡임/idle sway 애니메이션 — W3
- [ ] INA219 calibration + 실측 대조 — W4
- [ ] 음성 응답음 WAV 자산 — W6
- [ ] macOS `canduck-agent` (별도 디렉토리/레포) — W6

## 6. 회귀 체크리스트 (매 배포 후)

- [ ] `systemctl status canduck` → active (running)
- [ ] 부팅 후 30초 내 UART PING/PONG 성공
- [ ] FSM idle 상태 정상 진입
- [ ] 텔레메트리(전압) 로그 주기적으로 찍힘
- [ ] 강제 kill 후 systemd 자동 재기동 확인 (`sudo systemctl kill canduck` → 재시작 로그 확인)

## 7. 산출물

- 배포/트러블슈팅 결과 → `docs/reports/W{n}-T{m}-{slug}.md`
- 반복되는 이슈는 이 문서에 트러블슈팅 표로 누적
