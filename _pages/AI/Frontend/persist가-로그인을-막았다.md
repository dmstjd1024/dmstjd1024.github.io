---
title:  "localStorage에 남은 isAuthenticated: true가 로그인을 막았다"

categories:
  - AI
tags:
  - AI
  - Claude Code
  - Zustand
  - React
  - Next.js

date: 2026-05-09
thumbnail: "/assets/img/thumbnail/sample.png"
---

## 문제: 로그인 페이지가 "로딩 중..."에서 안 넘어간다

사용자 포털에서 올라온 버그다. 한동안 안 쓰다가 다시 들어오면 로그인 화면이 "로딩 중..."만 띄운 채 멈춘다. 폼이 안 나오니 로그인할 방법이 없다. localStorage를 비우면 정상으로 돌아왔다.

localStorage를 비워야 풀린다는 건 지속된 상태가 원인이라는 뜻이다.

## 원인: persist된 인증 상태와 토큰 수명이 어긋난다

인증은 Zustand `persist` 미들웨어로 localStorage에 저장한다. 저장 대상에 `isAuthenticated` 불리언이 들어 있다. 토큰의 실제 만료와 이 불리언은 아무 연결이 없다. 토큰이 만료돼도 localStorage 안의 `isAuthenticated`는 계속 `true`다.

이 어긋남을 정리하는 게 앱 부팅 시 도는 `checkAuth()`의 역할이었는데, 그 코드가 이랬다.

```ts
// 토큰 유효성 검사
if (!isTokenValid(token)) {
  // 토큰이 만료되었고 리프레시 토큰이 있으면 갱신 시도
  if (refreshToken) {
    await get().refreshAuth();
  } else {
    // 리프레시 토큰도 없으면 로그아웃
    get().logout();
  }
  set({ isLoading: false });
  return;
}
```

논리 자체는 자연스럽다. 만료됐으면 리프레시를 시도하고, 리프레시 토큰도 없으면 로그아웃. 문제는 `refreshAuth()`가 실제로는 아무것도 갱신하지 않는 껍데기였다는 점이다. 이 시스템은 토큰 갱신을 서버 필터에 위임하는 구조라, 클라이언트의 `refreshAuth()`는 이름만 남고 stale 인증 상태를 정리하지 않는다.

결과적으로 이 경로를 타면 `isAuthenticated: true`가 그대로 살아남는다. 만료된 토큰과 참인 인증 플래그가 공존하는 상태로 앱이 부팅된다.

그리고 `LoginForm`의 렌더 가드가 여기서 막혔다.

```tsx
if (isAnyLoading || userLoading || isAuthenticated) {
  return <div className="p-4 text-white">로딩 중...</div>;
}
```

세 조건 중 두 개가 문제다.

- `isAuthenticated`가 `true`다. persist된 stale 값 그대로.
- `userLoading`도 `true`다. `useUser` 쿼리가 만료 토큰으로 사용자 정보를 요청하고 실패한 뒤 재시도를 도는 중이라 계속 로딩이다.

두 조건 모두 스스로 풀릴 방법이 없다. 로그인 폼은 영영 렌더되지 않고, 리다이렉트도 일어나지 않는다. 교착이다.

## 어떻게 고쳤나

두 군데를 고쳤다.

### 1. 클라이언트 만료 판정이면 즉시 로그아웃

```ts
if (!isTokenValid(token)) {
  // 클라이언트 측 토큰 만료 → 즉시 로그아웃하여 stale 인증 상태 제거
  // (refreshAuth는 실제 갱신 없이 서버 필터에 위임하므로 여기서 정리)
  get().logout();
  set({ isLoading: false });
  return;
}
```

분기를 없앴다. 클라이언트가 토큰 만료를 확인했으면 `refreshToken` 유무와 무관하게 로그아웃한다. `refreshAuth()`가 상태를 정리하지 않는 이상, 그쪽으로 보내는 건 정리 없이 통과시키는 것과 같다.

### 2. 렌더 가드에서 리다이렉트 책임 분리

```tsx
// userLoading(useUser 재시도 대기)은 로그인 폼 표시를 막지 않음
// isAuthenticated는 useEffect에서 리다이렉트 처리하므로 여기서는 제외
if (isAnyLoading) {
  return <div className="p-4 text-white">로딩 중...</div>;
}
```

`isAnyLoading`만 남겼다. 이건 `isLoading || loginMutation.isPending`이라, 사용자가 방금 누른 로그인 요청이 진행 중일 때만 참이 된다. 시작과 끝이 명확한 조건이다.

`isAuthenticated`는 뺐다. 이미 인증된 사용자를 로그인 페이지에서 내보내는 건 `useEffect`의 리다이렉트가 하는 일이다. 같은 상태를 렌더 가드에서도 처리하면 책임이 둘로 갈린다.

## 왜 렌더 가드와 리다이렉트를 같이 두면 교착인가

이게 이 버그의 일반화된 형태다.

`useEffect` 리다이렉트와 렌더 가드는 실행 순서가 다르다. 렌더가 먼저고 이펙트가 나중이다. `isAuthenticated`가 참일 때 렌더 가드가 로딩 화면을 반환하면, 그 렌더에서는 아무것도 안 보이고 이펙트가 리다이렉트를 시작한다. 정상 경로에서는 이게 한 프레임이라 티가 안 난다.

문제는 `isAuthenticated`가 참인데 리다이렉트가 실행되지 않거나 실패하는 경우다. 이때 화면에 남는 건 렌더 가드가 반환한 로딩 화면뿐이고, 그 화면에는 상태를 바꿀 수 있는 요소가 하나도 없다. 사용자에게는 탈출구가 없다.

`userLoading`도 같은 함정이다. 쿼리 실패 후 재시도 대기 중인 `isLoading`은 사용자 행위와 무관하게 길어질 수 있고, 인증이 깨진 상황에서는 영원히 안 끝난다. 끝난다는 보장이 없는 조건은 렌더 가드에 넣으면 안 된다.

| 조건 | 종료 보장 | 렌더 가드에 넣어도 되나 |
|---|---|---|
| `loginMutation.isPending` | 응답 오면 끝남 | 가능 |
| `userLoading` (재시도 포함) | 없음 | 불가 |
| `isAuthenticated` | 상태가 안 바뀌면 계속 참 | 불가 — 리다이렉트가 담당 |

## 남는 교훈

`persist`는 편하지만, 지속되는 값 중에 **외부 수명에 묶인 것**이 있으면 위험하다. `isAuthenticated`는 토큰 수명에 종속된 파생값인데 원본과 따로 저장됐다. 원본이 만료돼도 사본은 그대로다. 애초에 이걸 persist 대상에서 빼고 토큰에서 매번 계산했다면 이 버그는 생길 수 없었다.

그리고 "리다이렉트가 처리할 상태를 렌더 가드에도 넣지 마라"는 규칙 하나는 챙길 만하다. 리다이렉트가 안 도는 순간 그 렌더 가드가 사용자를 가둔다.
