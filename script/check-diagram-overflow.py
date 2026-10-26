#!/usr/bin/env python3
"""도식에서 상자 밖으로 넘친 글자를 브라우저로 재서 찾는다.

왜 브라우저인가 — 글자 폭은 소스를 읽어서 알 수 없다. 글자 수로 추정해 봤더니
146건이 걸렸고 그중 절반이 거짓 양성이었다 (실측 2026-10-26). 폰트가 실제로
그린 폭은 `getBBox()` 만 안다. 같은 날 실측으로 다시 세면 48건이었다.

제외 규칙 두 가지가 있다. 둘 다 빼지 않으면 결과가 거짓 양성으로 덮인다:

- `dg-zone` / `dg-lane` — 묶음 영역이다. 라벨이 테두리 위로 걸쳐 나오는 것이
  설계다. 넘침이 아니다.
- `dg-mask` — 선을 가리는 배경이다. 글자보다 좁아도 된다.

그리고 **이 스크립트가 통과한 것이 도식이 멀쩡하다는 뜻은 아니다.** 1위로
올라온 넘침 101px 은 상자 안 글자가 아니라 화살표 옆 라벨이었다. 상자에
속한다고 짝지은 것 자체가 틀렸고, 그건 스크린샷을 봐야 보인다. 이 검사는
후보를 좁히는 도구이고 판정은 눈이 한다.

쓰는 법 — jekyll 서버를 띄운 뒤 실행한다:

    bundle exec jekyll serve --port 4000 &
    python3 script/check-diagram-overflow.py --base http://127.0.0.1:4000

`--min` 으로 문턱을 올린다 (기본 10px — 그 아래는 눈에 띄지 않는다).
"""
import argparse
import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = ROOT / "_site"

# taskSpace() / console 은 ego-browser 런타임이 전역으로 넣어준다.
# `require('ego-browser')` 같은 모듈은 없고, top-level await 을 쓴다.
# URL 목록은 소스에 박아 넣는다 - ego 가 nodejs 를 별도 프로세스로 띄우므로
# 환경변수(`process.env`)로는 건너가지 않는다.
MEASURE_JS = r"""
const urls = __DG_URLS__;
const task = await taskSpace("diagram overflow check");
const page = await task.newPage();
const all = [];
try {
  for (const url of urls) {
    await page.goto(url);
    const hits = await page.evaluate(() => {
      const out = [];
      document.querySelectorAll('.diagram svg').forEach((svg, si) => {
        const vb = svg.viewBox.baseVal;
        // 묶음 영역과 마스크는 뺀다 - 라벨이 걸쳐 나오는 것이 설계다.
        const boxes = [...svg.querySelectorAll('rect')]
          .filter(r => !/dg-zone|dg-lane|dg-mask/.test(r.getAttribute('class') || ''))
          .map(r => ({
            cls: r.getAttribute('class'),
            x: +r.getAttribute('x'), y: +r.getAttribute('y'),
            w: +r.getAttribute('width'), h: +r.getAttribute('height'),
          }));
        svg.querySelectorAll('text').forEach(t => {
          const b = t.getBBox();
          const tx = +t.getAttribute('x'), ty = +t.getAttribute('y');
          // 글자 시작점을 품는 가장 작은 상자가 그 글자의 상자다.
          const box = boxes
            .filter(r => tx >= r.x - 1 && tx <= r.x + r.w
                      && ty >= r.y - 2 && ty <= r.y + r.h + 2)
            .sort((a, c) => a.w * a.h - c.w * c.h)[0];
          const right = b.x + b.width;
          if (box) {
            const over = right - (box.x + box.w);
            if (over > 0) out.push({ svg: si, kind: 'box', cls: box.cls,
                                     text: t.textContent, over: +over.toFixed(1) });
          }
          const vbOver = right - vb.width;
          if (vbOver > 0) out.push({ svg: si, kind: 'viewBox',
                                     text: t.textContent, over: +vbOver.toFixed(1) });
        });
      });
      return out;
    });
    for (const h of hits) all.push({ url, ...h });
  }
} finally {
  console.log('__DG_RESULT__' + JSON.stringify(all));
}
await task.finish({ keep: [] });
"""


def page_urls(base):
    """_site 의 글 중 도식을 품은 것만 고른다."""
    urls = []
    for html in sorted(SITE.rglob("*.html")):
        text = html.read_text(encoding="utf-8", errors="ignore")
        if 'class="diagram"' not in text:
            continue
        rel = html.relative_to(SITE).as_posix()
        urls.append(f"{base.rstrip('/')}/{rel}")
    return urls


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://127.0.0.1:4000",
                    help="jekyll serve 주소")
    ap.add_argument("--min", type=float, default=10.0,
                    help="이 값(px)보다 큰 넘침만 보고한다")
    args = ap.parse_args()

    if not SITE.is_dir():
        sys.exit("_site 가 없다. 먼저 jekyll build 를 돌린다.")

    urls = page_urls(args.base)
    if not urls:
        sys.exit("_site 에서 도식을 품은 글을 못 찾았다.")
    print(f"도식을 품은 글 {len(urls)}편을 잰다...", file=sys.stderr)

    # `ego-browser nodejs` 는 파일 경로를 받지 않는다 - stdin 으로만 넘긴다
    # (경로를 주면 "accepts at most one source argument" 로 끝난다).
    script = MEASURE_JS.replace("__DG_URLS__", json.dumps(urls))
    proc = subprocess.run(["ego-browser", "nodejs"],
                          input=script, capture_output=True, text=True)

    # ego 는 결과 앞뒤로 자기 로그를 섞어 내보낸다. 마커가 붙은 줄만 고른다.
    marker = "__DG_RESULT__"
    payload = next((line.split(marker, 1)[1]
                    for line in proc.stdout.splitlines() if marker in line), None)
    if payload is None:
        print(proc.stdout, file=sys.stderr)
        print(proc.stderr, file=sys.stderr)
        sys.exit("측정에 실패했다. ego-browser 를 사용자가 쥐고 있으면 "
                 "제어권을 돌려받은 뒤 다시 돌린다.")

    hits = json.loads(payload)
    hits = [h for h in hits if h["over"] >= args.min]
    # 한 글에 같은 도식이 두 번 들어가면 같은 글자가 두 번 걸린다. 한 번만 본다.
    seen, uniq = set(), []
    for h in hits:
        key = (h["url"], h["svg"], h["kind"], h["text"], h["over"])
        if key not in seen:
            seen.add(key)
            uniq.append(h)
    hits = sorted(uniq, key=lambda h: -h["over"])

    if not hits:
        print(f"넘침 {args.min:.0f}px 이상 없음.")
        return

    for h in hits:
        page = re.sub(r"^https?://[^/]+/", "", h["url"])
        print(f'{h["over"]:6.1f}px  {h["kind"]:7s}  {page}  svg[{h["svg"]}]  '
              f'{h["text"][:40]!r}')
    print(f"\n{len(hits)}건. 이 목록은 후보다 — 고치기 전에 스크린샷으로 "
          "실제로 가려졌는지 본다.", file=sys.stderr)


if __name__ == "__main__":
    main()
