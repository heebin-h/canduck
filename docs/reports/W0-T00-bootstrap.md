# W0-T00 — Bootstrap & Workflow Agreement

- **Date**: 2026-05-23
- **Owner**: Claude (planning) + heebin (decisions, execution-side)
- **Status**: in_progress
- **Phase**: Phase 0 (Infra setup)

---

## 1. What happened this session

세션 초반 API 400 (`no low surrogate in string`) 에러로 답변이 중간에 끊겼고 cwd가 일시적으로 사라지는 불안정 상황 발생. 재진입 후 W0 스캐폴딩 29파일 무결성 확인하고 워크플로우 합의 진행.

핵심 합의: 캔덕 프로젝트의 제작·개발 영역을 Claude에게 최대한 위임하되, IP 경계와 작업 책임 분담을 명확히 함.

## 2. Decisions made

### 2.1. 작업 분담 원칙

| 영역 | Claude | heebin |
|---|---|---|
| 회로/PCB (KiCad sch/pcb, DRC, Gerber) | ✅ | 발주, 땜질, 실측 |
| 펌웨어 (C/C++, ISR, UART, PWM, FSM) | ✅ | 플래시, 시리얼 로그 캡처 |
| 호스트 (Python, systemd, MQTT) | ✅ | RPi 배포, journalctl 전달 |
| 3D 모델링 — 엔지니어링 (내부 공간, 마운트, 분할, 파라메트릭) | ✅ | — |
| 3D 모델링 — 캐릭터 외형 디자인 (비례 추출, 형태 결정) | ❌ | ✅ heebin 책임 영역 |
| 부품 선정 (데이터시트 분석, 대안 비교, BOM 검증) | ✅ | 발주, 입고 확인 |
| 테스트 (자동화 스크립트, 측정 프로토콜) | ✅ | 실측·전달 |

### 2.2. 캐릭터 디자인 — IP 경계

heebin이 의도하는 외형은 노란 오리 캐릭터의 외양을 따라가는 데스크탑 펫 (개인 비공개 제작). 이 맥락에서:

- **Claude가 안 함**: 공식 디지털 에셋(3D 모델 파일·일러스트) 다운로드/분석, 공식 캐릭터 이미지에서 비례·형태를 추출하는 작업.
- **Claude가 함**: heebin이 직접 만든 1차 3D 모델(.step/.stl)을 받아서 엔지니어링 처리 (파라메트릭화, 내부 공간 확보, 서보·PCB 마운트 추가, 3D 프린팅용 분할, 슬라이서 호환 검증).

→ 캐릭터 디자인 결정은 전부 heebin 영역. Claude는 함수 본체(엔지니어링)만 책임.

### 2.3. Phase 2 측정 방식

heebin이 피규어 보유하지 않음. 두 옵션 중 택1:
- **A**: Fusion 360에 공식 이미지 정면/측면을 reference image로 깔고 스케치 → 모델링
- **B**: 종이 손 스케치 (정면도/측면도 2장) → 그 위에서 비례 정함 → Fusion/Blender로 옮김

작업 산출물: `assets/3d/canduck_v0.step` + `assets/3d/measurements.md` (heebin이 정한 비례 메모)

### 2.4. API 끊김 대비 — 작업 보고서 시스템

- 각 task 단위로 `docs/reports/W{n}-T{m}-{slug}.md` 생성
- 포맷: What happened / Decisions / Files / Next actions / Context notes
- git commit msg에 task ID 포함 (예: `W0-T00: bootstrap workflow agreement`)
- 추가: `docs/logs/session-YYYY-MM-DD.md` 에 모든 user/assistant 대화 자동 append (hook 기반, 다음 task에서 셋업)

### 2.5. Tool Sandbox

이 프로젝트는 1인 메이커 워크플로우이므로 외부 협업 MCP (Asana/Linear/Notion/Slack/Figma/Atlassian/Gmail/Drive 등)는 **불필요**. 전부 로컬 도구 (KiCad CLI, PlatformIO, CadQuery, Python, KiCad 9, OpenSCAD) 로 처리. 향후 RPi5 SSH 접속만 추가 셋업 예정.

## 3. Files created/modified this task

- `docs/reports/W0-T00-bootstrap.md` (this file)

(이외 변경 없음 — git init은 heebin이 직접 실행 대기 중)

## 4. Pending heebin actions

1. **git init** — 다음 한 줄 명령 실행:
   ```bash
   cd /Users/heebiny/canduck && git init -b main && <gitignore 생성> && git add -A && git status
   ```
   → `git status` 출력을 Claude에게 전달
2. **CAD 도구 결정** — Fusion 360 / Blender / FreeCAD 중 택1 (Phase 2 진입 전)
3. **KiCad 9 + PlatformIO CLI 로컬 설치** (Phase 1~3 진입 전)

## 5. Next actions (Claude)

1. **Hook 시스템 셋업** — `.claude/settings.json` + 로그 스크립트로 모든 user/assistant 메시지를 `docs/logs/session-*.md` 에 자동 append (새 세션·이 디렉토리 한정)
2. **W0-T01: 6종 스킬 문서 작성**
   - `docs/skills/kicad-workflow.md`
   - `docs/skills/cadquery-modeling.md`
   - `docs/skills/firmware-test-loop.md`
   - `docs/skills/host-deploy-loop.md`
   - `docs/skills/measurement-protocol.md`
   - `docs/skills/bom-sourcing.md`
3. **W0-T02: parts.md 재검토 보고서** — 빠진 부품·대체품·가격 비교
4. **W1 진입 컨펌 후**: PCB 작업 본격 시작

## 6. Context notes (다음 세션 진입 시 읽을 것)

- 세션 시작 시 `docs/reports/` 의 가장 최근 보고서 + 이번 세션 `docs/logs/session-YYYY-MM-DD.md` 읽으면 컨텍스트 즉시 복구 가능.
- API 400 (low surrogate) 에러는 한국어 답변 중 일부 surrogate pair 직렬화 충돌로 추정. 매우 긴 한 번의 답변보다 짧은 단위로 끊어가며 진행하는 것이 안전.
- Sequential Tool Execution Protocol 적용 중 (`~/.claude/CLAUDE.md` 참조) — 한 응답에 하나의 tool_use만, tool_result 받고 다음 진행.
- heebin은 임베디드/IoT/Linux 풀스택. C/Python/Shell 주력. 실시간·라이브 시스템 안정성 우선.
