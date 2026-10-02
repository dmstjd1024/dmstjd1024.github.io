#!/usr/bin/env python3
"""글의 프론트매터를 검사한다. 하나라도 걸리면 종료 코드 1 로 빌드를 세운다.

왜 있나 — `description` 이 빠지면 jekyll-seo-tag 가 본문 첫 덩어리를 가져가,
검색 결과 설명이 `"한 줄로"` 같은 H2 토막이 된다. 눈에 띄지 않아 오래 간다
(실측 2026-10: 122편이 그 상태였다).

규칙 문서와 체크리스트로 두 번 막아 봤지만 재발했다 — 규칙 추가 13시간 뒤에
쓴 글이 또 비어 있었다. 사람이 기억해야 하는 검사는 언젠가 빠진다.

검사 대상은 `_pages/` 의 글이다. `index.md` 는 카테고리 목록 페이지라
프론트매터에 title 도 없고 description 도 필요 없으므로 제외한다.
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGES = ROOT / "_pages"

# description 이 이 값이면 본문 H2 가 새어 들어온 것으로 본다.
# 실제로 스니펫에 나갔던 값들이다.
LEAKED = {"한 줄로", "문제의 코드", "결론부터", "정리"}


def front_matter(text):
    """--- 로 감싼 첫 덩어리를 돌려준다. 없으면 None."""
    m = re.match(r"^---\n(.*?)\n---", text, re.S)
    return m.group(1) if m else None


def field(fm, key):
    m = re.search(rf"^{key}:\s*(.+)$", fm, re.M)
    return m.group(1).strip().strip("\"'") if m else None


def main():
    problems = []
    checked = 0

    for path in sorted(PAGES.rglob("*.md")):
        if path.name == "index.md":
            continue

        rel = path.relative_to(ROOT)
        fm = front_matter(path.read_text(encoding="utf-8", errors="replace"))
        if fm is None:
            problems.append((rel, "프론트매터(--- 블록)가 없다"))
            continue

        checked += 1
        desc = field(fm, "description")

        if not desc:
            problems.append((rel, "description 이 없다 — subtitle 과 같은 값을 넣는다"))
        elif desc in LEAKED:
            problems.append((rel, f'description 이 본문 H2 토막이다 — "{desc}"'))

        if not field(fm, "title"):
            problems.append((rel, "title 이 없다"))

    if problems:
        print(f"프론트매터 검사: {len(problems)}건 걸림 (글 {checked}편 검사)\n", file=sys.stderr)
        for rel, why in problems:
            print(f"  {rel}\n      {why}", file=sys.stderr)
        print(
            "\n규칙은 .claude/skills/blog-post/references/frontmatter.md 에 있다.",
            file=sys.stderr,
        )
        return 1

    print(f"프론트매터 검사: 글 {checked}편 이상 없음")
    return 0


if __name__ == "__main__":
    sys.exit(main())
