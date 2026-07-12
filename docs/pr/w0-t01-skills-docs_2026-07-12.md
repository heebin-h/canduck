# PR — W0-T01 skills docs (6종) + PR 본문 housekeeping

- **Branch**: `w0/t01-skills-docs` → **⚠️ target = `w0/t00-initial-scaffolding` (develop 아님, 아래 § Notes 참고)**
- **Date**: 2026-07-12
- **Base / Compare**: base=`w0/t00-initial-scaffolding` (`329b1e2`) ← compare=`w0/t01-skills-docs` (`533ff11`)
- **Commits**: 2 — `0a28a64` / `533ff11`
- **Diff**: 7 files, +537 / -0

> GitHub PR 본문에 붙여넣을 내용은 아래 `## What` 부터입니다 (이 메타 헤더는 기록용).

---

## What
W0-T01: `docs/skills/` 6종 문서 작성 (KiCad, CadQuery 엔지니어링, 펌웨어 테스트 루프, 호스트 배포 루프, 측정 프로토콜, BOM 소싱). 각 문서는 `hardware/*.md`, `firmware/README.md`, `host/README.md`의 현재 구현 상태를 근거로 작성. 부수적으로 6/8에 작성됐지만 미커밋 상태였던 W0-T00 PR 본문도 housekeeping commit으로 편입.

## Files
**skills (신규)**
- `docs/skills/kicad-workflow.md` — schematic → PCB → DRC → Gerber → JLCPCB, Board A/B 핀맵·체크리스트 포함
- `docs/skills/cadquery-modeling.md` — heebin 원본 `.step`/`.stl` 엔지니어링 전용, **IP 경계(CLAUDE.md §3) 명시**
- `docs/skills/firmware-test-loop.md` — PlatformIO build/flash/serial monitor 루프, 스모크 테스트 시퀀스
- `docs/skills/host-deploy-loop.md` — RPi5 systemd 배포 + journalctl 분석 루프
- `docs/skills/measurement-protocol.md` — 전원 레일/서보 실측 프로토콜, CSV 데이터 포맷
- `docs/skills/bom-sourcing.md` — 부품 비교·데이터시트 체크리스트·발주 워크플로우

**housekeeping**
- `docs/pr/w0-t00-initial-scaffolding_2026-06-08.md` — 2026-06-08에 작성됐으나 develop 워킹트리에 미추적 상태로 남아있던 첫 PR 본문. 유실 방지를 위해 이번 커밋으로 보존.

## Notes
- ⚠️ **머지 순서 의존성**: 이 브랜치는 `develop`이 아니라 `w0/t00-initial-scaffolding`에서 분기했습니다. `w0/t00` PR이 아직 `develop`에 머지되지 않았기 때문입니다 (2026-07-12 기준 `origin/develop` = 초기 커밋 그대로).
  - 옵션 A: `w0/t00` PR을 먼저 develop에 머지 → 이 브랜치를 `develop` 기준으로 rebase → PR target을 `develop`으로 변경해서 오픈
  - 옵션 B: 지금 이 상태로 `w0/t00-initial-scaffolding`을 target으로 PR 오픈(스택형) → `w0/t00`이 develop에 머지된 후 GitHub가 자동으로 target을 develop으로 재조정하도록 처리(또는 수동 rebase)
  - 권장: **옵션 A** (Git Flow lite 원칙 §8.1 "작업 브랜치는 항상 develop에서 분기"에 부합, 스택 PR로 인한 리뷰 혼선 방지)
- `docs/skills/cadquery-modeling.md`는 IP 경계 규칙을 문서 최상단에 재명시 — 캐릭터 외형 디자인/분석은 Claude 영역 아님, heebin이 만든 파일의 엔지니어링만 수행.
- 이번 세션에서 develop 워킹트리에 남아있던 미추적 stray 파일 2개(구버전 세션로그 조각 + 이 PR 본문 원본)를 정리. 원본 PR 본문은 유실 없이 이 브랜치로 이전.

## heebin 액션 (§8.2)
1. `git push -u origin w0/t01-skills-docs`
2. **먼저 `w0/t00-initial-scaffolding` → `develop` PR부터 merge** (아직 안 열려있으면 `docs/pr/w0-t00-initial-scaffolding_2026-06-08.md` 본문으로 오픈)
3. `w0/t00` 머지 완료 후 이 브랜치를 develop 기준으로 rebase 요청하거나, Claude에게 rebase 진행 지시
4. rebase 후 GitHub에서 PR open (target=`develop`), 위 `## What`~`## Notes` paste, merge
