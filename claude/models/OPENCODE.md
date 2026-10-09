# OpenCode 위임 실행 런북 (DeepSeek Flash · Muse Spark)

`opencode`(전역 PATH) 고유 사항만 다룬다. 브리프 작성·전달·재개·검증 신뢰는 `DELEGATION.md`, 관측 경위는 `investigation/CLI_DELEGATION_OBSERVATIONS.md`.

## 호출

```bash
cd <작업-레포-루트> && opencode run \
  -m opencode-go/deepseek-v4.1-flash \
  --variant high \
  --title "<고유 세션 제목>" \
  "docs/plan/briefs/<작업명>.md 를 읽고 그대로 수행할 것. 레포 루트 CLAUDE.md 의 규칙도 함께 지킬 것. 브리프를 읽은 직후 <가장 먼저 만들/고칠 파일> 편집부터 시작하고, 편집 없이 종료하지 말 것."
```

- **variant 값 집합은 모델마다 다르고, 미지원 값은 오류 없이 무시된 채 기본값으로 돈다.** 표에 없는 모델은 `~/.cache/opencode/models.json` 의 `reasoning_options` 로 먼저 확인한다.
- **`--title` 은 고유하게 붙인다.** 같은 워킹 트리에서 다른 세션의 런이 동시에 돌므로 진행 판정·프로세스 특정은 제목으로만 한다(§진행 확인).
- 작업 디렉토리는 `cd` 또는 `--dir <path>` — 실행 디렉토리가 곧 워크스페이스다.
- 결과는 기본 출력(툴 호출 로그 + 최종 메시지)을 읽는다. 구조적 파싱은 `--format json`(`type:"text"` = 발화, `step_finish` = 토큰·비용). 장시간 런은 Bash `run_in_background`.
- 비-TTY 에서 stdin 을 기다리지 않는다(`< /dev/null` 불요). 세션 이어가기는 `-s <sessionID>`(동시 세션이 있으면 `-c` 로 추정하지 않는다).
- **병렬 런은 기동 사이에 ~6s 간격을 둔다.** 같은 순간에 띄우면 세션 DB 생성이 겹쳐 `database is locked` 로 즉시 죽는다. 동시 수는 감독 가능한 3~4 런으로 제한한다.

## 모델

`-m` 에는 아래 ID 를 그대로 쓴다. 같은 모델의 다른 제공자 경로로 바꾸지 않는다.

| 모델 | ID | variant (기본 / 상위) |
|---|---|---|
| DeepSeek Flash | `opencode-go/deepseek-v4.1-flash` | `high` / `max` |
| Muse Spark | `opencode-go/muse-spark-1.3-contributor` | `high` / `xhigh` |
| Muse Spark **Free** | `opencode/muse-spark-1.3-contributor-free` | `high` / `xhigh` |

- 제공자 목록에 없는 ID 는 `UnknownError / Unexpected server error` 로 즉시 실패한다(로그에 모델명도 남지 않는다). 이 오류가 나면 `opencode models <provider>` 부터 본다.
- 표에 없는 모델은 텍스트 응답 1회 + 도구 호출(Read→Write) 1회로 도달·편집 가능 여부를 확인한 뒤 쓴다.

## 권한 (비대화형)

비대화형 `opencode run` 은 `ask` 권한을 자동 거부한다(`permission requested: …; auto-rejecting` — 그 호출만 실패하고 런은 계속). 검증 단계에서 걸리면 검증이 누락된 채 끝날 수 있다.

- 허용: 워크스페이스 내부 편집·셸 실행, `%LOCALAPPDATA%\Temp\opencode\**` 쓰기(`~/.config/opencode/opencode.jsonc` 의 `external_directory` 예외 — 브리프 §임시 파일 에 추가 허용 경로로 적는다).
- 거부: 그 밖의 워크스페이스 외부 쓰기(타 레포·Claude 스크래치패드 포함). `--auto`·`external_directory` 확대는 쓰지 않는다.

## 편집 없이 끝나는 런 — 확증·재개

판정·재개 원칙은 `DELEGATION.md` §편집 없이 끝나는 런. 대형 입력을 통째로 읽은 뒤 첫 쓰기에 닿는 런이 가장 잘 끊긴다.

- **확증**: `opencode export <sessionID>` 의 마지막 assistant 메시지가 `finish = "unknown"` 이고 parts 가 `step-start,reasoning,step-finish` 뿐이면(tool·text 없음) 이 실패다. 정상 진행은 `finish = "tool-calls"` 와 `tool` part 가 있다.

```bash
opencode export <sessionID> | node -e "let s='';process.stdin.on('data',d=>s+=d).on('end',()=>{const d=JSON.parse(s.slice(s.indexOf('{')));for(const m of d.messages){const i=m.info||m;if(i.role!=='assistant')continue;console.log(i.finish,'|',(m.parts||[]).map(p=>p.type).join(','));}})"
```

```bash
opencode session list                     # 세션 ID·제목·갱신 시각
opencode run -s <sessionID> -m <provider>/<model> --variant high \
  "읽기는 충분하다. 파일을 더 읽지 말고 곧바로 <파일 A> 를 만들고 <파일 B> 를 고쳐라. 남은 항목: (1) … (2) …. 편집 없이 종료하는 것은 실패다."
```

- 같은 세션이 배너만 찍고 종료하면 죽은 세션이다 — 새 세션으로 시작한다.

## 진행 확인 (멈춤 판별)

백그라운드 런은 완료 전까지 출력이 0B 라 출력 크기는 진행 신호가 아니다. 로그로 본다.

```bash
# 런별 첫/마지막 타임스탬프·라인 수·stream 횟수·cwd 집계
node -e "
const fs=require('fs');
const p=process.env.USERPROFILE+'/.local/share/opencode/log/opencode.log';
const runs={};
for(const l of fs.readFileSync(p,'utf-8').split(/\r?\n/)){
  const m=l.match(/timestamp=(\S+).*run=([a-f0-9]+)/); if(!m) continue;
  const r=m[2]; runs[r]=runs[r]||{first:m[1],last:m[1],n:0,cwd:new Set(),stream:0};
  runs[r].last=m[1]; runs[r].n++;
  if(l.includes('message=stream')) runs[r].stream++;
  const c=l.match(/cwd=\"([^\"]+)\"/); if(c) runs[r].cwd.add(c[1]);
}
for(const [r,v] of Object.entries(runs)) if(v.last>='<ISO 하한>')
  console.log(r,v.first,v.last,'lines',v.n,'streams',v.stream,[...v.cwd].join('|'));"
```

- 정상이면 `message=loop`·`message=stream` 이 쌓인다. `init` 이후 `cleanup prune=7.days` 틱만 있고 `loop`·`stream` 이 0 이면 멈춘 것이다.
- 로그 타임스탬프는 UTC, 파일 mtime·`date` 는 로컬 시각이다 — 비교 전에 맞춘다.
- **귀속은 `--title` 로만 한다.** `cwd` 는 같은 트리를 여러 세션이 쓰므로 근거가 아니다. 1차 수단은 `opencode session list`(제목·마지막 갱신)이지만 세션 행은 런 시작보다 한참 늦게 생길 수 있다 — 행이 없다는 것은 아직 아무것도 내지 않았다는 뜻이지 죽었다는 뜻이 아니다.
- 편집 여부는 대상 파일 mtime 으로 본다(`git status` 의 `M` 은 이전 미커밋 변경일 수 있다). 편집 시각이 이번 런의 프로세스 생성보다 앞서면 이번 런의 편집이 아니다.
- **`stream` 이 0 인 채 수십 분 무응답이면 죽은 런이다.** 명령줄의 `--title` 로 PID 를 확인한 뒤 그 런만 죽인다.

```bash
powershell -NoProfile -Command "Get-CimInstance Win32_Process -Filter \"name='opencode.exe'\" | Select-Object ProcessId,CommandLine | Format-List"
taskkill //PID <pid> //T //F        # --title 로 확인한 PID 만
```
