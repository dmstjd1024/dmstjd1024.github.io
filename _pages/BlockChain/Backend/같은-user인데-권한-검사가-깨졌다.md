---
title:  "같은 User인데 권한 검사가 깨졌다 — 재사용의 숨은 계약"

categories:
  - BlockChain
tags:
  - BlockChain
  - AI
  - Claude Code
  - Spring
  - JPA
  - 성능

date: 2026-05-07
thumbnail: "/assets/img/thumbnail/bricks.webp"
---
## 3분 만에 되돌린 최적화

인증 경로에서 DB를 네 번 때리던 걸 걷어낸 이야기는 [인증 필터가 매 요청 DB를 네 번 때리고 있었다](/AI/Backend/인증-필터가-매-요청-db를-네번-때렸다)에 썼다. 감사 로그 비동기화, 커넥션 풀, 인메모리 캐시까지 29분 동안 커밋 여섯 개가 나갔다.

그 글에 안 쓴 게 하나 있다. **여섯 중 하나는 3분 전 내 최적화가 만든 회귀를 고치는 커밋이었다.**

- 20:24:19 — 사용자 재조회를 없앴다
- 20:27:11 — 그것 때문에 깨진 권한 검사를 고쳤다

2분 52초. 이 글은 그 사이에 무슨 일이 있었는지에 대한 것이다.

## 없앤 것: 같은 요청에서 두 번 조회

필터 두 개가 같은 사용자를 각자 조회하고 있었다.

- 인증 필터 — 토큰에서 username을 꺼내 User 조회
- 권한 필터 — 그 사용자의 역할을 보려고 User를 **다시** 조회

앞에서 조회한 걸 뒤에서 쓰면 왕복 한 번이 사라진다. 요청 스코프에 얹어 넘겼다.

```java
// 인증 필터 — 조회한 것을 넣어둔다
request.setAttribute("AUTH_USER", user);
```

```java
// 권한 필터 — 있으면 쓰고, 없으면 직접 조회 (다른 경로 대비)
User user = (User) request.getAttribute("AUTH_USER");
if (user == null) {
    user = userRepository.findUserWithRoleByUsername(username)
        .orElseThrow(() -> new BusinessLogicException(ExceptionCode.NOT_FOUND_USER));
}
```

fallback까지 남겼으니 안전하다고 생각했다. **그런데 권한 검사가 통과하지 못했다.**

<div class="diagram" role="img" aria-label="앞 필터가 조회한 엔티티를 뒤 필터가 재사용하게 바꿨더니, 두 쿼리의 fetch 범위가 달라 권한 검사가 깨진 과정">
{% include diagrams/tps--fetch-contract.svg %}
</div>

## 원인: 두 필터가 서로 다른 쿼리를 쓰고 있었다

권한 검사는 사용자의 역할 목록을 본다.

```java
List<Role> roleList = user.getUserRoleList().stream()
    .map(UserRole::getRole)
    .distinct()
    .toList();
```

그리고 두 필터가 User를 가져오던 쿼리는 이랬다.

| 필터 | 쿼리 | `userRoleList` |
|---|---|---|
| 권한 필터 (원래 자기가 쓰던 것) | `findUserWithRoleByUsername` | fetch join 됨 |
| 인증 필터 (넘겨준 쪽) | `findByDelYnFalseAndUsername` | **없음** |

- 권한 필터는 원래 **역할을 fetch join 한 쿼리**로 직접 조회했다. 그래서 `getUserRoleList()`가 동작했다
- 재조회를 없애면서 받게 된 객체는 **역할이 로딩되지 않은** 사용자다
- 필터 체인은 트랜잭션·영속성 컨텍스트 밖이라, 그 시점에 역할 목록을 채울 방법이 없다

fallback은 도움이 되지 않았다. `AUTH_USER`가 `null`이 아니었기 때문이다 — 객체는 멀쩡히 있었고, 안이 비어 있었을 뿐이다. **`null` 체크는 "값이 있나"를 묻지, "쓸 수 있는 값인가"를 묻지 않는다.**

수정은 인증 필터의 쿼리를 권한 필터가 쓰던 것으로 올리는 것이었다.

```java
-User user = userRepository.findByDelYnFalseAndUsername(username)
+User user = userRepository.findUserWithRoleByUsername(username)
     .orElseThrow();
```

## 무엇을 착각했나

"같은 User 객체니까 재사용하면 된다"고 생각한 것이 착각이었다.

- 공유되는 건 **참조**지 **로딩 상태**가 아니다
- 같은 엔티티라도 **어떤 쿼리로 가져왔는지가 계약의 일부**다
- 그런데 그 계약은 타입에 안 나타난다. `User`는 그냥 `User`이고, 역할이 채워졌는지는 시그니처가 말해주지 않는다

컴파일러가 못 잡는 이유가 여기 있다. 생산자를 바꿔치웠는데 타입은 그대로라 아무 경고도 없었다. **JPA에서 "이 엔티티"는 하나가 아니라, 쿼리마다 다른 상태의 객체다.**

지금이라면 이렇게 했을 것이다.

- 요청 스코프에 넣는 값은 **가장 넓은 fetch 범위로 통일한다** — 실제로 택한 방법이고, 가장 싸다
- 또는 필요한 연관관계가 로딩됐는지를 타입으로 표현한다(전용 DTO, 또는 역할만 담은 별도 값 객체)
- 최소한 `setAttribute` 옆에 "이 객체는 userRoleList를 포함한다"는 주석을 남긴다

## 남는 교훈

**재사용은 공짜가 아니다 — 암묵적 계약이 딸려 온다.**

- 최적화는 대체로 무언가를 공유하는 일이다. 공유하는 순간 "이게 어떤 상태여야 하는가"라는 조건이 생긴다
- 그 조건이 코드에 안 적혀 있으면, 조건을 아는 사람이 떠난 뒤에 깨진다
- 여기서는 조건을 만든 사람과 깨뜨린 사람이 같았고, 간격이 3분이었다

**`null`이 아니라고 쓸 수 있는 값은 아니다.**

- 방어 코드가 있어서 안심했는데, 정작 그 방어가 검사한 건 존재 여부뿐이었다
- 부분적으로 초기화된 객체는 `null`보다 나쁘다. `null`은 즉시 터지지만, 이쪽은 조용히 틀린 답을 낸다

**빠른 연속 커밋은 지우지 않는 편이 낫다.**

- 20:24에 최적화하고 20:27에 고친 이력이 남아 있다. squash 했으면 사라졌을 것이다
- 지금 이 글을 쓸 수 있는 이유가 그 커밋이 남아서다
- 깔끔한 히스토리가 항상 좋지는 않다 — 시도와 실패의 간격 자체가 정보다
