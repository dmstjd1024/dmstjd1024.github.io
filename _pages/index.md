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
    <div class="hero__main">
      <p class="hero__eyebrow">백엔드 · 풀스택</p>
      <h1 class="hero__name">전은성</h1>
      <p class="hero__role">6년차 백엔드 개발자 · 레거시 개선과 데이터 모델 전환</p>
      <p class="hero__line">멈추면 안 되는 시스템을 바꾸는 일을 합니다.</p>
      <p class="hero__links">
        <a href="https://github.com/dmstjd1024">GitHub</a>
        <a href="/글/index.html">기술 글</a>
      </p>
    </div>

{%- comment -%}
  오른쪽 지표판.

  왼쪽 텍스트 뭉치만 두면 화면의 3/4 이 빈다. 이 사람의 설득력은 측정값에서
  나오므로(블로그 글도 전부 문제→진단→결과 구조다) 그 성격을 첫 화면에
  그대로 세운다. 숫자를 크게, 단위를 작게, 한 줄 설명을 붙인다.
{%- endcomment -%}
    <dl class="hero__facts">
      <div>
        <dt>실무</dt>
        <dd><b>6</b><i>년차</i></dd>
        <p>Java · Spring 중심, 프론트까지</p>
      </div>
      <div>
        <dt>기술 글</dt>
{%- comment -%}
  글 수는 세어서 쓴다. 손으로 박아두면 글을 올릴 때마다 같이 고쳐야 하고,
  실제로 79 로 적힌 채 86 편이 될 때까지 아무도 눈치채지 못했다.
  측정하지 않은 숫자를 쓰지 않는다는 이 블로그의 원칙이 첫 화면에서
  먼저 깨져 있던 셈이다.

  기준을 thumbnail 로 잡은 이유:
  카테고리 인덱스(_pages/*/index.md)는 frontmatter 가 비어 있어 글이 아닌데,
  title 로는 걸러지지 않는다 — Jekyll 이 파일명에서 "Index" 를 자동으로
  채워 넣기 때문이다. categories·tags 도 안 된다. 인덱스에서 빈 배열이
  되는데 Liquid 에서 빈 배열은 참이라 where_exp 를 그냥 통과한다(113개 전부).
  thumbnail 은 글에만 있고 인덱스에는 아예 없는 유일한 필드다.
{%- endcomment -%}
        <dd><b>{{ site.pages | where_exp: "p", "p.thumbnail" | size }}</b><i>편</i></dd>
        <p>문제 · 원인 · 해결 기록</p>
      </div>
      <div>
        <dt>운영 시스템</dt>
        <dd><b>3</b><i>개</i></dd>
        <p>탄소배출 · 블록체인 · 장비 관리</p>
      </div>
    </dl>
  </header>

  <section class="stack" aria-labelledby="h-stack">
    <h2 class="sec__title" id="h-stack">기술 스택</h2>
    <p class="sec__note">문제를 겪고 판단을 내린 것만. 학습만 한 것은 뺐습니다.</p>
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
    <p class="sec__note">여기엔 결론만 적었습니다. 대부분 과정이 글에 남아 있습니다.</p>

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
        제품 단위 탄소배출량을 산정하는 서비스. 스키마 관리, 조회 성능, 누적된
        이중 구조를 차례로 정리했습니다.
      </p>
      <ul class="cases">
        <li>
          <h4>도입한 도구를 3주 만에 걷어냄</h4>
          <p>
            Flyway가 기존 DB에서는 무사한데 새 DB에서만 실패했습니다. 마이그레이션
            도구의 핵심 가치가 재현성인데 그게 깨진 상태였고, 예외를 커스텀 로직으로
            계속 흡수하는 쪽은 기각했습니다 — 설정이 221줄까지 자란 시점이 이미 신호였습니다.
          </p>
          <p class="case__out"><code>도입 22일 → 철수, 필요한 부분만 자동화로 대체</code></p>
          <p class="case__src">
            <a href="/Database/flyway를-도입하고-3주-만에-걷어낸-이야기.html">Flyway를 3주 만에 걷어낸 이야기</a>
            <a href="/Database/ddl-auto-update의-빈틈을-보완-ddl-자동화로-메우기.html">그 뒤 빈틈을 메운 방법</a>
          </p>
        </li>
        <li>
          <h4>읽기 비용을 쓰기 시점으로</h4>
          <p>
            5중 CTE 뷰가 조회마다 재계산되고 있었습니다. 물질화 테이블로 옮기되
            섀도우·전환 2단계로 무중단 롤아웃했고, 갱신 지점은 기존 캐시 무효화
            지점만 믿지 않고 전수조사해 가장 빈번한 경로가 빠진 것을 찾았습니다.
          </p>
          <p class="case__out"><code>PDF 생성 6.4s → 0.7s</code></p>
          <p class="case__src">
            <a href="/Database/뷰를-물질화-테이블로-읽기-비용을-쓰기-시점으로-옮기기.html">뷰를 물질화 테이블로</a>
            <a href="/Spring/n+1-제거-4종-세트-fetch-join이-답이-아닐-때.html">N+1 제거 4종 세트</a>
            <a href="/React/한글-폰트-pdf-성능.html">PDF 7초의 범인</a>
          </p>
        </li>
        <li>
          <h4>같은 버그를 두 번 고친 날</h4>
          <p>
            V1/V2 이중 스택이 남아 한 버그를 양쪽에서 고쳐야 했습니다. 단계를 나눠
            통합했고, 도달 불가능한 파일도 함께 걷어냈습니다 — 죽은 코드가 더 최신이라
            판단 근거를 오염시키던 상태였습니다.
          </p>
          <p class="case__out"><code>2,389줄 삭제 · 죽은 파일 102개 정리</code></p>
          <p class="case__src">
            <a href="/Develop/v1-v2-이중-스택-정리.html">같은 버그를 두 번 고친 날</a>
            <a href="/Develop/죽은-파일이-더-최신이었다.html">죽은 파일이 더 최신이었다</a>
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
          <span>백엔드 · 인프라 담당 · 프론트 협업 1명</span>
        </p>
      </header>
      <p class="proj__what">
        기관마다 격리된 Kubernetes 클러스터와 블록체인 네트워크를 REST API 한 번으로
        만들어 주는 멀티테넌시 BaaS 플랫폼입니다. 공공 SI라 감리·인수인계·폐쇄망이
        전제였고, 그 제약이 기술 선택을 대부분 규정했습니다. 인터넷이 차단된 환경이라
        전체 이미지를 로컬 레지스트리로 미리 적재하고 외부 pull 시도 자체를 막았습니다.
      </p>
      <ul class="cases">
        <li>
          <h4>기관 온보딩을 API 한 번으로</h4>
          <p>
            신규 기관 1곳에 약 157회의 CLI 조작과 설정 파일 5종 직접 작성이 필요했습니다.
            단계마다 수 분씩 대기가 걸리는데 그때마다 사람이 다음 명령을 쳐야 해서 하루가
            통째로 묶였습니다. 전 과정을 스크립트로 통합하고 WAS가 SSH로 원격 실행하게
            했습니다. 프로비저닝이 20~43분 걸리므로 <b>트랜잭션 커밋 이후 비동기로 돌려</b>
            HTTP 요청을 붙잡지 않게 했고, 상태를 DB에 남겨 실패 시점을 확인할 수 있게 했습니다.
          </p>
          <p class="case__out"><code>운영자 조작 157회 → 1회 · 개입 시간 수 시간 → 0분</code></p>
          <p class="case__note">
            전체 소요 시간이 준 것은 아닙니다. Kind·Istio·Helm의 물리적 대기 20~43분은
            자동화 전후가 같고, 줄어든 것은 사람이 붙어 있어야 하는 시간입니다.
          </p>
        </li>
        <li>
          <h4>격리를 네임스페이스가 아니라 클러스터 단위로</h4>
          <p>
            기관 간 데이터 격리가 감리 요구사항이었습니다. 네임스페이스 격리는 커널과 API
            서버를 공유해 블록체인 노드처럼 상태를 가진 워크로드에는 부족하다고 보고
            <b>기관당 독립 클러스터</b>를 택했습니다. 포트는 기관마다 10개 블록을 배정하되
            <b>재사용을 전면 금지</b>했습니다 — 삭제된 기관의 포트를 다시 쓰면 잔여 연결과
            충돌하는데, 최대값 +1로만 할당하면 그 경우가 구조적으로 생기지 않습니다.
          </p>
          <p class="case__out"><code>기관당 독립 클러스터 · 포트 재사용 0</code></p>
          <p class="case__note">
            대가는 자원입니다. 기관 1곳당 약 0.9 core · 2.4GiB · PVC 28Gi가 필요해
            수용 가능한 기관 수가 제한됩니다. 격리 수준과 집적도를 맞바꾼 선택이었습니다.
          </p>
        </li>
        <li>
          <h4>성격이 다른 두 블록체인을 같은 API로</h4>
          <p>
            Fabric(허가형·체인코드·인증서)과 Besu(EVM·스마트 컨트랙트·계정)는 배포와 운영
            방식이 완전히 다릅니다. 그대로 두면 사용자가 두 체인의 CLI를 각각 배워야 했습니다.
            원격 실행 계층을 추상 클래스로 두고 체인별 구현을 분리해 같은 REST 인터페이스로
            제공했고, Pod 기동 지연으로 산발적으로 나던 실패는 대기·재시도를 공통 헬퍼로
            뽑아 흡수했습니다.
          </p>
          <p class="case__out"><code>Fabric 네트워크 생성 20단계 자동화 · 스크립트 1,178줄</code></p>
          <p class="case__src">
            <a href="/Spring/toctou-버그-클래스-제거.html">TOCTOU 한 건 대신 버그 클래스를</a>
            <a href="/Spring/비동기-api가-무조건-200을-반환했다.html">비동기 API의 거짓 성공</a>
            <a href="/Infra/오퍼레이터-버그를-crd-스키마-패치로-우회하기.html">오퍼레이터 버그를 CRD 패치로</a>
            <a href="/Infra/kubectl-exec-타임아웃과-재시도.html">kubectl exec은 왜 멈추는가</a>
          </p>
        </li>
      </ul>
      <p class="proj__scale">
        백엔드 655파일 · 63,828줄 &nbsp;/&nbsp; 인프라 셸 49개 · 8,831줄(전량 작성)
        &nbsp;/&nbsp; REST 컨트롤러 123개 &nbsp;/&nbsp; 프론트 536파일 &nbsp;/&nbsp; 커밋 1,083
      </p>
    </article>

    <article class="proj">
      <header>
        <h3>장비 관리 시스템 <em>레거시</em></h3>
        <p class="proj__stack">PostgreSQL · MyBatis · Spring · JSP</p>
      </header>
      <p class="proj__what">
        JSP와 바닐라 JS로 짜인 화면 수십 개가 있는 시스템. 권한 모델과 조회 성능을
        개선했습니다.
      </p>
      <ul class="cases">
        <li>
          <h4>표현할 수 없는 상태 때문에 한 역정규화</h4>
          <p>
            장비의 소속 조직을 두 단계 조인으로 유도하는데 "고객과 다른 조직에 속한
            장비"를 모델이 표현할 수 없었습니다. 성능이 아니라 표현력 문제라 캐시나
            뷰는 애초에 답이 아니었습니다. 백필을 기존 조인 경로 그대로 작성해 신구
            경로가 같은 답을 내는 구간을 만들었습니다.
          </p>
          <p class="case__out"><code>전환 중에도 화면이 깨지지 않는 구간 확보</code></p>
          <p class="case__src">
            <a href="/Database/정규화된-조인을-버리고-역정규화하기.html">정규화된 조인을 버리고</a>
          </p>
        </li>
        <li>
          <h4>인덱스를 만든 날과 쓰인 날이 13일 떨어져 있었다</h4>
          <p>
            GIN trigram 인덱스가 실행 계획에 안 나타났습니다. 쿼리가 컬럼을
            <code>LOWER()</code>로 감싸 인덱스 표현식과 달라진 것이었고, 인덱스를
            다시 만드는 대신 쿼리를 인덱스에 맞췄습니다. 제조사 검색은 드롭다운으로
            바꾸니 부분일치 자체가 필요 없어졌습니다.
          </p>
          <p class="case__out"><code>130개소 ILIKE 전환 · 매 검색 풀스캔 해소</code></p>
          <p class="case__src">
            <a href="/Database/gin-trigram-인덱스가-안-먹던-이유.html">왜 안 빨라지지?</a>
            <a href="/Spring/인증-필터가-매-요청-db를-네번-때렸다.html">인증 필터가 DB를 네 번</a>
            <a href="/Java/depth-10-방어-코드가-버그를-감추고-있었다.html">방어 코드가 감춘 버그</a>
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
        직접 만들어 실계좌로 운용 중입니다. "맞게 생겼는지"와 "실제로 그런지"를
        구분하는 습관이 여기서 나왔습니다.
      </p>
      <ul class="cases">
        <li>
          <h4>체결 47건을 역산해서야 드러난 오차</h4>
          <p>
            화면 표시가 이상하다는 데서 출발해 실제 체결 내역을 역산했더니 요율이
            틀려 있었습니다. 원인이 셋이었고 성격이 각각 달랐습니다 — 상수 미갱신,
            세법 개정 누락, 참조 데이터 소스 자체의 오염. 판별 실패 시엔 과세 쪽으로
            fallback하게 했습니다. 손익을 크게 보이게 하는 쪽이 더 위험합니다.
          </p>
          <p class="case__out"><code>세금 상대오차 1.250% → 0.068%</code></p>
          <p class="case__src">
            <a href="/Etc/수수료율-4배-오차.html">4.1배짜리 수수료 오차</a>
          </p>
        </li>
        <li>
          <h4>켜는 게 맞나 — 3방향으로 검증하고 전부 기각</h4>
          <p>
            ML 기능의 설정 버그를 고친 뒤 "그럼 켜는 게 맞나"를 별도 질문으로
            분리했습니다. 교차검증에서 유의미해 보이는 값이 나왔지만 믿지 않고
            walk-forward로 재측정한 결과 0과 구분되지 않았습니다. 검증 방식 자체의
            낙관 편향이었습니다.
          </p>
          <p class="case__out"><code>A/B · 분류 · 회귀 3방향 검증 → 전부 기각</code></p>
          <p class="case__src">
            <a href="/Etc/ML을-껐다-켜봤더니.html">ML을 켜는 게 맞나</a>
            <a href="/Etc/필터-기여도-계측으로-찾은-무거래-원인.html">체결이 0건인 이유</a>
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
    <p class="sec__note">위 프로젝트는 글로 근거를 댈 수 있는 것만 골랐습니다. 전체 이력은 아래와 같습니다.</p>
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
          <b>SI·솔루션 기업</b> 개발
          <em>관리자 페이지 기능 개발 · 유지보수 · 솔루션 리뉴얼(MSA) · 국방부 시스템 개발 및 유지보수</em>
        </span>
      </li>
    </ol>
  </section>

  <section class="how" aria-labelledby="h-how">
    <h2 class="sec__title" id="h-how">일하는 방식</h2>
    <p class="sec__note">
      AI 페어링을 실무에 씁니다. 도구 자랑이 아니라 검증 장치를 어디에 두느냐의
      문제로 다룹니다.
    </p>
    <ul class="how__list">
      <li>
        스펙을 쓰게 하고 <b>컨텍스트를 끊은 뒤</b> 자기검토를 시킵니다. 같은
        세션에서 물으면 대체로 "문제 없다"는 답이 옵니다.
      </li>
      <li>
        병렬 에이전트로 메모리 누수 51건을 찾았지만 그대로 믿지 않고 검증 게이트를
        거쳐 49건만 적용했습니다. 1건은 데이터 유실 위험이라 보류했습니다.
      </li>
      <li>
        실패한 것도 남겼습니다 — AI가 쓴 커밋 메시지가 실제 diff와 달랐던 일이 있습니다.
      </li>
    </ul>
    <p class="case__src">
      <a href="/AI/Claude/ai에게-스펙을-쓰게-하고-자기검토를-시키고-구현하기.html">스펙을 쓰게 하고 자기검토를</a>
      <a href="/AI/Claude/에이전트-72개-메모리-누수-감사.html">에이전트 72개로 누수 감사</a>
      <a href="/AI/Claude/ai가-쓴-커밋-메시지가-거짓말을-했다.html">커밋 메시지가 거짓말을 했다</a>
    </p>
  </section>

  <footer class="home__foot">
    <div class="now">
      <h2>요즘</h2>
      <ul>
        <li>자동매매 시스템의 전략 검증 방법을 다듬는 중</li>
        <li>관심사 — 마이그레이션 안전성, 검증 장치를 코드에 심는 방법</li>
      </ul>
    </div>
    <a class="allposts" href="/글/index.html">
      <b>기술 글</b>
      <span>문제 · 원인 · 해결 기록 →</span>
    </a>
  </footer>

</div>
