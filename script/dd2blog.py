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
    # 잉크 계열 보조 면이다. 배경 토큰으로 보내면 그 위에 파낸 흰 글자가
    # 다크에서 같이 어두워져 사라진다 — high-level 의 단계 띠가 그랬다.
    "#3d4460": "var(--fg-subtle)",
    "#4a5270": "var(--fg-subtle)",
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
    "#b88670": "var(--accent)",       # dp-integration 다크의 --custom-red
    "#5e7a9b": "var(--accent)",
    "#ff5a36": "var(--accent)",       # 터미널 변형의 강조
    "#6e6479": "var(--fg-subtle)",    # process 의 보조 글자
    "#8e8c83": "var(--fg-subtle)",    # 따뜻한 회색 변형의 선·보조 글자
    "#96928a": "var(--fg-subtle)",
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
RGBA = re.compile(r"rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*(?:,\s*([\d.]+)\s*)?\)")
# 색을 hex 로만 찾으면 CSS 키워드를 놓친다. 노드 상자 11개가 fill="white"
# 였고, 그래서 다크모드에서 흰 상자 위에 흰 글자가 됐다 — 실측 2026-10-29.
KEYWORD = {"white": "var(--bg)", "black": "var(--fg)"}


def extract_svg(html: str) -> str:
    start = re.search(r"<svg\b", html)
    if not start:
        raise SystemExit("SVG 를 찾지 못했다 — diagram-design 산출물이 맞는지 본다")
    # 도형 안에 아이콘용 <svg> 가 중첩돼 있다. 첫 </svg> 에서 끊으면
    # 그 뒤가 전부 날아가므로 여닫는 수를 세어 짝을 맞춘다.
    depth, pos = 0, start.start()
    for m in re.finditer(r"<svg\b|</svg\s*>", html[start.start():]):
        depth += 1 if m.group(0).startswith("<svg") else -1
        if depth == 0:
            pos = start.start() + m.end()
            break
    else:
        raise SystemExit("</svg> 짝이 맞지 않는다")
    svg = html[start.start():pos]

    # XML 주석 안에서는 '--' 가 금지다. 본문에 var(--fg) 를 적어둔 주석이 있다.
    svg = re.sub(r"<!--.*?-->", "", svg, flags=re.S)

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


# diagram-design 이 자기 verify-geometry.py 용으로 남기는 표시다. 값 없는
# 속성(data-box 처럼)은 HTML 에서는 되지만 XML 로는 깨진다 — 브라우저는
# 인라인 SVG 를 HTML 파서로 읽어 그려지긴 하지만, XML 로 읽는 도구가
# 걸린다. 렌더링에 쓰이지 않으므로 떼어낸다.
BOOL_ATTR = re.compile(r"\s(data-[a-z0-9-]+)(?=[\s>/])")


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
    # 같은 색이 hex 와 rgba() 두 꼴로 쓰이고, 투명도는 제각각이다. 꼴마다
    # 규칙을 두는 대신 rgb 값을 hex 로 되돌려 같은 표에서 찾는다.
    def rgba_to_token(m):
        hex_ = "#{:02x}{:02x}{:02x}".format(*(int(m.group(i)) for i in (1, 2, 3)))
        token = {**COLOR, **STATUS}.get(hex_)
        if not token:
            return m.group(0)
        alpha = float(m.group(4)) if m.group(4) is not None else 1.0
        if alpha >= 1.0:
            return token
        return f"color-mix(in srgb, {token} {alpha * 100:.0f}%, transparent)"

    out = RGBA.sub(rgba_to_token, out)
    # fill="white" 같은 키워드는 속성·CSS 값 자리에서만 바꾼다.
    for word, token in KEYWORD.items():
        out = re.sub(rf'(?<=[:"\s]){word}(?=[;"\s])', token, out)
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
    # hex 만 세면 white·rgba() 가 빠져나간다 — 그게 다크모드를 깨뜨린 경로다.
    leftover += sorted(set(re.findall(r'(?<=[:"\s])(?:white|black)(?=[;"\s])', out)))
    leftover += sorted(set(re.findall(r"rgba?\([^)]*\)", out)))
    return out, leftover


def selfcheck():
    """실제로 깨졌던 세 가지가 다시 깨지지 않는지 본다.

    색이 안 남았다는 것만으로는 부족했다 — 아이콘 <svg> 중첩 때문에 그림이
    잘려도, 흰 상자 위 흰 글자가 돼도 '남은 hex 0개' 는 그대로였다.
    """
    import xml.etree.ElementTree as ET

    # 1) 중첩 <svg> 에서 첫 </svg> 로 끊지 않는다
    nested = '<svg a="1"><g><svg><path/></svg></g><text>끝</text></svg>'
    assert extract_svg(nested).endswith("</svg>"), "중첩 svg 를 잘랐다"
    assert "끝" in extract_svg(nested), "중첩 svg 뒤를 잃었다"

    # 2) 색은 hex 가 아닌 꼴로도 온다
    got, _ = retheme('<svg><rect fill="white"/><rect fill="rgba(191,69,32,0.1)"/></svg>')
    assert 'fill="var(--bg)"' in got, "white 키워드를 못 바꿨다"
    assert "var(--accent) 10%" in got, "rgba 강조색을 못 바꿨다"

    # 3) 값 없는 속성을 떼야 XML 로 읽힌다
    ET.fromstring(BOOL_ATTR.sub("", '<svg><g data-box data-focal/></svg>'))
    print("selfcheck ok")


def main():
    if len(sys.argv) == 2 and sys.argv[1] == "--selfcheck":
        return selfcheck()
    if len(sys.argv) != 3:
        raise SystemExit("usage: dd2blog.py <in.html> <out.svg>")
    src, dst = Path(sys.argv[1]), Path(sys.argv[2])
    html = src.read_text(encoding="utf-8")
    svg, leftover = retheme(extract_svg(html), html)
    # 폭은 블로그가 CSS 로 잡는다 — 고정 width/height 를 뗀다.
    svg = re.sub(r'\s(width|height)="[^"]*"', "", svg, count=2)
    svg = BOOL_ATTR.sub("", svg)
    dst.write_text(svg + "\n", encoding="utf-8")
    print(f"wrote {dst}")
    if leftover:
        print(f"⚠️  토큰으로 못 바꾼 색 {len(leftover)}개: {leftover}")
    else:
        print("남은 hex 없음 — 다크모드 따라감")


if __name__ == "__main__":
    main()
