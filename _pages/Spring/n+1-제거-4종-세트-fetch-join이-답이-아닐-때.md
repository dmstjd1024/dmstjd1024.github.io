---
title:  "N+1 제거 4종 세트 — fetch join이 답이 아닐 때"

categories:
  - Spring
tags:
  - AI
  - Claude Code
  - JPA
  - 성능최적화
  - QueryDSL

date: 2026-06-12
thumbnail: "/assets/img/thumbnail/sample.png"
---
## N+1은 하나의 문제가 아니다

- 기간: 한 달 반
- 작업: 대시보드 조회 성능 개선
- N+1 조우 횟수: 여러 번, 매번 처방이 상이

- "N+1이면 fetch join" 반사가 통하지 않는 경우: 절반 이상

## (a) fetch join을 못 쓸 때 — @BatchSize

- 첫 케이스

- 위치: 제품 목록 조회
- 증상: `product.getLcaList()` 지연 로딩으로 제품당 1쿼리
- 시도: fetch join
- 결과: `MultipleBagFetchException`

원인:

- `Product`의 컬렉션 2개 — `lcaList`, `productUnitProcesses`
- **둘 다 bag (List, 순서 보장 없음)**
- Hibernate는 bag 2개 동시 fetch join 시 카테시안 곱 구분 불가 → 거부

<div class="diagram" role="img" aria-label="컬렉션 두 개를 동시에 fetch join 할 수 없는 이유">
{% include diagrams/n1--multiple-bag.svg %}
</div>

- 대안: `@BatchSize(100)`
- 효과: 지연 로딩 유지, N번 나가던 쿼리를 IN 절 배치 조회로 통합

```java
@BatchSize(size = 100)
private List<Lca> lcaList;
```

- 다른 조회 경로에서도 동일 판단

- 임계 경로 `cfResults` → fetch join
- 두 번째 컬렉션 `lciaCfMonthlyMetaList` → `@BatchSize(100)`
- 둘 다 fetch join 시 역시 `MultipleBagFetchException`
- 직전 커밋에 월별 메타를 fetch join으로 시도했다 되돌린 흔적 잔존

- 정리: **컬렉션 1개면 fetch join, 2개 이상이면 하나만 fetch join + 나머지 @BatchSize**

## (b) 루프 안의 집계 쿼리 — 집합을 넓혀 1회 호출

- 최대 효과 구간 — 커밋 2개에 걸친 작업

- 유형: 엔티티 연관관계 N+1 아님
- 실제 형태: **애플리케이션 코드가 루프를 돌며 집계 쿼리 반복 호출**
- 사업장 목록 API — 사업장마다 집계 쿼리 2개 호출
- 제품 목록 API — 제품마다 2개씩 호출

- 처방: 새 repository 메서드 신설이 아니라 **기존 IN 쿼리의 집합 확대**

- 전 사업장의 대상 id를 합집합으로 수집
- 쿼리는 1회씩만 실행
- 결과를 `groupingBy`로 사업장별 · 제품별 재분배

<div class="diagram" role="img" aria-label="루프 안 쿼리를 IN 집합으로 합치고 메모리에서 재분배하는 방식">
{% include diagrams/n1--in-widening.svg %}
</div>

| 경로 | 이전 | 이후 |
|---|---|---|
| 사업장 집계 | 3N 쿼리 | ~3 고정 |
| 제품 집계 | 2P 쿼리 | 2 고정 |
| 사업장 LCA 목록 | N 쿼리 | 1 |

### 결과가 변하지 않음을 논증하기

- 이 방식의 성격: "쿼리를 합치고 메모리에서 나눈다" → 합계 변동 가능성 확인 필요
- 근거 기록 위치: 커밋 메시지

- 행 단위 연산(변환 · 곱셈 · 나눗셈)은 개별 행에만 적용 → 집합을 넓혀도 각 행의 결과 동일
- **`BigDecimal`의 덧셈은 결합법칙 · 교환법칙 만족** → 어떤 순서로 묶어 더해도 합계 동일
- `BigDecimal`은 임의 정밀도 → `double`과 달리 덧셈 순서에 따른 오차 누적 없음

이 성질이 없었다면 "쿼리 하나로 합치기"는 값이 미세하게 달라질 수 있는 변경이었다. 성능 최적화가 **결과 불변임을 논증할 수 있는 변경**인지 확인하는 건 리뷰어 입장에서 가장 알고 싶은 부분이라고 본다.

유지한 기존 동작:

- 빈 사업장 제외 규칙
- `TreeMap` 출력 정렬

## (c) 전체 로드 후 Java 합산 — SQL SUM

- (a)의 첫 케이스 커밋에 포함된 또 하나의 사례

- 증상: 기간별 총량 메서드가 해당 기간 행을 전부 엔티티로 로드 후 Java에서 합산
- 조치: `SUM(kgAmount)` 집계 쿼리로 전환
- null 처리: `ZERO`

행이 늘어날수록 격차가 커지는 종류의 문제라, 지금 당장 느리지 않아도 고칠 가치가 있다.

## (d) DTO 매퍼가 유발한 N+1 — @EntityGraph 배치 조회

- 조금 다른 형태

- 위치: 사용자 목록 조회
- 증상: DTO 매퍼가 `rg.getRoleGroup().getName()`으로 LAZY 프록시를 **목록 사용자 수만큼** 접근
- 특이점: 서비스 계층 쿼리는 정상, 매퍼가 N+1 유발

조치:

- `@EntityGraph(roleGroup)` 적용한 조회 메서드 추가
- 서비스에서 `Map<Long, List<String>>`으로 일괄 배치 조회 후 매퍼에 주입
- 매퍼는 3인자 오버로드로 확장
- 기존 2인자 호출부는 위임으로 유지 → 호환성 보존

## 곁들여 — dev 로깅 끄기

- (b)의 최대 효과 구간 커밋에 포함된 성능 수정 하나 추가

- 조치: dev 환경 P6Spy SQL 로깅 비활성화
- 이유: 요청당 10여 개 쿼리를 전부 문자열 포매팅해 로깅하는 고정 오버헤드
- 유지 대상: prod / stg / local

측정 환경 자체가 느리면 최적화 효과를 제대로 볼 수 없다. 성능 작업을 할 때 계측 도구가 오버헤드를 만들고 있지 않은지 먼저 확인할 필요가 있다.

## 남는 교훈

처방 정리:

| 증상 | 처방 |
|---|---|
| 연관 컬렉션 1개 지연로딩 | fetch join |
| 연관 컬렉션 2개 이상 | 1개 fetch join + 나머지 @BatchSize |
| 루프 안 집계 쿼리 반복 | IN 집합 확대 + groupingBy 재분배 |
| 전체 로드 후 Java 집계 | SQL 집계 함수 |
| DTO 매퍼의 프록시 접근 | @EntityGraph + Map 배치 주입 |

N+1은 원인이 여러 갈래인데 증상이 같아서 하나의 처방으로 뭉뚱그리기 쉽다. 쿼리 로그를 보고 "N번 나간다"까지만 확인한 뒤 fetch join을 붙이면, `MultipleBagFetchException`을 만나거나 (b)처럼 애초에 엔티티 연관관계 문제가 아니어서 붙일 곳조차 없다.

**어디서 N이 발생하는지 — 연관 로딩인지, 애플리케이션 루프인지, DTO 매퍼인지 — 를 먼저 구분하는 게 처방보다 앞선다.**

<div class="diagram" role="img" aria-label="N 이 발생하는 세 갈래와 각각의 처방">
{% include diagrams/n1--where-n-happens.svg %}
</div>
