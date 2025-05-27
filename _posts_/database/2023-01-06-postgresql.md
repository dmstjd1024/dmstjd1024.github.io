---
title:  "PostgreSQL이란"

categories:
  - database
tags:
  - [Database, Postgresql]

toc: true
toc_sticky: true

date: 2023-01-06
last_modified_at: 2023-01-06
---

# PostgreSQL
---
오픈 소스 객체 관계형 데이터베이스  
새로운 하나의 프로그래밍처럼 구현하는 기능을 제공한다.

## 구조

클라이언트 / 서버 모델 사용


## 기능

트랜잭션과 ACID(Atomicity, Consistency, Isolation, Durability)를 지원
또한 주요 기능들을 많이 가지고 있다고 한다.

Nested transactions (savepoints)    
Point in time recovery  
Online/hot backups, Parallel restore  
Rules system (query rewrite system)  
B-tree, R-tree, hash, GiST method indexes  
Multi-Version Concurrency Control (MVCC)  
Tablespaces  
Procedural Language  
Information Schema  
I18N, L10N  
Database & Column level collation  
Array, XML, UUID type  
Auto-increment (sequences),  
Asynchronous replication  
LIMIT/OFFSET  
Full text search  
SSL, IPv6  
Key/Value storage  
Table inheritance

등등 여러 기능들을 제공한다고 하는데 여기서 Auto-increment나 Limit 등등 빼고는 잘 접하지 않아서 그런지 이해는 못하겠다. 나중에 PostgreSQL을 좀 더 많이쓰는 일이 생기면 접할 것 같다.

## 특징

- 유연한 객체 생성  
  단순한 자료 저장소로써의 기능을 넘어 마치 하나의 새로운 프로그래밍 언어처럼 개발자의 창의성에 따라 무한한 기능을 손쉽게 구현할 수 있도록 한다.

- 상속  
  java 또는 C++ 프로그래밍 언어와 같이 테이블을 만들어 그 테이블 상속 기능을 이용해 하위 테이블을 만들 수 있다. 테이블에 저장된 자료는 상위 테이블을 조회하면, 해당 테이블의 하위 테이블에 포함된 모든 자료를 조회할 수 있으며, 하위 테이블을 만들 때, 상위 테이블의 칼럼을 그대로 상속 받으면서, 하위 테이블에만 속하는 칼럼을 추가로 만들 수 있다.

- 함수  
  때때로, ‘저장 프로시저’라고 불리는 SQL문으로 작성된 함수를 서버환경에서 사용할 수 있다. 비록 다른 언어와는 달리 제어문과 반복문을 사용하지는 못하지만, 다른 언어와 결합시킬 수 있다. 일부 언어에서는 심지어 트리거 내부에서 실행시킬 수 있다.

---  

## 내 생각

일단은 이러한 장점들이 있지만 현재 프로젝트에선 JPA를 활용하여 진행하므로 PostgreSQL의 장점을 활용할 기회가 있을지는 잘 모르겠다. 차후 postgresQL의 특징을 사용하는 경험이나 정보를 듣는다면 추가로 적용하겠다.
