## 리뷰 포인트

- **호스트 FSM**: 이 PR 전에는 structlog `event=` 충돌로 전이가 전부 실패했음 → 수정 (`fsm.py`)
- **⚠️ 배포**: DONE 포맷이 `< DONE POSE <name>`로 바뀜 → 펌웨어·호스트 **같이 배포**해야 함
- **동작 변경**: UART EOF·장치 분리 → exit 1(systemd 재기동) / ERROR 시 서보 OFF / surprised·listening 타이머, headache·happy 15초 타임아웃으로 idle 복귀 / 잘못된 숫자 입력은 이제 ERR / 표정 창 기본 OFF
- **⚠️ 운용 UART(ttyAMA0)**: ESP32 무응답은 아직 감지 못 함 — PING 감시 W3
- **미검증**: DevKit 실기·`canduck-smoke --check`·RPi4 배포
