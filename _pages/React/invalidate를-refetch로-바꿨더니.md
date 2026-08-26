---
title:  "invalidateQueries를 refetchQueries로 바꿨더니"

categories:
  - React
tags:
  - AI
  - Claude Code
  - TanStack Query
  - React
  - Next.js

date: 2026-05-07
thumbnail: "/assets/img/thumbnail/sample.png"
---
## 문제: mutation 후 목록이 즉시 안 바뀐다

관리자 포털과 사용자 포털 양쪽에서 반복된 QA 피드백.

- 증상 — 항목을 삭제하거나 생성했는데 목록이 그대로
- 반영 시점 — 탭을 옮겼다 오거나 새로고침한 뒤
- 전제 — mutation 성공 후 `invalidateQueries` 호출 중이었음

## 원인: invalidate는 lazy하다

`invalidateQueries`의 동작 — 쿼리를 stale로 표시. 그 다음 동작은 쿼리 상태에 따라 분기.

- **활성(active)** 쿼리 — 화면 어딘가에서 구독 중이면 즉시 refetch
- **비활성(inactive)** 쿼리 — 마운트된 옵저버가 없으면 표시만 하고 종료. 다음에 구독될 때 refetch

문제 화면들의 구조:

- 대부분 탭 구조
- 기대 동작 — 탭 A에서 작업하고 탭 B의 목록이 갱신되는 것
- 실제 — 탭 B 컴포넌트가 언마운트 상태라 해당 쿼리는 비활성
- invalidate가 남기는 것 — "다음에 볼 때 새로 받아라"는 메모뿐

<div class="diagram" role="img" aria-label="활성 쿼리와 비활성 쿼리에서 invalidate 동작이 갈리는 구조">
{% include diagrams/invalidate--active-inactive.svg %}
</div>

여기에 겹친 변수들 — 모달 닫은 뒤 목록 재마운트 타이밍, `staleTime` 설정, 캐시 gc 시점.

- 사용자 체감: "가끔 되고 가끔 안 되는" 동작

- `refetchQueries`의 동작 — 활성 여부를 따지지 않고 지금 다시 요청
- 조치 — `invalidateQueries`를 `refetchQueries`로 일괄 치환

```diff
- queryClient.invalidateQueries({ queryKey: notificationKeys.lists() });
+ queryClient.refetchQueries({ queryKey: notificationKeys.lists() });
```

정리:

| | invalidateQueries | refetchQueries |
|---|---|---|
| 활성 쿼리 | 즉시 refetch | 즉시 refetch |
| 비활성 쿼리 | stale 표시만 (lazy) | 즉시 refetch |
| 네트워크 비용 | 필요한 만큼 | 안 보는 화면도 요청 |

이건 트레이드오프지 정답이 아니다.

- 지불한 비용: 안 보이는 화면까지 지금 요청
- 산 것: 확실한 갱신
- 선택 근거: 목록 규모가 작음 + QA 국면에서 "안 바뀐다" 리포트 감소가 우선

## 진짜 버그: 공통 팩토리 안의 조건부 분기

일괄 치환 이후 발견한 더 고약한 것:

- 구조 — mutation 훅들이 공통 팩토리 `createSuccessHandler`로 onSuccess 생성
- 그 안의 코드:

```ts
if (keys.lists) {
  queryClient.refetchQueries({ queryKey: keys.lists() });
}
if (keys.detail && data?.id) {
  queryClient.refetchQueries({ queryKey: keys.detail(data.id) });
}
```

두 번째 조건이 문제:

- 조건 — `data?.id`가 있을 때만 상세 캐시 갱신
- 이 프로젝트의 실제 mutation 응답 — 생성/수정된 리소스의 id를 미포함. 성공 여부와 메시지만 반환
- 결과 — `data?.id`가 `undefined`라 조건이 거짓, 상세 캐시 갱신이 **조용히 스킵**
- 에러/경고 — 없음
- 사용자가 보는 것 — 상세 화면에 수정 전 데이터 그대로

수정 방향 — 조건 제거:

```diff
- if (keys.detail && data?.id) {
-   queryClient.refetchQueries({ queryKey: keys.detail(data.id) });
+ if (keys.details) {
+   queryClient.invalidateQueries({ queryKey: keys.details() });
  }
```

- `keys.details()`의 의미 — 이 도메인의 상세 쿼리 전체를 가리키는 상위 키
- 효과 — 어떤 id인지 몰라도 상세 캐시 전부를 무효화
- 부수 효과 — 응답 페이로드에 대한 의존 제거

여기서 `refetch`가 아니라 `invalidate`를 쓴 이유:

- 상세 캐시 전체를 지금 다시 받으면 — 캐시에 남은 모든 상세 항목을 한꺼번에 요청
- 상세의 갱신 필요 시점 — 사용자가 열어볼 때. 즉 lazy가 적절

목록은 refetch, 상세는 invalidate — 같은 핸들러 안에서 둘을 다르게 쓰는 것이 의도된 선택

## 팩토리로 감싼 코드는 아무도 안 본다

같은 커밋에서 mutation 훅들을 훑다가 나온 것들:

- `useSignUp` — `onSuccess`가 사실상 비어 있음. 주석 처리된 죽은 코드 여덟 줄만 있고 실행 문장 0개
- `useCreateNotification` — `onSuccess`와 `onError` 자체가 부재. `mutationFn`만 있는 훅
- `useRefreshToken` — 토큰 저장 로직이 통째로 주석 처리. 갱신에 성공해도 새 토큰을 아무 데도 저장 안 함
- `useUpdateMenuGroup` — `onSuccess`만 있고 `onError` 없음

공통점:

- 겉보기 — 다른 훅들과 동일한 모양
- 파일 구성 — `useMutation({ mutationFn, onSuccess: createSuccessHandler(...) })` 패턴이 열 몇 개 나열
- 결과 — 그중 하나만 `onSuccess`가 없다는 걸 눈으로 잡아내기 어려움
- 리뷰에서도 안 걸리는 이유 — 팩토리로 감싸면 각 훅의 실제 동작이 호출부에 안 보임

`data?.id` 조건도 동일 문제.

- 팩토리 내부 조건부 분기 → 각 호출부에서 참/거짓 판별 불가
- 실패해도 무음

**공통화는 중복을 줄이지만 동시에 실패를 안 보이게 만든다.**

## 안티패턴 하나

탭 전환 시 갱신 문제를 다르게 푼 커밋도 존재. 탭 값 변경 시 `useEffect`로 `refetch()`를 강제 호출하는 코드를 네 개 페이지에 복붙:

```tsx
useEffect(() => {
  if (value === "codeGroup") refetchCodeGroupList();
  if (value === "code") refetchCodeList();
}, [value]);
```

- 당장의 동작 — 정상
- 책임 이동 — 캐시 갱신이 mutation 쪽에서 화면 쪽으로 이전
- 확산 비용 — 탭이 있는 페이지마다 이 블록 복사
- 새 탭 추가 시 — `if`가 증가, 빠뜨리면 그 탭만 갱신 누락

무효화의 올바른 위치 — 데이터를 바꾼 쪽

## 남는 교훈

invalidate와 refetch의 차이는 "언제 다시 받느냐"가 아니라 **"안 보고 있는 데이터를 지금 받을 것이냐"** 다.

- 답을 결정하는 변수: 화면 구조(탭 다수 여부) + 데이터 크기
- 따라서 프로젝트마다 상이

**공통 핸들러 팩토리의 조건부 분기는 재고 대상.**

- 조건이 거짓일 때: 아무 일도 없고 아무도 인지 불가
- 권장: 팩토리에는 무조건 실행되는 것만 배치
- 분기 필요 시: 팩토리 자체를 둘로 분리
