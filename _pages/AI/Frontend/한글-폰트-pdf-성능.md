---
title:  "PDF 다운로드가 7초 걸렸는데, 범인은 한글 폰트였다"

categories:
  - AI
tags:
  - AI
  - Claude Code
  - React
  - 성능최적화

date: 2026-06-21
thumbnail: "/assets/img/thumbnail/sample.png"
---

## 문제

제품 배출량을 산정하는 B2B 웹앱에서 결과 리포트를 PDF로 내려받는 기능이 있었다. 버튼을 누르면 약 7초가 걸렸다. 그동안 화면은 로딩만 돌고 아무 일도 일어나지 않는다. 사용자가 "먹통이 됐나" 하고 다시 누르기 충분한 시간이다.

구현은 `@react-pdf/renderer` 4.x였다. 화면의 차트 6종을 off-screen에 마운트해 canvas로 뽑고, 그 이미지들을 `SummaryPdf` 컴포넌트에 넘겨 PDF를 만드는 구조였다.

## 원인 조사

chrome-devtools로 계측하면서 변수를 하나씩 지워봤다. 20여 종의 조합을 돌린 끝에 병목이 명확해졌다.

| 조건 | 소요 시간 |
|---|---|
| 전체 (한글 폰트 포함) | 약 7s |
| 폰트를 제거하고 생성 | 약 0.1s |

폰트를 빼는 순간 70배가 빨라졌다. 차트 캡처도, 데이터 가공도, blob 생성도 아니었다. **react-pdf가 한글 텍스트를 layout하는 단계 자체**가 시간을 다 먹고 있었다.

여기서부터 흔히 시도하는 것들을 순서대로 밟았고, 전부 효과가 없었다.

- 폰트 서브셋팅 — 무효
- 줄바꿈 옵션 조정 — 무효
- hyphenation 비활성화 — 무효
- 라이브러리 버전업 — 4.x가 이미 최신이라 올릴 곳이 없었다

중간에 텍스트 자체를 줄여보기도 했다. PDF 서문과 notes 문구를 한글로 축약해 layout 대상 글자 수를 깎는 접근이었다(커밋 `dadecf37`). 체감할 만큼 줄지 않았다. 글자 수에 선형으로 비례하는 문제가 아니었다는 뜻이다.

## 어떻게 고쳤나

시도를 다 소진한 뒤 방향을 바꿨다. 텍스트 layout을 빠르게 만드는 게 아니라, **텍스트 layout을 아예 하지 않는 것**이다.

화면에 이미 렌더링돼 있는 콕핏 DOM을 `html2canvas`로 캡처하고, 그 이미지를 `jsPDF`로 감싸 이미지 PDF를 만든다. PDF 안에는 텍스트 객체가 하나도 없으므로 layout할 대상 자체가 없다.

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

결과는 3656px짜리 큰 DOM 기준 약 0.7초, JPEG 용량 약 170KB였다. 6.4초에서 0.7초로 약 9배다. `html2canvas`와 `jspdf`는 이미 프로젝트에 있던 의존성이라 **신규 라이브러리 추가는 0개**였고, 서버 쪽 변경도 0이었다.

부수적으로 캡처 대상 차트들의 애니메이션도 껐다(커밋 `7344d9f4`). 캡처 시점에 애니메이션이 진행 중이면 절반쯤 그려진 차트가 그대로 PDF에 박히기 때문이다.

### 훅 인터페이스도 다시 설계했다

기존 `usePdfDownload`는 `lcaInfo`, `companyName`, `finalIoList`, `report` 네 덩어리를 받아 내부에서 PDF 문서를 조립하는 형태였다. 화면 캡처 방식으로 바꾸면서 이 인자들이 전부 불필요해졌다.

```ts
const { pdfLoading, trigger, captureRef } = usePdfDownload();
// <div ref={captureRef}> ...콕핏... </div>
// <Button onClick={() => trigger(productName)} disabled={pdfLoading} />
```

`trigger(productName)` + `captureRef` 두 개로 줄였다. 이 인터페이스 덕에 결과요약 화면과 전과정해석 화면 두 곳이 같은 훅을 그대로 공유한다.

## 트레이드오프

이미지 PDF라서 **텍스트 선택과 검색이 안 된다.** 이건 명확한 손실이다. 다만 이 리포트는 화면에 보이는 결과를 그대로 보관·공유하는 용도였고, 7초 대기와 텍스트 선택 불가를 저울질했을 때 후자를 택하는 게 맞다고 봤다. 출력물이 화면 콕핏과 1:1로 동일해진다는 부수 효과도 있었다.

## 남는 교훈

"PDF 생성이 느리다"에서 바로 최적화에 들어갔다면 서브셋팅·줄바꿈 같은 걸 계속 만졌을 것이다. 실제로 그것들을 다 시도했고 전부 실패했다. 방향이 잡힌 건 폰트를 완전히 제거해봤을 때 0.1초가 나온 순간이었다.

병목을 좁힐 때 "이걸 빼면 얼마나 빨라지나"를 극단적으로 확인해보는 실험이 유효했다. 그 실험 자체는 배포할 수 없는 코드지만(한글 없는 PDF는 쓸모없다), 어디를 우회해야 하는지를 알려줬다.
