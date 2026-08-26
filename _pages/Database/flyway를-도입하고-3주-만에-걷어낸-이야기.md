---
title:  "Flyway를 도입하고 3주 만에 걷어낸 이야기"

categories:
  - Database
tags:
  - AI
  - Claude Code
  - Flyway
  - 데이터베이스
  - 멀티모듈

date: 2026-05-13
thumbnail: "/assets/img/thumbnail/sample.png"
---
## 도입과 철수 사이 22일

- 도입 — 2026년 5월 13일
- 철수 — 6월 4일
- 기간 — 22일
- 그 사이 FlywayConfig — 221줄까지 성장 후 통째로 삭제

성공담이 아니라 철수 회고다.

## 왜 도입했나

프로젝트 구조:

- 빌드 — Gradle 멀티모듈 7개 (common / shared / platform / feature_a / feature_b / integration / app)
- 모듈 간 의존 — 단방향
- JPA `ddl-auto`의 한계 — 컬럼 타입 변경, 제약 교체 반영 불가
- 그래서 필요했던 것 — 스키마 변경을 코드로 관리할 도구

Flyway는 자연스러운 선택으로 보였다. 그런데 전제가 어긋나 있었다.

- Flyway의 전제 — **빈 DB에서 시작해 마이그레이션으로 쌓아 올린 스키마**
- 이 프로젝트의 실제 — 이미 81개 테이블이 존재하는 레거시 스키마

<div class="diagram" role="img" aria-label="Flyway 의 전제와 레거시 스키마의 불일치">
{% include diagrams/flyway--premise-mismatch.svg %}
</div>

## 무엇이 계속 터졌나

### 1. 베이스라인 만들기부터 쉽지 않았다

기존 스키마 덤프를 추출해 `V1__initial_schema.sql` 생성. 덤프를 그대로 넣는 것으로는 불충분:

- 멱등성 확보 — `CREATE TABLE IF NOT EXISTS`로 변환
- 제외 대상 — 뷰로 교체된 3개 테이블
- 추가 제외 — 후속 마이그레이션과 충돌하는 컬럼
- 추가 포함 — 반대로 참조되는 컬럼
- `baselineVersion` 조정 — "1"에서 "0"으로. 그래야 fresh DB에서 V1이 baseline에 가려 스킵되지 않음

### 2. 모듈별로 쪼개자 실행 순서가 깨졌다

이어서 마이그레이션을 platform / feature_a / feature_b 모듈로 분리:

- Spring Boot 자동 Flyway — 비활성화
- 대체 — 모듈별 인스턴스 수동 등록, 독립 history 테이블 각각 배치

그런데 모듈별로 순차 실행하면 **날짜 순서와 실행 순서가 어긋난다.**

- 사례 — feature_a의 `V20260515`가 platform의 `V20260522`보다 날짜상 먼저
- "platform 전체 → feature_a 전체" 순 실행 시 — 나중에 실행됨
- 결과 — MySQL 1054 (Unknown column)

그래서 세 모듈의 pending 마이그레이션을 **글로벌 버전순으로 정렬해 하나씩 적용하는 인터리브 로직**을 FlywayConfig에 직접 구현.

- 의미: 프레임워크가 해주지 않는 일을 설정 클래스가 떠안기 시작한 지점

### 3. collation 불일치

같은 커밋에서 터진 collation 문제:

- 발단 — 한 마이그레이션이 테이블을 `utf8mb4_unicode_ci`로 변환
- 결과 — 다른 마이그레이션의 `UPDATE ... JOIN` 비교에서 1267 (Illegal mix of collations) 발생
- 수습 — 다수(381개 컬럼)에 맞춰 소수(13개)를 변환하는 마이그레이션을 out-of-order 슬롯에 삽입

### 4. FK 이름이 환경마다 달랐다

- Hibernate 자동 생성 FK 이름 — `FKr19hq...` 형태, 환경마다 상이
- 증상 — 하드코딩한 `DROP FOREIGN KEY`가 fresh DB에서만 실패
- 조치 — `information_schema`로 FK 존재 확인 후 동적 실행
- 파급 — 이게 이후 팀 규칙이 됨

## 결정적이었던 것

이 문제들의 공통점 — **기존 DB에서는 무사, fresh DB에서만 발생**:

- 로컬 DB(점진 적용) — 멀쩡히 동작
- 처음부터 전부 실행 시 — 부팅 실패
- 버전 충돌 수정 커밋 — 5건 이상 누적

- 즉 Flyway 사용 중임에도 "마이그레이션 전량 재실행 시 스키마 재현" 보장 부재
- 상태: Flyway의 핵심 가치 붕괴
- 그럼에도 그 상태를 유지하는 비용은 계속 발생 중

## 걷어낸 뒤

철수 시점에 정리한 것:

- FlywayConfig 221줄 — 삭제
- Gradle 의존성, yml 설정 — 주석 처리
- 마이그레이션 SQL 파일 — 이력·참고용으로 보존
- 대체 방식 — **스키마 덤프 import**. 로컬 환경은 기준 환경의 스키마 덤프로 구성

| 항목 | Flyway | 스키마 덤프 import |
|---|---|---|
| 로컬 스키마 구성 | 마이그레이션 전량 재생 | 스키마 덤프 import |
| 실행 순서 관리 | 모듈 인터리브 직접 구현 | 불필요 |
| fresh DB 재현성 | 보장 실패 | 기준 환경과 동일 보장 |
| 스키마 변경 이력 | 파일로 추적 | 추적 약화 |

- 이력 추적 약화: 명백한 손실
- 후속 처리: 이후 별도의 보완 DDL 자동화에서 재차 대응

## 남는 교훈

Flyway가 나쁜 도구여서가 아니다. **"멀티모듈 + 이미 존재하는 레거시 스키마"라는 조합에서 비용이 특히 비쌌다.**

- 모듈 다수 → 마이그레이션 경로도 다수 → Flyway 기본 제공 단일 버전 축 붕괴
- 순서 보장을 직접 구현하는 시점 = 이미 도구의 범위 이탈

되짚어보면 신호는 일찍부터 있었다.

- 신호 발생 시점: FlywayConfig에 커스텀 로직이 붙기 시작한 때 (모듈별 분리 시점)
- 그때 했어야 할 질문: "이 도구가 이 구조에 맞는가"
- 실제 선택: 문제가 생길 때마다 설정 클래스를 키우는 방향으로 3주 경과
