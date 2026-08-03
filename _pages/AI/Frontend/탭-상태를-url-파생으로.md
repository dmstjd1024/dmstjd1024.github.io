---
title:  "탭 상태를 useState에 두지 마라 — URL 파생 상태로 바꾸기"

categories:
  - AI
tags:
  - AI
  - Claude Code
  - React
  - Next.js
  - TypeScript

date: 2026-04-19
thumbnail: "/assets/img/thumbnail/sample.png"
---

## 문제: 사이드 메뉴로 이동하면 탭이 안 바뀐다

관리자 포털의 여러 목록 화면이 탭을 갖고 있다. 탭 상태는 `?tab=` 쿼리 파라미터에 실려 있어서 링크 공유와 새로고침이 된다. 이걸 담당하는 게 `useTabQuery` 훅이었다.

QA에서 올라온 증상은 이랬다. 사이드 메뉴에 `?tab=code`로 가는 링크와 `?tab=codeGroup`으로 가는 링크가 나란히 있는데, 한 화면에서 다른 탭 링크를 누르면 **URL은 바뀌는데 화면의 탭은 그대로**였다. 새로고침하면 그제서야 맞는 탭이 나온다.

## 원인: 양방향 동기화

기존 훅은 이렇게 생겼다.

```ts
export const useTabQuery = (initialValue: string) => {
  const router = useRouter();
  const searchParams = useSearchParams();
  const pathname = usePathname();

  // URL에서 tab 파라미터를 읽어와서 초기값 설정
  const initialTabValue = useMemo(() => {
    return searchParams.get("tab") || initialValue;
  }, [searchParams, initialValue]);

  const [value, setValue] = useState(initialTabValue);

  // value가 변경될 때 URL 업데이트
  useEffect(() => {
    const params = new URLSearchParams(searchParams.toString());
    if (value) {
      params.set("tab", value);
    } else {
      params.delete("tab");
    }
    router.replace(`${pathname}?${params.toString()}`, { scroll: false });
  }, [value, router, pathname, searchParams]);

  return { pathname, value, setValue /* ... */ };
};
```

같은 정보가 두 군데에 있다. URL의 `tab` 파라미터와 `useState`의 `value`. 그리고 둘 사이를 두 방향으로 잇는 배선이 있다.

- URL → state: `useState(initialTabValue)`의 초기값. **초기값은 딱 한 번만 쓰인다.**
- state → URL: `useEffect` 안의 `router.replace`

여기서 URL → state 방향이 마운트 시점 1회로 끝난다는 게 버그의 전부다. 컴포넌트가 마운트된 채로 URL만 바뀌면 state는 따라갈 방법이 없다. `useMemo`의 의존성에 `searchParams`가 들어 있어도 소용없다. `initialTabValue`가 새 값으로 다시 계산되긴 하는데, `useState`는 그 값을 두 번째 렌더부터는 쳐다보지도 않는다.

Next.js App Router에서 같은 페이지 컴포넌트를 유지한 채 쿼리만 바꾸는 네비게이션은 리마운트를 일으키지 않는다. 그래서 사이드 메뉴 이동에서만 정확히 이 증상이 났다.

덤으로, `useEffect` 의존성 배열에 `searchParams`와 `value`가 같이 들어 있고 이펙트 본문이 `router.replace`로 `searchParams`를 바꾼다. 이펙트가 자기 의존성을 갱신하는 구조다. `replace`한 값이 현재 URL과 같으면 대체로 조용히 멈추지만, 애초에 무한 루프 위험을 자기 안에 안고 있는 배선이다.

## 어떻게 고쳤나

동기화를 고치는 대신 동기화할 대상을 없앴다. `useState`, `useEffect`, `useMemo`를 전부 지웠다.

```ts
"use client";

import { useRouter, useSearchParams, usePathname } from "next/navigation";

export const useTabQuery = (initialValue: string) => {
  const router = useRouter();
  const searchParams = useSearchParams();
  const pathname = usePathname();

  // value는 항상 URL에서 파생 — 사이드 메뉴 이동 시 즉시 반영됨
  const value = searchParams.get("tab") || initialValue;

  const setValue = (newValue: string) => {
    const params = new URLSearchParams(searchParams.toString());
    if (newValue) {
      params.set("tab", newValue);
    } else {
      params.delete("tab");
    }
    router.replace(`${pathname}?${params.toString()}`, { scroll: false });
  };

  return { pathname, value, setValue /* ... */ };
};
```

한 줄이 전부다.

```ts
const value = searchParams.get("tab") || initialValue;
```

URL이 단일 진실 공급원이 되고, `value`는 렌더마다 URL에서 계산되는 순수 파생값이 됐다. `setValue`는 더 이상 상태를 바꾸는 setter가 아니라 URL을 바꾸는 **액션**이다. 상태 갱신은 `searchParams`가 바뀔 때 React가 알아서 리렌더를 일으키며 일어난다.

바뀐 부분을 나란히 놓으면 이렇다.

| 항목 | before | after |
|---|---|---|
| 진실 공급원 | URL + useState (둘) | URL (하나) |
| URL → 화면 | 마운트 시 1회 | 매 렌더 |
| 화면 → URL | useEffect 부수효과 | setValue 직접 호출 |
| 훅 라인 수 | 32줄 | 24줄 |
| 무한 replace 위험 | 있음 | 구조적으로 없음 |

## 남는 교훈

`useState`에 담아야 하는 값과 담으면 안 되는 값의 기준은 명확하다. **다른 곳에서 이미 관리되는 값이면 담지 않는다.** URL, props, 서버 응답에서 계산할 수 있는 값을 state에 복사하는 순간 원본과 사본을 맞추는 코드가 생기고, 그 코드는 언젠가 어긋난다.

증상만 보면 "URL 변화를 감지해서 state를 갱신하는 useEffect를 추가한다"가 자연스러운 수정처럼 보인다. 그러면 배선이 하나 더 늘고, 그때부터는 state → URL과 URL → state가 서로를 트리거하는 진짜 루프가 된다. 동기화 코드를 추가하고 싶어질 때가 대체로 동기화 자체를 없앨 때다.

useState/useEffect/useMemo를 셋 다 지웠는데 기능이 늘었다는 게 이 수정에서 제일 마음에 드는 부분이다.
