---
title:  "인증 필터가 매 요청 DB를 네 번 때리고 있었다"

categories:
  - Spring
tags:
  - AI
  - Claude Code
  - Spring
  - 성능

date: 2026-05-07
thumbnail: "/assets/img/thumbnail/spring_thumbnail.webp"
card_thumbnail: "/assets/img/thumbnail/spring_card.webp"
---
## 문제: TPS가 안 나온다

- 부하 테스트에서 목표 TPS 미달
- 애플리케이션 로직 자체는 가벼움
- 조사 방향: 비즈니스 코드가 아니라 **모든 요청이 반드시 지나가는 경로**

- 구성: Spring Security + JWT
- 필터 체인 추적 결과: DB 접근이 겹겹이 누적

| 지점 | 하는 일 |
|---|---|
| `JwtFilter` | 토큰에서 username 꺼내 User 조회 |
| `ResourceAuthorizationFilter` | User를 **다시** 조회 |
| `ResourceAuthorizationFilter` | 역할별 메뉴 권한 목록 조회 (`findByRoleIn`) |
| `HttpReqResLoggingFilter` | 감사 로그 INSERT |

- 리소스 하나 읽는 GET 요청 → 인증·인가·로깅만으로 DB 4회 접근
- 캐시 없음 → 100% 매 요청 발생

<div class="diagram" role="img" aria-label="필터 체인에서 DB 를 네 번 접근하는 구조">
{% include diagrams/auth-filter--four-queries.svg %}
</div>

## 어떻게 고쳤나 — 29분에 커밋 여섯 개

- 2026년 5월 7일 저녁 29분, 커밋 6개가 순서대로 반영
- 순서 자체가 작업 방식 — 하나 없애고, 다시 재고, 다음으로

아래 네 단계로 묶어 정리했다. 나머지 한 커밋은 2번이 만든 회귀를 3분 뒤에 고친 것이라 [같은 User인데 권한 검사가 깨졌다](/BlockChain/Backend/같은-user인데-권한-검사가-깨졌다)에 따로 썼다.

### 1. 감사 로그 INSERT를 요청 경로에서 빼냈다

- 가장 명백한 대상: 감사 로그
- 응답 생성에 전혀 필요 없는 쓰기 작업이 응답 경로 안에 존재
- 조치: `@Async`로 분리

여기서 예상 못 한 문제가 나왔다.

- 기존 구현: `saveAuditLog` 안에서 `SecurityContext`로 현재 사용자 조회
- 충돌 — **SecurityContext는 기본적으로 비동기 스레드에 전파되지 않는다.**
- 이유: `ThreadLocal` 기반

- 선택지 1: 전파 설정(`DelegatingSecurityContextAsyncTaskExecutor` 등)
- 선택지 2(채택): 필터에서 username을 미리 꺼내 인자로 전달, 비동기 쪽은 SecurityContext 미사용

```java
// SecurityContext 가 불필요한 비동기 조회용
User findByUsernameForAudit(String username);
```

- 메서드 하나 증가
- 대신 비동기 경계에서 암묵적 컨텍스트 의존 제거
- 로깅 필터가 이미 아는 값을 넘기는 것뿐 → 전파 설정 삽입보다 의존 관계 명확

<div class="diagram" role="img" aria-label="SecurityContext 가 비동기 스레드로 전파되지 않는 문제와 두 선택지">
{% include diagrams/auth-filter--securitycontext.svg %}
</div>

### 2. 중복 조회를 request attribute로 제거

- `JwtFilter`가 조회한 User를 `ResourceAuthorizationFilter`가 재조회
- 두 필터는 같은 요청 스레드에서 순차 실행
- 조치: 앞에서 request attribute에 넣고 뒤에서 꺼냄
- 커밋 diff: 6줄 추가 / 2줄 삭제
- 비용 대비 효과: 이런 게 제일 저렴

### 3. 인메모리 캐시 — JwtFilter와 메뉴 권한

- 남은 두 건: 값 자체가 요청마다 바뀌지 않는 조회
- 조치: `ConcurrentHashMap`을 빈으로 올려 캐시로 사용

```java
@Bean
public ConcurrentHashMap<String, User> userAuthCache() {
    return new ConcurrentHashMap<>();
}
```

- 메뉴 권한(`findByRoleIn`)도 동일 방식으로 캐싱

### 4. HikariCP 풀 20 → 50

- 앞의 네 건으로 요청당 DB 접근 감소
- 마지막으로 커넥션 풀 20 → 50
- 커밋 메시지: "TPS 100 달성"
- 한 줄짜리 설정 변경

순서가 중요하다. 풀부터 늘렸다면 불필요한 쿼리 네 개를 그대로 둔 채 커넥션만 더 태우는 꼴이 됐을 것이다. **쿼리를 없앤 다음에 남은 쿼리를 위해 풀을 늘리는 것**과 순서가 반대다.

<div class="diagram" role="img" aria-label="쿼리를 먼저 없애고 마지막에 풀을 늘린 순서">
{% include diagrams/auth-filter--fix-order.svg %}
</div>

## 솔직히 써야 할 트레이드오프

단순 `ConcurrentHashMap` 캐시를 쓸 때 함께 따라오는 문제가 있다. TTL도,
최대 크기도, 변경 시 evict도 없다는 것.

무효화 전략 없는 권한 캐시가 일반적으로 안고 가는 것:

- 권한·역할 변경이 캐시 수명 동안 반영되지 않음
- 엔트리가 쌓이기만 하고 줄지 않음

그래서 권한 캐시는 **무효화 설계를 함께 정하지 않으면 도입하지 않는 편이 낫다.**
선택지는 Caffeine TTL 캐시, 또는 Redis 같은 공유 저장소 + 변경 시 evict다.

- 자료구조 선택은 "옳아서"가 아니라 "그 시점 요구에 충분해서"인 경우가 많다
- 그 구분을 기록해두면 나중에 바꿀 때 판단 근거가 남는다

## 곁다리: 로깅 필터가 메모리를 먹고 있었다

- 같은 시기, 로깅 필터의 다른 문제도 정리
- 증상: 응답 바디를 로그에 남기려고 무조건 `byte[]`로 읽음
- 대상에 이미지·파일 다운로드 응답도 포함
- 큰 응답 몇 개가 겹치면 힙을 그대로 밀어냄

- 조치: 크기와 Content-Type을 **먼저 확인하고** 읽도록 변경
- 이미지 타입이거나 50KB 초과 → 바디를 읽지 않고 조기 반환
- 근거: 그 지점부터는 로그에서 얻는 정보의 가치가 비용을 못 따라감

## 남는 교훈

**측정 → 병목 하나 제거 → 재측정.**

- 시간순 커밋 6개 = 여섯 번 나눠 확인했다는 뜻
- 한 커밋에 몰아넣었을 경우: 변경별 기여도 파악 불가, 문제 발생 시 되돌릴 단위도 부재

**모든 요청이 지나가는 경로부터 본다.** 필터 체인은 요청 수만큼 곱해지는 곳이라, 여기 있는 쿼리 하나는 컨트롤러 안의 쿼리 하나와 무게가 다르다.

**설정값 조정은 마지막이다.**

- 풀 크기 증가의 성격: 병목 제거가 아니라 병목을 더 많이 감당하게 만드는 일
- 순서: 먼저 없앨 수 있는 걸 없앤 뒤 착수
