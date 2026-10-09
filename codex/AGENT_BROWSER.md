# agent-browser 실행

agent-browser를 실제 실행할 때만 읽는다. 브라우저 작업 절차는 해당 스킬을 따르고, 위임·checkout 정책은 현재 사용자·프로젝트 지침을 따른다.

- **agent-browser 영구 승인 호출 형식**: `agent-browser`는 사용자 `PATH`에 등록되어 있고 `~/.codex/rules/default.rules`에서 명령 prefix가 영구 허용되어 있다. 샌드박스 밖 실행은 `agent-browser <args>`를 단일 명령 segment로 직접 호출한다. `powershell.exe -Command`, `& '...\\agent-browser.ps1'`, 여러 호출을 `;`로 결합한 wrapper는 명령 전체가 별도 승인 대상으로 분류되므로 사용하지 않는다. 기존 허용 규칙과 사용자의 명시 지시가 있으면 같은 승인을 다시 요청하지 않는다.
