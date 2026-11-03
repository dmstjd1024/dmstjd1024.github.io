---
title:  "RDS 란"
subtitle: "Aurora·OLTP/OLAP·백업 정리"
description: "Aurora·OLTP/OLAP·백업 정리"
categories:
  - AWS
tags:
  - AWS
  - RDS
  - Database

date: 2025-06-05
thumbnail: "/assets/img/thumbnail/aws_thumbnail.jpeg"
card_thumbnail: "/assets/img/thumbnail/aws_card.jpeg"
---
## RDS 란

- 관계형 데이터 베이스 서비스
- 백업·패치·장애 복구 등을 AWS가 관리

## Amazon Aurora
- MySQL·PostgreSQL과 호환되는 AWS의 관계형 DB 엔진. 서버리스는 운영 방식 중 하나이며, 머신러닝 전용 DB는 아님

## 데이터 웨어하우스
- 데이터 관리하는 시스템 유형
- 데이터 분석 작업 진행
- 즉, '데이터를 보관하고 사용하는 저장 창고'
- 하나 혹은 여러 개의 소스로부터 데이터 수집, 보관, 규모가 큰 데이터를 분석하는 데 사용

## OLTP vs OLAP
- **OLTP (Online Transaction Processing)**: 주문·결제처럼 짧은 읽기·쓰기 트랜잭션을 다수 처리하는 시스템
- **OLAP (Online Analytical Processing)**: 대량의 데이터를 분석하고, 복잡한 쿼리를 실행하는 시스템

<div class="diagram" role="img" aria-label="OLTP 와 OLAP 비교">
{% include diagrams/rds--oltp-olap.svg %}
</div>

## 데이터베이스 백업

<div class="diagram" role="img" aria-label="자동 백업과 스냅샷 비교">
{% include diagrams/rds--backup.svg %}
</div>

## 자동 백업 (AB : Auto Backup)
- 0~35일 설정(0은 자동 백업 비활성화, 콘솔 기본값은 7일), 스냅샷과 트랜잭션 로그 생성
- 백업은 S3에 저장되지만, 요금은 RDS 백업 저장 공간 기준으로 계산. 무료 허용량과 초과분은 엔진·리전의 요금표에서 확인
- 백업 초기화 중 I/O가 잠시 멈출 수 있음. MySQL·MariaDB·PostgreSQL·Oracle의 Multi-AZ는 대기 인스턴스에서 백업하므로 주 인스턴스의 I/O를 중지하지 않음
- RDS 인스턴스 삭제 시, 자동 백업은 유지 여부를 선택하며 수동·최종 스냅샷은 남음

## 스냅샷 (Snapshot)
- 수동으로 생성, 백업 크기만큼 S3에 저장
- 개발자가 수동으로 실행

## 복원 원리
- 백업에서 복원 시, 새로운 인스턴스 생성
- 원본과 복원 인스턴스 이름은 사용자가 정함. `original`, `restored`는 예시 이름

## 다중 가용 영역과 읽기 전용

<div class="diagram" role="img" aria-label="Multi-AZ 와 Read Replica 비교">
{% include diagrams/rds--multi-az.svg %}
</div>

## 다중 가용 영역 (Multi-AZ)
- Multi-AZ DB 인스턴스는 다른 가용영역의 대기 인스턴스에 **동기 복제**하며, 장애가 나면 자동 전환
- 이 대기 인스턴스는 읽기 분산용이 아님. 읽기도 제공하는 Multi-AZ DB 클러스터와 구분

## 읽기 전용 (Read Replica)
- 읽기 전용 인스턴스 생성, 원본 인스턴스에 대한 읽기 작업을 분산시켜 성능 향상
- 복제본 개수는 엔진별로 다르며, MySQL·MariaDB·PostgreSQL은 최대 15개

## 캐시로 성능 향상(엘라스틱캐시)

- AWS 리소스, 클라우드 내 인메모리를 사용해 데이터베이스 성능 향상
- 종류 : 맴캐시드, 레디스

## 맴캐시드
- 오브젝트 캐시 라고 불리며, 메모리 사용량에 있어 문자열 자료형을 처리할 때 주로 사용
- 캐시의 몸집이 커졌다 작아졌다 함

## 레디스
- 복잡한 데이터 타입 메모리 저장
- 리스트·해시·집합 등 여러 자료구조 지원. 점수 기반 정렬은 정렬 집합(Sorted Set)을 사용
- 다중 가용 영역 기능 포함

<div class="diagram" role="img" aria-label="맴캐시드와 레디스 비교">
{% include diagrams/rds--cache.svg %}
</div>
