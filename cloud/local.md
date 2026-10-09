# 클라우드 환경 조항

Claude Code 클라우드 세션(Anthropic 관리 VM)에서만 성립하는 조항이다. 공통 원칙은 `~/.claude/CLAUDE.md` 가 갖는다. 클라우드 환경의 setup script 가 이 레포를 `/root/dotfiles` 에 clone 하고 이 파일을 `~/.claude/rules/local.md` 로 연결한다.

## 환경

- Ubuntu 24.04 x86_64 VM 이고 `HOME` 은 `/root` 다. Python 실행 명령은 `python3`.
- **지침 파일은 읽기 전용 사본이다.** `/root/dotfiles` 는 세션 시작 시점의 clone 이므로 지침 수정은 클라우드 세션에서 하지 않는다. 고칠 점을 발견하면 보고에 적는다.
- **`~/.claude/memory/` 는 이 환경에 없다.** 지침의 `→ 상세`·`→ 근거` 포인터는 끊겨 있으니 포인터를 따라가려 하지 말고 지침 본문 조항만 따른다.
- 서브에이전트 중첩 깊이 상한은 클라우드 환경 변수 `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=2` 로 정한다 — 메인 루프 → 서브에이전트 → Haiku 까지만 허용한다(전역 §Haiku 보조 위임).
- 각 클라우드 세션은 VM 을 독점하므로 로컬 실행 자원(포트·브라우저·워킹 트리)은 다른 세션과 겹치지 않는다. 원격 브랜치는 겹치므로 push 전에 fetch 해 다른 세션의 커밋 위로 rebase 한다.

## Git

- 세션이 만든 작업 브랜치가 아니라 사용자가 세션을 시작할 때 고른 브랜치(main·dev 등)에 직접 커밋하고 push 한다(전역 §Git / 브랜치).

## 외부 CLI 위임

- codex·opencode·cmdc·agy·rtk 는 설치돼 있지 않다. 외부 CLI 모델이 지정돼도 쓸 수 없으므로 전역 §위임 매트릭스 의 대체 조항대로 Claude 서브에이전트로 대체하고 보고에 적는다. `~/.claude/models/` 의 CLI 런북은 이 환경에 해당하지 않는다.

## 시각 검증 구동

배정·위임 규칙은 전역 §시각 검증 이 갖고, 이 절은 이 환경의 구동 도구만 정한다.

- verifier 는 setup script 가 설치한 `agent-browser` 로 headless Chrome 을 구동한다. 브리프에 `~/.claude/models/AGENT_BROWSER.md` 경로와 verifier 별 `--session` 이름을 적는다 — 런북의 Git Bash·PowerShell·codex 샌드박스 조항은 해당하지 않는다. 메인 루프의 전 세션 정리 명령은 `agent-browser close --all` 이다.
- 브라우저가 닿는 도메인은 클라우드 환경의 네트워크 접근 수준이 정한다. 차단으로 보이는 실패는 우회하지 말고 대상 도메인과 오류를 그대로 보고한다.
