# Codex CLI sandbox 관측 기록

2026-09-12 문서 정리 시 기존 CODEX.md에서 보존한 2026-07 및 2026-09-10 관측이다. 이 작업에서 재실측하지 않았다. 아래 판단은 당시 환경에 대한 기록이며 현재 실행 지침은 `../CODEX.md`를 따른다.

Windows `workspace-write` 실측 (2026-07, codex-cli 0.144.0):
- 워크스페이스 내부 파일 쓰기 PASS, `%TEMP%` 쓰기 PASS, `npm` 실행 PASS
- **`git commit` FAIL** — 워크스페이스 내부라도 `.git/` 쓰기가 차단됨 (`.git/index.lock: Permission denied`)
- 워크스페이스 밖 쓰기 FAIL (설계대로)
- `danger-full-access` 에서는 동일 조건 `git commit` PASS (실측 검증 완료)

**의존성이 워크스페이스 밖에 있으면 `workspace-write` 는 검증을 못 돌린다** (2026-09-10 실측, loh-character-viewer). 샌드박스는 워크스페이스 밖 **읽기**도 막으므로, 인터프리터의 user site-packages(`AppData/Roaming/Python/<ver>/site-packages`)에 있는 패키지를 못 읽는다 — 같은 인터프리터가 샌드박스 밖에서는 멀쩡히 도는데 런 안에서는 `ModuleNotFoundError: No module named 'numpy'`(pytest 가 collection error 로 무더기 실패)와 `No module named ruff` 가 난다. venv 가 레포 안에 있으면 해당 없다.

- **위임 전에 확인한다**: `python -c "import <핵심 패키지>; print(<패키지>.__file__)"` 로 경로가 워크스페이스 밖이면 그 레포의 위임은 `-s danger-full-access` 가 기본이다.
- **편집 런과 검증 런을 나누지 않는다.** 편집을 `workspace-write` 로, 검증만 `danger-full-access` 로 따로 띄우는 분리는 런이 하나 더 늘고(컨텍스트를 새로 사는 비용), 무엇보다 **편집 런이 자기 실수를 스스로 고칠 수 없게 된다** — 당시 공통 런북 §실행 검증 이 한 런으로 끝내라고 하는 이득이 사라진다. 검증 실패를 메인 루프가 받아 다시 브리프로 돌려주는 왕복이 그 자리를 대신하는데 그게 더 비싸다.
- 따라서 이 경우 **편집+검증을 한 런에서 `danger-full-access`** 로 돌리고, 커밋 금지는 브리프의 §금지 사항 으로 건다(샌드박스가 아니라 지시로 막는다). 메인 루프가 브리프와 diff 를 감독하는 것이 그 전제다.
- 증거가 없는 채로 런이 끝나면 그것은 미실행이다(당시 공통 런북 §검증 결과 신뢰). 샌드박스 때문이었는지 구별하려면 보고에 원문 오류를 요구한다 — 위 두 메시지가 보이면 정책 문제이지 코드 문제가 아니다.

**`workspace-tools` 에서 agent-browser 는 `--args '--no-sandbox'` 로만 Chrome 을 띄운다** (2026-09-23 실측, codex-cli 0.156.1, agent-browser 0.32.3, loh-aio-archive). 런은 샌드박스 사용자(`C:\Users\CodexSandboxOnline`)로 돈다. `agent-browser doctor` 는 Chrome(`C:\Program Files\Google\Chrome\Application\chrome.exe`)을 찾지만 Launch test 가 `Browser launch failed: CDP response channel closed` 로 실패하고, `open` 도 같은 오류(`Auto-launch failed: …`)를 낸다. ms-playwright chromium 으로 `--executable-path` 를 바꿔도 같은 오류다. `--args '--no-sandbox'` 를 주면 같은 프로필에서 `open`·`eval` 이 성공한다 — Chrome 자체의 프로세스 샌드박스가 샌드박스 사용자 토큰 아래에서 뜨지 못하는 것으로 보이나 원인은 확인하지 않았다. `danger-full-access` 는 필요 없다. 실행 지침은 `../AGENT_BROWSER.md` §codex 샌드박스.
- 같은 날 `gpt-6-luna` 는 codex-cli 0.154.0 에서 `not supported when using Codex with a ChatGPT account`(400)로 거부되고 0.156.1 에서는 동작했다.


