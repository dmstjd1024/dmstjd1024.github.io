---
title:  "navigator.clipboard는 HTTPS에서만 동작한다"

categories:
  - AI
tags:
  - AI
  - Claude Code
  - React
  - Next.js
  - 브라우저 API

date: 2026-04-20
thumbnail: "/assets/img/thumbnail/sample.png"
---

## 문제: 복사 버튼이 아무 반응이 없다

- 화면: 관리자 포털 대시보드
- 기능: 토큰 복사 버튼
- 로컬: 정상 동작
- 배포 환경: 버튼 눌러도 무반응
- 에러 토스트 없음, 콘솔 출력 없음

- 원인 위치 — 코드가 아니라 배포 환경

- 배포 환경: 폐쇄망 HTTP
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
- rejection은 어디에도 도달하지 않고 소멸
- 스낵바는 복사 여부와 무관하게 노출

"복사되었습니다"라는 성공 메시지가 뜨면서 클립보드는 비어 있는 상태다. 무반응보다 나쁘다.

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
- 결론: HTTP 환경에서는 유일한 선택지

- 사용자 포털 — 공통 유틸 `helpers.ts`의 `copyToClipboard`에 일괄 반영

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

## 클라이맥스: 왜 opacity를 버렸나

- 관리자 포털 — 여기서 한 번 더 수정
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

그 textarea가 화면에 보이면 안 되니까 숨겨야 하는데, 여기서 숨기는 방법이 결과를 가른다.

`opacity: 0`의 경우:

- 요소는 렌더 트리에 잔존, 투명 처리만 됨
- 브라우저가 비가시 요소의 선택을 거부하거나 무시하는 경우 존재
- `select()` 호출돼도 실제 selection 미형성
- 복사 대상이 없으므로 `execCommand("copy")`는 아무것도 복사하지 않음

`left/top: -999999px`의 경우:

- 요소는 완전히 정상 렌더, 선택 가능
- 위치만 뷰포트 바깥
- 브라우저 입장에서 "숨겨진 요소"가 아니라 "저 멀리 있는 요소"
- 선택도 되고 복사도 됨

`display: none`이나 `visibility: hidden`은 더 확실하게 안 된다. 렌더 트리에서 빠지거나 선택 대상이 아니게 되므로 selection API가 잡을 것이 없다.

- 같이 들어간 나머지 두 개 — 같은 문제의 다른 면

- `textarea.focus()` — `select()` 전 포커스 부여로 selection 안정화. 특히 iOS Safari
- `execCommand` 반환값 체크 — 예외 미발생, `false` 반환. 반환값 미확인 시 1단계의 `try/catch`가 이 경로에서 무용지물. 실패 시 명시적 `throw`로 catch에 전달

- 정리

| 숨김 방법 | 렌더 트리 | select() 동작 | 폴백에 쓸 수 있나 |
|---|---|---|---|
| `display: none` | 제외 | 불가 | 불가 |
| `visibility: hidden` | 포함(비가시) | 불안정 | 불가 |
| `opacity: 0` | 포함(투명) | 브라우저에 따라 거부 | 불안정 |
| `left/top: -999999px` | 포함(화면 밖) | 정상 | 가능 |

## 남는 교훈

브라우저 API의 동작 조건을 코드가 아니라 배포 환경이 결정하는 경우가 있다.

secure context를 요구하는 API:

- `navigator.clipboard`
- `navigator.geolocation`
- Service Worker
- `crypto.subtle`

- localhost는 secure context로 취급됨
- 따라서 로컬 개발에서는 이 제약이 전부 투명해짐
- 폐쇄망 HTTP 배포가 전제라면 이 목록은 처음부터 확인 대상

그리고 이 두 번의 커밋은 같은 얘기를 반복한다. **1단계는 실패를 감지 가능하게 만들었고, 2단계는 감지 가능해진 실패를 실제로 고쳤다.** 순서가 반대였으면 `opacity: 0` 버전이 여전히 실패하고 있다는 사실조차 몰랐을 것이다.
