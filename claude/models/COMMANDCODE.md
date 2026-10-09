# CommandCode 위임 실행 런북 (DeepSeek Flash)

`cmdc`(Command Code, 전역 PATH) 고유 사항만 다룬다. 브리프 작성·전달·재개·검증 신뢰는 `DELEGATION.md`, 관측 경위는 `investigation/CLI_DELEGATION_OBSERVATIONS.md`.

## 호출

```bash
cd <작업-레포-루트> && cmdc -p \
  "docs/plan/briefs/<작업명>.md 를 읽고 그대로 수행할 것. 레포 루트 CLAUDE.md 의 규칙도 함께 지킬 것. 브리프를 읽은 직후 <가장 먼저 만들/고칠 파일> 편집부터 시작하고, 편집 없이 종료하지 말 것." \
  -m deepseek/deepseek-v4.1-flash --effort high --max-turns 300 \
  -n "<고유 세션명>" -t --skip-onboarding --no-auto-update --yolo
```

- **모델**: `-m deepseek/deepseek-v4.1-flash` 만 쓴다(목록은 `cmdc --list-models`).
- **`--effort`**: `high`(기본) / `max`(상위). CLI 가 받는 값은 `low`·`high`·`max` 뿐이고 그 밖의 값은 `Unknown effort` 로 즉시 실패한다.
- **`--max-turns 300` 을 매 호출에 명시한다.** 기본값 100 은 구현 위임을 완주시키지 못하고(초과 시 exit 8, 대개 테스트 작성 같은 뒷부분이 남는다), 설정 파일·`--config` 로는 바꿀 수 없다.
- **`-n` 세션명은 고유하게** 붙인다 — 재개(`-r <name>`)와 프로세스 특정이 이름으로 선다.
- `-t`(프로젝트 신뢰 프롬프트 생략)·`--skip-onboarding`·`--no-auto-update`(런 도중 바이너리가 교체되면 후속 호출이 `No such file` 로 실패한다)·`--yolo`(→ §권한) 를 붙인다.
- **병렬 런은 기동 시점을 몇 초 이상 어긋나게 띄운다.** 같은 순간 기동하면 `--effort` 를 전역 설정에 쓰는 구간이 충돌해 늦은 쪽이 `EPERM … config.json` 으로 즉사한다. 이 실패는 기동 즉시 exit 1 이고 트리에 흔적이 없으므로, 나머지가 기동을 마친 뒤 죽은 런만 다시 띄운다.
- 결과는 기본으로 최종 메시지만 stdout 에 나온다. 도구 호출 로그·토큰은 `--output-format json`(NDJSON, 마지막 `{"type":"result",…}` 줄에 `usage`·`finalText`). 장시간 런은 Bash `run_in_background`.
- 비-TTY 에서 stdin 을 기다리지 않는다(`< /dev/null` 불요). 세션 이어가기는 `-r <name|id>`, 전사본은 `~/.commandcode/projects/<cwd-slug>/<id>.jsonl`. 실행 위치가 워크스페이스이고 추가 경로는 `--add-dir`.

## 권한 (print 모드)

`-p` 는 `--yolo` 없이는 쓰기 도구(`write_file`·`edit_file`)와 비-읽기 셸을 열지 않는다. 다른 permission mode·allow 규칙으로도 열리지 않고, 모델이 셸로 우회해 반쯤 열린 런이 되므로 처음부터 `--yolo` 로 띄운다.

- **안전장치는 deny 규칙이다** — `--yolo` 아래서도 듣는다. 위치는 `~/.commandcode/settings.json`:

```json
{ "permissions": { "deny": [
  "Shell(git stash:*)", "Shell(git push:*)", "Shell(git worktree:*)", "Shell(git branch:*)",
  "Shell(git checkout:*)", "Shell(git switch:*)", "Shell(git reset:*)" ] } }
```

- 워크스페이스 밖 쓰기는 `--yolo` 에서도 비대화형이면 실패한다 — 산출물·임시 파일은 워크스페이스 안에 둔다.
- 신뢰 레포에서 메인 루프가 브리프와 결과 diff 를 감독하므로 `--yolo` 를 허용한다.
- **Claude auto 모드의 분류기는 `--yolo` 를 막는다.** `~/.claude/settings.json` 의 `Bash(cmdc:*)`·`Bash(timeout * cmdc *)` 허용 규칙이 분류기보다 먼저 적용되므로, 호출은 `cmdc` 로 시작하는 형태(`cd <레포> && cmdc …` 또는 `timeout <s> cmdc …`)를 유지한다.

## 셸 환경

cmdc 런의 셸은 `NODE_ENV=production` 을 설정한다. 그대로 두면 Node 테스트 러너(vitest 등)가 환경 탓으로 실패한다 — 편집 결함으로 읽지 않는다. 브리프의 Node 검증 명령에는 `NODE_ENV` 를 비우는 두 형태를 함께 적는다(cmd 인용이 깨지는 경우가 있다):

```
set "NODE_ENV=" && npm test
$env:NODE_ENV = $null; npm test      # PowerShell
```

## 진행 확인

- 프로세스는 `Get-CimInstance Win32_Process -Filter "name='node.exe'"` 의 `CommandLine` 에서 `-n <세션명>` 으로 특정하고, 그 PID 만 `taskkill //PID <pid> //T //F` 한다.
- 편집 여부는 대상 파일 mtime 으로 본다(`DELEGATION.md` §편집 없이 끝나는 런). 편집 없이 끝난 런은 전사본 `.jsonl` 의 마지막 assistant 메시지에 tool 호출이 없는지로 확증한다.
