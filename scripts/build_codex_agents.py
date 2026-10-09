# -*- coding: utf-8 -*-
"""codex/AGENTS.md 를 common/GUIDELINES.md + codex/AGENTS.local.md 로 생성한다.

Codex 는 AGENTS.md 안의 @import 를 해석하지 않으므로 공통 규율을 파일 결합으로 싣는다.
--check: 생성물이 원본과 어긋나면 exit 1 (pre-commit 훅이 쓴다).
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCES = [ROOT / "common" / "GUIDELINES.md", ROOT / "codex" / "AGENTS.local.md"]
OUTPUT = ROOT / "codex" / "AGENTS.md"
BANNER = (
    "> 생성 파일이다. 편집은 `~/dotfiles/common/GUIDELINES.md`·`~/dotfiles/codex/AGENTS.local.md` 에서 하고 "
    "`python ~/dotfiles/scripts/build_codex_agents.py` 로 다시 생성한다.\n"
)


def render() -> str:
    parts = [p.read_text(encoding="utf-8").replace("\r\n", "\n").strip() for p in SOURCES]
    return BANNER + "\n" + "\n\n".join(parts) + "\n"


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    text = render()
    if "--check" in sys.argv[1:]:
        current = OUTPUT.read_text(encoding="utf-8").replace("\r\n", "\n") if OUTPUT.exists() else ""
        if current != text:
            print(f"{OUTPUT.relative_to(ROOT)} 가 원본과 다르다 — scripts/build_codex_agents.py 를 실행한다.")
            return 1
        return 0
    OUTPUT.write_text(text, encoding="utf-8", newline="\n")
    print(f"wrote {OUTPUT.relative_to(ROOT)} ({len(text.encode('utf-8'))} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
