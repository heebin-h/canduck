# Skill — Measurement Protocol (전력/서보 실측 자동화 + 데이터 포맷)

> 대상: 전원 계통 검증(`hardware/power-budget.md` 예측치 vs 실측), 서보/모터 특성화.
> 측정 장비는 heebin이 랩 도구로 확보 (`hardware/parts.md` § 랩 도구 — 멀티미터/오실로스코프/로직애널라이저/벤치 PSU).
> Claude는 측정 절차 설계·데이터 분석·오차 리포트를 담당, 실측 행위 자체는 heebin.

## 1. 전원 레일 검증 (power-budget.md 예측치 대조)

### 1.1. 정적 전압 (무부하/부하 시)

| 레일 | 예측치 | 측정 지점 | 허용 오차 |
|---|---|---|---|
| +5V_MAIN | 5.0~5.1V | TP_A3 | ±3% |
| +6V_SERVO | 6.0V | TP_A4 | ±3% |
| +3V3_LOGIC | 3.3V | TP_A5 | ±3% |
| VBAT | 7.4~8.4V (2S 리포 범위) | TP_A1 | 배터리 SOC 따라 변동 |

- 측정: 멀티미터 DC 전압, 무부하 → idle 부하 → 활동 부하 순으로 3단계 기록

### 1.2. 전류 (INA219 vs 벤치 PSU 실측 대조)

- INA219 #1 (5V 레일, addr 0x40), #2 (6V 레일, addr 0x41) — I2C로 읽은 값과 벤치 PSU 표시 전류 대조 (calibration 오차 확인)
- power-budget.md 부하 리스트 기준 시나리오별 측정:
  - Idle: RPi5 유휴, 서보 중립
  - Active: 대화 응답 + 표정 전환
  - Peak: 전체 포즈 시퀀스(headache) 실행 중 순간 전류

### 1.3. 캡 뱅크 검증 (6V 레일)

- 오실로스코프로 서보 시동 순간 6V 레일 전압 dip 관찰 (캡 뱅크 470μF×4 = 1880μF 적정성 확인)
- dip이 정상 동작 임계 이하로 떨어지면 → 캡 용량 증설 또는 buck 모듈 응답속도 재검토

## 2. 배터리 런타임 실측

- power-budget.md 예측: 휴면 3시간+, 활동 1.5~2시간, 보행+풀모션 1시간
- 실측 방법: 완충 상태에서 시나리오별 연속 운영 → 배터리 전압이 컷오프(2S 리포 기준 셀당 3.3V, 합 6.6V) 도달까지 시간 기록
- 데이터: 5분 간격 VBAT 전압 로그 (`telemetry.py` 출력 또는 수동 멀티미터) → 방전 곡선

## 3. 서보/모터 특성화

| 항목 | 측정 방법 |
|---|---|
| 서보 stall 전류 (SG90/MG90S) | 벤치 PSU 6V 고정, 서보 물리적으로 정지시킨 상태에서 전류 측정 |
| 서보 응답 지연 | 로직 애널라이저로 PWM 신호 vs 실제 회전 시작 타이밍 |
| 휠 모터(N20) free/stall 전류 | 무부하 회전 vs 축 고정 상태 전류 비교 |
| 토크 부족 확인 (W7 게이트) | 팔 시퀀스(headache) 중 서보가 목표 각도 도달 실패 시 → SG90/MG90S → MG996R 교체 판단 |

## 4. 데이터 포맷 (heebin → Claude 전달 표준)

측정 결과는 아래 CSV 포맷으로 전달 권장 (분석 자동화 용이):

```csv
timestamp,rail,scenario,voltage_v,current_ma,note
2026-0X-XX 14:32:01,5V_MAIN,idle,5.05,720,
2026-0X-XX 14:32:31,6V_SERVO,headache_peak,5.82,3100,dip observed
```

- 오실로스코프/로직 애널라이저 캡처는 스크린샷(PNG) + 캡처 시점 조건 메모로 전달
- 파일 저장 위치 제안: `docs/measurements/{date}-{topic}.csv` + `docs/measurements/{date}-{topic}.png`

## 5. 분석 → 리포트 루프

1. heebin이 실측 데이터 전달 (CSV + 스크린샷)
2. Claude가 예측치(power-budget.md) 대비 편차 계산, 원인 가설 제시
3. 편차가 허용 오차 초과 시 → 설계 수정 제안 (buck 모듈 교체, 캡 증설, shunt 저항 값 재계산 등)
4. 결과를 `docs/reports/W{n}-T{m}-{slug}.md`에 정리, 필요 시 `hardware/power-budget.md` 수치 갱신

## 6. 체크리스트 요약

- [ ] 무부하 정적 전압 3레일 확인
- [ ] INA219 실측값 vs 벤치 PSU 대조 (calibration 오차 %)
- [ ] 6V 레일 캡 뱅크 dip 오실로스코프 캡처
- [ ] 배터리 방전 곡선 (최소 1개 시나리오)
- [ ] 서보 stall 전류 실측 (최소 대표 1개 모델)
- [ ] 측정 데이터 CSV 포맷으로 보존
