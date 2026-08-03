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

앞서 [Flyway를 도입하고 3주 만에 걷어낸 이야기](/AI/flyway를-도입하고-3주-만에-걷어낸-이야기.html)를 썼다. 걷어낸 뒤 스키마는 JPA `ddl-auto`와, 사람이 손으로 적용하는 SQL 파일 묶음(`db/manual/*.sql`)으로 관리해 왔다.

여기엔 두 가지 구멍이 있었다. stg 환경은 `ddl-auto: validate`라 테이블·컬럼을 만들어주지 않았고, 보완 DDL은 담당자가 stg에 같은 SQL을 손으로 1회씩 적용해 왔다. PR #898/#899에서 이 둘을 자동화했다.

## 먼저 확인한 것 — update가 manual SQL을 대체할 수 있나

자동화하기 전에 답해야 할 질문이 있었다. `ddl-auto: update`를 켜면 `db/manual`의 SQL 중 일부는 필요 없어지는 것 아닌가?

34개 파일을 전수 검토했다. **대체 가능한 파일은 0개였다.**

`update`는 **추가만** 한다. 새 테이블, 새 컬럼은 만들어준다. 하지만 아래는 하지 않는다.

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

둘은 대체 관계가 아니라 상호 보완이다. 그래서 `7a5efb9c`에서 stg의 `ddl-auto`를 `validate`에서 `update`로 바꾸면서도 manual SQL 경로는 그대로 유지했다. 이렇게 하면 local·dev·stg 세 환경의 스키마 적용 경로가 동일해진다. prod는 `validate`를 유지하고 사람이 통제한다.

## 어떻게 자동 적용하나

`63d54cfc`에서 `ManualSqlRunner`를 `ApplicationRunner`로 구현했다.

```java
@Component
@Profile({"local", "dev", "stg"})
public class ManualSqlRunner implements ApplicationRunner {
    private static final String LOCATION_PATTERN = "classpath:db/manual/*.sql";
```

설계에서 중요한 지점 세 가지다.

**`ApplicationRunner`인 이유** — ALTER 대상 테이블이 먼저 존재해야 하므로 `ddl-auto`가 선행해야 한다. 부팅 완료 후에 도는 `ApplicationRunner`가 그 순서를 보장한다.

**멱등 SQL이라 이력 테이블이 필요 없다** — 모든 SQL을 여러 번 실행해도 안전하게 작성한다. MySQL 8/9에는 `ADD COLUMN IF NOT EXISTS`가 없으므로 `information_schema`로 존재를 확인한 뒤 `PREPARE`/`EXECUTE`로 동적 실행한다. 멱등이면 Flyway 같은 적용 이력 테이블이 불필요하다.

**파일 단위로 한 커넥션을 유지한다** — SQL 파싱은 직접 `split(";")` 하지 않고 Spring의 `ScriptUtils.executeSqlScript(conn, resource)`에 맡긴다(주석·세미콜론·멀티라인 안전 처리). 그리고 한 파일을 같은 Connection에서 실행해야 `SET @var`/`PREPARE` 세션 변수가 살아있다.

## 실패 격리가 자동화의 전제 조건이었다

stg를 자동 적용 대상에 넣으려면 먼저 해결해야 할 게 있었다. 기존 구조는 **SQL 한 개가 실패하면 `ApplicationRunner` 예외가 그대로 나가 스프링 컨텍스트 기동이 통째로 실패**했다. 같은 사고가 다른 초기화기에서 실제로 배포를 연쇄 실패시킨 전례가 있었고, 그 기록이 코드 주석에 남아 있었다.

특히 위험한 건 유니크 인덱스를 추가하는 파일들(008·010·018)이었다. 기존 데이터에 중복이 있으면 **실패하도록 설계된** 파일이다 — 원래는 사람이 사전 점검하던 관문이었다. 자동화하면 이게 부팅을 죽인다.

그래서 파일 단위 try/catch로 바꿨다. 한 파일이 실패해도 ERROR 로그만 남기고 다음 파일을 계속 적용한다. 모든 SQL이 멱등이라, 원인을 해소하고 재기동하면 실패한 파일만 다시 적용된다.

다만 실패를 조용히 삼키면 "앱은 떴는데 보완 DDL은 빠진" 상태를 나중에 런타임 에러로 늦게 발견하게 된다. 그래서 부팅 로그 끝에 `{성공}/{전체}`와 실패 파일명을 요약해 남긴다.

## 자동화하면 사라지는 안전장치

PR 본문에 이 점을 명시했다. **사람이 손으로 적용하던 시절에는 "사전 중복 점검"이라는 암묵적 관문이 있었다.** 유니크 인덱스 추가 SQL이 실패하면 담당자가 그 자리에서 중복 데이터를 확인하고 정리했다. 자동화는 그 관문을 없앤다 — 실패 로그를 누군가 읽어야만 알 수 있는 구조로 바뀐다.

없앤 걸 없앴다고 적어두는 것과, 없앤 줄 모르는 것은 다르다. 자동화 PR에는 얻은 것뿐 아니라 잃은 안전장치도 함께 적는 게 맞다고 본다.

## 별건으로 제기한 리스크

작업 중에 스키마명 검증이 없다는 걸 발견해 별건으로 제기했다. Runner는 주입받은 `DataSource`에 그대로 DDL을 날린다 — **접속 설정이 잘못된 DB를 가리키고 있으면 무인으로 DDL이 적용된다.** MySQL DDL은 롤백이 불가능하므로 되돌릴 수도 없다.

당장 고치지는 않았지만, 자동 DDL을 넓힐 때 반드시 따라와야 하는 가드로 보인다.

## 남는 교훈

Flyway 철수는 "이력 추적을 포기하고 편해졌다"가 아니었다. 포기한 자리를 다른 방식으로 메워야 했고, 그 메우는 작업이 이 PR이다.

그리고 이번에 가장 값어치가 있었던 건 34개 파일 전수 검토였다. "update를 켜면 manual SQL이 좀 줄겠지"는 그럴듯한 직관이었지만, 실제로 세어보니 0개였다. 도구의 능력 범위를 감으로 어림잡는 대신 실제 파일에 대조해보는 것 — 그게 "둘은 상호 보완"이라는 결론에 근거를 준다.
