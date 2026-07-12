# 다음 세션 핸드오프 — Phase 0 완료, W1(KiCad schematic) 진입 대기

> 작성: 2026-07-12 (이번 세션 마무리 시점)
> 트리거: heebin이 새 세션 시작 시 § 5 "복붙용 프롬프트" 를 그대로 채팅에 붙여넣음.
> 이전 핸드오프(2026-05-25, git init 관련)는 이 파일로 대체됨 — git/gh 셋업은 이미 오래 전에 끝남.

---

## 1. 현재 상태 스냅샷 (2026-07-12 기준)

### 1.1. Git / 브랜치 정책
- **main이 유일한 트렁크**. `develop`은 폐지됨 (2026-07-12 확정, `CLAUDE.md` §8 참고).
  - 배경: W0-T00/T00b/T00c PR이 실제로는 `develop`이 아니라 `main`으로 머지됐고 remote `develop`은 삭제된 상태로 발견됨. 1인 메이커 프로젝트라 이중 브랜치 관리 실익 없다고 판단해 main 단일 트렁크로 공식 전환.
- 작업 브랜치 네이밍: `w{week}/t{task}-{slug}`, main에서 분기 → main으로 PR 머지.
- `release/*`·`hotfix/*`는 여전히 W9(RPi systemd 배포 시작) 시점에 도입 검토 예정 — 미변경.
- main 직접 commit 금지 원칙 유지 (`CLAUDE.md` §8.5).

### 1.2. main에 머지 완료된 것 (PR #1~#4)
| PR | 브랜치 | 내용 |
|---|---|---|
| #1 | `w0/t00-initial-scaffolding` | firmware/host/hardware 골격 39파일 + 로깅 시스템 |
| #2 | `w0/t01-skills-docs` | `docs/skills/` 6종 (아래 1.3 참고) |
| #3 | `w0/t00d-main-trunk-policy` | `CLAUDE.md` §8 개정(main 단일 트렁크) + `.gitignore`에 `.obsidian/`/`.omc/` 추가 |
| #4 | `w0/t02-parts-review` | `hardware/parts.md` 재검토 (누락 부품 7종 추가, 데이터시트 링크, 총합 재계산) |

### 1.3. 존재하는 파일 (주요)
- `docs/skills/`: `kicad-workflow.md`, `cadquery-modeling.md`, `firmware-test-loop.md`, `host-deploy-loop.md`, `measurement-protocol.md`, `bom-sourcing.md`
- `hardware/`: `parts.md`(재검토 완료), `schematic-spec.md`, `power-budget.md`
- `firmware/`, `host/`: W0 스캐폴딩 그대로 (코드 변경 없음, W3부터 본격 개발)
- `docs/`: `architecture.md`, `roadmap.md`(12주 계획, 시작일 아직 TBD), `reports/`(W0-T00~T00c), `logs/session-2026-07-12.md`(이번 세션 turn 1~6)
- `CLAUDE.md` — §8 브랜치 정책 갱신 완료

### 1.4. 아직 안 끝난 것 (진짜 loose end)
- ⏸ **`w0/t02c-session-log-sync` 브랜치** — 이번 세션 turn-6 로그만 담은 작은 브랜치, 아직 push/PR/merge 안 됨. 다음 세션에서 먼저 처리하거나 지금 push해도 됨.
- ⏸ **BOM 발주 결제** — 2026-07-12 turn-8~10에서 최종 confirm 완료 (RPi4 보유분 사용, 전량 JLC 어셈블리, 배터리·스코프 등 보류, 랩 도구 최소 셋 — `hardware/parts.md` "발주 확정"/"최소화" 참고, 코어 ~606K). 배치 1(~446K) 결제 실행만 남음 (heebin, 이번 주 내 권장).
- ⚠️ **W1 설계 제약 추가**: 전량 JLC 어셈블리 확정이라 schematic 부품 선정은 JLC Parts Library(Basic 우선) 재고에 맞출 것. **W2 발주 시 스텐실 불필요** (기존 스킬 문서의 "Stencil 포함 발주"는 직접 실장 전제 — 무시). schematic-spec의 J_A4 핀수 불일치(6핀 표기 vs 신호 8개)는 W1에서 8핀으로 정정 (`docs/reports/W0-T02e-order-final.md` 검증표 참고).
- ⚠️ **W1 설계 변경 (2026-07-12 품목 심사 반영)**: ① LCD·INMP441·PAM8403·스피커 탈락 → **Board B에서 I2S 라인, 오디오 앰프 회로, J_B3(LCD)/J_B4(마이크)/J_B6(스피커) 커넥터 삭제 검토** — 오디오·영상은 3-in-1 USB 카메라(마이크·스피커 내장)로 대체, PCB 무관. ② v1 표정 렌더(face.py) 표시 수단 미정 — 스코프 조정 필요. ③ 모터 최종안은 `docs/reports/W0-T02g-motor-selection.md` (MG90S×10 통일 + N20 100RPM×2).
- ⏸ **roadmap 일정 재캘린더링** — roadmap.md 작성 시점(W0~W12) 이후 실제로 한 달 넘게 정체된 구간이 있었음. 시작일을 다시 못박을지는 heebin 판단.
- ⏸ **KiCad 9 설치** (heebin) — W1 진입 전제조건, 아직 확인 안 됨.

---

## 2. 다음 세션 첫 액션

### 2.1. Claude가 할 일 (세션 시작 시)
1. `git log --oneline -10` (main 기준)으로 위 상태가 여전히 맞는지 확인
2. `w0/t02c-session-log-sync` 브랜치가 아직 안 머지됐으면 heebin에게 push 요청 (또는 그 내용만 다시 커밋)
3. TaskList 확인 (현재 이 harness 세션 한정 task이므로 새 세션엔 비어있을 가능성 높음 — 아래 §1.4 기준으로 재등록)

### 2.2. heebin이 할 일
- KiCad 9 설치 여부 확인/완료
- BOM 최종 confirm + 발주 결제 여부 결정
- (선택) `w0/t02c-session-log-sync` push+merge

### 2.3. W1 진입 조건 충족 시 — Claude가 할 일
`docs/skills/kicad-workflow.md` 기준으로:
1. 새 브랜치 `w1/t03-pcb-schematic` (main에서 분기)
2. Board A(`canduck-power`), Board B(`canduck-hat`) KiCad 프로젝트 스캐폴딩 가이드 작성 (실제 .kicad_sch 파일은 heebin이 KiCad에서 작업, Claude는 스펙 대조·리뷰·체크리스트 지원)
3. `hardware/schematic-spec.md` 핀맵/네트 규칙 대조하며 리뷰
4. 매 task 종료 시 commit (`W1-T0N: <slug>`) + PR 본문 작성

---

## 3. 복붙용 프롬프트 (다음 세션에서 그대로 붙여넣기)

```
캔덕 프로젝트 재진입. 다음 순서로 컨텍스트 복구해줘:

1. /Users/heebiny/canduck/CLAUDE.md (프로젝트 룰, §8 브랜치 정책 특히)
2. /Users/heebiny/canduck/docs/handoff/next-session.md (이번 핸드오프 — 가장 중요)
3. /Users/heebiny/canduck/docs/logs/session-2026-07-12.md (직전 세션 전체)
4. git log --oneline -10 (main 기준 최신 상태 확인)
5. TaskList 확인

읽기 끝나면:
(A) 현재 상태 2~3줄 요약
(B) §1.4 loose end 중 뭐가 처리됐고 뭐가 남았는지 확인
(C) 다음 진행 액션 제안 (KiCad 설치 됐으면 W1 진입 제안)
```

---

## 4. Context 노트

- **main 단일 트렁크** — `develop` 언급이 오래된 문서(`docs/reports/W0-T00b-workflow-pr.md` 등)에 남아있어도 그건 그 시점 기록이라 그대로 둠. 현재 유효한 룰은 `CLAUDE.md` §8만.
- **로깅 룰** — 매 응답 끝에 `docs/logs/session-{date}.md`에 turn 블록 append. 새 날짜면 새 파일.
- **IP 경계** — Claude는 캐릭터 외형 디자인 결정 안 함. heebin이 1차 3D 모델링 후 `.step`/`.stl` 전달 시 엔지니어링(내부공간/마운트/분할)만 수행 (`docs/skills/cadquery-modeling.md` 참고).
- **작업 분담** — `CLAUDE.md` §4 표 그대로. 회로/펌웨어/호스트/3D엔지니어링/부품선정/테스트설계는 Claude, 발주·땜질·플래시·RPi배포·실측·3D외형디자인은 heebin.
- **sandbox 네트워크 제약** — 이 harness의 bash sandbox는 SSH(git@github.com) 아웃바운드가 막혀있고 HTTPS(`https://github.com/...`)만 됨. `git fetch`/`ls-remote`는 HTTPS 원격 URL로 해야 함. push는 heebin이 자기 터미널에서 SSH remote로 수행.
- **main 직접 commit 금지** — Claude는 항상 feature 브랜치 생성 → 작업 → PR 본문 작성까지만. push/merge는 heebin.
