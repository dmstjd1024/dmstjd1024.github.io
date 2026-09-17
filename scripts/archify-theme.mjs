#!/usr/bin/env node
// Archify 산출물을 이 블로그의 색과 밀도에 맞춘다.
//
// 왜 후처리인가 — ~/.claude/skills/archify 는 업스트림 산출물이다. 거기를
// 고치면 스킬을 다시 설치할 때마다 날아가고, 업데이트와도 충돌한다.
// deliver 가 뱉은 HTML 에 <style> 한 덩이를 덧대는 쪽이 안전하다.
//
// 무엇을 맞추나 — 기본 팔레트가 Slate 계열(#020617, 강조 초록)이라
// 이 블로그(#0d1117, 강조 파랑)와 나란히 두면 도식만 색이 따로 논다.
// 아래 토큰은 _sass/vars.scss 의 값을 그대로 옮긴 것이다. 그쪽을 바꾸면
// 여기도 같이 바꿔야 한다 — 빌드가 연결해주지 않는다.
//
//   node scripts/archify-theme.mjs assets/diagrams/foo.html

import { readFile, writeFile } from "node:fs/promises";

const OVERRIDE = `
<style data-archify-blog-theme>
  /* ── 색: _sass/vars.scss 와 같은 값 ───────────────────────── */
  [data-theme="dark"] {
    --bg: #0d1117;
    --panel: rgba(21, 27, 35, 0.6);
    --panel-border: #3d444d;
    --grid: #21262d;
    --lane-fill: rgba(22, 27, 34, 0.35);
    --lane-stroke: #3d444d;
    --text: #e6edf3;
    --text-muted: #b7bfc8;
    --text-dim: #9198a1;
    --text-faint: #9198a1;
    --mask: #161b22;
    --arrow: #6e7681;
    --arrow-emphasis: #4493f8;   /* 초록 → 블로그 파랑 */
    --toolbar-bg: rgba(21, 27, 35, 0.92);
    --toolbar-border: #3d444d;
    --toolbar-text: #e6edf3;
    --toolbar-menu-bg: #151b23;
  }
  [data-theme="light"] {
    --bg: #ffffff;
    --panel: #ffffff;
    --panel-border: #d1d9e0;
    --grid: #eaeef2;
    --lane-fill: rgba(246, 248, 250, 0.7);
    --lane-stroke: #d1d9e0;
    --text: #1f2328;
    --text-muted: #59636e;
    --text-dim: #818b98;
    --text-faint: #59636e;
    --mask: #ffffff;
    --arrow: #818b98;
    --arrow-emphasis: #0969da;
    --toolbar-bg: rgba(255, 255, 255, 0.92);
    --toolbar-border: #d1d9e0;
    --toolbar-text: #1f2328;
    --toolbar-menu-bg: #ffffff;
  }

  /* ── 밀도: 글 안에 박히는 도식이라 저자용 컨트롤은 뺀다 ────── */
  /* 남기는 것 — 테마(도식만 따로 열어볼 때 필요), 검색, 경로, 렌즈,
     상·하류 추적. 글에서 "노드를 클릭해보라"고 안내하는 기능들이다. */
  #btn-preset,        /* 시각 프리셋 순환: 저자가 정할 일 */
  #btn-motion,        /* 모션: 정적 도식이라 쓸 일 없음 */
  #btn-present,       /* 프레젠테이션: iframe 안에서 의미 없음 */
  #btn-export,        /* 내보내기: sandbox 가 다운로드를 막는다 */
  #export-menu,
  .preset-menu,
  .overview-map-hint {
    display: none !important;
  }

  /* 툴바가 도식을 가리지 않게 살짝 줄인다 */
  .toolbar { transform: scale(0.92); transform-origin: top right; }
</style>
`;

const [, , target] = process.argv;
if (!target) {
  console.error("사용법: node scripts/archify-theme.mjs <산출물.html>");
  process.exit(2);
}

const html = await readFile(target, "utf8");

if (html.includes("data-archify-blog-theme")) {
  console.log(`이미 적용됨: ${target}`);
  process.exit(0);
}

// </head> 직전에 넣어야 원본 테마 규칙보다 뒤에 온다. 같은 명시도라면
// 나중에 선언된 쪽이 이긴다 — !important 를 색에까지 쓰지 않는 이유다.
const marker = "</head>";
if (!html.includes(marker)) {
  console.error(`</head> 를 찾지 못했다: ${target}`);
  process.exit(1);
}

await writeFile(target, html.replace(marker, `${OVERRIDE}${marker}`), "utf8");
console.log(`적용: ${target}`);
