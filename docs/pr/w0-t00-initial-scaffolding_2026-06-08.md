# PR — W0 initial scaffolding + ops rules (Phase 0)

- **Branch**: `w0/t00-initial-scaffolding` → `develop`
- **Date**: 2026-06-08
- **Base / Compare**: base=`develop` (`79b4ed3`) ← compare=`w0/t00-initial-scaffolding` (`329b1e2`)
- **Commits**: 3 — `ce33772` / `b6207d0` / `329b1e2`
- **Diff**: 46 files, +4105 / -210

> GitHub PR 본문에 붙여넣을 내용은 아래 `## What` 부터입니다 (이 메타 헤더는 기록용).

---

## What
W0 전체 스캐폴딩 + 운영 룰 확정. 펌웨어/호스트 골격, 하드웨어 사양 초안, docs·로깅 인프라, PR 워크플로우(Git Flow lite) 합의까지 Phase 0 결과물을 `develop`에 한 번에 통합. (3 commits, 46 files, +4105/-210)

## Files
**규칙·운영 / 로깅 인프라**
- `CLAUDE.md` — 로깅·작업분담·IP경계·Phase roadmap·§8 Git Flow lite PR 흐름
- `.claude/hooks/log-conversation.py`, `.claude/settings.json` — 세션 자동 로깅 hook

**docs**
- `docs/architecture.md`, `docs/roadmap.md`, `docs/handoff/next-session.md`
- `docs/reports/` — W0-T00-bootstrap / W0-T00b-workflow-pr / W0-T00c-status
- `docs/logs/session-*.md` — 05-23 ~ 06-06 세션 로그

**firmware (PlatformIO, C++)**
- `firmware/platformio.ini`, `src/` (main / comm / poses / servo_ctrl), `include/` (pins / comm / poses / servo_ctrl)

**host (Python)**
- `host/canduck/` — daemon / fsm / mqtt_client / uart_client / face / voice / telemetry / config
- `host/systemd/` — canduck.service + env.example, `host/pyproject.toml`

**hardware**
- `hardware/parts.md`, `power-budget.md`, `schematic-spec.md`

## Notes
- 첫 PR. base=`develop`, compare=`w0/t00-initial-scaffolding`
  - `ce33772` 초기 스캐폴딩 / `b6207d0` PR 워크플로우 합의 / `329b1e2` status check + 세션 로그
- `.gitignore` 대량 축소(-210): GitHub 기본 placeholder → 프로젝트 실사용본으로 교체 (§8.4 로컬본 채택 원칙)
- `W0-T00c-status.md` + 누적 세션 로그 9개를 commit 3으로 backfill — 이전 세션들이 commit 없이 끊겨 working tree에 떠 있던 것 정리 (이번 PR에 포함하기로 §5 Q1 확정)
- `main`은 W8까지 frozen — 이 PR은 `develop`으로만 머지
