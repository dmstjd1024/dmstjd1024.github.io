---
title:  "GIN trigram 인덱스를 만들었는데 왜 안 빨라지지?"

categories:
  - Database
tags:
  - AI
  - Claude Code
  - PostgreSQL
  - 성능최적화

date: 2026-03-25
thumbnail: "/assets/img/thumbnail/sample.png"
---
## 인덱스를 만든 날과 인덱스가 실제로 쓰인 날이 13일 떨어져 있다

- 2026-03-12 — GIN trigram 인덱스 추가
- 2026-03-25 — 인덱스가 쿼리 플랜에 처음 등장
- 그 사이 13일 동안 인덱스는 디스크만 차지
- 이 글의 주제 — 그 13일

## 문제

- 환경: Spring Boot 3.2 + PostgreSQL 15
- 도메인: B2B 산업용 관리 시스템
- 화면: 장비 목록
- 검색 대상: 장비번호 · 고객명 · 관리번호
- 방식: 부분일치 검색

- 결과 쿼리 형태

```sql
WHERE c.name LIKE '%' || #{keyword} || '%'
```

- 앞에 `%`가 붙은 LIKE는 B-tree 인덱스 사용 불가
- 이유: 선행 문자열이 고정돼야 범위 스캔 가능
- 결과: 매 검색이 풀스캔

<div class="diagram" role="img" aria-label="선행 와일드카드가 B-tree 를 무력화하고 trigram 이 이를 푸는 방식">
{% include diagrams/gin-trgm--leading-wildcard.svg %}
</div>

## 1차 시도: pg_trgm + GIN 인덱스

- PostgreSQL이 제공하는 도구

- `pg_trgm` 확장 — 문자열을 3글자 단위(trigram)로 분해
- `gin_trgm_ops` 연산자 클래스 — GIN 인덱스로 `%keyword%` 지원

- 해당 마이그레이션 — 확장 활성화 후 인덱스 생성

```sql
CREATE EXTENSION IF NOT EXISTS pg_trgm;

CREATE INDEX IF NOT EXISTS idx_device_no_trgm
    ON tb_device USING GIN (device_no gin_trgm_ops)
    WHERE is_deleted = FALSE AND removal_date IS NULL;
```

- 부분 인덱스(`WHERE` 절) 채택은 의도적

- 목록 조회는 항상 삭제되지 않은 행만 조회
- 죽은 행 제외 시 인덱스 크기 감소
- 갱신 비용도 감소

같은 계열 작업:

- 후속 마이그레이션 — 주소 · 장비 식별자 컬럼에 GIN 인덱스 추가
- LATERAL JOIN이 매 행마다 실행되던 구간에 커버링 인덱스 추가

- 여기까지 작업 후 커밋
- 당시 전제 — 인덱스를 만들었으니 빨라졌을 것

## 그런데 안 빨라졌다

13일 뒤 다시 들여다봤을 때, 실행 계획에 여전히 Seq Scan이 찍히고 있었다. 인덱스는 분명히 존재하는데 옵티마이저가 쓰지 않았다.

- 원인 위치: 쿼리 쪽
- 매퍼 XML의 실제 조건절

```sql
LOWER(c.name) LIKE LOWER('%' || #{keyword} || '%')
```

- 목적: 대소문자 구분 없는 검색
- 방식: 양쪽에 `LOWER()` 래핑
- 흔한 패턴이고, 그 자체로 틀린 코드도 아님

- 문제의 핵심 — **인덱스는 `name`에 존재, `LOWER(name)`에는 부재**

- PostgreSQL 입장에서 `name`과 `LOWER(name)`은 전혀 다른 표현식
- 인덱스 정의와 쿼리 표현식이 문자 그대로 일치해야 후보로 등록
- 함수를 한 번 감싸는 순간 인덱스는 없는 것과 동일

<div class="diagram" role="img" aria-label="함수로 감싸면 인덱스 표현식과 달라져 사용되지 않는 구조">
{% include diagrams/gin-trgm--function-wrap.svg %}
</div>

- 선택지 둘

| 방법 | 내용 | 판단 |
|---|---|---|
| 표현식 인덱스로 맞추기 | `GIN (LOWER(name) gin_trgm_ops)` 로 재생성 | 인덱스가 커지고, 모든 검색 컬럼마다 별도 인덱스 필요 |
| 쿼리를 인덱스에 맞추기 | `LOWER(x) LIKE LOWER(y)` → `x ILIKE y` | 인덱스 그대로 사용 가능 |

- `ILIKE` — PostgreSQL의 대소문자 무시 LIKE
- 의미는 `LOWER() LIKE LOWER()`와 동일
- trigram GIN 인덱스가 지원하는 연산자

- 채택: 후자

## 어떻게 고쳤나

13일 뒤 커밋에서 일괄 전환.

- 대상 패턴: `LOWER(...) LIKE LOWER(...)` → `ILIKE`
- 변경 규모: 130개소 남짓
- 조직 관련 매퍼 하나만 373줄 변경

- 기계적 치환처럼 보이나 함정 하나 존재

- `LOWER(a) LIKE LOWER(b)`와 `a ILIKE b`는 ASCII 범위에서 동일
- 로케일에 따라 특수 문자에서 결과가 갈릴 수 있음
- 검색 대상이 장비번호 · 고객명 수준이라 실질 위험은 없다고 판단하고 진행

### 덤: 인덱스가 아예 필요 없어진 케이스

- 같은 커밋에서 제조사 검색 UI 수정

- 기존: 제조사명 텍스트 입력 → 부분일치 검색
- 변경: 드롭다운 선택
- 추가 작업: 제조사 목록 엔드포인트 신설

그 결과:

- 조건절 `ILIKE '%...%'` → `= '...'` 로 강등
- 정확매칭은 일반 B-tree 인덱스로 충분
- trigram GIN 불필요

**가장 빠른 부분일치 검색은 부분일치를 하지 않는 것이다.**

- 적용 조건: 검색어 후보 집합이 유한 + 사용자가 그중에서 선택 가능
- 그 경우 자유 텍스트 입력 고수의 근거 없음

## 남는 교훈

이 일에서 실제로 배운 건 인덱스 문법이 아니다.

**인덱스를 만든 것과 인덱스가 쓰이는 것은 별개의 사건이다.** 그리고 그 둘 사이에는 아무런 자동 연결이 없다.

- `CREATE INDEX`는 성공 여부만 통보
- "이 인덱스는 아무 쿼리도 타지 않습니다"는 알려주지 않음
- 13일 동안 조용했던 이유

DDL을 커밋하기 전에 `EXPLAIN`으로 대상 쿼리가 실제로 그 인덱스를 타는지 확인했다면 13일이 아니라 13분이면 끝났을 일이다.

- 인덱스 작업의 완료 조건: "인덱스 생성"이 아니라 "플랜에 인덱스가 등장"

<div class="diagram" role="img" aria-label="인덱스를 만든 날과 실제로 쓰인 날이 13일 떨어져 있던 흐름">
{% include diagrams/gin-trgm--create-vs-used.svg %}
</div>

- 부수 시사점 — 함수로 감싼 조건절의 조용한 인덱스 무력화

- 주의 대상: `LOWER()`, `CAST()`, `COALESCE()`
- 조건절 좌변에 쓰고 있다면 그 컬럼의 인덱스는 대체로 미사용 상태
