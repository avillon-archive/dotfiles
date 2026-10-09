# agent-browser 실행 런북 (브라우저 구동)

시각 검증에서 브라우저를 구동하는 수단인 전역 CLI `agent-browser`(PATH)의 사용 함정과 계측 레시피다. verifier 배정은 `~/.claude/CLAUDE.md` §시각 검증, 브리프 형식·판정 규약은 `~/dotfiles/common/VISUAL_VERIFICATION.md` 가 갖는다.

**이 문서를 읽는 주체는 브라우저를 구동하는 쪽**이다 — 보통 verifier 이고, 메인 루프가 직접 구동할 때도 같다. 위임할 때는 브리프에 이 경로를 적는다.

공식 사용법은 CLI 가 들고 있다 — 플래그 문서로 추측하지 말고 먼저 읽는다.

```bash
agent-browser skills get core --full     # 개요 + 전체 명령 레퍼런스 + 템플릿
agent-browser skills list                # electron·slack·탐색적 테스트 등 특화 스킬
```

아래 명령은 전부 **Bash 도구(Git Bash)** 전제다. `timeout` 은 coreutils 의 것이다 — PowerShell 의 `timeout` 은 단순 대기 명령이라 감싸도 아무것도 끊지 않는다.

## 세션 — 브리프가 지정한 `--session` 만 쓴다

`--session` 없이 부르면 **기본 세션 하나를 모든 호출자가 공유**한다. 병렬 verifier 가 각자 `set viewport`·`open` 을 하면 서로의 페이지를 덮어쓰고, 스크린샷은 남의 뷰포트가 찍힌다.

- 브리프에 적힌 세션명을 **모든** 호출에 붙인다(`agent-browser --session <name> ...`). 한 번이라도 빠뜨리면 그 호출은 기본 세션으로 간다. `export AGENT_BROWSER_SESSION=<name>` 이 셸 단위로 기본값을 바꾸지만 Bash 도구는 호출마다 셸이 새로 뜨므로 믿지 않는다 — 플래그로 매번 붙인다.
- 끝나면 **자기 세션만** `close` 한다. `close --all` 은 **다른 verifier 의 세션까지** 닫는다 — verifier 는 쓰지 않는다. 메인 루프가 전 verifier 종료 뒤 정리할 때만 쓴다.
- 시작 전에 같은 이름의 세션이 남아 있을 수 있다(이전 런 중단). 첫 `open` 이 이상하면 `--session <name> close` 후 다시 연다.

## 함정 — codex 샌드박스에서는 `--args '--no-sandbox'` 없이 Chrome 이 뜨지 않는다

**조건**: codex CLI 런(`default_permissions="workspace-tools"`) 안에서 agent-browser 를 구동한다. 런은 샌드박스 사용자(`C:\Users\CodexSandboxOnline`)로 돌고, 그 토큰 아래에서는 Chrome 이 실행 직후 CDP 채널을 닫는다. `open` 은 `Auto-launch failed: CDP response channel closed` 로, `agent-browser doctor` 의 Launch test 는 `Browser launch failed: CDP response channel closed` 로 실패한다.

- **모든 호출에 `--args '--no-sandbox'` 를 붙인다**(`agent-browser --session <이름> --args '--no-sandbox' <명령>`). 이 인자가 있으면 같은 `workspace-tools` 프로필에서 정상 구동된다 — 권한 부족이 아니므로 `danger-full-access` 로 올리지 않는다.
- 이 오류를 "서버가 안 떠 있다"·"권한 프로필에 agent-browser 가 없다" 로 읽지 않는다. 서버 부재는 페이지 오류로 돌아오고, `workspace-tools` 프로필은 agent-browser 경로를 이미 허용한다(`~/.codex/config.toml` `[permissions.workspace-tools.filesystem]`).
- `--executable-path` 로 ms-playwright chromium 을 지정해도 같은 오류다 — 실행 파일 문제가 아니다.
- 샌드박스 밖(메인 루프가 직접 구동)에서는 이 인자가 필요 없다.

실측 기록: `investigation/CODEX_SANDBOX_OBSERVATIONS.md`.

## 함정 — rAF 상시 구동 페이지에서 `open` 이 반환하지 않는다

**조건**: 프레임 루프를 쉬지 않고 도는 페이지(WebGL 뷰어·게임 캔버스·상시 애니메이션). network idle 에 도달하지 않아 `open` 이 정상 종료하지 않는다. 정적 페이지나 클릭 이펙트 정도만 쓰는 페이지에서는 나타나지 않는다.

**브라우저는 정상적으로 뜨고 페이지도 로드되며 이후 명령은 전부 정상**이다 — 매달린 것은 그 호출 하나뿐이다.

- **매달림을 "서버가 안 떠 있다" 로 읽지 않는다.** 서버 부재는 `open` 이 즉시 오류로 돌아온다. 매달리면 페이지는 떠 있는 것이다 — dev 서버를 새로 띄우지 않는다(띄우는 것은 메인 루프 몫이고, 고정 포트 레포에서는 두 번째 기동이 포트 충돌로 죽는다).
- 그런 페이지를 열 때는 `timeout <초>` 를 씌우고 출력을 버린 뒤 `get url` 로 로드를 확인한다. Bash 도구의 기본 타임아웃(120 s)보다 짧게 잡는다 — 도구 타임아웃으로 죽으면 오류처럼 보여 같은 호출을 반복하게 된다.
- 세션은 프로세스 밖에 살아 있어 이후 명령이 같은 페이지에 붙는다. 끝나면 자기 세션만 `close` 한다(§세션).
- 매달린 `open` 이 떠 있는 동안 다른 호출(`doctor` 등)도 막힐 수 있다 — 그 호출을 먼저 끝내고 진행한다.

```bash
S="--session <브리프의 세션명>"
timeout 60 agent-browser $S open "<url>" >/dev/null 2>&1
timeout 40 agent-browser $S get url            # 로드 확인 — 페이지 준비는 별개(아래)
timeout 40 agent-browser $S set viewport 1280 800
timeout 40 agent-browser $S screenshot <path>
timeout 40 agent-browser $S close             # 종료 시 — 자기 세션만
```

`get url` 은 네비게이션 확인이지 **페이지 준비 확인이 아니다**. 모델·에셋을 비동기로 싣는 페이지는 `open` 직후 캔버스가 비어 있고 컨트롤도 빈 채다 — 고정 `sleep` 으로 때우지 말고, 레포 문서가 정한 준비 신호(특정 컨트롤에 옵션이 채워짐·캔버스 비빈 픽셀 등)를 `eval` 로 폴링한 뒤 찍는다. 준비 전 스크린샷으로 FAIL 을 내는 것이 false-FAIL 의 주된 경로다.

## 결정적 프레임 검증 — rAF 게이트

애니메이션·전이처럼 **한 프레임짜리 결함**은 스크린샷 폴링으로 잡지 못한다. `eval` 로 페이지의 프레임 루프를 수동 시계로 바꿔 한 장씩 진행시킨다. 렌더 루프가 전역 `requestAnimationFrame` 을 매번 이름으로 부르면(대부분 그렇다) 런타임 패치가 그대로 먹는다.

```js
const q = []; let t = performance.now();
performance.now = () => t;                       // 시계도 함께 고정해야 dt 가 튀지 않는다
window.requestAnimationFrame = (cb) => q.push(cb);
window.cancelAnimationFrame = () => {};
window.__gate = { step(n=1) { for (let i=0;i<n;i++) { t += 1000/60;
  for (const cb of q.splice(0, q.length)) cb(t); } return q.length; } };
window.__run = async (n, ms) => { for (let i=0;i<n;i++) { __gate.step(1);
  await new Promise(r => setTimeout(r, ms)); } };   // setTimeout 은 실시간이라 로드가 해소된다
```

`step` 후 `pending` 이 1 이면 루프가 게이트에 걸린 것이다. 프레임을 진행시키지 않으면 캔버스는 갱신되지 않으므로, 스크린샷이 느려도 각 PNG 는 **정확히 프레임 하나**다.

## 캔버스 수치 계측 — 육안보다 먼저

"한 프레임만 튀는가" 를 육안으로 판정시키면 미세한 변화를 놓친다. 프레임 콜백 **직후 같은 프레임 안에서** 캔버스를 읽어 수치로 남긴다(WebGL 캔버스는 `preserveDrawingBuffer` 없이는 그 시점에만 읽힌다 — 나중에 읽으면 빈 이미지다).

```js
const small = document.createElement("canvas"); small.width = 128; small.height = 96;
const sctx = small.getContext("2d", { willReadFrequently: true });
// __gate.step 의 콜백 루프 바로 뒤에서 호출한다
sctx.drawImage(document.querySelector("canvas"), 0, 0, 128, 96);
const d = sctx.getImageData(0, 0, 128, 96).data;   // 임계값으로 대상 bbox·픽셀수 산출
```

계단(불연속)이 몇 번 나타나는지로 판정한다 — 원자적으로 적용되어야 할 두 변화가 갈라지면 **계단이 두 번** 생긴다. 나머지 프레임의 연속 변화는 애니메이션이다.

## 함정 — 캐시가 더우면 검증 대상 경로를 아예 안 탄다

비동기 대기 구간의 결함을 보려면 그 대기가 실재해야 한다. 캐시 적중이면 `await` 가 없어 전이가 한 프레임에 끝나고, **"통과" 가 아니라 "그 경로를 안 탄 것"** 이 된다.

- 대상 요청만 지연시켜 창을 넓힌다: `window.fetch` 를 감싸 패턴이 맞는 URL 에 `await sleep(2500)`. 코드가 `fetch` 를 자유 식별자로 부르면(대부분) 런타임 패치가 먹는다.
- **지연 래퍼가 실제로 걸렸는지 카운터로 확인**한다(`slow: 0` 이면 그 경로를 안 탄 것이다). 요청이 0 이면 입력을 바꾼다 — 캐시를 비우거나(재로드·다른 대상), 같은 자원을 공유하지 않는 대상을 고른다.

## 정리

verifier 는 `--session <name> close` 로 자기 세션만 닫는다. `close --all` 과 dev 서버 정리는 메인 루프 몫이다(전역 CLAUDE.md §실행 검증 의 포트 정리 절차) — verifier 는 이미 떠 있는 주소에 붙기만 하고, 서버를 띄우지도 죽이지도 않는다.
