# 로컬 환경 조항

이 기기(Windows, 로컬 CLI 설치본)에서만 성립하는 조항이다. 공통 원칙은 `~/.claude/CLAUDE.md` 가 갖는다.

## 환경

- Python 실행 명령은 `python`(not `python3`).
- **지침 파일은 `~/dotfiles` 레포에 있다.** `~/.claude/` 의 `CLAUDE.md`·`FLUENT_KOREAN.md`·`models/`·`rules/` 는 `~/dotfiles/claude/` 의 심링크이고, 공통 규율은 `~/dotfiles/common/GUIDELINES.md` 다. Edit/Write 도구는 심링크에 쓰지 않으므로 dotfiles 쪽 실제 경로를 편집하고 그 레포에 커밋한다. 공통 규율이나 Codex 전용 지침(`~/dotfiles/codex/AGENTS.local.md`)을 고쳤으면 `python ~/dotfiles/scripts/build_codex_agents.py` 로 Codex 지침을 다시 생성한다(커밋 훅이 누락을 막는다). 클라우드 조항(`~/dotfiles/cloud/local.md`)을 고쳤으면 같은 커밋에서 README setup script 의 `dotfiles rev` 를 올리고, 클라우드 환경 설정에도 반영하라고 사용자에게 알린다. `~/.claude/memory/` 와 rtk 가 생성·갱신하는 `RTK.md` 는 레포 대상이 아니다.
- 서브에이전트 중첩 깊이 상한은 `~/.claude/settings.json` 의 `env.CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH = "2"` 다 — 메인 루프 → 서브에이전트 → Haiku 까지만 허용하고 2층에서는 Agent 도구가 주어지지 않는다(전역 §Haiku 보조 위임).

## 외부 CLI 위임

- **사용 조건**: 외부 CLI 모델은 사용자가 CLI 와 모델을 함께 지정했을 때만 쓴다. 두 CLI 가 같은 모델을 제공하는데 CLI 명시가 없으면 묻는다.
- **역할**:
	- DeepSeek Flash(opencode·`cmdc`): Sonnet 과 같은 역할 — 목표·범위가 명확한 작업.
	- GPT-6.1 Sol(codex): 구현·리뷰에서 Sonnet 과 같은 역할.
	- Muse Spark 1.3(opencode): 무료 경로(Free)는 사용자가 "Muse Spark Free" 라고 지정했을 때만 쓴다.
- **effort**: 모델·effort 는 매 호출에 명시한다(CLI 기본값은 예고 없이 바뀐다). effort 는 그 모델이 맡는 작업 범위 안에서 난도로 골라, 각 런북 모델 표의 기본 단계와 상위 단계 중 하나를 쓴다.
- **런북**: OpenCode·CommandCode 는 `~/.claude/models/DELEGATION.md` 를 먼저 읽고, Codex 는 `~/.claude/models/CODEX.md` 만 따른다.

## 별도 세션 위임

- 별도 세션 위임(`claude --bg --model <m> --effort <lvl>`)은 사용자가 지켜보거나 메인 세션보다 오래 도는 작업에만 쓴다. 브리프 첫머리에 "위임받은 작업 세션이며 메인 루프가 아니다 — 재위임 없이 직접 수행하고 결과를 보고한다" 를 적는다.

## 시각 검증 구동

배정·위임 규칙은 전역 §시각 검증 이 갖고, 이 절은 이 기기의 구동 도구만 정한다.

- verifier 는 전역 CLI `agent-browser` 로 브라우저를 직접 구동한다. 브리프에 `~/.claude/models/AGENT_BROWSER.md` 경로와 verifier 별 `--session` 이름을 적는다. 메인 루프의 전 세션 정리 명령은 `agent-browser close --all` 이다.
- Antigravity(`agy`) Gemini 는 사용자가 지정했을 때만 verifier 로 쓴다(`~/.claude/models/ANTIGRAVITY.md`).

## CodeGraph

레포 루트에 `.codegraph/` 가 있으면 코드를 찾거나 이해할 때 grep·파일 읽기보다 먼저 쓴다 — MCP `codegraph_explore`(지연 로드면 tool search 로 불러온다) 또는 셸 `codegraph explore "<심볼·질문>"`. `.codegraph/` 가 없으면 쓰지 않는다(인덱싱은 사용자가 정한다).
