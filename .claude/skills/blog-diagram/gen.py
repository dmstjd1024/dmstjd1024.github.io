#!/usr/bin/env python3
"""로드맵 글의 단계별 도식을 같은 규격으로 생성한다.

구조는 전체 흐름 도식과 같다: 존(묶음)으로 나누고 존 사이를 화살표로 잇는다.
좌표를 손으로 찍으면 도식마다 미세하게 어긋나므로 여기서 계산한다.
색은 넣지 않는다 — dg-* 클래스로 블로그 테마를 따라간다.
"""
import html

W = 720           # viewBox 폭 (가로본)
W_NARROW = 360    # 폰 폭. 본문 폭이 이보다 좁아지면 세로본으로 바꾼다
PAD = 24          # 좌우 여백
ZONE_PAD = 24     # 존 안쪽 여백
NODE_H = 52
NODE_GAP = 16
ZONE_LABEL_H = 24
ZONE_GAP = 44     # 존 사이 세로 간격(화살표 자리)
ROW_GAP = 14      # 존 안에서 줄이 넘어갈 때 간격


def esc(s):
    return html.escape(s, quote=False)


def wrap_rows(items, avail_w):
    """노드를 가로로 채우다 폭이 넘치면 다음 줄로 접는다."""
    rows, cur, cur_w = [], [], 0
    for it in items:
        w = it["w"]
        add = w if not cur else w + NODE_GAP
        if cur and cur_w + add > avail_w:
            rows.append(cur)
            cur, cur_w = [it], w
        else:
            cur.append(it)
            cur_w += add
    if cur:
        rows.append(cur)
    return rows


def node_width(label, sub, W=W):
    """글자 수로 대략의 폭을 잡는다. 한글은 넓게 친다.

    상한은 존 안쪽 폭을 넘지 않게 잡는다 — 세로본(360)에서 232 를 그대로
    쓰면 상자가 존 밖으로 삐져나온다.
    """
    def vis(s):
        return sum(2 if ord(c) > 0x2000 else 1 for c in s)
    cap = min(232, W - 2 * PAD - 2 * ZONE_PAD)
    n = max(vis(label), vis(sub or "") * 0.82)
    return max(min(96, cap), min(cap, int(n * 5.4) + 40))


def render(zones, focal_zone, W, arw="br-arw"):
    """주어진 폭으로 도형을 그려 (줄 목록, 전체 높이) 를 돌려준다.

    폭만 바꾸면 wrap_rows 가 알아서 다음 줄로 접으므로, 같은 코드로
    가로본(720)과 세로본(360)을 만든다.
    """
    body, y = [], 32

    for zi, z in enumerate(zones):
        nodes = [dict(n, w=node_width(n["t"], n.get("s"), W)) for n in z["nodes"]]
        rows = wrap_rows(nodes, W - 2 * PAD - 2 * ZONE_PAD)

        zone_h = ZONE_LABEL_H + len(rows) * NODE_H + (len(rows) - 1) * ROW_GAP + ZONE_PAD
        is_focal = (focal_zone == zi)
        zcls = "dg-zone-a" if is_focal else "dg-zone"
        tcls = "dg-n" if is_focal else "dg-s"
        ncls = "dg-hl" if is_focal else "dg-item"
        ltcls = "dg-n" if is_focal else "dg-t"
        lscls = "dg-n" if is_focal else "dg-s"

        body.append(f'\n  <!-- {z["name"]} -->')
        body.append(f'  <rect class="{zcls}" x="{PAD}" y="{y}" width="{W-2*PAD}" height="{zone_h}" rx="8"/>')
        lw = int(sum(2 if ord(c) > 0x2000 else 1 for c in z["name"]) * 4.2) + 16
        body.append(f'  <rect class="dg-mask" x="{PAD+16}" y="{y-6}" width="{lw}" height="12" rx="2"/>')
        body.append(
            f'  <text class="{tcls}" x="{PAD+20}" y="{y+3}" font-size="7" '
            f'font-family="\'Geist Mono\', ui-monospace, monospace" letter-spacing="0.14em">{esc(z["name"])}</text>')

        ny = y + ZONE_LABEL_H
        for row in rows:
            total = sum(n["w"] for n in row) + NODE_GAP * (len(row) - 1)
            nx = (W - total) // 2
            for i, n in enumerate(row):
                # 같은 줄의 노드는 기본적으로 나열(병렬)이다. 순서가 있는 존만
                # seq=True 를 줘서 화살표로 잇는다 — 선택지끼리 화살표로 이으면
                # "PostgreSQL 다음에 MySQL" 처럼 없는 순서를 만들어낸다.
                if i > 0 and z.get("seq"):
                    body.append(
                        f'  <path class="dg-arw" d="M{nx-NODE_GAP},{ny+NODE_H//2} H{nx-3}" '
                        f'marker-end="url(#{arw})"/>')
                body.append(f'  <rect class="{ncls}" x="{nx}" y="{ny}" width="{n["w"]}" height="{NODE_H}" rx="6"/>')
                cx = nx + n["w"] // 2
                if n.get("s"):
                    body.append(
                        f'  <text class="{ltcls}" x="{cx}" y="{ny+22}" font-size="12" font-weight="600" '
                        f'font-family="\'Geist\', system-ui, sans-serif" text-anchor="middle">{esc(n["t"])}</text>')
                    body.append(
                        f'  <text class="{lscls}" x="{cx}" y="{ny+39}" font-size="9" '
                        f'font-family="\'Geist Mono\', ui-monospace, monospace" text-anchor="middle">{esc(n["s"])}</text>')
                else:
                    body.append(
                        f'  <text class="{ltcls}" x="{cx}" y="{ny+31}" font-size="12" font-weight="600" '
                        f'font-family="\'Geist\', system-ui, sans-serif" text-anchor="middle">{esc(n["t"])}</text>')
                nx += n["w"] + NODE_GAP
            ny += NODE_H + ROW_GAP

        y += zone_h
        if zi < len(zones) - 1:
            body.append(
                f'  <path class="dg-arw" d="M{W//2},{y} V{y+ZONE_GAP-6}" marker-end="url(#{arw})"/>')
            y += ZONE_GAP

    return body, y + 16


def build(zones, out_path, title, desc, focal_zone=None):
    """가로본과 세로본을 한 파일에 나란히 넣는다.

    SVG 의 viewBox 는 CSS 로 바꿀 수 없다. 그래서 하나를 두고 늘이는 대신
    형제 <svg> 2개를 두고 diagram.scss 가 display 로 하나만 보여준다.
    한 장만 두면 폰에서 720 폭이 통째로 축소돼 존 라벨이 3.6px 까지
    작아졌다 (390px 뷰포트 실측, 2026-10-29).
    """
    stem = out_path.stem
    arw = f"{stem}-arw"
    wide_body, wide_h = render(zones, focal_zone, W, arw + "-w")
    narrow_body, narrow_h = render(zones, focal_zone, W_NARROW, arw + "-n")

    def defs(suffix):
        # 두 본이 한 문서에 같이 있으므로 marker id 가 겹치면 안 된다.
        return [
            '  <defs>',
            f'    <marker id="{arw}{suffix}" markerWidth="8" markerHeight="6" '
            'refX="7" refY="3" orient="auto">',
            '      <path d="M0 0 L8 3 L0 6 z"/>',
            '    </marker>',
            '  </defs>',
        ]

    def one(cls, vb_w, vb_h, lines, suffix, labelled):
        # 접근성 이름은 한쪽에만 둔다 — 둘 다 주면 같은 설명이 두 번 읽힌다.
        a11y = (f' role="img" aria-labelledby="{stem}-title {stem}-desc"'
                if labelled else ' role="presentation" aria-hidden="true"')
        head = [f'<svg xmlns="http://www.w3.org/2000/svg" class="{cls}" '
                f'viewBox="0 0 {vb_w} {vb_h}"{a11y}>']
        if labelled:
            head += [f'  <title id="{stem}-title">{esc(title)}</title>',
                     f'  <desc id="{stem}-desc">{esc(desc)}</desc>']
        return head + [''] + defs(suffix) + lines + ['</svg>']

    out = (one("dg-wide", W, wide_h, wide_body, "-w", True)
           + one("dg-narrow", W_NARROW, narrow_h, narrow_body, "-n", False))
    out_path.write_text("\n".join(out) + "\n", encoding="utf-8")
    return wide_h
