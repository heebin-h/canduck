# Canduck — Project Local Rules

이 파일은 `/Users/heebiny/canduck` 작업 시 Claude Code가 cwd 진입 시 자동 로드.
글로벌 `~/.claude/CLAUDE.md` 와 함께 적용되며, 충돌 시 이 파일이 우선.

---

## 1. 대화 로깅 (MANDATORY)

**규칙**: 매 응답을 종료하기 직전에 반드시 `docs/logs/session-{오늘날짜}.md` 끝에 이번 turn을 append.

### 1.1. 파일 경로
- 경로: `/Users/heebiny/canduck/docs/logs/session-YYYY-MM-DD.md`
- 오늘 날짜는 conversation context의 `# currentDate` 값을 사용 (예: `2026-05-25`)
- 파일이 없으면 헤더 `# Session Log — YYYY-MM-DD\n\n` 으로 새로 생성 (Write)
- 파일이 있으면 끝부분에 append (Edit, `old_string` 으로 마지막 마커 또는 마지막 줄을 잡고 그 뒤로 추가)

### 1.2. 한 turn 포맷

```
---

## [HH:MM] heebin → Claude

{사용자 메시지: 짧으면 전문, 길면 1~3줄 요약}

## [HH:MM] Claude → heebin

{내 응답 핵심 1~5줄 요약}

- **Tools used**: Write, Edit, Bash, TaskCreate (예시)
- **Files changed**: `docs/skills/kicad-workflow.md` (new), `hardware/parts.md` (mod)
- **Decisions/Next**: 다음 단계 또는 결정 사항
```

### 1.3. 작성 원칙
- HH:MM 은 현실 시각이 아니라 turn 순서를 표현. 모르면 `[turn-N]` 으로 대체 가능
- 사용자 프롬프트가 1줄 이하면 전문, 그 외엔 요약
- 코드·명령어 전문은 적지 말 것 — 어떤 파일에 무엇을 했는지만
- API 키·비밀번호·SSH 키 등 민감 정보는 절대 로그 X
- 응답 흐름이 길어 사용자가 부담되지 않게 — append는 silent하게 (응답 본문에 "[로그 append 완료]" 같은 메타 알림 금지)

### 1.4. 예외
- 사용자가 명시적으로 "로그 생략" 요청한 turn 은 skip
- API 에러로 응답이 중간에 끊긴 경우 — 다음 turn 시작 시 backfill
- 짧은 ack ("ㅇㅋ" / "기다려" 등) 은 한 줄로 간략히 (skip 금지)

---

## 2. 작업 보고서

각 task 또는 의미 있는 작업 단위 완료 시:
- 경로: `docs/reports/W{week}-T{task}-{slug}.md`
- 포맷: `docs/reports/W0-T00-bootstrap.md` 참고
- 섹션: What happened / Decisions / Files / Next actions / Context notes

---

## 3. IP 경계 (캐릭터 디자인)

자세한 합의는 `docs/reports/W0-T00-bootstrap.md` § 2.1, § 2.2 참조. 요약:

- **Claude 안 함**: 공식 캐릭터 디지털 에셋 다운로드/분석, 공식 이미지에서 비례·형태 추출.
- **Claude 함**: heebin이 직접 만든 `.step`/`.stl` 받아서 파라메트릭화·내부 공간·서보/PCB 마운트·3D 프린팅 분할·슬라이서 호환 검증.

→ 캐릭터 외형 디자인 결정은 전부 heebin 영역.

---

## 4. 작업 분담

| 영역 | Claude | heebin |
|---|---|---|
| 회로/PCB (KiCad sch/pcb, DRC, Gerber) | ✅ | 발주, 땜질, 실측 |
| 펌웨어 (C/C++, ISR, UART, PWM, FSM) | ✅ | 플래시, 시리얼 로그 캡처 |
| 호스트 (Python, systemd, MQTT, FSM) | ✅ | RPi 배포, journalctl 전달 |
| 3D 모델링 — 엔지니어링 | ✅ | — |
| 3D 모델링 — 캐릭터 외형 | ❌ | ✅ |
| 부품 선정 (데이터시트, BOM 검증) | ✅ | 발주, 입고 확인 |
| 테스트 (자동화, 측정 프로토콜) | ✅ | 실측, 사진/오실로 결과 전달 |

---

## 5. Sequential Tool Execution

`~/.claude/CLAUDE.md` 의 **Sequential Tool Execution Protocol** 그대로 적용. 한 응답에 하나의 `tool_use` 만, `tool_result` 수신 후 다음 호출. 병렬 호출 금지.

---

## 6. Phase Roadmap (요약)

상세 계획은 `docs/roadmap.md`, `docs/reports/W0-T00-bootstrap.md`.

- **Phase 0** (Infra): git init, 6종 스킬 문서, parts.md 검토, 로깅 시스템 ← 현재 위치
- **Phase 1** (Sourcing): parts.md 최종, heebin 결제·발주
- **Phase 2** (Mech): heebin 1차 3D 모델 → Claude 엔지니어링
- **Phase 3+** (W1~W12): PCB → 펌웨어 → 호스트 → 통합 → 폴리시

---

## 7. 세션 진입 시 권장 동선

새 세션 시작 시 Claude는 다음 순서로 컨텍스트 복구:

1. `docs/reports/` 의 가장 최근 보고서 1~2개 Read
2. `docs/logs/session-{최근날짜}.md` 마지막 N개 turn Read
3. `TaskList` 로 미완료 task 확인
4. (필요 시) `git log --oneline -10` 으로 최근 commit 확인

이 4단계만 거치면 즉시 작업 재개 가능.

---

## 8. PR 워크플로우 — Git Flow lite (2026-05-29 합의)

브랜치 전략 = **`main` + `develop` + feature**. `release/*` · `hotfix/*` 는 W9 (RPi systemd 배포 시작) 시점에 도입 검토.

### 8.1. 브랜치 정의
| 브랜치 | 의미 | 직접 commit | PR target | 도입 시점 |
|---|---|---|---|---|
| `main` | 배포 안정본 (release tag `v0.x.y`) | ❌ | release/hotfix only | W9+ 부터 의미 |
| `develop` | 개발 통합 trunk (default branch) | ❌ | ✅ feature PR 기본 target | 지금부터 |
| `w{n}/t{m}-{slug}` | feature (작업 브랜치) | ✅ Claude | (자기 자신) | task 단위 |
| `release/*` | 배포 준비 (선택) | ❌ | develop + main | W9+ 검토 |
| `hotfix/*` | 운영 버그 긴급 (필수) | ❌ | main + develop | W9+ (첫 배포 직후) |

- 작업 브랜치 명명: `w{week}/t{task}-{kebab-slug}` (예: `w0/t00-initial-scaffolding`, `w1/t03-pcb-schematic`)
- 작업 브랜치는 항상 **develop에서 분기 → develop으로 머지**.
- main은 W0~W8 동안 `Initial commit` 또는 첫 release tag 직전 상태로 frozen.

### 8.2. 역할 분담
| 단계 | Claude | heebin |
|---|---|---|
| develop 기준 작업 브랜치 생성 | ✅ | — |
| 코드/문서 변경 + commit (msg `W{n}-T{m}: <slug>`) | ✅ | — |
| `git push -u origin <branch>` | — | ✅ |
| GitHub 웹에서 PR open (target = **`develop`**) + 본문 paste | — | ✅ |
| PR 본문 작성 + `pbcopy` 로 클립보드 복사 | ✅ | — |
| review (선택) + Merge 클릭 | — | ✅ |
| merge 후 `git checkout develop && git pull` | ✅ | — |
| 다음 task 진입 | ✅ | — |

### 8.3. PR 본문 포맷
```markdown
## What
<1~3줄 요약>

## Files
- 그룹별 / 디렉토리별 묶어서

## Notes
- 결정사항 / 트레이드오프 / 충돌 해결 내역
```

### 8.4. 충돌 해결 원칙
- rebase 시 작업 브랜치 commit 쪽 우선 (`git checkout --theirs ...`)
- GitHub 자동 생성 파일 (README/.gitignore placeholder)은 로컬본 채택

### 8.5. main 보호
- main 직접 commit 금지
- main은 W9+ release/hotfix PR로만 갱신
- force-push 금지

### 8.6. 초기 셋업 (heebin 1회)
1. credential helper: `git config --global credential.helper osxkeychain`
2. develop 브랜치 push: `git push -u origin develop`
3. **GitHub repo Settings → Branches → Default branch → `develop` 으로 변경** (이후 PR 기본 target = develop)
4. (선택) main branch protection rule — direct push 금지, PR-only

### 8.7. W9 시점에 검토할 것 (메모)
- `release/*` 도입 여부 (배포 빈도가 잦으면 도입)
- `hotfix/*` 도입 (운영 버그 응답 — 거의 필수)
- semver tag 정책 (`v0.1.0` 부터, MAJOR.MINOR.PATCH)
- main branch protection 강화 (review approval 필수 등)
