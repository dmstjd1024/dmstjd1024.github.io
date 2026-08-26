---
title:  "readOnly 트랜잭션에서 write를 잡아내는 테스트 가드레일"

categories:
  - Spring
tags:
  - AI
  - Claude Code
  - Spring
  - 트랜잭션
  - 테스트

date: 2026-06-01
thumbnail: "/assets/img/thumbnail/spring_thumbnail.webp"
---
## 조회 API가 매번 write 트랜잭션을 만들고 있었다

- 발단 — 대시보드 조회 API 응답 지연
- 확인 결과 — eco-view의 배출원 조회 경로가 `lcaStepService.updateStepOnly(write)`를 부수효과로 호출
- 즉 대시보드를 열 때마다 write 트랜잭션 생성

조치:

- 조회 전용 메서드 `getGwpTotalForView` 신규
- 계산 로직 공통화로 부수효과 분리

- 여기까지는 평범한 수정
- 진짜 문제: **이런 걸 어떻게 다시 안 생기게 하느냐**

## 먼저 실패한 시도 — readOnly=true를 붙였다 떼기

- 시간을 조금 앞으로 돌리면, 2026-05-29에 이미 한 번 실패

- 대상 — `getCutOffIoList`·`getFinalIoList` 두 메서드에 `@Transactional(readOnly = true)` 부착
- 충돌 — 이 메서드들이 내부적으로 호출하는 `updateStepAndSubStepOnly`가 쓰기 트랜잭션
- 결과 — `readOnly = true`를 도로 제거하는 커밋

"조회 메서드니까 readOnly를 붙이면 되겠지"가 통하지 않았던 것이다.

<div class="diagram" role="img" aria-label="애노테이션으로 막는 방식과 테스트로 감시하는 방식의 차이">
{% include diagrams/readonly--guardrail.svg %}
</div>

- 실태: 조회 메서드 안에서 상태를 갱신하는 GET-in-write 패턴이 여러 곳 잔존
- 애노테이션 하나로 걷어낼 수 있는 범위 밖

- 해당 메서드에는 구조 설명 + TODO 주석 잔류
- 내용 — Read Replica 도입 시 별도 엔드포인트 분리가 선행돼야 함

즉 문제는 두 층:

1. 조회 경로에 write 혼입 (개별 수정 대상)
2. 혼입 여부를 **자동으로 알 방법 부재** (구조적 문제)

## 가드레일을 만들었다

- 두 번째 시도에서 `ReadOnlyTxGuardConfig` 추가 (약 200줄)
- 목적 — readOnly 트랜잭션 안에서 write SQL 실행 시 테스트 실패

동작 방식:

- `BeanPostProcessor`로 `DataSource` 빈을 가로채 **JDK 동적 프록시**로 래핑
- Statement 실행 직전 `TransactionSynchronizationManager.isCurrentTransactionReadOnly()` 확인
- readOnly인데 SQL이 INSERT / UPDATE / DELETE / MERGE 중 하나면 `AssertionError`

```java
if (TransactionSynchronizationManager.isCurrentTransactionReadOnly()
        && isWriteStatement(sql)) {
    throw new AssertionError(...);
}
```

## 설계에서 신경 쓴 것

**테스트 전용**

- `@TestConfiguration` 선언 → 프로덕션 컨텍스트 미적재
- 이유 — 운영 트래픽에 SQL 문자열 검사를 끼워 넣는 건 비용도 위험도 큼

**선택적 활성화**

- 전역 적용 아님. `@Import(ReadOnlyTxGuardConfig.class)`를 붙인 테스트에서만 활성화
- 이유 — GET-in-write 패턴 잔존 상태라 전부 켜면 기존 테스트 대량 실패
- 방식 — 정리된 영역부터 하나씩 확대

**기존 래핑과 공존**

- 이 프로젝트의 `DataSource`는 이미 P6Spy(SQL 로깅)·HikariCP(커넥션 풀)로 다중 래핑 상태
- JDK 동적 프록시로 인터페이스 레벨에서 감싸는 방식 채택 → 그 계층들과 충돌 없이 적재

- 상속·구체 클래스 프록시 채택 시 이 조합에서 파손 예상

## 왜 SQL 레벨인가

readOnly 위반 감지 후보 — JPA 레벨 dirty checking 감시, AOP로 서비스 메서드 검사 등.

SQL 레벨을 택한 건 **거기가 마지막 관문이기 때문**이다.

- JPA 우회 native query, QueryDSL 벌크 연산, JdbcTemplate 직접 호출 — 어떤 경로든 결국 `Statement` 통과
- 상위 계층 감지 시 우회로 발생

| 감지 위치 | 잡히는 범위 | 우회 가능성 |
|---|---|---|
| 서비스 메서드 AOP | 애노테이션 붙은 호출 | 내부 호출·native 우회 |
| JPA dirty checking | 엔티티 변경 | 벌크·native 우회 |
| Statement 실행 직전 | 모든 SQL | 없음 |

## 남는 교훈

- 이 작업의 핵심: 같은 문제를 두 번 다르게 처리

- 1차 시도(5월 29일) — `readOnly = true`를 붙여 "선언". 되돌려짐
- 2차 시도 — 위반을 **검출**하는 쪽으로 방향 전환

선언은 코드베이스가 이미 그 규약을 지키고 있을 때만 통한다. 지키지 않는 코드가 남아 있는 상태에서 선언부터 붙이면 런타임에 터진다. 검출 장치는 반대다 — 지키지 않는 곳이 어디인지 먼저 알려주고, 정리된 영역부터 규약을 확대할 수 있게 해준다.

- "조회 API가 write를 유발한다" — 코드 정독으로 알아내기 어려운 종류
- 호출 체인 서너 단계 아래의 부수효과는 육안 식별 불가
- 노출 조건: 실행 시점에 SQL을 붙잡는 장치
