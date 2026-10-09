# Antigravity 위임 실행 런북 (Gemini 3.6 Flash)

시각 검증을 agy(Gemini)로 실행하는 절차다. 사용 조건은 `~/.claude/rules/local.md` §시각 검증 구동, 브리프 형식·판정 규약은 `~/dotfiles/common/VISUAL_VERIFICATION.md` 가 갖는다. 대상 CLI: `agy`(전역 PATH).

## 호출

```bash
cd <작업-레포-루트> && agy -p "<검증 브리프>" \
  --model <모델ID> \
  --output-format json
```

- `-p` 는 단발 실행이고 기본 `--print-timeout` 은 5m 다. 멀티스텝 브라우저 검증은 `--print-timeout 15m` 등으로 늘리고 Bash `run_in_background` 로 띄운다.
- 모델 ID 에 effort 가 붙어 있다(`agy models` 로 확인). Pro 계열은 무료 플랜 한도상 쓰지 않는다.

| 대상 | 모델 ID |
|---|---|
| 단순 체크리스트(요소 존재·가시성·overflow·단일 뷰포트) | `gemini-3.6-flash-low` |
| 기본 검증(상대 위치·반응형 비교·멀티스텝 흐름) | `gemini-3.6-flash-medium` (어려우면 `-high`) |

- UNCERTAIN·증거 충돌·주관 품질·루브릭 없는 레퍼런스 비교는 GPT-6 Luna(`CODEX.md`)로 넘긴다.
- 판정 스키마를 강제하려면 `--json-schema '<schema.json 경로>'`(print 모드 최종 결과에 적용).
- 실행 위치가 워크스페이스이고 추가 경로는 `--add-dir`(반복 가능). trust 설정이 없는 레포에서 처음 쓸 때는 사용자에게 trust 설정을 요청한다.
- 순수 텍스트 응답은 권한 플래그가 필요 없다. 브라우저 도구가 승인 프롬프트에서 멈추면 `--dangerously-skip-permissions` 를 쓰고 브리프에 비가역 행동 금지를 적는다.

## Rate-limit (무료 플랜)

- 호출 수를 줄이는 것이 1차 대응이다 — 체크를 한 브리프에 묶고, 뷰포트별 분리가 필요하면 순차 호출 사이에 간격을 둔다.
- 한도 오류는 60초 이상 기다린 뒤 1회만 재시도한다. 그래도 막히면 GPT-6 Luna(codex, `high`)로 넘기고 보고에 그 사실을 적는다.

## 브리프

- 자립적으로 쓴다: URL·뷰포트·사전 조건·체크별 관찰 가능한 assertion·요구 증거(스크린샷 + DOM/bbox)·판정 3값(PASS/FAIL/UNCERTAIN).
- 증거가 부족하면 PASS 대신 UNCERTAIN 을 반환하라고 적는다 — false PASS 방지가 최우선이다.
- 검증 전용 위임이다 — 파일 수정·커밋을 지시하지 않는다.
