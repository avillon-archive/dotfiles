# OpenCode·CommandCode 위임 실측 기록

런북(`OPENCODE.md`·`COMMANDCODE.md`·`DELEGATION.md`)의 제약이 어디서 나왔는지의 기록이다. 런북은 제약만 갖고, 관측 경위·수치·시점은 여기에 둔다.

## 공통 (DELEGATION.md)

- **읽을 문서 지목**: 테스트 설계 규칙이 레포 권위 문서에 있는데도 브리프 본문에 "CLAUDE.md 도 지킬 것" 을 산문으로만 적은 위임 런이 구현 가정대로 fixture 를 만든 일이 두 번 재발했다 → `## 읽을 문서` 블록 형식을 필수 조항으로 둠.
- **실물 입력 스모크**: 유닛 테스트가 초록인데 실데이터 적용 건수가 0 인 파서 위임이 있었다 → 합격선을 실물 입력 1건 변환으로 둠.

## OpenCode

- **동시 기동 충돌**: 4 런을 같은 순간에 띄우자 1 런이 `database is locked` 로 즉시 exit 1. 기동 사이 ~6s 간격으로 재발 없음.
- **편집 없이 끝나는 런**: 큰 산출물을 "append 로 쪼개 쓰라" 지시로 25 런 중 22 런이 한 번에 완료. 끊긴 3 런은 전부 입력 1,300 줄 이상을 통째로 읽은 뒤 첫 쓰기에 닿은 경우.
- **세션 행 생성 지연**: `opencode session list` 의 행이 기동 34분 뒤에 생긴 사례.

## CommandCode (cmdc)

- **effort 값** (2026-09-10): DeepSeek Flash 는 `low`·`high`·`max` 만 받고 `medium` 은 `Unknown effort` 로 즉시 실패.
- **자동 업데이트** (2026-09-03, 1.40.1→1.43.0): 런 도중 바이너리가 교체되며 `cmdc` 가 PATH 에서 사라져 후속 호출이 `No such file` 로 실패.
- **`--max-turns`** (2026-09-04, v1.43.0): 기본 100 에서 모듈 신설 + 결함 9건 수정 위임이 편집을 마치고 테스트 7건을 남긴 채 exit 8. `~/.commandcode/config.json` 키가 아니고 `--config maxTurns=300` 은 `Unknown config setting` 으로 거부.
- **동시 기동 EPERM** (2026-09-05, v1.43.0): 같은 순간 기동한 런 중 늦은 쪽이 `--effort` 를 전역 설정에 쓰는 구간의 rename 충돌로 `EPERM … config.json` 사망. 몇 초 간격이면 공존(같은 날 재실측). 2026-09-11 에는 응답마다 하나씩 띄운 세 런 중 첫 런이 같은 EPERM 으로 죽었고, 나머지 기동 완료 뒤 단독 재기동으로 성공.
- **print 모드 권한** (2026-09-03, v1.40.1·1.43.0): `--yolo` 없이는 `write_file`·`edit_file` 이 `Tool "write_file" requires permissions. Use --yolo …` 로 거부되고, `--permission-mode auto-accept`·`dont-ask`·allow 규칙으로도 열리지 않음. 모델이 PowerShell 로 우회해 파일을 쓴 런이 있었음. deny 규칙은 `--yolo` 아래서도 `git stash` 를 거부.
- **`NODE_ENV=production`** (2026-09-10): cmdc 셸에서 vitest 여러 suite 가 `No such built-in module: node:` 로 실패, `set "NODE_ENV=" && npm test` 로 통과. 2026-09-30 에는 그 형태의 인용이 깨져 전 suite 가 `TypeError: Cannot read properties of undefined (reading 'config')` 로 죽었고 PowerShell `$env:NODE_ENV = $null; npm test` 로 통과.
