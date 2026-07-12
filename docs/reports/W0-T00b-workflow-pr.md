# W0-T00b — PR Workflow Agreement (Git Flow lite)

- **Date**: 2026-05-29
- **Owner**: Claude (구현) + heebin (결정)
- **Status**: completed
- **Phase**: Phase 0 (Infra setup) — W0-T00 보완

---

## 1. What happened this task

W0-T00 (bootstrap) 직후, GitHub repo 생성 + push 단계에서 인증 막힘 (gh 미설치, credential helper 없음, SSH 키 미등록). heebin이 "나는 push + merge 만 하고 나머지 다 Claude" 라고 워크플로우 명확화 요청. 추가로 브랜치 전략 (main/develop 분리, hotfix 도입 시점)도 함께 합의.

## 2. Decisions made

### 2.1. 브랜치 전략 — Git Flow lite

`main` + `develop` + `feature` 셋. `release/*` · `hotfix/*` 는 **W9 (RPi systemd 배포 시작) 시점에 도입 검토**.

| 브랜치 | W0~W8 (개발 단계) | W9+ (운영 단계) |
|---|---|---|
| `main` | frozen (`Initial commit`) | release tag 시 갱신 |
| `develop` | 개발 통합 trunk, default branch, PR target | 동일 |
| `w{n}/t{m}-{slug}` | feature, develop에서 분기 → develop으로 머지 | 동일 |
| `release/*` | 없음 | 검토 (선택) |
| `hotfix/*` | 없음 | 도입 (필수) |

선택 이유:
- 1인 메이커지만 임베디드/IoT 라이브 운영 시스템이라 **main = 배포 안정본** 의미를 처음부터 보호.
- develop을 통합 trunk로 두면 feature PR 흐름이 자연스럽고, main은 W9+ release/hotfix 시점부터만 갱신 → 운영 안정성 확보.
- Git Flow full (release/* + hotfix/* 모두)은 1인에 과도 → W9 시점에 도입 검토로 미룸.

### 2.2. 워크플로우 (요약)

매 task = develop에서 새 작업 브랜치 → commit (Claude) → push (heebin) → PR open (target = develop, Claude가 본문 작성, heebin이 웹에서 paste) → merge (heebin) → develop pull (Claude) → 다음 task 진입.

상세는 [`/CLAUDE.md`](../../CLAUDE.md) § 8 참조.

### 2.3. PR 도구 — gh CLI 안 씀

gh CLI 셋업 vs GitHub 웹 paste 사이에서 heebin이 **웹 paste** 선택. Claude는 PR 본문을 마크다운으로 작성해 `pbcopy` 로 클립보드 복사. heebin은 GitHub 웹 → "Compare & pull request" → 본문 paste → Create → Merge.

### 2.4. 첫 commit (W0 scaffolding) 도 PR로

force-push 방식(이전 합의)에서 PR 방식으로 전환. 일관성을 위해 첫 commit부터 PR 흐름. main은 GitHub 자동 `Initial commit` (79b4ed3) 그대로 유지, 작업 브랜치 `w0/t00-initial-scaffolding` 에서 develop으로 PR.

### 2.5. 충돌 해결 — 우리 것 채택

GitHub 자동 생성 `README.md` (2줄 placeholder) + `.gitignore` (Python 템플릿)는 로컬본이 명확히 우월 (heebin이 직접 작성한 README + 프로젝트 맞춤 .gitignore — PlatformIO/KiCad/CAD/secrets 커버). rebase 시 `git checkout --theirs` 로 작업 commit 쪽 채택. 이후 모든 task에 동일 원칙.

### 2.6. 인증 — credential helper

`git config --global credential.helper osxkeychain` 1회 설정 후 첫 push 때 GitHub PAT 입력 → keychain 영구 저장.

## 3. Files created/modified this task

- `CLAUDE.md` § 8 추가 (PR 워크플로우 + 브랜치 전략)
- `docs/reports/W0-T00b-workflow-pr.md` (this file)
- `docs/logs/session-2026-05-28.md`, `session-2026-05-29.md` (로깅 룰 따라 turn append)

## 4. Branch / Commit state (PR 직전)

```
* w0/t00-initial-scaffolding  d1ab1aa  W0-T00b: PR workflow agreement
                              ce33772  W0: initial scaffolding (firmware + host + docs + logging)
  main                        79b4ed3  [origin/main] Initial commit
  develop                     79b4ed3  [곧 push 예정]
```

## 5. Pending heebin actions

1. **credential helper 1회**:
   ```bash
   git config --global credential.helper osxkeychain
   ```
2. **develop 브랜치 push**:
   ```bash
   cd /Users/heebiny/canduck && git push -u origin develop
   ```
3. **GitHub repo 설정** (브라우저):
   - Settings → Branches → Default branch → `develop` 으로 변경
4. **작업 브랜치 push**:
   ```bash
   git push -u origin w0/t00-initial-scaffolding
   ```
   첫 push 시 username (`heebin-h`) + PAT 입력.
5. **GitHub 웹에서 PR open**:
   - Compare & pull request 클릭 (target = develop 자동)
   - 본문 칸 paste (Claude가 클립보드 복사해 둠)
   - Create pull request → Merge

## 6. Next actions (Claude)

merge 완료 알림 받으면:
1. `git checkout develop && git pull`
2. **W0-T01 진입**: 6종 스킬 문서 작성 (`docs/skills/`)
   - kicad-workflow.md / cadquery-modeling.md / firmware-test-loop.md
   - host-deploy-loop.md / measurement-protocol.md / bom-sourcing.md
3. 새 작업 브랜치 `w0/t01-skills-docs` (develop 기준) 에서 진행

## 7. Context notes

- W0-T00 (bootstrap) + W0-T00b (PR workflow + 브랜치 전략) 합의가 Phase 0의 인프라/룰 기반. 이후 모든 task는 § 8 흐름 따름.
- session log는 CLAUDE.md 룰 따라 매 turn append. PR 본문에는 포함되지만 read-only stream (코드 변경 아님).
- W9 (RPi systemd 첫 배포) 시점에 `release/*` · `hotfix/*` 도입 + main branch protection 강화 검토.
