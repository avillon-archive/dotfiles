# dotfiles

코딩 에이전트(Claude Code·Codex) 사용자 범위 설정. 파일을 `~/.claude/`·`~/.codex/` 에 심링크로 연결해 쓴다.

| 경로 | 내용 |
|---|---|
| `common/GUIDELINES.md` | 두 에이전트가 함께 읽는 공통 규율 |
| `claude/CLAUDE.md` | Claude Code 전용 지침(공통 규율을 `@` import) |
| `claude/rules/local.md` | 특정 기기의 도구·환경에 묶인 조항(사용자 범위 rules 로 자동 로드) |
| `claude/FLUENT_KOREAN.md` | 권위 문서 한국어 문장 규범 |
| `claude/models/` | 외부 CLI 위임 런북과 실측 기록 |
| `cloud/local.md` | Claude Code 클라우드 세션 전용 조항(클라우드에서 `claude/rules/local.md` 자리에 연결) |
| `codex/AGENTS.local.md` | Codex 전용 지침 |
| `codex/AGENTS.md` | 생성물 — 공통 규율 + Codex 전용 지침 |
| `codex/AGENT_BROWSER.md` | Codex 의 agent-browser 호출 규칙 |

Codex 는 AGENTS.md 안의 `@` import 를 해석하지 않으므로 `codex/AGENTS.md` 는 `scripts/build_codex_agents.py` 가 원본을 합쳐 만든다. 원본을 고친 뒤 스크립트를 실행하고, 생성물이 원본과 어긋난 채 커밋되지 않도록 훅을 건다.

## 연결 (Windows, 개발자 모드)

```bash
git config core.hooksPath .githooks
export MSYS=winsymlinks:nativestrict
for f in CLAUDE.md FLUENT_KOREAN.md models agents rules; do
  ln -s ~/dotfiles/claude/$f ~/.claude/$f
done
for f in AGENTS.md AGENT_BROWSER.md; do
  ln -s ~/dotfiles/codex/$f ~/.codex/$f
done
ln -s ~/.claude/RTK.md ~/dotfiles/claude/RTK.md
```

`~/.claude/RTK.md` 는 `rtk init -g` 가 생성·갱신하는 파일이라 이 레포에 두지 않는다. `CLAUDE.md` 끝의 `@RTK.md` 는 rtk 가 설정 완료로 확인하는 문자열이고, 심링크된 `CLAUDE.md` 의 상대 import 는 링크 대상 폴더 기준으로 풀리므로 `claude/RTK.md` 에 `~/.claude/RTK.md` 를 가리키는 링크를 둔다(gitignored). `codex/AGENTS.local.md` 끝의 CodeGraph 블록은 codegraph 설치기가 관리하는 마커 블록이므로 마커를 유지한다. 링크를 만들기 전에 같은 이름의 기존 파일·디렉터리를 치운다. Edit/Write 도구는 심링크에 쓰지 않으므로 편집은 이 레포의 실제 경로에 한다.

## 연결 (Claude Code 클라우드 세션)

클라우드 세션은 작업 레포만 clone 하므로 `~/.claude/` 의 사용자 범위 설정을 읽지 않는다. 그래서 claude.ai/code 의 개인 클라우드 환경에 아래 두 값을 등록해 지침을 연결한다.

Environment variables:

```text
CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=2
```

Setup script:

```bash
#!/bin/bash
set -euo pipefail
# dotfiles rev: 2   — dotfiles 변경을 반영하려면 이 값을 올려 환경 캐시를 다시 만든다
git clone --depth 1 https://github.com/avillon-archive/dotfiles.git /root/dotfiles
mkdir -p /root/.claude/rules
for f in CLAUDE.md FLUENT_KOREAN.md models; do
  ln -sfn /root/dotfiles/claude/$f /root/.claude/$f
done
ln -sfn /root/dotfiles/cloud/local.md /root/.claude/rules/local.md
touch /root/dotfiles/claude/RTK.md
npm install -g agent-browser && agent-browser install --with-deps || echo "agent-browser 설치 실패" >&2
```

`agent-browser install` 은 Chrome for Testing 버전 정보를 `googlechromelabs.github.io` 에서 받는데, 이 도메인은 Trusted 허용 목록에 없다. 네트워크 접근 수준을 Full 로 두거나, Custom 에 기본 목록을 포함하고 이 도메인을 추가한다. 브라우저 설치는 세션 시작에 필수가 아니므로 실패해도 스크립트가 0 으로 끝나게 둔다.

`claude/rules/local.md` 는 이 기기에만 해당하는 조항이므로 클라우드에서는 같은 자리에 `cloud/local.md` 를 연결한다. 클라우드에는 rtk 가 없고 rtk 훅이 걸린 사용자 `settings.json` 도 읽히지 않으므로, `@RTK.md` import 가 깨지지 않도록 빈 파일만 만든다. setup script 의 결과는 환경 캐시로 저장되어 이후 세션이 재사용하므로, push 한 지침 변경은 스크립트를 수정해 캐시가 다시 만들어진 뒤에 반영된다. `cloud/local.md` 를 고치는 커밋은 위 스크립트의 `dotfiles rev` 값도 함께 올리고, 클라우드 환경 설정의 setup script 에 같은 값을 반영한다. 다른 지침 변경은 클라우드에 바로 필요할 때만 올린다. 연결 결과는 새 세션에서 `/context` 를 실행해 Memory files 목록으로 확인한다.
