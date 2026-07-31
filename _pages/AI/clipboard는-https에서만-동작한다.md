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

# 문제: 복사 버튼이 아무 반응이 없다

관리자 포털의 대시보드 화면에는 토큰을 복사하는 버튼이 있다. 로컬에서는 잘 됐다. 배포 환경에 올리니 버튼을 눌러도 아무 일도 일어나지 않았다. 에러 토스트도 없고 콘솔에도 아무것도 안 찍혔다.

원인은 코드가 아니라 배포 환경이다. 이 시스템은 폐쇄망 HTTP 환경에 배포된다. 그리고 `navigator.clipboard`는 secure context — HTTPS이거나 localhost일 때만 동작한다. HTTP로 서비스하면 브라우저에 따라 `navigator.clipboard` 자체가 `undefined`이거나, 객체는 있는데 `writeText()`가 rejected Promise를 돌려준다.

원래 코드는 이랬다.

```ts
const copyToken = () => {
  navigator.clipboard.writeText(dashboardToken);
  showSnackbar({ message: "토큰이 복사되었습니다.", type: "success" });
};
```

반환된 Promise를 아무도 안 받는다. rejection은 어디에도 도달하지 않고 조용히 사라지고, 스낵바는 복사 여부와 무관하게 뜬다. "복사되었습니다"라는 성공 메시지가 뜨면서 클립보드는 비어 있는 상태다. 무반응보다 나쁘다.

# 1단계: async로 바꾸고 실패를 보이게

첫 커밋에서 한 일은 실패를 실패로 만든 것이다.

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

기능이 고쳐진 건 아니다. 여전히 복사는 안 된다. 다만 이제 안 된다는 게 화면에 보인다. 조용히 실패하는 코드를 시끄럽게 실패하게 만드는 게 항상 첫 단계다.

# 2단계: execCommand 폴백

그 다음 `document.execCommand("copy")` 폴백을 붙였다. 폐기 예정 API지만, secure context를 요구하지 않는다는 점 때문에 HTTP 환경에서는 이게 유일한 선택지다.

사용자 포털에서는 공통 유틸 `helpers.ts`의 `copyToClipboard`에 한 번에 넣었다.

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

두 갈래로 나뉜다. `navigator.clipboard`가 아예 없으면 바로 폴백, 있으면 시도해보고 `.catch()`에서 폴백. 존재 여부와 동작 여부가 별개라서 두 경우를 다 막아야 한다.

# 클라이맥스: 왜 opacity를 버렸나

관리자 포털은 여기서 한 번 더 손봤다. 두 번째 커밋의 diff에서 제일 중요한 줄은 이거다.

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

`execCommand("copy")`는 **현재 선택 영역(selection)** 을 복사한다. 그래서 폴백은 임시 textarea를 만들어 값을 넣고 `select()`로 선택시킨 뒤 복사를 실행한다. 그 textarea가 화면에 보이면 안 되니까 숨겨야 하는데, 여기서 숨기는 방법이 결과를 가른다.

`opacity: 0`은 요소를 렌더 트리에 남긴 채 투명하게만 만든다. 그런데 브라우저는 사용자에게 보이지 않는 요소에 대한 선택을 거부하거나 무시하는 경우가 있다. `select()`가 호출되어도 실제 selection이 잡히지 않으면, 복사할 대상이 없으니 `execCommand("copy")`는 아무것도 복사하지 않는다.

`left/top: -999999px`는 다르다. 요소는 완전히 정상적으로 렌더되고 선택 가능하며, 다만 뷰포트 바깥 좌표에 있을 뿐이다. 브라우저 입장에서 이건 "숨겨진 요소"가 아니라 "저 멀리 있는 요소"다. 선택도 되고 복사도 된다.

`display: none`이나 `visibility: hidden`은 더 확실하게 안 된다. 렌더 트리에서 빠지거나 선택 대상이 아니게 되므로 selection API가 잡을 것이 없다.

같이 들어간 나머지 두 개도 같은 문제의 다른 면이다.

- `textarea.focus()` — `select()` 전에 포커스를 줘야 selection이 안정적으로 잡힌다. 특히 iOS Safari에서 그렇다.
- `execCommand` 반환값 체크 — `execCommand`는 예외를 던지지 않고 `false`를 돌려준다. 반환값을 안 보면 1단계에서 애써 만든 `try/catch`가 이 경로에서는 무용지물이다. 실패하면 명시적으로 `throw`해서 catch로 흘려보낸다.

정리하면 이렇다.

| 숨김 방법 | 렌더 트리 | select() 동작 | 폴백에 쓸 수 있나 |
|---|---|---|---|
| `display: none` | 제외 | 불가 | 불가 |
| `visibility: hidden` | 포함(비가시) | 불안정 | 불가 |
| `opacity: 0` | 포함(투명) | 브라우저에 따라 거부 | 불안정 |
| `left/top: -999999px` | 포함(화면 밖) | 정상 | 가능 |

# 남는 교훈

브라우저 API의 동작 조건을 코드가 아니라 배포 환경이 결정하는 경우가 있다. `navigator.clipboard`, `navigator.geolocation`, Service Worker, `crypto.subtle` 모두 secure context를 요구한다. localhost는 secure context로 취급되기 때문에, 로컬 개발에서는 이런 제약이 전부 투명해진다. 폐쇄망 HTTP 배포가 전제라면 이 목록은 처음부터 확인하고 들어가야 한다.

그리고 이 두 번의 커밋은 같은 얘기를 반복한다. **1단계는 실패를 감지 가능하게 만들었고, 2단계는 감지 가능해진 실패를 실제로 고쳤다.** 순서가 반대였으면 `opacity: 0` 버전이 여전히 실패하고 있다는 사실조차 몰랐을 것이다.
