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
    <p class="hero__eyebrow">백엔드 · 풀스택</p>
    <h1 class="hero__name">전은성</h1>
    <p class="hero__line">
      이미 돌아가는 시스템을 고칩니다.
      <span>레거시 개선 · 성능 · 데이터 모델 전환</span>
    </p>
    <ul class="hero__facts">
      <li><b>6년차</b><span>실무</span></li>
      <li><b>79편</b><span>기술 글</span></li>
      <li><b>3개</b><span>운영 시스템</span></li>
    </ul>
  </header>

  <section class="stack" aria-labelledby="h-stack">
    <h2 class="sec__title" id="h-stack">기술 스택</h2>
    <p class="sec__note">문제를 겪고 판단을 내린 것만. 학습만 한 것은 뺐습니다.</p>
{%- comment -%}
  기술 스택 배지. shields.io 에서 받아 assets/img/badge/ 에 넣어둔 SVG 다.
  외부에서 매번 불러오면 요청 18개가 남의 서버로 나가고, 그쪽이 느리거나
  죽으면 이 화면이 같이 깨진다. 같은 도메인에서 서빙하는 편이 빠르고 안전하다.

  로고가 있는 것은 공식 브랜드 색을, 없는 것(QueryDSL·MyBatis)은 회색을 쓴다 —
  없는 로고를 억지로 끼우면 엉뚱한 아이콘이 붙는다.

  배지를 바꾸려면 shields.io 에서 새로 받아 같은 파일명으로 덮어쓴다.
{%- endcomment -%}
    <dl class="stack__grid">
      <div>
        <dt>백엔드</dt>
        <dd>
          <img src="/assets/img/badge/spring.svg" alt="Spring" height="28">
          <img src="/assets/img/badge/spring-security.svg" alt="Spring Security" height="28">
          <img src="/assets/img/badge/jpa-hibernate.svg" alt="JPA / Hibernate" height="28">
          <img src="/assets/img/badge/querydsl.svg" alt="QueryDSL" height="28">
          <img src="/assets/img/badge/mybatis.svg" alt="MyBatis" height="28">
          <img src="/assets/img/badge/java.svg" alt="Java" height="28">
        </dd>
      </div>
      <div>
        <dt>데이터베이스</dt>
        <dd>
          <img src="/assets/img/badge/postgresql.svg" alt="PostgreSQL" height="28">
          <img src="/assets/img/badge/mysql.svg" alt="MySQL" height="28">
          <img src="/assets/img/badge/redis.svg" alt="Redis" height="28">
        </dd>
      </div>
      <div>
        <dt>프론트엔드</dt>
        <dd>
          <img src="/assets/img/badge/react.svg" alt="React" height="28">
          <img src="/assets/img/badge/nextjs.svg" alt="Next.js" height="28">
          <img src="/assets/img/badge/typescript.svg" alt="TypeScript" height="28">
          <img src="/assets/img/badge/tanstack-query.svg" alt="TanStack Query" height="28">
          <img src="/assets/img/badge/rtk-query.svg" alt="RTK Query" height="28">
        </dd>
      </div>
      <div>
        <dt>인프라</dt>
        <dd>
          <img src="/assets/img/badge/kubernetes.svg" alt="Kubernetes" height="28">
          <img src="/assets/img/badge/docker.svg" alt="Docker" height="28">
          <img src="/assets/img/badge/github-actions.svg" alt="GitHub Actions" height="28">
          <img src="/assets/img/badge/linux.svg" alt="Linux" height="28">
        </dd>
      </div>
    </dl>
  </section>

  <section class="work" aria-labelledby="h-work">
    <h2 class="sec__title" id="h-work">프로젝트</h2>
    <p class="sec__note">각 항목의 과정은 글에 남아 있습니다. 여기엔 결론만 적었습니다.</p>

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
            <a href="/AI/DB-Query/flyway를-도입하고-3주-만에-걷어낸-이야기.html">Flyway를 3주 만에 걷어낸 이야기</a>
            <a href="/AI/DB-Query/ddl-auto-update의-빈틈을-보완-ddl-자동화로-메우기.html">그 뒤 빈틈을 메운 방법</a>
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
            <a href="/AI/DB-Query/뷰를-물질화-테이블로-읽기-비용을-쓰기-시점으로-옮기기.html">뷰를 물질화 테이블로</a>
            <a href="/AI/Backend/n+1-제거-4종-세트-fetch-join이-답이-아닐-때.html">N+1 제거 4종 세트</a>
            <a href="/AI/Frontend/한글-폰트-pdf-성능.html">PDF 7초의 범인</a>
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
            <a href="/AI/Frontend/v1-v2-이중-스택-정리.html">같은 버그를 두 번 고친 날</a>
            <a href="/AI/Frontend/죽은-파일이-더-최신이었다.html">죽은 파일이 더 최신이었다</a>
          </p>
        </li>
      </ul>
    </article>

    <article class="proj">
      <header>
        <h3>블록체인 관리 플랫폼</h3>
        <p class="proj__stack">Hyperledger Fabric/Besu · Kubernetes · Next.js · 폐쇄망</p>
      </header>
      <p class="proj__what">
        웹에서 버튼을 눌러 블록체인 네트워크를 Kubernetes에 배포하는 플랫폼.
        관리자·사용자 포털 두 벌이 같은 백엔드를 씁니다.
      </p>
      <ul class="cases">
        <li>
          <h4>한 건이 아니라 버그 클래스를 제거</h4>
          <p>
            SFTP 디렉터리 생성에서 TOCTOU(확인과 사용 사이에 상태가 바뀌는 문제)가
            났습니다. 예외로 감싸는 대신 명령 자체에 위임해 틈을 없앴고, 이어서
            같은 형태가 상위 계층에도 있는 것을 찾았습니다. 낙관적 재시도와 비관적
            락은 기준을 정리한 뒤 이 경우엔 맞지 않다고 판단했습니다.
          </p>
          <p class="case__out"><code>35줄 → 20줄, 같은 클래스 상위 계층까지</code></p>
          <p class="case__src">
            <a href="/AI/Backend/toctou-버그-클래스-제거.html">TOCTOU 한 건 대신 버그 클래스를</a>
            <a href="/AI/Backend/비동기-api가-무조건-200을-반환했다.html">비동기 API의 거짓 성공</a>
          </p>
        </li>
        <li>
          <h4>오퍼레이터 버그를 CRD 스키마 패치로</h4>
          <p>
            포크 · 다운그레이드 · 스키마 패치를 비교했습니다. 폐쇄망이라 커스텀 이미지
            파이프라인 부담이 크고 업스트림 리베이스가 영구 비용이 된다는 점에서
            스키마 패치를 택했고, 우회 조치에는 버전과 증상을 주석으로 남겼습니다.
          </p>
          <p class="case__out"><code>업스트림 수정 대기 없이 배포 재개</code></p>
          <p class="case__src">
            <a href="/AI/Infra/오퍼레이터-버그를-crd-스키마-패치로-우회하기.html">CRD 스키마 패치로 우회하기</a>
            <a href="/AI/Infra/kubectl-exec-타임아웃과-재시도.html">kubectl exec은 왜 멈추는가</a>
          </p>
        </li>
        <li>
          <h4>장애가 사용자에게 닿는 방식</h4>
          <p>
            게이트웨이가 죽었을 때 F5 연타가 폭주로 이어졌습니다. sessionStorage
            기반 서킷 브레이커로 끊었고, HTTP 환경이라 clipboard API가 동작하지 않는
            문제도 폴백으로 처리했습니다.
          </p>
          <p class="case__out"><code>장애 시 요청 폭주 차단 · 폐쇄망 복사 기능 복구</code></p>
          <p class="case__src">
            <a href="/AI/Frontend/브라우저-서킷-브레이커.html">사용자가 F5를 누른다</a>
            <a href="/AI/Frontend/로그아웃은-토큰만-지우는게-아니다.html">로그아웃은 토큰만 지우는 게 아니다</a>
          </p>
        </li>
      </ul>
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
            <a href="/AI/DB-Query/정규화된-조인을-버리고-역정규화하기.html">정규화된 조인을 버리고</a>
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
            <a href="/AI/DB-Query/gin-trigram-인덱스가-안-먹던-이유.html">왜 안 빨라지지?</a>
            <a href="/AI/Backend/인증-필터가-매-요청-db를-네번-때렸다.html">인증 필터가 DB를 네 번</a>
            <a href="/AI/Backend/depth-10-방어-코드가-버그를-감추고-있었다.html">방어 코드가 감춘 버그</a>
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
            fallback하게 했습니다. 손익을 크게 보이는 쪽이 더 위험합니다.
          </p>
          <p class="case__out"><code>세금 상대오차 1.250% → 0.068%</code></p>
          <p class="case__src">
            <a href="/AI/AI-Pairing/수수료율-4배-오차.html">4.1배짜리 수수료 오차</a>
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
            <a href="/AI/AI-Pairing/ML을-껐다-켜봤더니.html">ML을 켜는 게 맞나</a>
            <a href="/AI/AI-Pairing/필터-기여도-계측으로-찾은-무거래-원인.html">체결이 0건인 이유</a>
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
          <b>그리너리</b> 백엔드 개발
          <em>탄소배출 산정 웹앱 · 블록체인 관리 플랫폼 · 장비 관리 시스템</em>
        </span>
      </li>
      <li>
        <span class="career__when">2020 — 2023</span>
        <span class="career__what">
          <b>퓨쳐누리</b> 개발
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
        실패도 적었습니다 — AI가 쓴 커밋 메시지가 실제 diff와 달랐던 일이 있습니다.
      </li>
    </ul>
    <p class="case__src">
      <a href="/AI/AI-Pairing/ai에게-스펙을-쓰게-하고-자기검토를-시키고-구현하기.html">스펙을 쓰게 하고 자기검토를</a>
      <a href="/AI/AI-Pairing/에이전트-72개-메모리-누수-감사.html">에이전트 72개로 누수 감사</a>
      <a href="/AI/AI-Pairing/ai가-쓴-커밋-메시지가-거짓말을-했다.html">커밋 메시지가 거짓말을 했다</a>
    </p>
  </section>

  <footer class="home__foot">
    <div class="now">
      <h2>요즘</h2>
      <ul>
        <li>자동매매 시스템의 전략 검증 방법을 다듬는 중</li>
        <li>관심사 — 마이그레이션 안전성, 검증 장치를 코드에 심는 방법</li>
      </ul>
      <p class="now__date">2026년 8월</p>
    </div>
    <a class="allposts" href="/글/index.html">
      <b>기술 글 79편</b>
      <span>문제 · 원인 · 해결 기록 →</span>
    </a>
  </footer>

</div>
