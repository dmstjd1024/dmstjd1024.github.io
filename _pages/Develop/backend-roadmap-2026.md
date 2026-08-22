---
title: "백엔드 개발자 로드맵 2026 — 전체 구조 한눈에 보기"

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

[roadmap.sh/backend](https://roadmap.sh/backend) 의 백엔드 개발자 로드맵을 그대로 옮겨 그렸다.
원본은 가로로 넓은 한 장짜리 마인드맵이라 화면에서 훑기가 불편해서, **단계별로 쪼개서** 정리했다.

기준 데이터는 2026-02-07 갱신본이고 **토픽 23개 · 세부 항목 132개**다.

먼저 색부터 짚고 간다. 로드맵의 색은 장식이 아니라 **분류**다.

| 색 | 의미 | 개수 |
|---|---|---|
| 🟣 보라 | 추천 — 기본으로 이걸 고르면 된다 | 71개 |
| 🟢 초록 | 대안 — 보라색 대신 **택1**, 둘 다 할 필요 없다 | 25개 |
| ⚪ 회색 | 순서 무관 — 아무 때나 배워도 된다 | 11개 |

이걸 모르면 로드맵이 **'다 해야 하는 목록'** 으로 보인다.
초록색은 택1이다. MySQL 과 PostgreSQL 을 둘 다 파야 하는 게 아니다.

---

전체 흐름
=====
-----

세부 항목을 다 넣으면 그림이 벽이 되므로, 큰 단계만 먼저 본다.

```mermaid
flowchart TD
    A[인터넷 기초] --> B[프론트엔드 기초]
    B --> C[백엔드 언어 선택]
    C --> D[버전 관리]
    D --> E[관계형 DB]
    E --> F[API]
    F --> G[캐싱]
    G --> H[웹 서버]
    H --> I[AI]
    I --> J[CI / CD]
    J --> K[테스트 · DB 심화]
    K --> L[메시지 브로커 · 검색엔진]
    L --> M[아키텍처 패턴]
    M --> N[실시간 데이터 · DB 확장]
    N --> O[대규모 서비스 대응]
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

백엔드를 하더라도 **HTML·CSS·JS 는 기초까지는 본다.**
내가 만든 API 를 결국 프론트가 쓰기 때문이다.

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

여기가 초보자가 가장 많이 헤매는 지점인데, **언어는 하나만 고르면 된다.**
로드맵이 여러 개를 나열한 건 선택지를 보여준 것이지 다 하라는 뜻이 아니다.

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

DB 는 **PostgreSQL 하나가 추천**이고 나머지는 전부 대안이다.
`N+1 문제` 가 세부 항목으로 따로 박혀 있는 게 눈에 띈다. 그만큼 자주 터진다는 뜻이다.

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

예전 로드맵에는 **한 칸도 없던 영역**이다.
위치도 눈여겨볼 만한데, 맨 뒤 부록이 아니라 **기본기 직후 · 심화 직전**에 들어가 있다.

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

**도구를 쓰는 것과 AI 기능을 만드는 것이 분리돼 있다.**
`Cursor 를 쓴다` 와 `스트리밍·Function Calling 으로 기능을 만든다` 는 다른 칸이고,
백엔드 개발자에게 요구되는 건 결국 뒤쪽이다.

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

마지막 칸이 요즘 로드맵에서 눈에 띄게 두꺼워진 부분이다.
`관측성(Observability)`, `서킷 브레이커`, `백프레셔` 같은 항목이 새로 올라왔다.

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

"여기서 갈라져 나가라"는 표시에 가깝다. 그만큼 각각이 하나의 큰 주제라는 뜻이다.

---

정리
=====
-----

- 뼈대는 **인터넷 기초 → 언어 → Git → DB → API → 캐싱 → 웹 서버** 까지가 기본기다.
- **AI 가 기본기 바로 다음**에 들어왔다. 예전 로드맵에는 없던 영역이다.
- 색을 먼저 본다. **초록은 택1**이지 전부 해야 할 목록이 아니다.
- Docker·쿠버네티스는 각자 다른 로드맵으로 빠진다.

로드맵은 체크리스트가 아니라 지도에 가깝다.
다 밟아야 하는 게 아니라, **지금 내가 어디쯤 서 있는지** 확인하는 용도로 보는 게 맞다고 생각한다.
