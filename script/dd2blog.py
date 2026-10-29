#!/usr/bin/env python3
"""diagram-design 의 HTML 산출물에서 SVG 만 떼어 블로그 도식으로 바꾼다.

diagram-design 은 색을 SVG 안에 hex 로 박는다. 이 블로그는 반대로 색을
SCSS 가 테마 토큰으로 칠해야 다크모드 토글(body.dark-theme)에 따라온다.
그래서 hex 를 var(--...) 로 갈아끼운다 — 쓰이는 색은 6개뿐이다.
"""
import re
import sys
from pathlib import Path

# diagram-design 의 기본 스킨 → 이 블로그의 테마 토큰.
# 왼쪽은 style-guide.md 의 라이트/다크 기본값이다. 45종 예제 전체에서
# 쓰이는 색을 세어 만들었다 — 라이트와 다크 값이 같은 토큰으로 모인다.
COLOR = {
    # 면
    "#f5f5f5": "var(--bg)",            # paper (light)
    "#ffffff": "var(--bg)",            # 흰 면
    "#fff\\b": "var(--bg)",            # 3자리 축약형
    "#2d3142": "var(--fg)",            # ink (light) = paper (dark)
    "#393e53": "var(--bg-sunken)",     # paper-2 (dark)
    "#ececec": "var(--bg-sunken)",     # paper-2 (light)
    "#3d4460": "var(--bg-sunken)",     # 보조 면 (dark)
    "#4a5270": "var(--bg-sunken)",
    "#141414": "var(--bg)",
    "#221f1c": "var(--bg)",
    # 글자·선
    "#4f5d75": "var(--fg-subtle)",     # muted
    "#5a6580": "var(--fg-subtle)",     # soft
    "#949eb2": "var(--fg-subtle)",     # soft (dark)
    "#bfc0c0": "var(--border)",        # rule-solid
    "#9a9a9a": "var(--fg-subtle)",
    "#5c5c5c": "var(--fg-subtle)",
    "#111111": "var(--fg)",            # ink-strong
    # 강조
    "#bf4520": "var(--accent)",        # accent (light)
    "#f08a59": "var(--accent)",        # accent (dark)
    "#2e5aa8": "var(--accent)",        # link (light)
    "#739fdf": "var(--accent)",        # link (dark)
    "#82a0c0": "var(--accent)",
    "#5e7a9b": "var(--accent)",
    "#ff5a36": "var(--accent)",       # 터미널 변형의 강조
    "#6e6479": "var(--fg-subtle)",    # process 의 보조 글자
}

# 상태색(좋음·주의·위험)은 의미가 색 자체에 있으므로 테마 토큰으로 뭉개지
# 않는다. 대신 다크에서도 읽히는 값으로만 바꾼다 — 블로그 SCSS 가
# dg-hotfix 등에 쓰는 것과 같은 방식이다.
STATUS = {
    "#b85450": "#cf222e",   # 위험
    "#d97a78": "#f85149",   # 위험 (dark)
    "#b8915a": "#bf8700",   # 주의
    "#d3ad7a": "#d29922",   # 주의 (dark)
    "#7c8f6f": "#1a7f37",   # 좋음
    "#9caf8f": "#3fb950",   # 좋음 (dark)
    "#9c6b50": "#bc4c00",
}
# rgba(45,49,66,α) 처럼 ink 를 투명도로 쓴 것들.
# font 단축속성(font: 600 9px X)에서는 inherit 이 무효다 — 선언째 버려진다.
SANS = "system-ui, -apple-system, sans-serif"
RGBA_INK = re.compile(r"rgba\(45,\s*49,\s*66,\s*([\d.]+)\)")
RGBA_PAPER = re.compile(r"rgba\(245,\s*245,\s*245,\s*([\d.]+)\)")


def extract_svg(html: str) -> str:
    m = re.search(r"<svg\b.*?</svg>", html, re.S)
    if not m:
        raise SystemExit("SVG 를 찾지 못했다 — diagram-design 산출물이 맞는지 본다")
    svg = m.group(0)

    # 글자 크기는 페이지 <style> 의 클래스에 있다. SVG 만 떼면 그게 빠져
    # 본문 17px 을 물려받아 글자가 상자를 뚫는다 — 그래서 같이 가져온다.
    css = "\n".join(re.findall(r"<style>(.*?)</style>", html, re.S))
    rules = [r.strip() for r in re.findall(r"\.[-\w][^{}]*\{[^{}]*\}", css)
             if re.search(r"fill|font|stroke|text-anchor|letter-spacing", r)]
    # body·h1 같은 페이지 레이아웃 규칙은 빼고 도형 규칙만 남긴다.
    rules = [r for r in rules if not re.match(r"\.(frame|eyebrow|legend-row|caption)\b", r)]
    if rules:
        style = "<style>\n" + "\n".join(rules) + "\n</style>"
        svg = re.sub(r"(<svg\b[^>]*>)", r"\1\n" + style, svg, count=1)
    return svg


def retheme(svg: str, page_css: str = "") -> tuple[str, list[str]]:
    """hex 를 테마 토큰으로 바꾸고, 못 바꾼 색을 같이 돌려준다."""
    out = svg

    # 일부 타입은 :root 에 자기만의 변수를 정의한다(--zone-fill 등).
    # 그 값을 먼저 펼쳐야 아래 hex 치환이 걸린다.
    root = re.search(r":root\s*\{([^}]*)\}", page_css, re.S)
    if root:
        local = dict(re.findall(r"(--[-\w]+)\s*:\s*([^;]+);", root.group(1)))
        for _ in range(3):  # 변수가 변수를 가리키는 경우가 있다
            for name, val in local.items():
                out = out.replace(f"var({name})", val.strip())
    # ink/paper 를 투명도와 함께 쓴 것은 color-mix 로 옮긴다.
    out = RGBA_INK.sub(
        lambda m: f"color-mix(in srgb, var(--fg) {float(m.group(1))*100:.0f}%, transparent)",
        out)
    out = RGBA_PAPER.sub(
        lambda m: f"color-mix(in srgb, var(--bg) {float(m.group(1))*100:.0f}%, transparent)",
        out)
    for hex_, token in {**COLOR, **STATUS}.items():
        out = re.sub(hex_, token, out, flags=re.I)

    # 가져온 CSS 가 쓰는 diagram-design 변수명을 블로그 토큰으로 잇는다.
    VAR = {
        "--paper-2": "--bg-sunken", "--paper": "--bg",
        "--ink-strong": "--fg", "--ink": "--fg",
        "--muted": "--fg-subtle", "--soft": "--fg-subtle",
        "--rule-solid": "--border", "--rule": "--border",
        "--accent-tint": "--accent", "--accent": "--accent",
        "--link": "--accent",
    }
    for src, dst in VAR.items():  # 긴 이름이 먼저 — --ink 가 --ink-strong 을 먹지 않게
        out = re.sub(rf"var\({src}\)", f"var({dst})", out)
    # 폰트 변수는 실제 폰트 스택으로 푼다.
    out = re.sub(r"var\(--mono\)", "ui-monospace, SFMono-Regular, Menlo, monospace", out)
    out = re.sub(r"var\(--serif\)", "Georgia, 'Times New Roman', serif", out)
    out = re.sub(r"var\(--sans\)", SANS, out)

    # 폰트는 블로그 본문을 물려받는다. diagram-design 은 Google Fonts 를
    # 전제하는데 인라인 SVG 로 들어오면 그 <link> 가 없다.
    out = re.sub(r"'Geist Mono', ?ui-monospace, ?monospace",
                 "ui-monospace, SFMono-Regular, Menlo, monospace", out)
    out = re.sub(r"'Instrument Serif', ?serif",
                 "Georgia, 'Times New Roman', serif", out)
    out = re.sub(r"'Geist', ?system-ui, ?sans-serif", SANS, out)

    # 상태색은 일부러 hex 로 남긴 것이므로 경고 대상이 아니다.
    intended = {v.lower() for v in STATUS.values()}
    leftover = sorted({h for h in re.findall(r"#[0-9a-fA-F]{3,6}", out)
                       if h.lower() not in intended})
    return out, leftover


def main():
    if len(sys.argv) != 3:
        raise SystemExit("usage: dd2blog.py <in.html> <out.svg>")
    src, dst = Path(sys.argv[1]), Path(sys.argv[2])
    html = src.read_text(encoding="utf-8")
    svg, leftover = retheme(extract_svg(html), html)
    # 폭은 블로그가 CSS 로 잡는다 — 고정 width/height 를 뗀다.
    svg = re.sub(r'\s(width|height)="[^"]*"', "", svg, count=2)
    dst.write_text(svg + "\n", encoding="utf-8")
    print(f"wrote {dst}")
    if leftover:
        print(f"⚠️  토큰으로 못 바꾼 색 {len(leftover)}개: {leftover}")
    else:
        print("남은 hex 없음 — 다크모드 따라감")


if __name__ == "__main__":
    main()
