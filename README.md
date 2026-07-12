# canduck

개인 데스크탑 펫 프로젝트. 하이브리드 폼팩터(물리 본체 + LCD 얼굴), 음성/터치/PC 상태 연동.

> **사용 범위**: 개인 소장용. 외형 자산(STL/렌더)은 외부 공유·SNS 업로드·판매 안 함.

## 현재 단계

- [x] 인터뷰 / 스코프 확정 (최대 스코프 — 머리 모션 / 두통포즈 / 팔 / 보행)
- [x] HW 플랫폼: RPi 5 8GB + 자체 설계 PCB 2장 (Board A 전원, Board B HAT)
- [ ] **W0** — 부품 발주, KiCad 셋업, 외형 모델링 학습 시작
- [ ] W1~W2 — schematic + PCB layout + JLCPCB 발주
- [ ] W3~W12 — 펌웨어/호스트/통합

상세 일정: [`docs/roadmap.md`](docs/roadmap.md)

## 디렉토리 구조

```
canduck/
├── README.md                  # 본 파일
├── hardware/
│   ├── parts.md               # 확정 BOM + 랩 도구 리스트
│   ├── power-budget.md        # 레일별 전원 계산서
│   └── schematic-spec.md      # PCB 설계 사양서 (KiCad 작업 가이드)
├── firmware/                  # ESP32-S3 펌웨어 (PlatformIO)
│   ├── platformio.ini
│   ├── include/
│   └── src/
├── host/                      # RPi5 호스트 데몬 (Python)
│   ├── canduck/
│   ├── systemd/
│   └── pyproject.toml
├── docs/
│   ├── architecture.md        # 시스템 아키텍처 + 프로토콜 명세
│   └── roadmap.md             # 12주 작업 계획
└── assets/                    # 외형 모델·표정 스프라이트 (gitignore)
```

## 핵심 결정 (확정)

| 항목 | 결정 |
|---|---|
| 메인 보드 | RPi 5 8GB + 액티브 쿨러 |
| 모터 컨트롤러 | ESP32-S3 (HAT 온보드, UART로 RPi와 연결) |
| PCB | 2장 분할 (Power / HAT), 4-layer, JLCPCB |
| 회로 설계 도구 | KiCad |
| 얼굴 디스플레이 | Waveshare 1.28" Round LCD (240×240, SPI) |
| 배터리 | 2S 리포 7.4V 5000mAh + BMS |
| 보행 방식 | 캠워커 또는 휠+다리 스윙 (W7에 결정) |
| 외형 모델링 | 본인이 Blender로 직접 (stylized chibi character workflow 학습) |

## 빠른 링크

- [BOM + 랩 도구](hardware/parts.md)
- [전원 계산서](hardware/power-budget.md)
- [PCB schematic 사양서](hardware/schematic-spec.md)
- [시스템 아키텍처](docs/architecture.md)
- [12주 로드맵](docs/roadmap.md)
