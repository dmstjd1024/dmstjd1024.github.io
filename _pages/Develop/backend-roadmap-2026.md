---
title: "백엔드 개발자 로드맵 2026"

categories:
  - Develop
tags:
  - Develop
  - Roadmap
  - Backend

date: 2026-08-22
thumbnail: "/assets/img/thumbnail/ect_thumbnail.jpg"
mermaid: true
---

| 색 | 의미 | 개수 |
|---|---|---|
| 🟣 보라 | 추천. 기본값으로 선택한다 | 71개 |
| 🟢 초록 | 대안. 보라색 대신 **택1** | 25개 |
| ⚪ 회색 | 순서 무관 | 11개 |

초록색은 택1이다. MySQL 과 PostgreSQL 을 둘 다 학습할 필요는 없다.

---

전체 흐름
=====
-----

세부 항목을 제외한 큰 단계만 표시한다.

```mermaid
flowchart TD
    subgraph ROW1[" "]
        direction LR
        A[인터넷 기초] --> B[프론트엔드 기초] --> C[백엔드 언어 선택] --> D[버전 관리]
    end

    subgraph ROW2[" "]
        direction LR
        E[관계형 DB] --> F[API] --> G[캐싱] --> H[웹 서버]
    end

    subgraph ROW3[" "]
        direction LR
        I[AI] --> J[CI / CD] --> K[테스트] --> L[DB 심화]
    end

    subgraph ROW4[" "]
        direction LR
        M[메시지 브로커<br/>검색엔진] --> N[아키텍처 패턴] --> O[실시간 데이터<br/>DB 확장] --> P[대규모 서비스 대응]
    end

    ROW1 ~~~ ROW2
    ROW2 ~~~ ROW3
    ROW3 ~~~ ROW4
```

---

1단계 · 기초
=====
-----

```mermaid
flowchart TD
    subgraph NET["인터넷 기초"]
        direction LR
        N1[인터넷 동작 원리] --- N2[HTTP] --- N3[도메인 · 호스팅] --- N4[DNS] --- N5[브라우저 동작 원리]
    end

    subgraph FE["프론트엔드 기초"]
        direction LR
        F1[HTML] --- F2[CSS] --- F3[JavaScript]
    end

    NET --> FE
```

백엔드 직군이라도 **HTML·CSS·JavaScript 는 기초 수준까지 포함된다.**
API 의 소비자가 프론트엔드이기 때문이다.

---

2단계 · 언어와 버전 관리
=====
-----

```mermaid
flowchart TD
    subgraph LANG["백엔드 언어 · 하나만 고른다"]
        direction LR
        L1["JavaScript · Python · Go<br/>(추천)"] --- L2["Java · C# · PHP<br/>Ruby · Rust (대안)"]
    end

    subgraph VCS["버전 관리"]
        direction LR
        V1[Git] --- V2["GitHub (추천)"] --- V3["GitLab (대안)"]
    end

    LANG --> VCS
```

**언어는 하나만 선택한다.** 나열된 항목은 선택지이며 전부 학습하는 대상이 아니다.

---

3단계 · 데이터베이스와 API
=====
-----

```mermaid
flowchart TD
    subgraph DB["관계형 DB"]
        direction LR
        D1["PostgreSQL (추천)"] --- D2["MySQL · MariaDB<br/>SQLite · MS SQL · Oracle (대안)"]
    end

    subgraph CONCEPT["같이 익히는 개념"]
        direction LR
        C1[마이그레이션] --- C2[N+1 문제]
    end

    subgraph API["API 스타일"]
        direction LR
        A1["REST · JSON API<br/>(추천)"] --- A2["GraphQL · gRPC · SOAP<br/>(순서 무관)"]
    end

    subgraph AUTH["인증"]
        direction LR
        T1[JWT] --- T2[OAuth] --- T3[Basic · Token · Cookie] --- T4["OpenID · SAML<br/>(순서 무관)"]
    end

    DB --> CONCEPT --> API --> AUTH
```

관계형 DB 는 **PostgreSQL 만 추천**이고 나머지는 대안이다.
`N+1 문제` 와 `마이그레이션` 은 특정 DB 에 종속되지 않는 공통 개념으로 분류돼 있다.

---

4단계 · 캐싱, 웹 서버, 보안
=====
-----

```mermaid
flowchart TD
    subgraph CACHE["캐싱"]
        direction LR
        K1["Redis (추천)"] --- K2["Memcached (대안)"] --- K3[HTTP 캐싱]
    end

    subgraph WEB["웹 서버"]
        direction LR
        W1["Nginx (추천)"] --- W2["Apache · Caddy · MS IIS<br/>(대안)"]
    end

    subgraph SEC["웹 보안"]
        direction LR
        S1[HTTPS · SSL/TLS] --- S2[CORS · CSP] --- S3[OWASP Top 10] --- S4["해시: bcrypt · scrypt<br/>MD5 · SHA"]
    end

    CACHE --> WEB --> SEC
```

---

5단계 · AI (2026년 신규)
=====
-----

이전 로드맵에는 없던 영역이다. 배치 위치는 맨 뒤가 아니라 **기본기 직후 · 심화 직전**이다.

```mermaid
flowchart TD
    subgraph BASIC["기초"]
        direction LR
        A1[LLM 동작 원리] --- A2[임베딩 · 벡터] --- A3[RAG]
    end

    subgraph TOOL["AI 코딩 도구"]
        direction LR
        B1["Claude Code (추천)"] --- B2["Cursor · Copilot<br/>(대안)"] --- B3[프롬프팅 기법]
    end

    subgraph BUILD["AI 기능 개발"]
        direction LR
        C1[Agents · MCP] --- C2[스트리밍] --- C3["구조화된 출력<br/>Function Calling"]
    end

    BASIC --> TOOL --> BUILD
```

**AI 도구의 사용과 AI 기능의 구현은 별도 항목으로 구분된다.**
백엔드 직군의 요구 범위는 후자, 즉 스트리밍·Function Calling 을 이용한 기능 구현이다.

---

6단계 · 심화
=====
-----

```mermaid
flowchart TD
    subgraph T["테스트"]
        direction LR
        T1[단위] --- T2[통합] --- T3[기능]
    end

    subgraph DB2["DB 심화"]
        direction LR
        D1[트랜잭션 · ACID] --- D2[정규화] --- D3[ORM] --- D4[인덱스]
    end

    subgraph MQ["메시지 브로커 · 검색엔진"]
        direction LR
        M1["Kafka (추천)"] --- M2["RabbitMQ (대안)"] --- M3["Elasticsearch (추천)"] --- M4["Solr (대안)"]
    end

    subgraph ARCH["아키텍처 패턴"]
        direction LR
        R1[모놀리식] --- R2[마이크로서비스] --- R3[SOA · 서버리스] --- R4[서비스 메시] --- R5[12 Factor App]
    end

    T --> DB2 --> MQ --> ARCH
```

---

7단계 · 규모 대응
=====
-----

```mermaid
flowchart TD
    subgraph RT["실시간 데이터"]
        direction LR
        E1[WebSocket] --- E2[SSE] --- E3[롱/숏 폴링]
    end

    subgraph SCALE["DB 확장"]
        direction LR
        S1[인덱스] --- S2[복제] --- S3[샤딩] --- S4[CAP 정리]
    end

    subgraph NOSQL["NoSQL"]
        direction LR
        N1["MongoDB · Redis<br/>(추천)"] --- N2["DynamoDB · Cassandra<br/>Neo4j · ClickHouse (대안)"]
    end

    subgraph OPS["대규모 서비스 대응"]
        direction LR
        O1[관측성 · 모니터링] --- O2[서킷 브레이커] --- O3[스로틀링] --- O4[우아한 성능 저하]
    end

    RT --> SCALE --> NOSQL --> OPS
```

`관측성(Observability)`, `서킷 브레이커`, `백프레셔`, `스로틀링` 등
장애 대응·복원력 관련 항목이 이 구간에 배치돼 있다.

---

Docker 와 Kubernetes 는?
=====
-----

로드맵을 보면 컨테이너 자리에 Docker·Kubernetes 가 있는데,
이 둘은 **로드맵 안의 학습 항목이 아니라 별도 로드맵으로 빠지는 버튼**이다.

```mermaid
flowchart LR
    B[백엔드 로드맵] --> D["Docker 로드맵<br/>roadmap.sh/docker"]
    B --> K["쿠버네티스 로드맵<br/>roadmap.sh/kubernetes"]
```

백엔드 로드맵 내부의 학습 항목이 아니라, 각각 독립된 로드맵으로 연결되는 분기점이다.

---

정리
=====
-----

- 기본기 구간은 **인터넷 기초 → 언어 → Git → DB → API → 캐싱 → 웹 서버** 까지다.
- **AI 는 기본기 직후**에 배치돼 있다. 이전 로드맵에는 없던 영역이다.
- **초록색은 택1**이며 전체 학습 대상이 아니다.
- Docker·쿠버네티스는 별도 로드맵으로 분리돼 있다.

---

참고
=====
-----

- [roadmap.sh/backend](https://roadmap.sh/backend) — 원본 로드맵 (2026-02-07 갱신본 기준, 토픽 23개 · 세부 항목 132개)
- [roadmap.sh/docker](https://roadmap.sh/docker) · [roadmap.sh/kubernetes](https://roadmap.sh/kubernetes) — 컨테이너 쪽에서 갈라져 나가는 로드맵
