# W0-T00c — Project Status Check & W0-T01 Prep

- **Date**: 2026-06-01
- **Owner**: Claude (PM) + heebin (confirm)
- **Status**: in_progress
- **Phase**: Phase 0 (Infra) — W0 마무리 직전

---

## 1. 현재 상태 스냅샷 (사실)

### 1.1. Git
| 항목 | 값 |
|---|---|
| 로컬 브랜치 | `develop` (79b4ed3, 로컬만), `main` (79b4ed3, origin/main 추적), `w0/t00-initial-scaffolding` (b6207d0, 2 commits) |
| origin remote | `git@github.com:heebin-h/canduck.git` (SSH) |
| origin 브랜치 (Claude 시야) | `origin/main` (79b4ed3), `origin/w0/t00-initial-scaffolding` (b6207d0) — heebin이 작업 브랜치는 push한 것으로 추정 |
| `origin/develop` | **미확인** — 아직 push 안 된 듯 (Claude fetch X) |

### 1.2. Phase 0 진행도
| Task | 내용 | 상태 |
|---|---|---|
| W0-T00 | bootstrap + workflow 합의 | ✅ completed (`docs/reports/W0-T00-bootstrap.md`) |
| W0-T00b | PR workflow + Git Flow lite 합의 | ✅ completed (`docs/reports/W0-T00b-workflow-pr.md`) |
| W0-T00c | status check + T01 prep | ⏳ in_progress (this file) |
| W0-T01 | docs/skills 6종 문서 | ⏸ pending (PR-merge 후 진입) |
| W0-T02 | parts.md 재검토 보고서 | ⏸ pending |

### 1.3. 결정 영구화 (룰)
- `CLAUDE.md` 1~8장 — 로깅 / 작업 분담 / IP 경계 / Phase Roadmap / 세션 진입 동선 / **§ 8 Git Flow lite + PR 흐름**
- `~/.claude/projects/-Users-heebiny-canduck/memory/` — `canduck-push-heebin` (push는 heebin 전담), `canduck-pm-mode` (PM 모드 룰)

### 1.4. 클립보드 / 임시
- `/tmp/canduck-pr-w0-t00.md` — 첫 PR 본문 마크다운 (commit 2개 기준, 곧 3개로 갱신)

---

## 2. W0 마무리 — 미진행 액션

### 2.1. heebin
| # | 액션 | 상태 |
|---|---|---|
| 1 | SSH 공개키 GitHub 등록 (`~/.ssh/id_ed25519.pub`) | ❓ (Claude는 인증 시도 안 함) |
| 2 | `git push -u origin develop` (origin/develop 생성) | ⏸ |
| 3 | GitHub repo Settings → Default branch → `develop` | ⏸ |
| 4 | 작업 브랜치 push (이미 됐으면 추가 commit 1개만 push) | 부분 완료? |
| 5 | GitHub 웹에서 PR open (base=develop) + 본문 paste + Merge | ⏸ |
| 6 | merge 완료 알리기 | ⏸ |

### 2.2. Claude (heebin merge 완료 신호 후)
| # | 액션 |
|---|---|
| 1 | (heebin이 fetch/pull 결과 공유 시) develop 동기화 확인 |
| 2 | W0-T01 진입 — 새 작업 브랜치 `w0/t01-skills-docs` (develop 기준) |
| 3 | docs/skills 6종 문서 작성 |
| 4 | commit + PR 본문 작성 + pbcopy |
| 5 | heebin 액션 안내 (push + PR + Merge) |

---

## 3. W0 다음 큐 (T01, T02)

### 3.1. W0-T01 — docs/skills 6종 문서
| 파일 | 내용 | 의존성 |
|---|---|---|
| `kicad-workflow.md` | KiCad 9 schematic → PCB → DRC → Gerber → JLCPCB | KiCad 9 설치 (heebin) |
| `cadquery-modeling.md` | heebin이 만든 .step 받아 엔지니어링 (내부공간/마운트/분할) | CAD 도구 결정 |
| `firmware-test-loop.md` | PlatformIO build → flash → serial log → 분석 | PlatformIO CLI (heebin) |
| `host-deploy-loop.md` | Python 패키징 → systemd 유닛 → RPi 배포 → journalctl | RPi5 SSH 셋업 |
| `measurement-protocol.md` | 측정 자동화 / 오실로 결과 캡처 / 데이터 포맷 | 측정 장비 |
| `bom-sourcing.md` | 부품 비교 / 데이터시트 분석 / 가격 추적 / 발주 워크플로우 | parts.md 확정 |

→ 문서 자체는 Claude가 작성 가능. 외부 의존성은 메모만 박고 진행.

### 3.2. W0-T02 — parts.md 재검토
- 빠진 부품 / 대체품 / 가격 / 데이터시트 링크 점검
- BOM 최종화 → Phase 1 (W1) 발주 준비

---

## 4. Phase 1+ 진입 준비 — 미해결 heebin actions

| 시점 | heebin 액션 | 비고 |
|---|---|---|
| W1 진입 전 | KiCad 9 설치 | schematic/PCB 작업 시작 시점 |
| W1 진입 전 | BOM 최종 confirm + 발주 결제 | W0-T02 후 |
| Phase 2 진입 전 | CAD 도구 결정 (Fusion 360 / Blender / FreeCAD) | 캐릭터 외형 1차 모델링 |
| W3 진입 전 | PlatformIO CLI 설치 | 펌웨어 작업 |
| W3 진입 전 | RPi5 SSH 셋업 | 호스트 작업 |
| W9 진입 전 | release/hotfix 도입 결정 (CLAUDE.md § 8.7) | 첫 배포 직전 |
| W9 진입 전 | main branch protection rule 강화 | GitHub Settings |

---

## 5. 컨펌 필요 결정 (PM → heebin)

1. **이 status 보고서를 첫 PR에 commit 3으로 추가?** (W0-T00c) — yes면 작업 브랜치에 push 부담 +1, no면 PR-merge 후 develop에 별도 commit
2. **W0-T01 (skills 6종)을 한 PR에 묶어 처리?** vs. 6개 파일을 2~3개 PR로 쪼개기 — 묶으면 PR 1번, 쪼개면 review 단위 짧음
3. **TaskList(harness)에 W0 task 등록할까?** — PM 모드 tracking 용. 등록 시 다음 세션에서도 큐 보존

---

## 6. Context notes

- 이 보고서는 일회성 (날짜 박힘). 다음 status check 시점에 새 파일 `W0-T0Xx-status-YYYY-MM-DD.md` 또는 living document `docs/status.md` 전환 가능 (heebin 컨펌 후).
- session log는 매 turn append 그대로. PR-merge 시 함께 머지되며 다음 working tree 변경부터 다음 PR 대상.
- 관련 메모리: `canduck-push-heebin`, `canduck-pm-mode` (다음 세션 자동 로드).
