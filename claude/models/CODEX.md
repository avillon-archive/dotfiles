# Codex 위임 실행 런북 (GPT-6.1 Sol · GPT-6 Luna)

Claude 가 Codex CLI 로 Sol·Luna 를 호출할 때의 독립 런북이다. OpenCode·CommandCode 용 `DELEGATION.md` 의 편집 강제·파일 개수 제한·실패 원인 가정은 적용하지 않는다. 실행 작업자의 공통 안전 규칙은 `~/.codex/AGENTS.md` 가 갖고, 관측 경위는 `investigation/CODEX_SANDBOX_OBSERVATIONS.md`.

## 모델

사용 조건·역할·effort 원칙은 `~/.claude/rules/local.md` §외부 CLI 위임·§시각 검증 이 정한다.

| 모델 | ID | effort (기본 / 상위) |
|---|---|---|
| GPT-6.1 Sol | `gpt-6.1-sol` | `high` / `xhigh` |
| GPT-6 Luna | `gpt-6-luna` | `high` / `xhigh` |

- 모델 지정이 `not supported when using Codex with a ChatGPT account`(400)로 거부되면 `codex --version` 부터 확인한다(구버전 CLI 가 신규 모델을 거부한다). 다른 모델로 임의 대체하지 않는다.

## 호출 템플릿

```bash
codex exec -C <작업-레포-루트> \
  -m <gpt-6.1-sol|gpt-6-luna> \
  -c model_reasoning_effort=<high|xhigh> \
  -c agents.enabled=false \
  -c default_permissions='"workspace-tools"' \
  --color never \
  -o <scratchpad>/codex-result.txt \
  "역할: 위임 작업자. <브리프 경로>를 읽고 목표·범위·제약·수용 기준에 따라 수행하라. 재위임·스테이징·커밋은 명시 허용 시에만 수행하라." < /dev/null
```

- 위임 작업자 역할은 호출 프롬프트 자체에 적는다 — CLI 실행 여부로 호출자를 판정하게 하지 않는다.
- `agents.enabled=false` 로 재위임을 끈다. 사용자가 재위임을 허용하면 이 override 를 빼고 허용 범위를 브리프에 적는다.
- `--profile` 은 쓰지 않는다 — 모델·effort·역할·권한은 위 명령의 인자로 준다.
- Bash 에서는 `< /dev/null` 로 stdin 을 막는다(다른 셸은 그 셸의 방식으로).
- `-o` 는 최종 메시지를 기록한다. 병렬 런은 `-o` 파일을 런마다 다르게 지정하고, 끝나면 즉시 회수한다. 실행 이벤트가 필요하면 `--json` 출력도 보존한다.

## 시각 검증 (사용자가 Luna 를 verifier 로 지정한 경우)

- 브리프 형식·판정 규약은 `~/dotfiles/common/VISUAL_VERIFICATION.md` 를 따른다. 브리프에 `~/.claude/models/AGENT_BROWSER.md` 경로와 verifier 별 `--session` 이름을 적는다.
- **모든 agent-browser 호출에 `--args '--no-sandbox'` 를 붙이라고 브리프에 적는다** — 없으면 codex 샌드박스에서 Chrome 이 뜨지 않는다(`AGENT_BROWSER.md` §codex 샌드박스).
- 스크린샷을 기록하므로 `workspace-tools` 로 실행한다.

## 권한 프로필

- 편집·검증·리뷰 문서 작성: `default_permissions="workspace-tools"`. 파일을 만들지 않는 읽기 전용 조사: `":read-only"`. 사용자가 제한 없는 실행을 명시 승인한 작업만 `":danger-full-access"`.
- `-s`·`--sandbox`·`sandbox_mode` 를 권한 프로필과 섞지 않는다. 호스트에서 CLI 를 실행하는 권한과 자식 Codex 가 명령을 실행하는 권한은 별개다.
- 외부 의존성이 필요하면 실제 interpreter·패키지 경로와 프로필 접근 권한을 확인한다. 워크스페이스 밖이라는 이유만으로 실패를 단정하거나 제한 없는 실행으로 넓히지 않고, 필요한 경로만 허용하거나 승인된 프로필을 고른다.
- 비대화형이므로 필요한 권한은 시작 전에 확정한다. 권한 거부는 원문 오류·경로와 함께 보고하고 코드 결함으로 다루지 않는다.
- 편집과 그 범위의 검증은 같은 런에서 끝낸다. 커밋을 맡길 때만 Git 쓰기 권한을 따로 확인한다.

## 위임 브리프

- 목표·수정 가능 경로·제약·산출물·수용 기준·검증 명령·읽을 권위 문서를 적는다. 필요한 내용은 발췌하되 원본 절도 지목할 수 있다.
- 작업 단위는 계약·의존성·검증 경계로 정하고 파일 개수로 고정하지 않는다. 조사·리뷰 작업에는 편집을 강제하지 않는다.
- 재위임·스테이징·커밋은 기본 금지이고, 허용하면 행위와 경로를 적는다. `git stash`·무단 브랜치 생성·전환·worktree 생성은 금지한다.
- 기존 변경과 다른 세션의 프로세스·산출물을 보존한다. 공유 트리의 소스를 되돌렸다 복구하는 회귀 확인은 시키지 않는다.
- 수정 파일·수행한 검증과 실제 출력 요약·미완료 항목과 원문 오류를 보고하게 한다. 테스트를 약화시켜 통과시키지 않는다. 범위 안 결함은 고치고 범위 밖 결함은 보고한다.

## 결과 회수와 재개

- 보고를 실제 diff·산출물·검증 출력과 대조하고 spec 적합성은 메인 루프가 판단한다. 같은 검증은 근거 부족·불일치·새 변경이 있을 때만 다시 돌린다.
- 출력이 비었거나 산출물이 없으면 종료 상태·이벤트·오류부터 확인한다. 모델의 추론 방식이나 세션 사망을 원인으로 단정하지 않는다.
- 재개는 세션 ID 와 남은 작업을 명시한다. 동시 작업이 있으면 `--last` 로 세션을 추정하지 않는다. 같은 실패가 반복되면 원인을 조사하고 필요한 범위만 다시 배정한다.

## 계획 리뷰 (첫 계획 세션)

- Sol 로 실행한다(실행 조건은 전역 CLAUDE.md §세션 체계).
- 원본 계획은 보존하고 같은 gitignored 폴더의 `<원본파일명>_review-sol.md` 에 별도 리뷰를 쓴다(`workspace-tools`).
- 원본 작성 모델을 알면 브리프에 적고, 모르면 추정하지 않는다.
- 리뷰는 지적 대상·근거·수정 제안이 자립적으로 읽히게 한다. 원본·리뷰 통합은 사용자가 지시하는 후속 작업이다.
