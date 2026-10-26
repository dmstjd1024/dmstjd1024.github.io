---
layout: default
---

{%- comment -%}
  홈 = 포트폴리오.

  글 화면(post-body)의 타이포그래피를 그대로 쓰면 워드 문서처럼 보인다.
  여기는 읽는 화면이 아니라 3초 안에 판단되는 화면이라 구조를 따로 짠다.
  스타일은 _sass/home.scss.
{%- endcomment -%}

<div class="home">

  <header class="hero">
    <p class="hero__eyebrow">6년 차 · Java · Spring</p>
    <h1 class="hero__title">백엔드 개발자<br>전은성입니다.</h1>
    <p class="hero__line">Java와 Spring으로 서비스를 개발합니다. 데이터 모델 변경, 조회 성능 개선, 배포 자동화를 맡아 왔습니다.</p>
    <p class="hero__links">
      <a class="hero__cta" href="#featured">주요 작업 보기</a>
      <a href="https://github.com/dmstjd1024">GitHub</a>
      <a href="/글/index.html">블로그 글</a>
    </p>
  </header>

{%- comment -%}
  대표 사례. 아래 "프로젝트" 에서 결과값이 가장 뚜렷한 셋만 위로 올렸다.
  수치는 아래 프로젝트 카드의 case__out 과 같은 값이어야 한다.
{%- endcomment -%}
  <section class="featured" id="featured" aria-labelledby="h-featured">
    <h2 class="sec__title" id="h-featured">주요 작업</h2>
    <ul class="featured__list">
      <li>
        <a href="/React/한글-폰트-pdf-성능.html">
          <b>탄소배출 산정 웹앱 — PDF 생성 속도 개선</b>
          <span>한글 텍스트 배치에서 발생한 지연을 확인하고, 화면을 이미지로 저장하는 방식으로 PDF 생성을 바꿨습니다.</span>
          <code>PDF 생성 6.4초 → 0.7초</code>
        </a>
      </li>
      <li>
        <a href="#h-work">
          <b>블록체인 DevOps 플랫폼 — 신규 기관 환경 구성 자동화</b>
          <span>기관별 클러스터와 블록체인 네트워크를 만드는 명령을 스크립트로 묶어, API 요청 한 번으로 실행하게 했습니다.</span>
          <code>운영자 수동 조작 157회 → 1회</code>
        </a>
      </li>
      <li>
        <a href="/Database/gin-trigram-인덱스가-안-먹던-이유.html">
          <b>장비 관리 시스템 — 검색 인덱스가 사용되도록 쿼리 수정</b>
          <span>검색 조건의 LOWER() 때문에 기존 인덱스가 사용되지 않았습니다. 검색 쿼리를 ILIKE로 바꿔 인덱스와 일치시켰습니다.</span>
          <code>검색 조건 약 130곳 수정</code>
        </a>
      </li>
    </ul>
  </section>

  <section class="recent" aria-labelledby="h-recent">
    <h2 class="sec__title" id="h-recent">최근 글</h2>
    <ul class="recent__list">
      {%- assign latest = site.documents | where_exp: "p", "p.description" | sort: "date" | reverse -%}
      {%- for p in latest limit: 3 -%}
        {%- assign seg = p.path | remove_first: '_pages/' | split: '/' -%}
        <li><a href="{{ p.url }}"><span>{{ p.title }}</span><i>{{ seg[0] }}</i></a></li>
      {%- endfor -%}
    </ul>
    <p class="recent__more"><a href="/글/index.html">모든 글 보기 →</a></p>
  </section>

  <section class="stack" aria-labelledby="h-stack">
    <h2 class="sec__title" id="h-stack">기술 스택</h2>
    <p class="sec__note">실무와 개인 프로젝트에서 사용한 기술입니다. 사용한 환경과 선택 이유는 아래 프로젝트에 정리했습니다.</p>
{%- comment -%}
  기술 스택.

  두 가지를 섞어 쓴다:
    - 아이콘(skillicons.dev) — 대표 기술. 한눈에 훑는 용도
    - 배지(shields.io) — 아이콘이 없는 기술 (지금은 Hyperledger Fabric 하나)

  아이콘이 있는 기술만 남기고 나머지(Spring Security · JPA · QueryDSL ·
  MyBatis 등)는 뺐다. 나열이 길어지면 훑는 용도라는 목적 자체가 사라진다.
  자세한 스택은 아래 프로젝트 카드의 proj__stack 줄에 적혀 있다.

  아이콘은 낱개 파일로 둔다. 묶음(icons-backend.svg 처럼 여러 개가 한 파일)
  이면 개별 hover 를 잡을 수 없어서다. 마우스를 올리면 이름이 뜬다.

  배경색이 SVG 안에 박혀 있어 밝은/어두운 두 벌을 받아 테마에 따라 하나만
  보인다. 기본 버전은 남색 배경이라 흰 바탕에서 그 줄만 튄다.

  바꾸려면 skillicons.dev/icons?i=<슬러그>&theme=light 와 theme 없는 주소로
  각각 받아 i-<슬러그>.svg / i-<슬러그>-dark.svg 를 덮어쓴다.

  예외: i-claude(-dark).svg 는 손으로 만든 것이다. skillicons 에 claude
  슬러그가 없어 빈 SVG 를 돌려주므로, simple-icons 의 로고를 같은 타일
  규격(256x256, rx=60)에 얹었다. 배경은 브랜드색이라 두 벌이 같은 내용이다.
  위 주소로 다시 받으면 빈 파일로 덮인다 — 받지 말 것.
{%- endcomment -%}
    <dl class="stack__grid">
      <div>
        <dt>백엔드</dt>
        <dd>
          <div class="stack__icons">
          <span class="ic" tabindex="0">
            <img class="ic__img ic__img--light" src="/assets/img/badge/i-java.svg" alt="Java" height="44">
            <img class="ic__img ic__img--dark" src="/assets/img/badge/i-java-dark.svg" alt="" aria-hidden="true" height="44">
            <span class="ic__name">Java</span>
          </span>
          <span class="ic" tabindex="0">
            <img class="ic__img ic__img--light" src="/assets/img/badge/i-spring.svg" alt="Spring" height="44">
            <img class="ic__img ic__img--dark" src="/assets/img/badge/i-spring-dark.svg" alt="" aria-hidden="true" height="44">
            <span class="ic__name">Spring</span>
          </span>
          <span class="ic" tabindex="0">
            <img class="ic__img ic__img--light" src="/assets/img/badge/i-python.svg" alt="Python" height="44">
            <img class="ic__img ic__img--dark" src="/assets/img/badge/i-python-dark.svg" alt="" aria-hidden="true" height="44">
            <span class="ic__name">Python</span>
          </span>
          </div>
        </dd>
      </div>
      <div>
        <dt>데이터베이스</dt>
        <dd>
          <div class="stack__icons">
          <span class="ic" tabindex="0">
            <img class="ic__img ic__img--light" src="/assets/img/badge/i-postgres.svg" alt="PostgreSQL" height="44">
            <img class="ic__img ic__img--dark" src="/assets/img/badge/i-postgres-dark.svg" alt="" aria-hidden="true" height="44">
            <span class="ic__name">PostgreSQL</span>
          </span>
          <span class="ic" tabindex="0">
            <img class="ic__img ic__img--light" src="/assets/img/badge/i-mysql.svg" alt="MySQL" height="44">
            <img class="ic__img ic__img--dark" src="/assets/img/badge/i-mysql-dark.svg" alt="" aria-hidden="true" height="44">
            <span class="ic__name">MySQL</span>
          </span>
          <span class="ic" tabindex="0">
            <img class="ic__img ic__img--light" src="/assets/img/badge/i-redis.svg" alt="Redis" height="44">
            <img class="ic__img ic__img--dark" src="/assets/img/badge/i-redis-dark.svg" alt="" aria-hidden="true" height="44">
            <span class="ic__name">Redis</span>
          </span>
          </div>
        </dd>
      </div>
      <div>
        <dt>프론트엔드</dt>
        <dd>
          <div class="stack__icons">
          <span class="ic" tabindex="0">
            <img class="ic__img ic__img--light" src="/assets/img/badge/i-react.svg" alt="React" height="44">
            <img class="ic__img ic__img--dark" src="/assets/img/badge/i-react-dark.svg" alt="" aria-hidden="true" height="44">
            <span class="ic__name">React</span>
          </span>
          </div>
        </dd>
      </div>
      <div>
        <dt>인프라</dt>
        <dd>
          <div class="stack__icons">
          <span class="ic" tabindex="0">
            <img class="ic__img ic__img--light" src="/assets/img/badge/i-kubernetes.svg" alt="Kubernetes" height="44">
            <img class="ic__img ic__img--dark" src="/assets/img/badge/i-kubernetes-dark.svg" alt="" aria-hidden="true" height="44">
            <span class="ic__name">Kubernetes</span>
          </span>
          <span class="ic" tabindex="0">
            <img class="ic__img ic__img--light" src="/assets/img/badge/i-docker.svg" alt="Docker" height="44">
            <img class="ic__img ic__img--dark" src="/assets/img/badge/i-docker-dark.svg" alt="" aria-hidden="true" height="44">
            <span class="ic__name">Docker</span>
          </span>
          <span class="ic" tabindex="0">
            <img class="ic__img ic__img--light" src="/assets/img/badge/i-githubactions.svg" alt="GitHub Actions" height="44">
            <img class="ic__img ic__img--dark" src="/assets/img/badge/i-githubactions-dark.svg" alt="" aria-hidden="true" height="44">
            <span class="ic__name">GitHub Actions</span>
          </span>
          <span class="ic" tabindex="0">
            <img class="ic__img ic__img--light" src="/assets/img/badge/i-linux.svg" alt="Linux" height="44">
            <img class="ic__img ic__img--dark" src="/assets/img/badge/i-linux-dark.svg" alt="" aria-hidden="true" height="44">
            <span class="ic__name">Linux</span>
          </span>
          </div>
          <div class="stack__sub">
            <img src="/assets/img/badge/hyperledger-fabric.svg" alt="Hyperledger Fabric" height="24">
          </div>
        </dd>
      </div>
      <div>
        <dt>AI</dt>
        <dd>
          <div class="stack__icons">
          <span class="ic" tabindex="0">
            <img class="ic__img ic__img--light" src="/assets/img/badge/i-claude.svg" alt="Claude Code" height="44">
            <img class="ic__img ic__img--dark" src="/assets/img/badge/i-claude-dark.svg" alt="" aria-hidden="true" height="44">
            <span class="ic__name">Claude Code</span>
          </span>
          </div>
        </dd>
      </div>
    </dl>
  </section>

  <section class="work" aria-labelledby="h-work">
    <h2 class="sec__title" id="h-work">프로젝트</h2>
    <p class="sec__note">프로젝트에서 맡은 일과 해결한 문제를 정리했습니다. 자세한 과정은 관련 글에서 볼 수 있습니다.</p>

{%- comment -%}
  프로젝트 카드. 제목 / 스택 / 사례 2~3개.
  사례마다 결과값을 모노스페이스로 못박는다 — 이 블로그 글의 설득력이
  측정값에서 나오기 때문에 그 성격을 화면에도 그대로 가져왔다.
{%- endcomment -%}

    <article class="proj">
      <header>
        <h3>탄소배출 산정 B2B 웹앱</h3>
        <p class="proj__stack">MySQL · JPA/QueryDSL · Gradle 멀티모듈 · React</p>
      </header>
      <p class="proj__what">
        제품별 탄소배출량을 계산하는 서비스입니다. DB 스키마 관리와 조회 성능을
        개선하고, 중복으로 유지되던 화면 구현을 통합했습니다.
      </p>
      <ul class="cases">
        <li>
          <h4>기존 스키마와 충돌한 Flyway를 제거하고 필요한 SQL만 자동 적용</h4>
          <p>
            Flyway 적용 후 새 DB에서 스키마를 재현하지 못하고, 모듈별 실행 순서와
            기존 스키마의 차이를 처리하는 설정이 221줄까지 늘었습니다. 이 구성을
            유지하는 대신 Flyway를 제거하고, JPA 스키마 관리와 보완 SQL 자동 실행으로 바꿨습니다.
          </p>
          <p class="case__out"><code>도입 22일 후 제거 · 보완 SQL 자동 적용</code></p>
          <p class="case__src">
            <a href="/Database/flyway를-도입하고-3주-만에-걷어낸-이야기.html">Flyway를 제거한 이유</a>
            <a href="/Database/ddl-auto-update의-빈틈을-보완-ddl-자동화로-메우기.html">스키마 변경 SQL 자동 적용</a>
          </p>
        </li>
        <li>
          <h4>집계 조회와 PDF 생성의 병목을 각각 개선</h4>
          <p>
            조회할 때마다 CTE 5개를 재계산하던 뷰는 집계 결과를 저장하는 테이블로
            옮겼습니다. 기존 조회를 유지한 채 데이터 일치를 확인한 뒤 읽기 경로를 전환했습니다.
            PDF 생성에서는 한글 텍스트 배치가 병목이어서, 화면 캡처 방식으로 바꿔 생성 시간을 줄였습니다.
          </p>
          <p class="case__out"><code>PDF 생성 6.4초 → 0.7초 · 이미지 방식이라 텍스트 검색 불가</code></p>
          <p class="case__src">
            <a href="/Database/뷰를-물질화-테이블로-읽기-비용을-쓰기-시점으로-옮기기.html">집계 뷰를 테이블로 전환한 과정</a>
            <a href="/Spring/n+1-제거-4종-세트-fetch-join이-답이-아닐-때.html">N+1 문제를 해결한 네 가지 사례</a>
            <a href="/React/한글-폰트-pdf-성능.html">PDF 생성 방식 변경과 성능 비교</a>
          </p>
        </li>
        <li>
          <h4>V1·V2 화면 구현을 통합하고 사용하지 않는 파일 정리</h4>
          <p>
            V1과 V2가 함께 남아 같은 버그를 두 번 수정해야 했습니다. 화면을 단계적으로
            V2로 통합했습니다. 별도로 실행 경로를 확인해, 최근까지 수정됐지만 실제로는
            사용하지 않는 파일도 정리했습니다.
          </p>
          <p class="case__out"><code>V1 코드 2,389줄 삭제 · 미사용 파일 누적 102개 정리</code></p>
          <p class="case__src">
            <a href="/Develop/v1-v2-이중-스택-정리.html">V1·V2 통합 과정</a>
            <a href="/Develop/죽은-파일이-더-최신이었다.html">실행 경로를 확인해 미사용 파일 정리</a>
          </p>
        </li>
      </ul>
    </article>

    <article class="proj">
      <header>
        <h3>블록체인 DevOps 플랫폼 <em>공공</em></h3>
        <p class="proj__stack">Java 21 · Spring Boot · Kubernetes · Hyperledger Fabric/Besu · Next.js · 폐쇄망</p>
        <p class="proj__meta">
          공공 스마트시티 사업 · 약 6개월
          <span>백엔드·인프라 담당 · 프론트엔드 개발자 1명과 협업</span>
        </p>
      </header>
      <p class="proj__what">
        기관별 Kubernetes 클러스터와 블록체인 네트워크를 생성·관리하는 플랫폼입니다.
        백엔드 API와 인프라 자동화를 담당했습니다. 인터넷이 차단된 환경에서 설치할 수
        있도록 필요한 이미지를 로컬 레지스트리에 미리 적재하고, 외부 다운로드를 막았습니다.
      </p>
      <ul class="cases">
        <li>
          <h4>신규 기관 환경 구성을 API 요청 한 번으로 자동화</h4>
          <p>
            신규 기관을 추가할 때 약 157회의 명령 실행과 설정 파일 5종 작성이 필요했습니다.
            각 단계가 끝날 때마다 운영자가 다음 명령을 실행하던 과정을 스크립트로 묶고,
            애플리케이션 서버에서 SSH로 실행하게 했습니다. 20~43분이 걸리는 환경 구성은
            <b>트랜잭션 커밋 후 비동기로 처리</b>해 HTTP 응답을 기다리지 않게 했습니다.
            진행 상태를 DB에 기록해 실패한 작업을 확인할 수 있게 했습니다.
          </p>
          <p class="case__out"><code>운영자 수동 조작 157회 → 1회 · 실행 후 추가 조작 불필요</code></p>
          <p class="case__note">
            환경 구성에는 자동화 후에도 20~43분이 걸립니다. 운영자는 시작 요청 후
            각 단계를 지켜보며 다음 명령을 실행할 필요가 없어졌습니다.
          </p>
        </li>
        <li>
          <h4>기관별 클러스터로 운영 환경 분리</h4>
          <p>
            기관별로 데이터와 운영 환경을 분리해야 했습니다. 네임스페이스만 나누면 API 서버와
            CRD(사용자 정의 리소스 정의)를 공유하므로, <b>기관마다 독립 클러스터</b>를 구성했습니다.
            포트는 기관당 10개씩 배정하고, DB에 남은 최대 대역 다음 번호부터 할당했습니다.
            중간의 빈 대역은 건너뛰지만, 가장 높은 대역을 삭제하면 그 대역이 다시 배정될 수 있습니다.
          </p>
          <p class="case__out"><code>기관별 독립 클러스터 · 포트 10개씩 배정</code></p>
          <p class="case__note">
            기관당 약 0.9코어·메모리 2.4GiB·저장 공간 28Gi가 필요합니다.
            기관별 설정을 분리할 수 있지만, 공유 클러스터보다 자원을 많이 사용해 서버 한 대에 수용할 수 있는 기관 수는 줄어듭니다.
          </p>
        </li>
        <li>
          <h4>Fabric과 Besu의 배포·운영을 공통 API로 제공</h4>
          <p>
            Fabric과 Besu는 네트워크 구성과 인증 방식이 달라 각각의 명령이 필요했습니다.
            원격 실행의 공통 절차와 체인별 구현을 분리해, 사용자가 같은 REST API로
            배포·운영할 수 있게 했습니다. 파드 시작이 늦어져 실패하던 작업에는
            공통 대기·재시도 처리를 적용했습니다.
          </p>
          <p class="case__out"><code>Fabric 네트워크 생성 20단계 자동화 · 배포 스크립트 1,178줄</code></p>
          <p class="case__src">
            <a href="/Spring/toctou-버그-클래스-제거.html">SFTP 디렉터리 생성의 동시성 오류 해결</a>
            <a href="/Spring/비동기-api가-무조건-200을-반환했다.html">비동기 작업의 요청 검증과 응답 처리</a>
            <a href="/Infra/오퍼레이터-버그를-crd-스키마-패치로-우회하기.html">CRD 스키마 패치로 배포 오류 우회</a>
            <a href="/Infra/kubectl-exec-타임아웃과-재시도.html">kubectl exec 타임아웃과 재시도 적용</a>
          </p>
        </li>
      </ul>
      <p class="proj__scale">
        프로젝트 규모: 백엔드 655파일·63,828줄 &nbsp;/&nbsp; REST 컨트롤러 123개
        &nbsp;/&nbsp; 프론트엔드 536파일 &nbsp;/&nbsp; 커밋 1,083개
        &nbsp;/&nbsp; 직접 작성한 인프라 셸 스크립트 49개·8,831줄
      </p>
    </article>

    <article class="proj">
      <header>
        <h3>장비 관리 시스템 <em>레거시</em></h3>
        <p class="proj__stack">PostgreSQL · MyBatis · Spring · JSP</p>
      </header>
      <p class="proj__what">
        JSP와 JavaScript로 구현한 업무 화면 수십 개를 운영하는 시스템입니다.
        장비의 조직 소속 모델, 권한 관리, 검색 쿼리를 개선했습니다.
      </p>
      <ul class="cases">
        <li>
          <h4>장비의 소속 조직을 고객과 독립적으로 관리하도록 모델 변경</h4>
          <p>
            기존에는 고객의 조직 정보로 장비의 소속을 결정해, 고객과 다른 조직에 속하거나
            고객이 아직 배정되지 않은 장비를 처리할 수 없었습니다. 장비에 조직 컬럼을
            추가하고 기존 조인 결과로 값을 채웠습니다. 기존 조회와 새 컬럼의 값이 일치하는지
            확인하며 조회 경로를 단계적으로 전환했습니다.
          </p>
          <p class="case__out"><code>장비의 조직 정보 직접 저장 · 기존 데이터 이전 후 조회 전환</code></p>
          <p class="case__src">
            <a href="/Database/정규화된-조인을-버리고-역정규화하기.html">조직 컬럼 추가와 데이터 이전 과정</a>
          </p>
        </li>
        <li>
          <h4>검색 조건을 인덱스에 맞춰 전체 스캔 해소</h4>
          <p>
            부분일치 검색용 GIN trigram 인덱스를 만들었지만 검색에 사용되지 않았습니다.
            검색 컬럼에 적용한 <code>LOWER()</code>가 인덱스 정의와 달라,
            쿼리를 ILIKE로 바꿨습니다. 제조사 검색은 드롭다운으로 바꿔 부분일치 검색을 없앴습니다.
          </p>
          <p class="case__out"><code>약 130곳 ILIKE 전환 · 검색 시 전체 스캔 해소</code></p>
          <p class="case__src">
            <a href="/Database/gin-trigram-인덱스가-안-먹던-이유.html">검색 쿼리와 인덱스가 일치하지 않았던 원인</a>
            <a href="/Spring/인증-필터가-매-요청-db를-네번-때렸다.html">인증·권한·로깅 필터의 DB 접근 개선</a>
            <a href="/Java/depth-10-방어-코드가-버그를-감추고-있었다.html">깊이 제한으로 누락된 조상 조직 조회 수정</a>
          </p>
        </li>
      </ul>
    </article>

    <article class="proj">
      <header>
        <h3>자동매매 시스템 <em>개인</em></h3>
        <p class="proj__stack">Python · 증권사 API · Docker Compose · 실계좌 운용</p>
      </header>
      <p class="proj__what">
        증권사 API로 주문과 체결을 처리하는 개인 프로젝트입니다. 직접 개발해 실계좌로
        운용하며, 실제 체결 내역과 백테스트 결과로 계산과 전략을 검증하고 있습니다.
      </p>
      <ul class="cases">
        <li>
          <h4>실제 체결 47건과 대조해 수수료·세금 계산 수정</h4>
          <p>
            증권사가 청구한 금액과 시스템의 계산값을 대조해 수수료율 오류, 거래세율
            변경 누락, ETF 분류 오류를 확인했습니다. 요율과 분류 기준을 수정하고,
            ETF 여부를 확인하지 못하면 세금을 포함해 손익을 계산하도록 했습니다.
          </p>
          <p class="case__out"><code>실제 청구 세금 대비 상대오차 1.250% → 0.068%</code></p>
          <p class="case__src">
            <a href="/Etc/수수료율-4배-오차.html">체결 내역으로 수수료와 세금 검증</a>
          </p>
        </li>
        <li>
          <h4>ML 설정 오류를 수정한 뒤에도 기능을 비활성화한 이유</h4>
          <p>
            환경변수 누락으로 ML 기능이 켜지지 않는 문제를 수정한 뒤, 기능 사용 여부는
            별도로 검증했습니다. A/B 비교와 분류·회귀 실험에서 수익 개선 근거를 얻지 못했습니다.
            과거 데이터로 학습하고 이후 기간을 평가하는 순차 검증에서도 효과가 확인되지 않아
            기본값을 비활성화로 유지했습니다.
          </p>
          <p class="case__out"><code>A/B 비교·분류·회귀 실험 후 ML 비활성화 유지</code></p>
          <p class="case__src">
            <a href="/Etc/ML을-껐다-켜봤더니.html">ML 사용 여부를 판단한 검증 과정</a>
            <a href="/Etc/필터-기여도-계측으로-찾은-무거래-원인.html">매수 신호 이후 체결이 없었던 원인 분석</a>
          </p>
        </li>
      </ul>
    </article>
  </section>

{%- comment -%}
  경력 — 프로젝트 카드로 다루기엔 근거 글이 없는 구간까지 포함한 전체 이력.
  위 "프로젝트" 는 글로 근거를 댈 수 있는 것만 올렸다.
{%- endcomment -%}
  <section class="career" aria-labelledby="h-career">
    <h2 class="sec__title" id="h-career">경력</h2>
    <p class="sec__note">2021년부터 업무 시스템과 웹 서비스의 개발·유지보수를 맡아 왔습니다.</p>
    <ol class="career__list">
      <li>
        <span class="career__when">2023 — 현재</span>
        <span class="career__what">
          <b>ESG 컨설팅 기업</b> 백엔드 개발
          <em>탄소배출 산정 웹앱 · 블록체인 DevOps 플랫폼 · 장비 관리 시스템</em>
        </span>
      </li>
      <li>
        <span class="career__when">2021 — 2023</span>
        <span class="career__what">
          <b>SI·솔루션 기업</b> 시스템 개발·유지보수
          <em>관리자 페이지 개발 · 솔루션의 마이크로서비스 구조 전환 · 국방부 시스템 개발·유지보수</em>
        </span>
      </li>
    </ol>
  </section>

  <section class="how" aria-labelledby="h-how">
    <h2 class="sec__title" id="h-how">AI를 활용하는 방식</h2>
    <p class="sec__note">
      AI를 설계와 코드 검토에 활용합니다. 생성한 결과는 별도 검토와 실제 변경 내용 대조를 거쳐 반영합니다.
    </p>
    <ul class="how__list">
      <li>
        AI가 작성한 명세는 <b>이전 대화 없이 새 세션에서 검토</b>하게 합니다.
        작성할 때의 가정을 그대로 반복하지 않도록 검토 단계를 분리했습니다.
      </li>
      <li>
        여러 에이전트로 메모리 누수 후보 51건을 찾고, 별도로 코드 경로를 확인해
        49건을 수정했습니다. 데이터 유실 위험이 있는 1건은 보류했습니다.
      </li>
      <li>
        AI가 작성한 커밋 메시지가 실제 변경 내용과 달랐던 사례도 기록했습니다.
        추정 원인과 커밋 전에 확인할 항목을 함께 정리했습니다.
      </li>
    </ul>
    <p class="case__src">
      <a href="/AI/Claude/ai에게-스펙을-쓰게-하고-자기검토를-시키고-구현하기.html">명세 작성과 검토를 분리한 과정</a>
      <a href="/AI/Claude/에이전트-72개-메모리-누수-감사.html">메모리 누수 후보의 독립 검증</a>
      <a href="/AI/Claude/ai가-쓴-커밋-메시지가-거짓말을-했다.html">커밋 메시지와 실제 변경 내용의 불일치</a>
    </p>
  </section>

  <footer class="home__foot">
    <div class="now">
      <h2>최근 관심사</h2>
      <ul>
        <li>자동매매 전략을 검증하는 방법 개선</li>
        <li>데이터 이전 중 기존 기능을 유지하는 방법과 자동 검증</li>
      </ul>
    </div>
    <a class="allposts" href="/글/index.html">
      <b>블로그 글</b>
      <span>개발 과정과 문제 해결 기록 보기 →</span>
    </a>
  </footer>

</div>
