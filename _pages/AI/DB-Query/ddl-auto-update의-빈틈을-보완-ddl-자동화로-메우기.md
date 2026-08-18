---
title:  "ddl-auto: update의 빈틈을 보완 DDL 자동화로 메우기"

categories:
  - AI
tags:
  - AI
  - Claude Code
  - JPA
  - Spring
  - 데이터베이스

date: 2026-07-30
thumbnail: "/assets/img/thumbnail/sample.png"
---

## Flyway를 걷어낸 뒤 남은 숙제

- 이전 글: [Flyway를 도입하고 3주 만에 걷어낸 이야기](/AI/flyway를-도입하고-3주-만에-걷어낸-이야기.html)
- 걷어낸 뒤 스키마 관리 방식
  - JPA `ddl-auto`
  - 사람이 손으로 적용하는 SQL 파일 묶음(`db/manual/*.sql`)

- 구멍 두 가지

- stg 환경은 `ddl-auto: validate` → 테이블·컬럼을 만들어주지 않음
- 보완 DDL은 담당자가 stg에 같은 SQL을 손으로 1회씩 적용

- 조치: PR 2건으로 둘을 자동화

## 먼저 확인한 것 — update가 manual SQL을 대체할 수 있나

- 자동화 전 답해야 할 질문: `ddl-auto: update`를 켜면 `db/manual`의 SQL 중 일부는 불필요해지는가
- 34개 파일 전수 검토
- 결과: **대체 가능한 파일 0개**

<div class="diagram" role="img" aria-label="ddl-auto update 가 하는 일과 하지 않는 일">
{% include diagrams/ddl-auto--add-only.svg %}
</div>

- `update`는 **추가만** 함 — 새 테이블, 새 컬럼은 생성
- 하지 않는 것

| 작업 | ddl-auto: update | manual SQL |
|---|---|---|
| 새 테이블·컬럼 추가 | O | 불필요 |
| ENUM 값 확장 | X | 필요 |
| 컬럼 타입 MODIFY | X | 필요 |
| nullable·DEFAULT 변경 | X | 필요 |
| 인덱스 교체 | X | 필요 |
| DROP COLUMN | X | 필요 |
| 뷰 생성·갱신 | X | 필요 |
| 데이터 백필 | X | 필요 |

- 관계 정리 — 대체가 아니라 상호 보완

- 첫 번째 PR — stg의 `ddl-auto`를 `validate` → `update`
- manual SQL 경로는 그대로 유지
- 효과: local·dev·stg 세 환경의 스키마 적용 경로 동일
- prod는 `validate` 유지, 사람이 통제

## 어떻게 자동 적용하나

- 두 번째 PR — `ManualSqlRunner`를 `ApplicationRunner`로 구현

```java
@Component
@Profile({"local", "dev", "stg"})
public class ManualSqlRunner implements ApplicationRunner {
    private static final String LOCATION_PATTERN = "classpath:db/manual/*.sql";
```

- 설계상 중요한 지점 세 가지

**`ApplicationRunner`인 이유**

- ALTER 대상 테이블이 먼저 존재해야 함 → `ddl-auto` 선행 필요
- 부팅 완료 후에 도는 `ApplicationRunner`가 그 순서를 보장

**멱등 SQL이라 이력 테이블 불필요**

- 모든 SQL을 여러 번 실행해도 안전하게 작성
- MySQL 8/9에는 `ADD COLUMN IF NOT EXISTS` 없음
- 대안: `information_schema`로 존재 확인 후 `PREPARE`/`EXECUTE`로 동적 실행
- 멱등이면 Flyway 같은 적용 이력 테이블 불필요

**파일 단위로 한 커넥션 유지**

- SQL 파싱을 직접 `split(";")` 하지 않음
- Spring의 `ScriptUtils.executeSqlScript(conn, resource)`에 위임 — 주석·세미콜론·멀티라인 안전 처리
- 한 파일을 같은 Connection에서 실행해야 `SET @var`/`PREPARE` 세션 변수가 살아있음

## 실패 격리가 자동화의 전제 조건이었다

- 기존 구조: **SQL 한 개 실패 → `ApplicationRunner` 예외 그대로 전파 → 스프링 컨텍스트 기동 전체 실패**
- 전례: 같은 사고가 다른 초기화기에서 실제로 배포를 연쇄 실패시킴
- 그 기록이 코드 주석에 남아 있었음

- 특히 위험한 대상: 유니크 인덱스 추가 파일(008·010·018)
- 기존 데이터에 중복이 있으면 **실패하도록 설계된** 파일 — 원래는 사람이 사전 점검하던 관문
- 자동화 시 부팅 실패로 직결

- 조치: 파일 단위 try/catch
- 한 파일이 실패해도 ERROR 로그만 남기고 다음 파일 계속 적용
- 모든 SQL이 멱등 → 원인 해소 후 재기동하면 실패한 파일만 재적용

- 남은 위험: 실패를 조용히 삼키면 "앱은 떴는데 보완 DDL은 빠진" 상태를 런타임 에러로 늦게 발견
- 보완: 부팅 로그 끝에 `{성공}/{전체}`와 실패 파일명 요약

## 자동화하면 사라지는 안전장치

- PR 본문에 명시한 점

**사람이 손으로 적용하던 시절에는 "사전 중복 점검"이라는 암묵적 관문이 있었다.**

- 기존 흐름: 유니크 인덱스 추가 SQL 실패 → 담당자가 그 자리에서 중복 데이터 확인·정리
- 자동화 후: 그 관문 소멸 — 실패 로그를 누군가 읽어야만 알 수 있는 구조

없앤 걸 없앴다고 적어두는 것과, 없앤 줄 모르는 것은 다르다.

- 원칙: 자동화 PR에는 얻은 것과 잃은 안전장치를 함께 기록

## 이 방식이 반드시 동반해야 할 가드

자동 DDL Runner를 만들 때 같이 설계해야 하는 것이 있다.

- Runner는 주입받은 `DataSource`에 DDL을 그대로 전송한다
- 즉 **접속 설정이 의도와 다른 DB를 가리키면 그대로 적용된다**
- MySQL DDL은 롤백이 안 되므로 되돌릴 방법이 없다

그래서 스키마명 검증(연결된 DB가 기대한 스키마가 맞는지 확인 후 실행)은
선택이 아니라 전제다. 자동 DDL 범위를 넓힐수록 이 가드의 중요도가 올라간다.

## 남는 교훈

Flyway 철수는 "이력 추적을 포기하고 편해졌다"가 아니었다. 포기한 자리를 다른 방식으로 메워야 했고, 그 메우는 작업이 이 PR이다.

- 이번 작업의 최대 소득 — 34개 파일 전수 검토
- 사전 직관: "update를 켜면 manual SQL이 좀 줄 것"
- 실측 결과: 0개

도구의 능력 범위를 감으로 어림잡는 대신 실제 파일에 대조해보는 것 — 그게 "둘은 상호 보완"이라는 결론에 근거를 준다.
