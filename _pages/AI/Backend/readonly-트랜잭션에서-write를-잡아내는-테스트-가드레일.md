---
title:  "readOnly 트랜잭션에서 write를 잡아내는 테스트 가드레일"

categories:
  - AI
tags:
  - AI
  - Claude Code
  - Spring
  - 트랜잭션
  - 테스트

date: 2026-06-01
thumbnail: "/assets/img/thumbnail/sample.png"
---

## 조회 API가 매번 write 트랜잭션을 만들고 있었다

대시보드 조회 API의 응답이 느려서 들여다봤는데, 조회 경로에서 write가 일어나고 있었다. `f6fd21ef`에서 확인한 내용이다 — eco-view의 배출원 조회 경로가 `lcaStepService.updateStepOnly(write)`를 부수효과로 호출하고 있었다. 대시보드를 열 때마다 write 트랜잭션이 생기는 구조였다.

조회 전용 메서드(`getGwpTotalForView`)를 새로 만들고 계산 로직을 공통화해서 부수효과를 떼어냈다. 여기까지는 평범한 수정이다. 문제는 **이런 걸 어떻게 다시 안 생기게 하느냐**였다.

## 먼저 실패한 시도 — readOnly=true를 붙였다 떼기

시간을 조금 앞으로 돌리면, `58134b6d`(2026-05-29)에서 이미 한 번 실패한 적이 있다. `getCutOffIoList`·`getFinalIoList` 두 메서드에 `@Transactional(readOnly = true)`를 붙였는데, 이 메서드들이 내부적으로 `updateStepAndSubStepOnly`라는 쓰기 트랜잭션과 충돌했다. 결국 `readOnly = true`를 도로 제거하는 커밋을 남겼다.

"조회 메서드니까 readOnly를 붙이면 되겠지"가 통하지 않았던 것이다. 이 코드베이스에는 조회 메서드 안에서 상태를 갱신하는 GET-in-write 패턴이 여러 곳 남아 있었고, 애노테이션 하나로 걷어낼 수 있는 게 아니었다. 해당 메서드들에는 구조 설명과 함께 TODO 주석을 남겼다 — Read Replica를 도입하려면 별도 엔드포인트 분리가 선행돼야 한다는 내용이다.

즉 문제는 두 층이었다.

1. 조회 경로에 write가 섞여 있다 (개별 수정 대상)
2. 그게 섞여 있는지 **자동으로 알 방법이 없다** (구조적 문제)

## 가드레일을 만들었다

`9723219b`에서 `ReadOnlyTxGuardConfig`를 추가했다(약 200줄). readOnly 트랜잭션 안에서 write SQL이 실행되면 테스트를 실패시키는 장치다.

동작 방식은 이렇다.

- `BeanPostProcessor`로 `DataSource` 빈을 가로채 **JDK 동적 프록시**로 감싼다
- Statement 실행 직전에 `TransactionSynchronizationManager.isCurrentTransactionReadOnly()`를 확인한다
- readOnly인데 SQL이 INSERT / UPDATE / DELETE / MERGE 중 하나면 `AssertionError`를 던진다

```java
if (TransactionSynchronizationManager.isCurrentTransactionReadOnly()
        && isWriteStatement(sql)) {
    throw new AssertionError(...);
}
```

## 설계에서 신경 쓴 것

**테스트 전용이다.** `@TestConfiguration`으로 선언해서 프로덕션 컨텍스트에는 절대 올라가지 않는다. 운영 트래픽에 SQL 문자열 검사를 끼워 넣는 건 비용도 위험도 크다.

**선택적으로 켠다.** 전역 적용이 아니라 `@Import(ReadOnlyTxGuardConfig.class)`를 붙인 테스트에서만 활성화된다. 앞서 말한 GET-in-write 패턴이 아직 남아 있는 상태라, 전부 켜면 기존 테스트가 대량으로 깨진다. 정리된 영역부터 하나씩 켜 나가는 방식이다.

**기존 래핑과 공존한다.** 이 프로젝트의 `DataSource`는 이미 P6Spy(SQL 로깅)와 HikariCP(커넥션 풀)로 겹겹이 감싸여 있다. JDK 동적 프록시로 인터페이스 레벨에서 감싸는 방식을 택한 덕에 그 계층들과 충돌 없이 얹힌다. 상속이나 구체 클래스 프록시를 썼다면 이 조합에서 깨졌을 것으로 보인다.

## 왜 SQL 레벨인가

readOnly 위반을 잡는 방법은 여러 가지가 있다. JPA 레벨에서 dirty checking을 감시하거나, AOP로 서비스 메서드를 검사하거나.

SQL 레벨을 택한 건 **거기가 마지막 관문이기 때문**이다. JPA를 우회하는 native query, QueryDSL의 벌크 연산, JdbcTemplate 직접 호출 — 어떤 경로로 오든 결국 `Statement`를 지난다. 상위 계층에서 잡으면 우회로가 생긴다.

| 감지 위치 | 잡히는 범위 | 우회 가능성 |
|---|---|---|
| 서비스 메서드 AOP | 애노테이션 붙은 호출 | 내부 호출·native 우회 |
| JPA dirty checking | 엔티티 변경 | 벌크·native 우회 |
| Statement 실행 직전 | 모든 SQL | 없음 |

## 남는 교훈

같은 문제를 두 번 다르게 다뤘다는 게 이 작업의 핵심이다. `58134b6d`에서는 `readOnly = true`를 붙이는 방식으로 "선언"했고, 그건 되돌려졌다. `9723219b`에서는 위반을 **검출**하는 쪽으로 방향을 바꿨다.

선언은 코드베이스가 이미 그 규약을 지키고 있을 때만 통한다. 지키지 않는 코드가 남아 있는 상태에서 선언부터 붙이면 런타임에 터진다. 검출 장치는 반대다 — 지키지 않는 곳이 어디인지 먼저 알려주고, 정리된 영역부터 규약을 확대할 수 있게 해준다.

그리고 "조회 API가 write를 유발한다"는 건 코드를 읽어서 알아내기 어려운 종류의 문제다. 호출 체인 서너 단계 아래에서 부수효과가 일어나면 눈으로는 안 보인다. 실행 시점에 SQL을 붙잡는 장치가 있어야 드러난다.
