---
title:  "소프트 삭제 전환과 @Filter가 새는 곳"

categories:
  - AI
tags:
  - AI
  - Claude Code
  - Hibernate
  - JPA
  - 데이터베이스

date: 2026-07-07
thumbnail: "/assets/img/thumbnail/sample.png"
---

## 엔티티 14개를 하드 삭제에서 소프트 삭제로

- 배경 — 보고서에서 참조하는 데이터가 삭제되면 과거 보고서가 파손
- 작업 — 삭제를 `is_delete` 플래그로 전환 (PR #792)
- 대상 — 엔티티 **14개**

개념은 단순한데 실제로 걸린 곳은 둘 — **유니크 제약**, **@Filter 미적용 경로**

## (a) 유니크 제약이 삭제된 행에 걸린다

- 하드 삭제 시 — `UNIQUE(company_id, name)` 같은 제약이 자연스럽게 동작. 행이 사라지니 같은 이름 재사용 가능
- 소프트 삭제 시 — 삭제된 행이 테이블에 잔존 → **"삭제 후 같은 이름으로 재생성"이 유니크 제약에 걸림**
- 사용자 입장 — 지운 이름을 다시 못 쓰는 이상한 동작

MySQL에는 부분 인덱스(PostgreSQL의 `WHERE is_delete = 0`) 부재. 대안은 **VIRTUAL 생성 컬럼**:

```sql
ALTER TABLE tb_xxx
  ADD COLUMN active_name VARCHAR(255)
  GENERATED ALWAYS AS (IF(is_delete = 0, name, NULL)) VIRTUAL;

ALTER TABLE tb_xxx ADD UNIQUE KEY uk_xxx_active (company_id, active_name);
```

- 활성 행 → 원래 값, 삭제된 행 → `NULL`
- MySQL 유니크 인덱스는 `NULL`을 중복으로 미취급 → 삭제된 행끼리는 몇 개가 겹쳐도 무방, 활성 행끼리만 유니크
- VIRTUAL이라 저장 공간 미사용
- 적용 대상 — 이름과 계수 값 양쪽 (`active_name`, `active_coefficient`)

### FK가 기존 유니크를 붙들고 있는 경우

여기서 걸린 것이 하나 더. **기존 유니크 인덱스를 FK가 지지하고 있으면 그냥 DROP할 수 없다.**

- MySQL 동작: FK가 참조하는 인덱스의 삭제 시도 → 거부

순서:

1. 같은 컬럼 조합으로 **비유니크 인덱스를 먼저 생성** — FK가 이걸 대신 지지
2. 기존 유니크 인덱스 DROP
3. `active_*` 기반 새 유니크 인덱스 생성

- SQL은 멱등으로 작성
- 로컬 실증 — 활성 행 중복은 새 유니크 제약 위반으로 거부, 소프트 삭제 후 동일 조합 재생성은 성공

## (b) 조회 필터를 @Filter 하이브리드로

`5ef40e1a`에서 조회 필터링을 Hibernate `@Filter`로 전환.

- `BaseEntity`에 `@FilterDef` 단일 정의
- 엔티티 **15종**에 `@Filter` 부착
- AOP로 트랜잭션 경계에서 필터 활성화

"하이브리드"라 부른 이유 — 전 경로에 필터를 걸지는 않기 때문:

| 경로 | 필터 |
|---|---|
| 목록·검색·드롭다운·유니크 검사 | 적용 |
| 단건 조회(보고서 참조 경로) | 미적용 |

- 보고서 요건: 삭제된 데이터라도 당시 값 그대로 노출
- 애초에 소프트 삭제로 전환한 이유가 바로 이것
- 따라서 `findById` 같은 참조 경로는 필터 미적용

필터 비활성화 남용 방지:

- `87d016f5`에서 봉인 유틸 `SoftDeleteFilterSupport` 신규
- `disable → 실행 → finally enable`을 한 메서드에 격리
- raw `session.disableFilter` 직접 호출 금지

- 필터를 끈 채 `finally` 없이 예외 발생 시: 같은 세션의 이후 쿼리 전량이 삭제 데이터 노출
- 성격: 조용히 번지는 종류의 사고

## (c) @Filter는 native SQL에 적용되지 않는다

이번 작업에서 가장 값진 발견 — 출처는 보안 리뷰.

**Hibernate `@Filter`는 HQL / JPQL / Criteria에만 적용된다. native SQL에는 적용되지 않는다.**

문제 지점:

- 대상 — 관리자용 전체 재동기화 기능. 물질화 테이블을 원본에서 재적재하는 로직
- 구현 — 성능 때문에 native `SELECT` 사용
- 결과 — `@Filter` 미적용 → **삭제된 행까지 긁어서 물질화 테이블에 재삽입**. 소프트 삭제한 데이터가 조회 화면에 부활

- `43b2346b`에서 native SELECT 2곳에 `AND ef.is_delete = 0` 명시 추가
- 추정으로 끝내지 않고 DB에서 실측

| 쿼리 | 삭제된 행 포함 |
|---|---|
| 수정 전 native SQL | 1건 |
| 수정 후 native SQL | 0건 |

- 같은 리뷰에서 `LEFT JOIN` 3곳에도 JOIN 조건에 `is_delete = 0` 추가 (LEFT 특성 유지)
- 보안 리뷰 결과 — MEDIUM 등급. CRITICAL / HIGH 없음

## 남는 교훈

소프트 삭제의 통상적 요약 — "`DELETE`를 `UPDATE`로 전환". 실제로 값을 치르는 곳은 그 주변.

**제약 조건은 행이 사라진다는 전제 위에 서 있다.**

- 얽혀 있는 것: 유니크 인덱스 + FK + 그 FK가 지지하는 인덱스
- 행이 남는 순간: 이 전제 전부가 재검토 대상으로 전환

**필터링은 적용 범위에 구멍이 있다.** `@Filter`는 잘 만든 장치지만 native SQL을 덮지 않는다.

- 구멍의 성격: 무음 — 에러 없이 삭제 데이터가 슬그머니 재노출
- 누수 시작 지점: "필터를 걸었으니 안전하다"고 판단한 뒤 native 쿼리를 추가하는 시점

가장 도움이 된 것 두 가지:

- 보안 리뷰라는 별도 관점의 검토
- DB 실측 (1건 → 0건)
- 근거: 코드가 "맞게 생겼는지"와 "실제로 그렇게 도는지"는 별개의 질문
