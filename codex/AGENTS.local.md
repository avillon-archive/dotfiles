# Codex 전용 지침

## 지침 파일

- `~/.codex/AGENTS.md` 는 `~/dotfiles/codex/AGENTS.md` 의 심링크이고, 그 파일은 `~/dotfiles/common/GUIDELINES.md`(공통 규율)와 `~/dotfiles/codex/AGENTS.local.md`(이 절 이하)를 합친 생성물이다. 지침을 고칠 때는 두 원본을 편집하고 `python ~/dotfiles/scripts/build_codex_agents.py` 로 다시 생성한 뒤 `~/dotfiles` 에 커밋한다. 생성물을 직접 고치지 않는다.

## 환경

- Python 실행 명령은 `python`(not `python3`).

## 프로젝트 지침과 우선순위

- 저장소 루트에 `CLAUDE.md` 가 있으면 작업 시작 시 읽고 프로젝트 로컬 지침으로 따른다. `CLAUDE.md` 가 가리키는 권위 문서와 작업 관련 참조 문서도 확인한다.
- 지침 우선순위는 사용자 프롬프트, 저장소 로컬 `CLAUDE.md`, 이 전역 지침 순이다. 시스템·개발자 지침과 실행 환경의 권한 제한은 이 우선순위보다 앞선다.

## 사용자 확인

- 합리적인 가정이 결과·범위를 크게 바꾸지 않으면 진행하고, 중요한 선택이나 권한 확대가 필요할 때만 사용자에게 묻는다.

## 도구 확인

- 도구 유무는 `Get-Command`·`where.exe`·`<이름> --help` 와 도구 검색으로 확인한다.
- **샌드박스 밖 전역 도구 재확인**: `agent-browser` 등 사용자가 설치·가용성을 확인한 전역 CLI 가 샌드박스의 `PATH`·파일 가시성·실행 권한 차이로 보이지 않거나 실행이 거부되면 미설치로 단정하지 않는다. 같은 읽기 전용 탐색·실행을 승인된 샌드박스 밖 경로로 다시 시도한 뒤에만 대체 도구 사용 여부를 판단한다.
- agent-browser 를 실행할 때만 `~/.codex/AGENT_BROWSER.md` 를 읽는다.

## 네이티브 서브에이전트 호출 설정

- 사용자가 별도 설정을 지정하지 않으면 `gpt-6.1-sol`은 `reasoning_effort="high"`, `gpt-6-luna`는 `reasoning_effort="xhigh"`로 호출한다. 모델별 업무 분담은 고정하지 않는다.
- 모델과 effort를 지정할 때는 네이티브 `spawn_agent`에 두 값을 명시하고 `fork_turns="none"` 또는 필요한 최근 턴 수를 지정한다. 전체 이력을 상속하는 `fork_turns="all"`은 부모 모델·effort를 상속하므로 모델·effort 변경에 사용하지 않는다. 호출 시 현재 도구 스키마를 확인한다.
- Codex 앱에서는 네이티브 서브에이전트 도구를 사용한다. 모델 선택을 위해 외부 Codex CLI를 중첩 호출하지 않는다. 지원되지 않는 설정은 임의로 대체하지 않고 보고한다.
- 작업은 현재 프로젝트 checkout의 local 환경에서 수행한다. worktree는 사용자가 명시적으로 요청한 경우에만 사용한다.
- 위임 시 대상 경로·수용 기준·검증 방법을 명시하고 기존 변경을 보존한다. 별도 허용이 없으면 작업자는 `git add`·`git commit`·재위임을 수행하지 않는다. 최종 통합 담당자는 diff와 근거를 직접 확인해 spec 적합성을 판단한다.

## 승인 요청과 임시 파일 비용 통제

- 명령을 실행하기 전에 sandbox writable root, 기존 승인 prefix, 파괴 동작 분류를 확인한다. 선택적 진단·임시 출력·cleanup 때문에 승인 요청을 만들지 않는다.
- stdout 또는 메모리 집계로 충분하면 임시 파일을 만들지 않는다. 지속 파일이 불필요한 경우 언어·도구의 자동 정리 temporary API를 같은 프로세스 안에서 사용해 별도 삭제 명령을 만들지 않는다.
- 임시 파일이 꼭 필요하면 사용자와 프로젝트 지침이 허용한 writable·gitignored 경로 하나로 한정한다. 저장소 밖 경로를 임의로 사용하거나, cleanup을 위해 광범위한 삭제·승인 요청을 추가하지 않는다.
- sandbox 실패가 예상되거나 한 번 확인되면 같은 명령을 포장만 바꿔 반복하지 않는다. 이미 승인된 정확한 prefix를 사용하거나, 작업 결과를 바꾸지 않는 범위에서 writable 경로·in-memory 흐름으로 설계를 바로잡는다.
- 사용자가 승인 요청을 금지한 작업에서는 승인 없이는 불가능한 부수 작업을 생략한다. 핵심 작업까지 새 권한이 필요한 경우에만 blocker로 보고하며, 우회성 명령으로 승인 체계를 회피하지 않는다.

## 커밋 메시지

- **커밋 메시지는 제목 + 충실한 본문이 기본** — 사용자가 한 줄 메시지나 별도 형식을 명시하지 않으면 최근 커밋을 확인해 프로젝트의 제목 형식·언어·본문 관례를 따른다. 제목만 작성하지 말고 본문에 변경 목적, 핵심 구현과 동작 계약, 중요한 설계 선택·트레이드오프를 구체적으로 기록한다. 통상적인 테스트 통과 여부·명령 목록·테스트 건수는 최종 작업 보고나 CI의 책임이므로 커밋 본문에 별도 검증 체크리스트로 기록하지 않는다. 특정 실측 결과가 설계 주장, 회귀 방지 근거, 미해결 제한을 이해하는 데 반드시 필요할 때만 해당 논점의 문단에 자연스럽게 통합한다. 추측·미실측 수치·파일 목록 복창으로 분량을 채우지 않으며, 서로 다른 논점은 문단이나 항목으로 분리해 커밋만 읽어도 변경 이유와 결과를 이해할 수 있게 한다.

<!-- CODEGRAPH_START -->
## CodeGraph

In repositories indexed by CodeGraph (a `.codegraph/` directory exists at the repo root), reach for it BEFORE grep/find or reading files when you need to understand or locate code:

- **MCP tool** (when available): `codegraph_explore` answers most code questions in one call — the relevant symbols' verbatim source plus the call paths between them, including dynamic-dispatch hops grep can't follow. Name a file or symbol in the query to read its current line-numbered source. If it's listed but deferred, load it by name via tool search.
- **Shell** (always works): `codegraph explore "<symbol names or question>"` prints the same output.

If there is no `.codegraph/` directory, skip CodeGraph entirely — indexing is the user's decision.
<!-- CODEGRAPH_END -->
