## 리뷰 포인트 (2026-11-10)

### 요약
처음에는 `poses.cpp` include 1줄 수정으로 시작한 PR입니다. 전체 코드 리뷰 결과를 반영하면서 펌웨어·호스트 동작 변경까지 범위가 넓어졌습니다. 아래는 동작이 바뀌는 지점만 추렸습니다. 결함 상세는 본문 "원인 / 결함 설명"에 있습니다.

### ⚠️ 이 PR 이전 호스트 FSM은 사실상 동작하지 않았음
`host/canduck/fsm.py`의 `log.info(..., event=...)`가 structlog 첫 위치 인자 `event`와 충돌했습니다. 그래서 **모든 전이가 `TypeError`로 실패**했고, uart handler가 예외를 삼켜 로그에만 남았습니다. 즉 PR #5의 "호스트 FSM 구현 완료"는 실제로는 검증된 적이 없습니다. 이번에 kwarg를 `trigger`로 바꾸고, 가짜 UART 시나리오로 전이를 처음 확인했습니다(11/11 PASS).

### 동작이 바뀌는 지점 (리뷰 시 확인)
| 위치 | 변경 | 영향 |
|---|---|---|
| `firmware/src/poses.cpp` + `host/canduck/daemon.py` | DONE 포맷: `< DONE <name>` → `< DONE POSE <name>`. 호스트는 현재 상태의 포즈와 일치하는 DONE만 처리 | **펌웨어와 호스트를 같이 배포해야 함.** 구 펌웨어와 신 호스트를 섞으면 DONE이 전부 무시되어 headache/happy 등에 고착 |
| `host/canduck/uart_client.py`, `daemon.py` | UART EOF 시 COMM_FAIL → stop → **exit 1** | 재연결은 systemd `Restart=on-failure`(3s)에 맡김. 수동 실행 시에는 그냥 종료 |
| `host/canduck/daemon.py` | ERROR 진입 시 `STOP` + `ENABLE 0`, ERROR 중 ESP32 `BOOT`에는 `ENABLE 1`을 보내지 않음 | ERROR는 회복 경로가 없어 데몬 재기동 전까지 서보 비활성 (기존 설계 유지) |
| `host/canduck/fsm.py`, `config.py` | surprised 1초 / listening 5초 후 idle 복귀 | `CANDUCK_SURPRISED_SEC`, `CANDUCK_LISTENING_SEC`로 조정 |
| `firmware/src/comm.cpp` | `atoi` → `strtol` 엄격 파싱, ARM/LEG 범위 검사 | 이전에 0이나 clamp 값으로 통과하던 입력(예: `HEAD 10abc`, `HEAD 65566`, 범위 밖 ARM/LEG)이 이제 `ERR` |
| `firmware/src/servo_ctrl.cpp` | 새 명령은 현재 보간 위치에서 출발, STOP 시 채널 상태 리셋 | STOP은 기존대로 즉시 중립(0°) 스냅 |

### 검증 범위
- ✅ 펌웨어 `pio run` SUCCESS (`~/.platformio/penv/bin/pio`, RAM 6.1% · Flash 9.5%)
- ✅ 호스트: 가짜 UART 시나리오 11/11 PASS, `py_compile` OK
- ❌ **미실행**: DevKit 실기 업로드, `canduck-smoke --dev /dev/ttyUSB0 --check`, RPi4 배포. 특히 DONE 포맷 변경은 실기 왕복으로 확인해야 함

### 머지 후 첫 실기 확인 순서
1. `pio run -t upload` → `canduck-smoke --dev /dev/ttyUSB0 --check`
2. 시리얼 모니터에서 `POSE idle` → `< DONE POSE idle` 확인
3. DevKit 단독으로 **데몬**을 돌리면 VBAT 분압 미연결 ADC 플로팅 값 때문에 바로 ERROR로 갈 수 있음 (보고서 §7). 이 경우 데몬 결함이 아님
