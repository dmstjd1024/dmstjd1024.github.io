---
title:  "localStorage에 남은 isAuthenticated: true가 로그인을 막았다"

categories:
  - React
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

사용자 포털 버그 리포트

- 한동안 안 쓰다가 다시 진입하면 로그인 화면이 "로딩 중..."만 표시한 채 정지
- 폼 미표시 → 로그인 경로 없음
- localStorage 비우면 정상 복귀

localStorage를 비워야 풀린다 → 원인은 지속된 상태

## 원인: persist된 인증 상태와 토큰 수명이 어긋난다

- 인증 저장 방식 — Zustand `persist` 미들웨어로 localStorage 저장
- 저장 대상에 `isAuthenticated` 불리언 포함
- 토큰의 실제 만료와 이 불리언은 무연결 → 토큰이 만료돼도 `isAuthenticated`는 계속 `true`

<div class="diagram" role="img" aria-label="저장된 인증 플래그와 실제 토큰 만료가 연결되어 있지 않은 구조">
{% include diagrams/persist--stale-flag.svg %}
</div>

이 어긋남의 정리 담당 — 앱 부팅 시 도는 `checkAuth()`. 그 코드는 아래와 같음

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

- 논리 자체는 자연스러움 — 만료 시 리프레시 시도, 리프레시 토큰 없으면 로그아웃
- 실제 문제 — `refreshAuth()`가 아무것도 갱신하지 않는 껍데기
- 구조상 이 시스템은 토큰 갱신을 서버 필터에 위임 → 클라이언트 `refreshAuth()`는 이름만 남고 stale 인증 상태 미정리

결과적으로 이 경로를 타면 `isAuthenticated: true`가 그대로 살아남는다. 만료된 토큰과 참인 인증 플래그가 공존하는 상태로 앱이 부팅된다.

그리고 `LoginForm`의 렌더 가드가 여기서 막힘

```tsx
if (isAnyLoading || userLoading || isAuthenticated) {
  return <div className="p-4 text-white">로딩 중...</div>;
}
```

세 조건 중 두 개가 문제

- `isAuthenticated` — `true`. persist된 stale 값 그대로
- `userLoading` — `true`. `useUser` 쿼리가 만료 토큰으로 사용자 정보를 요청하고 실패한 뒤 재시도 중이라 계속 로딩

두 조건 모두 스스로 풀릴 방법이 없다. 로그인 폼은 영영 렌더되지 않고, 리다이렉트도 일어나지 않는다. 교착이다.

## 어떻게 고쳤나

수정 지점 두 군데

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

- 분기 제거
- 클라이언트가 토큰 만료 확인 시 `refreshToken` 유무와 무관하게 로그아웃

`refreshAuth()`가 상태를 정리하지 않는 이상 — 그쪽으로 보내는 건 정리 없이 통과시키는 것과 동일

### 2. 렌더 가드에서 리다이렉트 책임 분리

```tsx
// userLoading(useUser 재시도 대기)은 로그인 폼 표시를 막지 않음
// isAuthenticated는 useEffect에서 리다이렉트 처리하므로 여기서는 제외
if (isAnyLoading) {
  return <div className="p-4 text-white">로딩 중...</div>;
}
```

- 잔존 조건은 `isAnyLoading` 하나
- 정의 — `isLoading || loginMutation.isPending`. 사용자가 방금 누른 로그인 요청 진행 중일 때만 참. 시작과 끝이 명확한 조건
- `isAuthenticated` 제외 — 이미 인증된 사용자를 로그인 페이지에서 내보내는 건 `useEffect` 리다이렉트의 역할

같은 상태를 렌더 가드에서도 처리 시 — 책임이 둘로 분산

## 왜 렌더 가드와 리다이렉트를 같이 두면 교착인가

이게 이 버그의 일반화된 형태

- `useEffect` 리다이렉트와 렌더 가드는 실행 순서가 다름 — 렌더가 먼저, 이펙트가 나중
- `isAuthenticated`가 참 → 렌더 가드가 로딩 화면 반환 → 그 렌더에서는 아무것도 안 보이고 이펙트가 리다이렉트 시작
- 정상 경로에서는 한 프레임이라 무감지

문제 상황 — `isAuthenticated`가 참인데 리다이렉트가 미실행 또는 실패

- 화면에 남는 것 — 렌더 가드가 반환한 로딩 화면뿐
- 그 화면의 구성 — 상태를 바꿀 수 있는 요소 전무

사용자에게는 탈출구가 없다.

`userLoading`도 같은 함정

- 쿼리 실패 후 재시도 대기 중인 `isLoading` — 사용자 행위와 무관하게 길어질 수 있음
- 인증이 깨진 상황 — 영원히 미종료
- 규칙 — 끝난다는 보장이 없는 조건은 렌더 가드에 넣지 않음

| 조건 | 종료 보장 | 렌더 가드에 넣어도 되나 |
|---|---|---|
| `loginMutation.isPending` | 응답 오면 끝남 | 가능 |
| `userLoading` (재시도 포함) | 없음 | 불가 |
| `isAuthenticated` | 상태가 안 바뀌면 계속 참 | 불가 — 리다이렉트가 담당 |

## 남는 교훈

`persist`는 편하지만, 지속되는 값 중에 **외부 수명에 묶인 것**이 있으면 위험하다.

- `isAuthenticated`의 정체 — 토큰 수명에 종속된 파생값인데 원본과 별도 저장
- 원본 만료 시 — 사본은 그대로
- 예방책 — persist 대상에서 제외하고 토큰에서 매번 계산

그리고 챙길 만한 규칙 하나 — "리다이렉트가 처리할 상태를 렌더 가드에도 넣지 마라"

- 이유 — 리다이렉트가 안 도는 순간 그 렌더 가드가 사용자를 가둠
