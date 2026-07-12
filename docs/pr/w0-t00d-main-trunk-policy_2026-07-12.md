# PR — W0-T00d: main 단일 트렁크 정책 확정

- **Branch**: `w0/t00d-main-trunk-policy` → `main`
- **Date**: 2026-07-12
- **Base / Compare**: base=`main` (`e8c0f9e`) ← compare=`w0/t00d-main-trunk-policy` (`fd2b395`)
- **Commits**: 1 — `fd2b395`
- **Diff**: 1 file, `CLAUDE.md` (+18/-21)

## What
W0-T00/T01 두 PR이 실제로는 `develop`이 아니라 `main`에 바로 머지됐고 remote `develop` 브랜치는 삭제된 상태로 확인됨. CLAUDE.md §8에 남아있던 "main+develop Git Flow lite" 문서를 실제 워크플로우(main 단일 트렁크 + feature 브랜치)에 맞춰 갱신.

## Files
- `CLAUDE.md` — §8 전체 개정: 브랜치 정의 표, 역할 분담 표, 초기 셋업 섹션에서 `develop` 제거, `main`을 PR target으로 명시. release/*·hotfix/* 도입 시점(W9)은 기존 계획 유지.

## Notes
- `develop` 언급이 남아있는 과거 `docs/reports/*.md`, `docs/logs/*.md`는 그 시점 기록이라 수정하지 않음. CLAUDE.md만 현재 유효한 룰로 갱신.
- heebin 확인 사항: main branch protection(직접 push 금지, PR-only) 아직 미설정이면 W1 진입 전 GitHub Settings에서 설정 권장 (§8.5).
