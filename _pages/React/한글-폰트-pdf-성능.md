---
title:  "PDF 다운로드가 7초 걸렸는데, 범인은 한글 폰트였다"

categories:
  - React
tags:
  - AI
  - Claude Code
  - React
  - 성능최적화

date: 2026-06-21
thumbnail: "/assets/img/thumbnail/sample.png"
---
## 문제

- 대상 — 제품 배출량을 산정하는 B2B 웹앱의 결과 리포트 PDF 다운로드
- 소요 시간 — 버튼 클릭 후 약 7초
- 그동안 화면 — 로딩만 회전, 아무 변화 없음
- 사용자 반응 — "먹통이 됐나" 하고 재클릭하기 충분한 시간

구현 스택 — `@react-pdf/renderer` 4.x.

- 처리 흐름 — 화면의 차트 6종을 off-screen에 마운트해 canvas로 추출
- 그다음 — 그 이미지들을 `SummaryPdf` 컴포넌트에 전달해 PDF 생성

## 원인 조사

- 방법: chrome-devtools 계측 + 변수 하나씩 제거
- 20여 종 조합 실행 후 병목 확정

| 조건 | 소요 시간 |
|---|---|
| 전체 (한글 폰트 포함) | 약 7s |
| 폰트를 제거하고 생성 | 약 0.1s |

- 폰트 제거 시 — 70배 향상
- 범인이 아닌 것 — 차트 캡처, 데이터 가공, blob 생성
- 진짜 병목 — **react-pdf가 한글 텍스트를 layout하는 단계 자체**

여기서부터 통상적 시도를 순서대로 진행 — 전부 무효:

- 폰트 서브셋팅 — 무효
- 줄바꿈 옵션 조정 — 무효
- hyphenation 비활성화 — 무효
- 라이브러리 버전업 — 4.x가 이미 최신이라 올릴 곳 없음
- 텍스트 자체 축약 — PDF 서문과 notes 문구를 한글로 축약해 layout 대상 글자 수 감축. 체감할 만큼 미감소

- 결론: 글자 수에 선형 비례하는 문제가 아님

## 어떻게 고쳤나

시도를 다 소진한 뒤 방향을 바꿨다.

- 전환된 목표: 텍스트 layout 고속화가 아니라 **텍스트 layout 자체를 제거**

- 방식 — 화면에 이미 렌더링된 콕핏 DOM을 `html2canvas`로 캡처
- 그다음 — 그 이미지를 `jsPDF`로 감싸 이미지 PDF 생성
- 원리 — PDF 안에 텍스트 객체가 0개이므로 layout할 대상 자체가 없음

<div class="diagram" role="img" aria-label="폰트 최적화 시도가 모두 실패한 뒤 텍스트를 없애는 방향으로 바꾼 과정">
{% include diagrams/pdf--font-bottleneck.svg %}
</div>

```ts
const CAPTURE_SCALE = 2;
const JPEG_QUALITY = 0.9;

const [{ default: html2canvas }, { jsPDF }] = await Promise.all([
  import('html2canvas'),
  import('jspdf'),
]);

const canvas = await html2canvas(node, {
  scale: CAPTURE_SCALE,
  backgroundColor: TOSS_BG,
  useCORS: true,
  logging: false,
});
const img = canvas.toDataURL('image/jpeg', JPEG_QUALITY);
```

결과:

- 소요 시간 — 3656px짜리 큰 DOM 기준 약 0.7초
- JPEG 용량 — 약 170KB
- 개선폭 — 6.4초에서 0.7초로 약 9배
- 신규 라이브러리 추가 — 0개 (`html2canvas`, `jspdf` 모두 기존 의존성)
- 서버 변경 — 0

- 부수 작업 — 캡처 대상 차트들의 애니메이션 비활성화
- 이유: 캡처 시점에 애니메이션 진행 중이면 절반쯤 그려진 차트가 그대로 PDF에 고정

### 훅 인터페이스도 다시 설계했다

- 기존 `usePdfDownload` 인자 — `lcaInfo`, `companyName`, `finalIoList`, `report` 네 덩어리
- 기존 동작 — 내부에서 PDF 문서 조립
- 화면 캡처 방식 전환 후 — 이 인자들이 전부 불필요

```ts
const { pdfLoading, trigger, captureRef } = usePdfDownload();
// <div ref={captureRef}> ...콕핏... </div>
// <Button onClick={() => trigger(productName)} disabled={pdfLoading} />
```

- 축소 결과 — `trigger(productName)` + `captureRef` 두 개
- 재사용 — 결과요약 화면과 전과정해석 화면 두 곳이 같은 훅 공유

## 트레이드오프

이미지 PDF라서 **텍스트 선택과 검색이 안 된다.** 이건 명확한 손실이다.

- 용도 판단: 이 리포트는 화면에 보이는 결과를 그대로 보관·공유하는 목적
- 저울질 대상: 7초 대기 vs 텍스트 선택 불가 → 후자 채택
- 부수 효과: 출력물이 화면 콕핏과 1:1 동일

## 남는 교훈

"PDF 생성이 느리다"에서 바로 최적화에 들어갔다면 서브셋팅·줄바꿈 같은 걸 계속 만졌을 것이다. 실제로 그것들을 다 시도했고 전부 실패했다. 방향이 잡힌 건 폰트를 완전히 제거해봤을 때 0.1초가 나온 순간이었다.

병목을 좁힐 때 "이걸 빼면 얼마나 빨라지나"를 극단적으로 확인해보는 실험이 유효했다. 그 실험 자체는 배포할 수 없는 코드지만(한글 없는 PDF는 쓸모없다), 어디를 우회해야 하는지를 알려줬다.
