---
title:  "navigator.clipboard는 HTTPS에서만 동작한다"
description: "로컬은 되는데 배포 환경에서만 안 된 이유"

categories:
  - React
tags:
  - AI
  - Claude Code
  - React
  - Next.js
  - 브라우저 API

date: 2026-04-20
thumbnail: "/assets/img/thumbnail/react_thumbnail.webp"
---
## 문제: 복사 버튼이 아무 반응이 없다

- 화면: 관리 화면
- 기능: 값 복사 버튼
- 로컬: 정상 동작
- 배포 환경: 버튼 눌러도 무반응
- 에러 토스트 없음, 콘솔 출력 없음

- 원인 위치 — 코드가 아니라 배포 환경

- 조건: HTTPS가 아닌 환경에서 서비스되는 경우
- `navigator.clipboard`는 secure context 전용 — HTTPS 또는 localhost
- HTTP 서비스 시 브라우저에 따라 `navigator.clipboard` 자체가 `undefined`
- 또는 객체는 존재하되 `writeText()`가 rejected Promise 반환

- 원래 코드

```ts
const copyToken = () => {
  navigator.clipboard.writeText(dashboardToken);
  showSnackbar({ message: "토큰이 복사되었습니다.", type: "success" });
};
```

- 반환된 Promise를 아무도 수신하지 않음
- rejection을 처리하지 않아 브라우저에 unhandled rejection으로 보고될 수 있음
- 스낵바는 복사 여부와 무관하게 노출

`writeText()`가 Promise를 반환한 뒤 거부되는 경로에서는 "복사되었습니다"라는 성공 메시지가 먼저 뜰 수 있다. `navigator.clipboard` 자체가 없으면 그 앞에서 동기 예외가 나므로 스낵바도 실행되지 않는다.

<div class="diagram" role="img" aria-label="secure context 여부에 따라 clipboard API 가 갈리는 구조">
{% include diagrams/clipboard--secure-context.svg %}
</div>

## 1단계: async로 바꾸고 실패를 보이게

- 첫 커밋의 내용 — 실패를 실패로 만들기

```ts
const copyToken = async () => {
  try {
    await navigator.clipboard.writeText(dashboardToken);
    showSnackbar({ message: "토큰이 복사되었습니다.", type: "success" });
  } catch (error) {
    showSnackbar({ message: "토큰 복사에 실패했습니다.", type: "error" });
  }
};
```

- 기능은 미수정 — 여전히 복사 불가
- 변화: 실패가 화면에 노출

조용히 실패하는 코드를 시끄럽게 실패하게 만드는 게 항상 첫 단계다.

## 2단계: execCommand 폴백

- 다음 조치 — `document.execCommand("copy")` 폴백 추가

- 상태: 폐기 예정 API
- 장점: secure context 미요구
- 결론: 당시 HTTP 환경을 지원하기 위해 선택한 호환성 폴백. 브라우저 정책과 사용자 동작 조건에 따라 실패할 수 있음

- 사용자 포털 — 공통 유틸 `helpers.ts`의 `copyToClipboard`에 일괄 반영
- 아래는 최초 폴백 버전이다. `opacity: 0`과 반환값 미검사가 남아 있어 최종 코드가 아니다.

```ts
export const copyToClipboard = (text: string) => {
  if (typeof window === "undefined") return;

  if (navigator.clipboard) {
    navigator.clipboard.writeText(text).catch(() => execCommandCopy(text));
  } else {
    execCommandCopy(text);
  }
};

function execCommandCopy(text: string) {
  const textarea = document.createElement("textarea");
  textarea.value = text;
  textarea.style.cssText = "position:fixed;left:-9999px;top:-9999px;opacity:0";
  document.body.appendChild(textarea);
  textarea.focus();
  textarea.select();
  document.execCommand("copy");
  document.body.removeChild(textarea);
}
```

- 분기 두 갈래
- `navigator.clipboard` 부재 → 즉시 폴백
- 존재 → 시도 후 `.catch()`에서 폴백
- 두 경우를 다 막는 이유: 존재 여부와 동작 여부가 별개

## 후속 수정: 숨김 위치·포커스·반환값 검사를 함께 바꿨다

- 같은 관리 화면 — 여기서 한 번 더 수정
- 두 번째 커밋 diff의 핵심 줄

```diff
  textarea.style.position = "fixed";
- textarea.style.opacity = "0";
+ textarea.style.left = "-999999px";
+ textarea.style.top = "-999999px";
  document.body.appendChild(textarea);
+ textarea.focus();
  textarea.select();
- document.execCommand("copy");
+ const result = document.execCommand("copy");
  document.body.removeChild(textarea);
+
+ if (!result) {
+   throw new Error("execCommand('copy') failed");
+ }
```

- `execCommand("copy")`의 복사 대상 — **현재 선택 영역(selection)**
- 폴백의 동작 순서

- 임시 textarea 생성
- 값 주입
- `select()`로 선택
- 복사 실행

textarea를 화면 밖에 두는 방식으로 바꾸면서 포커스 부여와 반환값 검사도 함께 추가했다. 따라서 이 diff만으로 `opacity: 0`이 단독 원인이었다고 확정할 수는 없다.

`opacity: 0`의 경우:

- 요소는 렌더 트리에 잔존, 투명 처리만 됨
- 투명하다는 사실만으로 선택이 불가능해지는 것은 아님
- 당시 실패가 투명도, 포커스, 브라우저 정책 중 어느 조건 때문인지는 따로 분리해 측정하지 않음

`left/top: -999999px`의 경우:

- 위치만 뷰포트 바깥으로 이동
- 이 위치 설정과 `focus()`, 반환값 검사를 함께 적용한 뒤 복사 동작을 확인

`display: none`이나 `visibility: hidden`처럼 선택할 수 없게 숨기는 방식은 피한다. 화면 밖 배치도 복사를 보장하지는 않으므로 실행 결과를 검사해야 한다.

- 함께 바꾼 두 가지

- `textarea.focus()` — `select()` 전에 명시적으로 포커스 부여
- `execCommand` 반환값 체크 — 예외 미발생, `false` 반환. 반환값 미확인 시 1단계의 `try/catch`가 이 경로에서 무용지물. 실패 시 명시적 `throw`로 catch에 전달

- 정리

| 숨김 방법 | 렌더 트리 | select() 동작 | 폴백에 쓸 수 있나 |
|---|---|---|---|
| `display: none` | 제외 | 불가 | 불가 |
| `visibility: hidden` | 포함(비가시) | 불안정 | 불가 |
| `opacity: 0` | 포함(투명) | 투명도만으로 불가하지 않음 | 단독 원인 미확정 |
| `left/top: -999999px` | 포함(화면 밖) | 선택 가능 | 포커스·반환값 검사와 함께 적용 |

## 남는 교훈

브라우저 API의 동작 조건을 코드가 아니라 배포 환경이 결정하는 경우가 있다.

secure context를 요구하는 API:

- `navigator.clipboard`
- `navigator.geolocation`
- Service Worker
- `crypto.subtle`

- localhost는 secure context로 취급됨
- 따라서 로컬 개발에서는 이 제약이 전부 투명해짐
- HTTPS를 쓸 수 없는 배포 환경이라면 이 목록은 처음부터 확인 대상

그리고 이 두 번의 커밋은 같은 얘기를 반복한다. **1단계는 실패를 감지 가능하게 만들었고, 2단계는 감지 가능해진 실패를 실제로 고쳤다.** 반환값을 검사하지 않으면 폴백이 `false`로 실패해도 성공으로 오인할 수 있다.

API의 보안 조건은 [Clipboard 명세](https://www.w3.org/TR/clipboard-apis/#navigator-interface)를 참고했다. secure context가 필요하며 권한·사용자 활성화 조건도 따로 확인해야 한다.
