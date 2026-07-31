---
title:  "invalidateQueries를 refetchQueries로 바꿨더니"

categories:
  - AI
tags:
  - AI
  - Claude Code
  - TanStack Query
  - React
  - Next.js

date: 2026-05-07
thumbnail: "/assets/img/thumbnail/sample.png"
---

# 문제: mutation 후 목록이 즉시 안 바뀐다

관리자 포털과 사용자 포털 양쪽에서 같은 QA 피드백이 반복됐다. 항목을 삭제하거나 생성했는데 목록이 그대로다. 탭을 옮겼다 오거나 새로고침하면 그제야 반영된다.

mutation 성공 후 `invalidateQueries`를 호출하고 있었는데도 그랬다.

# 원인: invalidate는 lazy하다

`invalidateQueries`는 쿼리를 stale로 표시한다. 그 다음 동작은 쿼리의 상태에 따라 갈린다.

- **활성(active)** 쿼리 — 지금 화면 어딘가에서 구독 중이면 즉시 refetch
- **비활성(inactive)** 쿼리 — 마운트된 옵저버가 없으면 표시만 하고 끝. 다음에 누군가 구독할 때 refetch

문제 화면들이 대부분 탭 구조였다. 탭 A에서 작업하고 탭 B의 목록이 갱신되기를 기대하는데, 탭 B 컴포넌트는 언마운트돼 있으니 그 쿼리는 비활성이다. invalidate는 "다음에 볼 때 새로 받아라"라고 메모만 남긴다. 그리고 모달을 닫고 목록이 다시 마운트되는 타이밍, `staleTime` 설정, 캐시 gc 시점이 겹치면서 사용자 눈에는 "가끔 되고 가끔 안 되는" 것으로 보였다.

`refetchQueries`는 활성 여부를 안 따지고 지금 다시 요청한다. 그래서 `invalidateQueries`를 `refetchQueries`로 일괄 치환했다.

```diff
- queryClient.invalidateQueries({ queryKey: notificationKeys.lists() });
+ queryClient.refetchQueries({ queryKey: notificationKeys.lists() });
```

정리하면 이렇다.

| | invalidateQueries | refetchQueries |
|---|---|---|
| 활성 쿼리 | 즉시 refetch | 즉시 refetch |
| 비활성 쿼리 | stale 표시만 (lazy) | 즉시 refetch |
| 네트워크 비용 | 필요한 만큼 | 안 보는 화면도 요청 |

이건 트레이드오프지 정답이 아니다. 안 보이는 화면까지 지금 요청하는 대가로 확실한 갱신을 산 것이다. 목록이 크지 않고 QA 국면에서 "안 바뀐다"는 리포트를 줄이는 게 우선이라 이쪽을 골랐다.

# 진짜 버그: 공통 팩토리 안의 조건부 분기

일괄 치환 이후에 더 고약한 걸 발견했다. mutation 훅들이 공통 팩토리 `createSuccessHandler`로 onSuccess를 만들어 쓰고 있었는데, 그 안이 이랬다.

```ts
if (keys.lists) {
  queryClient.refetchQueries({ queryKey: keys.lists() });
}
if (keys.detail && data?.id) {
  queryClient.refetchQueries({ queryKey: keys.detail(data.id) });
}
```

두 번째 조건이 문제다. `data?.id`가 있을 때만 상세 캐시를 갱신한다. 그런데 이 프로젝트의 여러 mutation 응답은 생성/수정된 리소스의 id를 담아주지 않는다. 성공 여부와 메시지만 온다.

그러면 `data?.id`가 `undefined`라서 조건이 거짓이 되고, 상세 캐시 갱신이 **조용히 스킵된다.** 에러도 없고 경고도 없다. 상세 화면을 열어보면 수정 전 데이터가 그대로 있다.

수정은 조건을 없애는 방향이었다.

```diff
- if (keys.detail && data?.id) {
-   queryClient.refetchQueries({ queryKey: keys.detail(data.id) });
+ if (keys.details) {
+   queryClient.invalidateQueries({ queryKey: keys.details() });
  }
```

`keys.details()`는 이 도메인의 상세 쿼리 전체를 가리키는 상위 키다. 어떤 id인지 몰라도 상세 캐시 전부를 무효화할 수 있다. 응답 페이로드에 대한 의존이 사라진다.

여기서는 `refetch`가 아니라 `invalidate`를 썼다. 상세 캐시 전체를 지금 다시 받아오면 캐시에 남아 있는 모든 상세 항목을 한꺼번에 요청하게 된다. 상세는 사용자가 열어볼 때 갱신되면 충분하니 lazy가 맞다. 목록은 refetch, 상세는 invalidate — 같은 핸들러 안에서 둘을 다르게 쓰는 게 의도된 선택이다.

# 팩토리로 감싼 코드는 아무도 안 본다

같은 커밋에서 mutation 훅들을 훑다가 이런 것들이 나왔다.

- `useSignUp`의 `onSuccess`가 사실상 비어 있었다. 안에 주석 처리된 죽은 코드만 여덟 줄 남아 있고 실행되는 문장이 하나도 없었다.
- `useCreateNotification`은 `onSuccess`와 `onError`가 아예 없었다. `mutationFn`만 있는 훅이었다.
- `useRefreshToken`은 토큰 저장 로직이 통째로 주석 처리돼 있었다. 갱신에 성공해도 새 토큰을 아무 데도 안 넣는다.
- `useUpdateMenuGroup`은 `onSuccess`만 있고 `onError`가 없었다.

공통점이 있다. 이 훅들은 겉보기에 다른 훅들과 똑같이 생겼다. `useMutation({ mutationFn, onSuccess: createSuccessHandler(...) })` 패턴이 열 몇 개 나열된 파일에서, 그중 하나만 `onSuccess`가 없다는 걸 눈으로 잡아내기 어렵다. 팩토리로 감싸면 각 훅의 실제 동작이 호출부에 안 보이니 리뷰에서도 안 걸린다.

`data?.id` 조건도 같은 문제다. 팩토리 안에 넣은 조건부 분기는 각 호출부에서 참인지 거짓인지 알 수 없다. 실패해도 조용하다. **공통화는 중복을 줄이지만 동시에 실패를 안 보이게 만든다.**

# 안티패턴 하나

탭 전환 시 갱신 문제를 다르게 푼 커밋도 있었다. 탭 값이 바뀌면 `useEffect`로 `refetch()`를 강제 호출하는 코드를 네 개 페이지에 복붙한 것이다.

```tsx
useEffect(() => {
  if (value === "codeGroup") refetchCodeGroupList();
  if (value === "code") refetchCodeList();
}, [value]);
```

당장은 동작한다. 하지만 캐시 갱신 책임이 mutation 쪽이 아니라 화면 쪽으로 넘어가고, 탭이 있는 페이지마다 이 블록을 복사해야 한다. 새 탭을 추가할 때마다 `if`가 늘고, 빠뜨리면 그 탭만 갱신이 안 된다. 무효화는 데이터를 바꾼 쪽에서 하는 게 맞다.

# 남는 교훈

invalidate와 refetch의 차이는 "언제 다시 받느냐"가 아니라 **"안 보고 있는 데이터를 지금 받을 것이냐"** 다. 그 답이 화면 구조(탭이 많은지)와 데이터 크기에 달려 있어서 프로젝트마다 다르다.

그리고 공통 핸들러 팩토리에 조건부 분기를 넣는 건 다시 생각해볼 일이다. 조건이 거짓일 때 아무 일도 안 일어나고 아무도 모른다. 팩토리에는 무조건 실행되는 것만 넣고, 갈라져야 하면 팩토리를 두 개로 나누는 편이 낫다.
