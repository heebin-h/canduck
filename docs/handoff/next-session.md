# 다음 세션 핸드오프 — git 초기화 & 푸시

> 작성: 2026-05-25 (현재 세션 마무리 시점)
> 트리거: heebin이 새 세션 시작 시 § 5 "복붙용 프롬프트" 를 그대로 채팅에 붙여넣음.

---

## 1. 현재 상태 스냅샷

### 1.1. 존재하는 파일
- `/Users/heebiny/canduck/` 루트: `README.md`
- `hardware/`: `parts.md`, `schematic-spec.md`, `power-budget.md`
- `firmware/`: `platformio.ini`, `README.md`, `include/*.h` (4개), `src/*.cpp` (4개)
- `host/`: `pyproject.toml`, `README.md`, `canduck/*.py` (8개), `systemd/*` (2개)
- `docs/`: `architecture.md`, `roadmap.md`
- `docs/reports/`: `W0-T00-bootstrap.md` (워크플로우 합의 영구화)
- `docs/logs/`: `session-2026-05-23.md`, `session-2026-05-25.md`
- `docs/handoff/`: `next-session.md` (이 파일)
- `CLAUDE.md` (프로젝트 로컬 룰)
- `.claude/hooks/log-conversation.py`, `.claude/settings.json` (hook 시스템 — 작동 안 함 확인됨, CLAUDE.md 룰로 대체)
- `assets/` (빈 디렉토리)

### 1.2. 미설정 상태
- ❌ git 저장소 (이전 세션에서 init 명령 줬으나 heebin 실행 안 함)
- ❌ GitHub remote
- ❌ 첫 commit

### 1.3. Task 상태
- #1 git 초기화 — pending (이 핸드오프 후 실행)
- #2 W0-T00 bootstrap + 로깅 — completed
- #3 hook 검증 — deleted (CLAUDE.md 룰로 대체)

---

## 2. 다음 세션 첫 액션 — heebin이 직접 실행

### 2.1. git 초기화 + 첫 commit

복사해서 터미널에 그대로 붙여넣기:

```bash
cd /Users/heebiny/canduck && \
git init -b main && \
cat > .gitignore <<'EOF'
# OS
.DS_Store

# Python
__pycache__/
*.pyc
.venv/
venv/
*.egg-info/
build/
dist/

# PlatformIO
.pio/
.vscode/

# KiCad backups
*-bak/
*.bak
fp-info-cache

# CAD locks
*.FCBak
*.f3d.lock

# Secrets
.env
.env.local
*.env
!*.env.example

# Build artifacts
assets/3d/build/
hardware/gerber/

# (선택) 대화 로그 민감 시 주석 해제
# docs/logs/
EOF
git add -A && \
git status
```

→ `git status` 출력 확인. staged 파일 약 30~35개 보여야 정상.

이상 없으면:

```bash
git commit -m "W0: initial scaffolding (firmware + host + docs + logging)"
git log --oneline
```

→ commit 1개 생성됨 확인.

### 2.2. GitHub private repo 생성 + push

먼저 `gh` CLI 준비 확인:

```bash
gh auth status
# 미인증이면: gh auth login (브라우저 인증 흐름)
```

그 다음 repo 생성 + 푸시 한 줄:

```bash
gh repo create canduck --private --source=. --remote=origin --push
```

→ 출력 끝에 `https://github.com/{user}/canduck` URL 보이면 성공.

### 2.3. 검증

```bash
git log --oneline -5
git remote -v
git branch -vv
git status
```

→ 다음이 모두 보여야 OK:
- 커밋 hash 1개
- `origin  https://github.com/{user}/canduck.git (fetch/push)`
- `main` 이 `origin/main` 추적 중
- working tree clean

---

## 3. 트러블슈팅

### 3.1. git commit이 거부됨 — user.name/email 미설정
```bash
git config --global user.name "Heebin"
git config --global user.email "heebin.h@alicorn.team"
git commit -m "W0: initial scaffolding (firmware + host + docs + logging)"
```
(Claude는 글로벌 git config를 자동 변경하지 않음 — heebin이 직접)

### 3.2. `gh` 명령 없음
```bash
brew install gh
gh auth login
```

### 3.3. `gh repo create` 가 "name already exists" 거부
- GitHub 에 같은 이름 repo 이미 있음. 옵션:
  ```bash
  # 다른 이름으로
  gh repo create canduck-rpi --private --source=. --remote=origin --push
  # 또는 기존 repo 지우고 (주의)
  gh repo delete {user}/canduck --yes
  ```

### 3.4. push 거부 — remote 충돌
```bash
git remote remove origin
gh repo create canduck --private --source=. --remote=origin --push
```

### 3.5. 일부만 진행됨 (예: init은 했는데 commit 안 함)
- 새 세션에서 Claude에게 그 상태 그대로 알려주면 됨. 프롬프트 § 5 의 마지막 줄 부분에 "어디까지 했음" 명시.

---

## 4. heebin 작업 끝난 뒤 Claude가 할 작업

heebin이 § 2 완료 + § 2.3 검증 출력을 새 세션에서 공유하면, Claude는:

1. 출력 확인 → Task #1 completed 마킹
2. **W0-T01 등록 + 진입**: 6종 스킬 문서 작성 (`docs/skills/`)
   - kicad-workflow.md
   - cadquery-modeling.md
   - firmware-test-loop.md
   - host-deploy-loop.md
   - measurement-protocol.md
   - bom-sourcing.md
3. **W0-T02 등록**: `hardware/parts.md` 재검토 보고서 (`docs/reports/W0-T02-parts-review.md`)
4. 매 task 종료 시 commit (commit msg: `W0-T0N: <slug>`)
5. 매 응답 끝 `docs/logs/session-{새날짜}.md` 에 turn 블록 append (CLAUDE.md 룰)

---

## 5. 복붙용 프롬프트 (다음 세션에서 그대로 붙여넣기)

```
캔덕 프로젝트 재진입. 다음 순서로 컨텍스트 복구해줘:

1. /Users/heebiny/canduck/CLAUDE.md (프로젝트 룰)
2. /Users/heebiny/canduck/docs/handoff/next-session.md (이번 핸드오프 — 가장 중요)
3. /Users/heebiny/canduck/docs/reports/W0-T00-bootstrap.md (워크플로우 합의)
4. /Users/heebiny/canduck/docs/logs/session-2026-05-25.md 마지막 50줄
5. TaskList 확인

읽기 끝나면:
(A) 현재 상태 2~3줄 요약
(B) 내가 git/gh 어디까지 했는지 보고 (아래 ★ 참고)
(C) 다음 진행 액션 제안

★ 내가 한 일:
- git init + commit: [완료 / 미완료 / 일부]
- gh repo create + push: [완료 / 미완료 / 일부]
- (필요 시) git log --oneline -5 / git remote -v 출력 첨부:

[여기에 출력 붙여넣기]
```

---

## 6. Context 노트

- **Sequential Tool Execution Protocol** 적용 (`~/.claude/CLAUDE.md` 참조) — 한 응답에 하나의 `tool_use` 만
- **CLAUDE.md 로깅 룰** — 매 응답 끝에 `docs/logs/session-{date}.md` 에 turn 블록 append
- **IP 경계** — Claude는 캐릭터 외형 디자인 결정 X. heebin이 1차 3D 모델링 후 `.step` 전달 시 엔지니어링만 수행
- **API 끊김 대비** — 모든 결정·작업은 `docs/reports/` + `docs/logs/` 에 영구화. 세션 시작 시 § 5 프롬프트만 붙여넣으면 완전 복구
- **hook 시스템** — `.claude/hooks/log-conversation.py` + `.claude/settings.json` 존재하지만 동일 세션 내 settings 변경 미적용으로 검증 실패. 새 세션에서 작동하면 보너스, 아니어도 CLAUDE.md 룰이 메인
