---
title:  "감사로그 IP 컬럼은 왜 varchar(45)여야 하는가 — STRICT 모드가 드러낸 것"
subtitle: "STRICT 모드가 드러낸 감사로그 IP 잘림을 컬럼 확장과 길이 제한으로 처리했다"
description: "STRICT 모드가 드러낸 감사로그 IP 잘림을 컬럼 확장과 길이 제한으로 처리했다"

categories:
  - Database
tags:
  - MySQL
  - STRICT_TRANS_TABLES
  - IPv6
  - Spring
  - 감사로그

date: 2026-09-15
---
## 한 줄로

감사로그의 `ip_address` 컬럼이 `varchar(16)`인데 IPv6 주소는 최대 39자다. 지금까지는 DB가 조용히 잘라 저장하고 성공으로 처리했고, `STRICT_TRANS_TABLES`를 켜자 그 자리가 `ERROR 1406`으로 드러났다. 컬럼을 45로 넓히고, 애플리케이션에서도 45자 초과분을 잘라서 넣도록 했다.

## STRICT 모드란?

MySQL의 `sql_mode` 설정값 중 하나다(`STRICT_TRANS_TABLES`). 트랜잭션 테이블에 잘못된 값이 들어올 때 어떻게 할지를 정한다.

- **꺼져 있으면**: `varchar(16)` 컬럼에 39자를 넣으면 앞 16자만 저장하고 warning 하나 남긴 뒤 INSERT는 성공한다. 애플리케이션 입장에서는 아무 일도 없었던 것처럼 보인다.
- **켜져 있으면**: 같은 INSERT가 `ERROR 1406`으로 실패한다.

즉 STRICT 모드 도입은 새 검증 규칙을 추가하는 일이 아니라, **이미 일어나고 있던 데이터 손실을 눈에 보이게 만드는 일**이다.

## 환경마다 sql_mode가 달랐다

이번에 조사하면서 확인한 것은 환경별 불일치였다.

| 환경 | sql_mode |
|---|---|
| 로컬 Docker (MySQL 8) | 이미 STRICT (MySQL 8 기본값) |
| dev Aurora | 없음 |
| 운영 Aurora | 없음 |

로컬에서 에러로 잡히던 것이 dev·운영에서는 조용히 잘린 셈이다. 이 불일치가 과거 한 티켓의 문제를 늦게 발견하게 만든 구조적 원인이었다.

dev에 STRICT를 적용한 결과는 이렇다.


```text
dev sql_mode: STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION
```

재부팅 없이 즉시 반영됐고, 길이 초과 INSERT가 `ERROR 1406`으로 바뀌는 것을 확인했다. dynamic 파라미터라 되돌리기도 즉시 가능하다.

```bash
aws rds modify-db-parameter-group --region ap-northeast-2 \
  --db-parameter-group-name <파라미터그룹> \
  --parameters "ParameterName=sql_mode,ParameterValue=NO_ENGINE_SUBSTITUTION,ApplyMethod=immediate"
```

마지막 줄의 `ApplyMethod=immediate`가 "재부팅 기다리지 말고 지금 바꾼다"는 뜻이다. 되돌릴 때 값 목록에서 `STRICT_TRANS_TABLES`만 빼면 된다.

## 켜기 전에 폭 여유를 조사했다

STRICT를 켜면 지금까지 조용히 잘리던 INSERT가 전부 에러로 바뀐다. 그래서 dev의 varchar 컬럼 305개를 엔티티 매핑과 교차해서 훑었다.

| 방어선 | 개수 | STRICT에서 |
|---|---|---|
| `@Size` 있음 | 168 | 앱이 먼저 400 |
| `@Size` 없음 | 105 | DB가 최종 방어선 → 500 |
| 엔티티 매핑 없음 | 32 | Bean Validation 없음 |

`@Size`는 Bean Validation 어노테이션(요청 값의 길이를 애플리케이션 단에서 검사하는 표시)이다. 이게 붙어 있으면 DB에 닿기 전에 400으로 막히므로 STRICT를 켜도 동작이 안 바뀐다. 문제는 방어선이 없는 137개다.

그중 여유 30자 미만은 6개뿐이었고, 그중 5개는 폭이 고정된 값(날짜 10자·연도 4자)이라 애초에 넘칠 수 없다.

## 실제 위험은 한 곳이었다

`audit_log.ip_address` — `varchar(16)`, `@Size` 없음, 18,353행.

dev에는 IPv6가 이미 들어오고 있었다. `0:0:0:0:0:0:0:1`이 774건. 이 표기는 15자라 컬럼에 들어간다. 실제 IPv6 주소(최대 39자)로 테스트해 보니 이렇게 갈렸다.

- 운영: 잘려서 저장되고 성공 처리
- dev(STRICT 적용 후): `ERROR 1406`

값이 어디서 오는지도 따라갔다. `HttpUtils.java:67-74`의 `getClientIP()`를 거친 `X-Forwarded-For` 헤더 값이 **검증 없이 그대로** 저장된다. 클라이언트가 임의로 넣을 수 있는 값이다.

여기서 중요한 것은, 이게 **STRICT와 무관하게 이미 결함**이라는 점이다. 감사로그에 틀린 IP가 기록되면 감사 추적 자체가 무의미해진다. STRICT는 이 결함을 만든 게 아니라 드러냈을 뿐이다.

## 고친 것

- `ip_address`를 `varchar(16)` → **45**로. IPv6 최대 길이다.
- 컬럼 변경 DDL은 별도 파일로 분리.
- `IP_ADDRESS_LENGTH = 45` 상수를 두고 `@Size`를 붙였다.
- `getClientIP()`가 45자 초과분을 **잘라서 반환**하도록.

테스트 5건을 새로 넣었고 249건 중 248건 통과. 실패한 1건은 gitignore 대상 로컬 파일을 잡는 `ResourceSecretGuardTest`로 이 변경과 무관하다 — 역검증까지 했다.

### 예외 대신 자르기로 한 이유

"길이 초과면 예외를 던지고 막는다"가 일반적인 선택이지만 여기서는 반대로 갔다.

호출부가 `AuditLogInterceptor.afterCompletion`이다. 이름 그대로 요청 처리가 **끝난 뒤** 도는 자리라, 여기서 예외가 나도 사용자 요청은 이미 성공한 채로 살고 감사로그만 유실된다.

예외로 막으면 조작된 `X-Forwarded-For` 헤더 하나로 감사 기록을 지울 수 있다는 것이 이 선택의 근거였다.

잘린 값이라도 남기는 쪽이 안전하다.

## 조사하면서 정정한 것 2건

- "폭 여유 0인 4개는 안전하다"고 한 첫 조사는 `@Size` 유무를 보지 않은 것이었다. 애초에 기준이 여유 폭이 아니라 **IPv6가 들어올 수 있다는 사실**이어야 했다.
- "STRICT를 켜면 이 자리가 500이 된다", "관리자 화면 전체를 못 쓰게 될 수 있다" — 둘 다 과했다. `@Size`가 있으면 400이고, `afterCompletion`이라 사용자 요청은 영향받지 않는다.

## 남은 것

dev DB의 DDL 실행이 권한 정책에 차단돼 있다. dev는 STRICT가 이미 켜져 있으므로, 컬럼이 16자인 채로 실제 IPv6가 들어오면 그 요청의 감사로그는 유실된다.

참고로 이 변경은 한쪽 서비스에만 해당한다 — `audit_log` 테이블이 그쪽에만 있고, 다른 서비스는 IP를 로그로만 남긴다.
