---
title:  "Expand/Migrate/Contract란?"
subtitle: "컬럼 이관은 Expand/Migrate/Contract를 따랐지만, 인스턴스 1대와 AllAtOnce 배포가 무중단을 막았다"
description: "컬럼 이관은 Expand/Migrate/Contract를 따랐지만, 인스턴스 1대와 AllAtOnce 배포가 무중단을 막았다"

categories:
  - Database
tags:
  - Aurora
  - MySQL
  - 무중단 배포
  - 스키마 마이그레이션
  - DDL

date: 2026-09-28
---
## 한 줄로

Expand/Migrate/Contract는 스키마 변경을 세 단계로 쪼개는 방식이다. 새 구조를 추가하고(Expand), 데이터를 옮긴 뒤(Migrate), 옛 구조는 한참 뒤에 지운다(Contract). 회사 프로젝트의 운영 DB 이관을 조사해 보니 DDL은 이미 이 표준대로 짜여 있었다. 무중단을 막고 있던 것은 DB가 아니라 배포 구조였다.

## 세 단계로 나눈다

컬럼 하나를 둘로 나누는 작업이 이번 사례다.

| 단계 | 하는 일 | 이번 작업에서 |
|---|---|---|
| Expand | 새 구조를 옛 구조 옆에 추가한다 | `ADD COLUMN file VARCHAR(512), reason VARCHAR(255)` |
| Migrate | 옛 데이터를 새 구조로 옮긴다 | File·Reason 이관 `UPDATE` 두 개 |
| Contract | 옛 구조를 지운다 | `DROP COLUMN data` |

핵심은 Expand와 Contract 사이에 옛 구조가 살아 있다는 점이다. 그 사이에 문제가 생겨도 새로 추가한 것만 걷어내면 원래 상태로 돌아간다.

## 실제로 겪은 것: 컬럼 하나를 둘로 나누기

기존 `data` 컬럼 하나에 `type`에 따라 파일 경로나 사유가 섞여 들어 있었다. 이것을 `file`·`reason` 두 컬럼으로 나누는 작업이다. 이관 SQL은 `ddl_20260922.sql`에 있다.

### 사전 검사

운영 DB에서 먼저 확인한 것은 다음과 같다.

- 오분류 검사 3개가 모두 0이다. `type`을 기준으로 이관해도 된다는 뜻이다.
- 대상은 78건이다(File 36 / Reason 42). 값은 최장 94자다.
- File 쪽 빈 문자열 25건은 원래 그런 데이터라 정상이다.
- `file`·`reason` 컬럼은 아직 없다.

운영 DB는 보안그룹에 작업 환경의 IP가 없다. 그래서 쿼리는 직접 실행한다.

### 순서: DDL 먼저, 배포 나중

1. `ADD COLUMN file VARCHAR(512), reason VARCHAR(255)`
2. File·Reason 이관 `UPDATE` 두 개
3. 검증: 기대값 `78/0/0/0/0`
4. 한 서비스 → 다른 서비스 순서로 배포
5. `DROP COLUMN data`

배포가 DDL보다 앞서면 안 된다. 앱이 `ddl-auto: validate`로 떠서, 엔티티에는 있는데 테이블에는 없는 컬럼을 만나면 검증에 실패하고 앱이 아예 뜨지 않는다. 컬럼을 먼저 만들어 두면 옛 앱은 새 컬럼을 무시하고 계속 돌고, 새 앱은 뜰 때 컬럼을 찾는다.

원복은 한 줄이다.

```sql
DROP COLUMN file, reason
```


5단계 전까지는 `data`가 그대로 남아 있으므로 원복해도 데이터를 잃지 않는다. 이것이 Contract를 맨 뒤로 미루는 이유다. 그래서 `DROP COLUMN data`는 관측 기간을 충분히 둔 뒤에 한다.

배포를 기다리는 커밋은 앞 서비스 6개, 뒤 서비스 4개다. 3단계 검증 결과와 실제 실행 여부는 이 글에 담지 않았다.

## 무중단을 막는 것은 DB가 아니었다

무중단 배포 방안을 조사한 결론은 새로 도입할 기법이 없다는 것이었다. `ddl_20260922.sql`이 이미 Expand/Migrate/Contract를 따르고 있다.

막는 것은 배포 구조다.

- 앱당 인스턴스가 1대다.
- 배포 방식이 `AllAtOnce`이고, autoRollback은 None이다.
- ALB 헬스체크가 60초 간격 5회다. 새 인스턴스가 트래픽을 다시 받기까지 최대 5분이 걸린다.

인스턴스가 1대뿐인데 한꺼번에 교체하면, 스키마를 아무리 안전하게 바꿔도 그 1대가 교체되는 동안은 서비스가 빈다.

조사 도중 이전 분석을 바로잡은 것도 있다. 처음에는 ALB가 없다고 봤지만, 실제로는 앱마다 ALB가 있고 타깃이 각 1대였다. 운영 배포에서는 `appspec-prod.yml` → `startup-prod.sh`가 `/monitor/health`를 120초 동안 확인하며 ValidateService 역할을 한다.

## INSTANT, 그리고 틀린 주석

DDL 파일에는 컬럼 추가·삭제라 테이블 재구성이 일어난다는 취지의 주석이 있었다. 이 주석은 틀렸다. Aurora `8.0.mysql_aurora.3.10.3`에서는 컬럼 추가와 삭제가 둘 다 INSTANT로 처리된다. INSTANT는 테이블을 다시 만들지 않고 메타데이터만 바꾸는 방식이다. 주석 수정은 승인을 기다리고 있다.

## 권고

시간 축에 따라 셋으로 나눴다.

- **지금 할 것**: DDL에 `ALGORITHM=INSTANT`를 명시한다. 배포 직전에 수동 스냅샷을 뜨고, 트래픽이 적은 시간대에 배포한다.
- **별도 티켓**: autoRollback을 켠다. 헬스체크를 10초 간격 2회로 줄이면 복귀 시간이 5분에서 20초로 준다.
- **구조 과제**: 인스턴스를 2대로 늘리고 `OneAtATime`으로 배포한다.

`ALGORITHM=INSTANT`를 명시해 두면 INSTANT로 처리할 수 없는 경우에 테이블 재구성으로 조용히 넘어가지 않고 그 자리에서 실패한다. 주석이 틀렸던 것처럼 사람의 예상과 실제 동작이 어긋날 때 그 차이가 드러난다.

## 정리

- Expand/Migrate/Contract는 옛 구조를 살려 둔 채 새 구조를 붙이는 방식이다. 원복이 쉬운 것은 그 덕분이다.
- `ddl-auto: validate`를 쓰는 앱은 순서가 강제된다. DDL을 먼저 하고 배포는 나중에 한다.
- 스키마를 표준대로 바꿔도 인스턴스 1대에 `AllAtOnce`라면 무중단은 되지 않는다. 먼저 배포 구조를 봐야 한다.
