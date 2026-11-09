## 리뷰 포인트

- **호스트 FSM**: 이 PR 전에는 structlog `event=` 충돌로 전이가 전부 실패했음 → 수정 (`fsm.py`)
- **⚠️ 배포**: DONE 포맷이 `< DONE POSE <name>`로 바뀜 → 펌웨어·호스트 **같이 배포**해야 함
- **동작 변경**: UART EOF → exit 1(systemd 재기동) / ERROR 시 서보 OFF / surprised·listening 타이머 복귀 / 잘못된 숫자 입력은 이제 ERR
- **미검증**: DevKit 실기·`canduck-smoke --check`·RPi4 배포
