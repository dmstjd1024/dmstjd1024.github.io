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

관리자 포털의 여러 목록 화면이 탭 보유

- 탭 상태 위치 — `?tab=` 쿼리 파라미터
- 그 덕에 되는 것 — 링크 공유, 새로고침
- 담당 훅 — `useTabQuery` 하나

QA에서 올라온 증상

- 사이드 메뉴 구성 — `?tab=code` 링크와 `?tab=codeGroup` 링크가 나란히 위치
- 한 화면에서 다른 탭 링크 클릭 시 — **URL은 바뀌는데 화면의 탭은 그대로**
- 새로고침하면 — 그제서야 맞는 탭 표시

<div class="diagram" role="img" aria-label="양방향 동기화와 URL 파생 상태의 차이">
{% include diagrams/tab-url--derived-state.svg %}
</div>

## 원인: 양방향 동기화

기존 훅

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

같은 정보의 저장 위치 둘 — URL의 `tab` 파라미터, `useState`의 `value`. 그리고 둘 사이를 두 방향으로 잇는 배선

- URL → state — `useState(initialTabValue)`의 초기값. **초기값의 사용 횟수는 딱 한 번**
- state → URL — `useEffect` 안의 `router.replace`

버그의 전부 — URL → state 방향이 마운트 시점 1회로 종료

- 마운트된 채로 URL만 바뀌면 — state는 따라갈 방법 없음
- `useMemo` 의존성에 `searchParams` 추가해도 — 무용
- 이유 — `initialTabValue`는 새 값으로 재계산되지만 `useState`는 두 번째 렌더부터 그 값을 무시

Next.js App Router의 동작 — 같은 페이지 컴포넌트를 유지한 채 쿼리만 바꾸는 네비게이션은 리마운트 미발생. 그래서 사이드 메뉴 이동에서만 정확히 이 증상이 났다.

덤으로 딸린 위험 요소

- `useEffect` 의존성 배열 — `searchParams`와 `value`가 함께 포함
- 이펙트 본문 — `router.replace`로 `searchParams`를 변경
- 구조 — 이펙트가 자기 의존성을 갱신
- 현재 상태 — `replace`한 값이 현재 URL과 같으면 대체로 조용히 멈춤

애초에 무한 루프 위험을 자기 안에 안고 있는 배선

## 어떻게 고쳤나

동기화를 고치는 대신 동기화할 대상 자체를 제거 — `useState`, `useEffect`, `useMemo` 전부 삭제

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

핵심은 한 줄

```ts
const value = searchParams.get("tab") || initialValue;
```

- 단일 진실 공급원 — URL
- `value`의 성격 — 렌더마다 URL에서 계산되는 순수 파생값
- `setValue`의 성격 — 상태를 바꾸는 setter가 아니라 URL을 바꾸는 **액션**
- 리렌더 발생 시점 — `searchParams`가 바뀔 때 React가 자동 처리

바뀐 부분을 나란히 놓으면 아래와 같음

| 항목 | before | after |
|---|---|---|
| 진실 공급원 | URL + useState (둘) | URL (하나) |
| URL → 화면 | 마운트 시 1회 | 매 렌더 |
| 화면 → URL | useEffect 부수효과 | setValue 직접 호출 |
| 훅 라인 수 | 32줄 | 24줄 |
| 무한 replace 위험 | 있음 | 구조적으로 없음 |

## 남는 교훈

`useState`에 담을 값과 담으면 안 되는 값의 기준 — **다른 곳에서 이미 관리되는 값이면 담지 않는다.**

- URL·props·서버 응답에서 계산 가능한 값을 state에 복사 시 — 원본과 사본을 맞추는 코드 발생
- 그 코드의 운명 — 언젠가 어긋남

증상만 보면 "URL 변화를 감지해 state를 갱신하는 useEffect 추가"가 자연스러운 수정처럼 보인다. 하지만 그 선택의 결과는 반대였다.

- 결과 — 배선 하나 추가
- 그때부터 — state → URL과 URL → state가 서로를 트리거하는 진짜 루프
- 판단 기준 — 동기화 코드를 추가하고 싶어지는 시점이 대체로 동기화 자체를 없앨 시점

useState/useEffect/useMemo를 셋 다 지웠는데 기능이 늘었다는 게 이 수정에서 제일 마음에 드는 부분이다.
