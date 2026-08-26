---
title: "JIRA 활용 - AI 붙여서 쓰기 (Rovo와 MCP)"

categories:
 - Jira
tags:
  - Jira
  - atlassian
  - rovo
  - AI
  - MCP

date: 2026-08-20
thumbnail: "/assets/img/thumbnail/jira_thumbnail.png"
---
> [JIRA 입문](/Jira/jira-basic.html), [JQL 심화와 자동화](/Jira/jira-automation.html), [스프린트 운영과 차트](/Jira/jira-team.html)에서 이어지는 글이다.
>
> ⚠️ **이 분야는 변화가 빠르다.** 이 글은 2026년 8월 기준으로 확인한 내용이며,
> 요금제·크레딧·기능명은 자주 바뀌므로 실제 적용 전에 [공식 문서](https://support.atlassian.com/rovo/)를 확인하는 것이 좋다.

먼저 이름 정리부터
=====
-----
JIRA의 AI 기능을 검색하면 두 이름이 섞여 나온다.

- **Atlassian Intelligence (AI)** — 이전 이름
- **Rovo(로보)** — 현재 이름

Atlassian이 AI 기능을 **Rovo 브랜드로 통합**하는 중이라, 공식 문서조차 두 표기가 혼재한다. 지금 시점에서는 **Rovo가 현재 이름**이라고 알아두면 된다. 이 글도 Rovo로 통일한다.

Rovo는 세 덩어리로 구성된다.

| 구성 | 하는 일 |
|---|---|
| **Rovo Search** | 자연어로 Atlassian 제품 + 외부 도구(Google Drive, Slack, Figma 등)를 통합 검색 |
| **Rovo Chat** | JIRA 안에서 대화하며 질문하고, 이슈 생성·수정·상태 보고서 작성까지 |
| **Rovo Agents** | 특정 업무를 맡기는 에이전트. 이슈 정리·생성·편집을 위임 |

돈 이야기부터 (크레딧)
=====
-----
기능 소개보다 이게 먼저다. **무엇이 무료이고 무엇이 크레딧을 쓰는지** 모르면 계획 없이 쓰다가 월 중순에 막힌다.

## 요금제별 크레딧

| 요금제 | 월 크레딧 (사용자당) |
|---|---|
| Free | **없음** |
| Standard | 25 |
| Premium | 70 |
| Enterprise | 150 |

- **조직 단위로 합산(pooling)** 된다. 10명이 Standard면 조직 전체가 월 250크레딧
- **매월 초기화되고 이월되지 않는다**
- 조직 관리자가 **업무용 도메인을 인증**해야 Rovo를 켤 수 있다 (gmail 같은 개인 도메인 불가)

## 무엇이 크레딧을 쓰나

| 기능 | 크레딧 |
|---|---|
| Rovo Search | **무료** |
| 요약(summaries) | **무료** |
| 용어 정의(definitions) | **무료** |
| 차트 인사이트 | **무료** |
| Rovo Chat 단답 / Rovo Agent 실행 | 10 |
| Deep Research | **100** |

<div class="diagram" role="img" aria-label="Rovo 크레딧이 무료 기능과 소모 기능으로 나뉘고 요금제별 월 할당량이 다른 구조">
{% include diagrams/jira--rovo-credits.svg %}
</div>

이 표가 이 글에서 가장 실용적인 부분이다. 계산해보면 답이 나온다.

- Standard 사용자 1인의 월 크레딧은 **25** → **Deep Research(100)는 한 번도 못 돌린다**
- Chat 한 번이 10크레딧 → 개인 할당량으로는 **월 2~3회**

**결론: 검색과 요약 위주로 쓰고, Chat·Agent는 정말 필요할 때만 쓴다.** 조직 단위 합산이라 실제로는 좀 더 여유가 있지만, 팀에서 몇 명이 Deep Research를 돌리면 전체 할당량이 순식간에 사라진다.

자연어로 이슈 검색하기
=====
-----
JQL을 외우지 않고 한국어(또는 영어)로 질문해 이슈를 찾는 기능이다. **크레딧을 쓰지 않으므로** 가장 부담 없이 시작할 수 있다.

## 쓰는 법

1. 이슈 **목록(List) 뷰**로 들어간다
2. 검색창 옆의 **Ask AI** 를 클릭한다
3. 질문을 입력하고 엔터
4. 닫으려면 **x** 를 눌러 기본 검색으로 돌아간다

**Ask AI 버튼이 안 보이면** 관리자가 AI 기능을 켜지 않은 것이다.

## JQL 공부용으로 쓰기

이 기능의 진짜 가치는 검색 자체가 아니다. **질문과 함께 생성된 JQL을 같이 보여준다는 점**이다.

```
질문: 지난주에 만들어진 미완료 버그
생성된 JQL: issuetype = Bug AND created >= -1w AND status != Done
```

[2편](/Jira/jira-automation.html)에서 JQL 문법을 다뤘는데, 자연어로 물어보고 나온 JQL을 읽는 방식으로 익히면 훨씬 빠르다. **결과를 필터로 저장하면 다음부터는 크레딧도 AI도 필요 없다.**

## 한국어 사용자가 알아야 할 한계

Atlassian이 공식 문서에서 직접 밝힌 제약이 있다.

> "Rovo가 생성한 정보의 품질, 정확성, 신뢰성은 다를 수 있습니다."

그리고 **영어 질의에 최적화**되어 있으며, 아래 경우엔 문서상 성능이 떨어진다고 명시한다.

- **영어가 아닌 질의** ← 한국어가 여기 해당한다
- 이슈가 아닌 대상 검색 (스페이스, 사용자, 보드)
- 차트용 데이터 분석

즉 **한국어로 물으면 정확도가 떨어질 수 있다.** 실무에서는 이렇게 쓰는 편이 낫다.

- 필드 값(프로젝트 키, 상태명)은 **실제 값 그대로** 넣는다
- 잘 안 나오면 영어로 바꿔 물어본다
- 나온 JQL을 **반드시 눈으로 검증**한다. 틀린 JQL도 문법은 멀쩡해 보인다

Rovo Chat과 Agent
=====
-----
크레딧을 쓰는 영역이다(각 10크레딧). 확인된 기능은 아래와 같다.

## Rovo Chat으로 할 수 있는 것

- 이슈나 프로젝트에 대해 맥락을 가지고 질문
- **이슈 생성·수정**
- 상태 보고서(status update) 초안 작성

긴 댓글 스레드 요약은 **요약 기능이라 무료**다. 20개 넘게 달린 댓글에서 결론만 뽑을 때 유용하다.

## 그 외 확인된 기능

| 기능 | 설명 |
|---|---|
| Work Create | Confluence·Slack·이메일·IDE·이미지에서 작업 항목 생성 |
| Work Breakdown | 큰 작업을 하위 작업으로 자동 분할 (요약·설명 포함) |
| Instant Context | 상태·기여자·블로커를 한눈에 정리 |
| Work Readiness Checker | 이슈가 착수 가능한 상태인지 점검 |
| Rovo Dev | JIRA 이슈에서 코드로 연결 |

**Work Breakdown**은 [3편](/Jira/jira-team.html)에서 다룬 "13포인트 넘으면 쪼개라"와 맞물린다. 다만 AI가 쪼갠 결과를 그대로 쓰지 말고 반드시 검토해야 한다. 도메인 맥락을 모르는 상태에서 쪼갠 것이기 때문이다.

## 자동화 규칙을 자연어로 만들기

[2편](/Jira/jira-automation.html)에서 트리거-조건-액션을 직접 설정했는데, 이걸 자연어로 만드는 기능도 있다.

단, **Premium·Enterprise 전용**이다. Standard에서는 쓸 수 없다.

MCP로 Claude에 붙이기
=====
-----
여기가 개발자에게 가장 쓸모 있는 부분이다.

**MCP(Model Context Protocol)** 는 AI 도구가 외부 시스템에 접근하는 표준 규격이다. Atlassian이 **공식 MCP 서버**를 제공하므로, Claude Code 같은 도구에서 JIRA 이슈를 직접 읽고 쓸 수 있다.

<div class="diagram" role="img" aria-label="개발 도구가 MCP 서버를 거쳐 지라 이슈를 읽고 쓰는 연결 구조">
{% include diagrams/jira--mcp-flow.svg %}
</div>

## 상태와 접근 권한

- **정식 출시(GA)** 상태다. 2025년 5월 베타로 시작해 2025년 12월 GA 전환
- 현재 명칭은 **Atlassian Rovo MCP Server**
- **모든 Atlassian Cloud 고객이 사용 가능하다. 무료 플랜 포함**

시간당 호출 한도

| 요금제 | 시간당 호출 |
|---|---|
| Free | 500 |
| Standard | 1,000 |
| Premium / Enterprise | 1,000 (최대 10,000까지 확장 가능) |

크레딧이 없는 Free 플랜에서도 MCP는 쓸 수 있다는 점이 중요하다.

> **참고**: 일반적인 읽기·쓰기 호출은 Rovo 크레딧을 쓰지 않는 것으로 알려져 있으나,
> Atlassian 공식 문서에서 이를 명시한 문장은 확인하지 못했다. 크레딧 잔량을 보면서 쓰는 편이 안전하다.

## Claude Code에 연결하기

```bash
claude mcp add --transport http atlassian https://mcp.atlassian.com/v1/mcp/authv2
```

등록 후 세션 안에서 `/mcp` 를 실행해 인증한다. 브라우저가 열리고 OAuth 로그인을 하면 연결된다.

다른 도구에서는

| 도구 | 방법 |
|---|---|
| Claude Desktop | 설정 → Extensions → Browse extensions → Plugins → "Atlassian" 검색 |
| VS Code | Extensions에서 `@mcp Atlassian` |
| Cursor | 마켓플레이스에서 설치 |

엔드포인트 URL

- 현재: `https://mcp.atlassian.com/v1/mcp/authv2`
- 구형(SSE): `https://mcp.atlassian.com/v1/sse` — 아직 동작하지만 이전을 권장

## 인증 방식

| 제품 | OAuth | API 토큰 |
|---|---|---|
| Jira | O | O |
| Confluence | O | O |
| Jira Service Management | X | O |
| Bitbucket | X | O |
| Compass | O | X |

- **OAuth 2.1**: 브라우저 로그인. **기존 사용자 권한을 그대로 따른다**
- **API 토큰**: 서버·스크립트 등 브라우저를 못 쓰는 환경용
- 사이트별로 관리자가 최초 사용을 승인해야 한다

## 보안상 주의점

Atlassian이 직접 경고하는 내용이다.

> "MCP 클라이언트는 당신의 기존 권한으로 작업을 수행할 수 있습니다.
> 최소 권한 원칙을 적용하고, 영향이 큰 변경은 검토하고, 감사 로그를 모니터링하십시오."

정리하면

- AI가 **당신 권한으로** 이슈를 만들고 고칠 수 있다. 계정 권한이 넓으면 AI 권한도 넓다
- 감사 로그에 `Rovo MCP User Actions`로 기록된다
- IP 허용 목록(allowlist)이 적용된다
- **FedRAMP·HIPAA는 지원하지 않는다.** 규제 산업이면 도입 전 확인 필요
- JIRA·Confluence 내용을 저장하거나 캐시하지 않는다

## 실제로 뭘 할 수 있나

MCP를 붙이면 이런 흐름이 한 대화 안에서 끝난다.

```
"SHOP-101 이슈 내용 읽고, 관련 코드 찾아서 구현해줘"

→ AI가 이슈를 읽고 (MCP)
→ 저장소에서 관련 코드를 찾고
→ 구현하고
→ 이슈에 진행 상황 댓글을 남긴다 (MCP)
```

```
"이번 스프린트 완료된 이슈로 릴리스 노트 만들어줘"

→ fixVersion = "v2.1.0" AND status = Done 으로 조회 (MCP)
→ 이슈 제목·설명을 읽고
→ 사용자 관점 릴리스 노트로 정리
```

두 번째 예시는 [2편에서 만든 JQL](/Jira/jira-automation.html)을 AI가 대신 실행하는 셈이다.

> **확인 못 한 것**: 제공되는 개별 도구(tool)의 전체 목록은 공식 문서에서 열거 형태로 찾지 못했다.
> 조회·생성·수정·검색이 가능하다는 것은 확인했다. 정확한 목록은 연결 후 `/mcp`로 직접 확인하는 편이 확실하다.

REST API로 직접 붙이기
=====
-----
MCP를 안 쓰고 스크립트에서 직접 호출하는 방법이다. AI에게 데이터를 넘기는 파이프라인을 만들 때 쓴다.

## 인증

1. [id.atlassian.com/manage/api-tokens](https://id.atlassian.com/manage/api-tokens) 에서 API 토큰 발급
2. `이메일:토큰` 형태의 Basic 인증

```bash
curl -u your-email@example.com:YOUR_API_TOKEN ...
```

Atlassian은 Basic 인증이 "다른 방식만큼 안전하지 않다"고 명시하며, 운영 환경에는 OAuth 2.0이나 Forge를 권장한다.

## 이슈 검색 — 엔드포인트가 바뀌었다

**중요**: 예전에 쓰던 `/rest/api/3/search`는 **제거되어 `410 Gone`을 반환한다.** 검색해서 나오는 옛날 예제 코드는 대부분 동작하지 않는다.

현재 엔드포인트는 `/rest/api/3/search/jql` 이다.

```bash
curl --request GET \
  --url 'https://<사이트>.atlassian.net/rest/api/3/search/jql?jql=project%3DSHOP%20AND%20created%3E%3D-7d&maxResults=50' \
  --user 'your-email@example.com:YOUR_API_TOKEN' \
  --header 'Accept: application/json'
```

- JQL은 **URL 인코딩** 해야 한다 (`=` → `%3D`, 공백 → `%20`)
- JQL이 길면 POST를 쓴다
- **페이지네이션이 `startAt`이 아니라 `nextPageToken` 방식**으로 바뀌었다
- 전체 개수(`totalIssues`)를 안 돌려준다. 필요하면 `POST /rest/api/3/search/approximate-count` 를 따로 호출한다

## 이슈 생성 — ADF 함정

`POST /rest/api/3/issue` 로 만든다. 여기서 많이 막히는 부분이 있다.

**v3 API에서 설명(description) 같은 서식 필드는 일반 문자열이 아니라 ADF(Atlassian Document Format)** 라는 중첩 JSON 구조여야 한다.

```json
{
  "fields": {
    "project": { "key": "SHOP" },
    "summary": "카드 결제 연동",
    "issuetype": { "name": "Task" },
    "description": {
      "type": "doc",
      "version": 1,
      "content": [
        {
          "type": "paragraph",
          "content": [
            { "type": "text", "text": "본문 내용" }
          ]
        }
      ]
    }
  }
}
```

간단한 스크립트라면 **v2 API(`/rest/api/2/issue`)를 쓰면 설명을 평범한 문자열로 넣을 수 있다.** 실무에서는 이쪽이 훨씬 편하다.

```json
{
  "fields": {
    "project": { "key": "SHOP" },
    "summary": "카드 결제 연동",
    "issuetype": { "name": "Task" },
    "description": "본문 내용을 그냥 문자열로"
  }
}
```

현실적인 활용 시나리오
=====
-----
마케팅 문구가 아니라, 실제로 시간이 절약되는 것들만 추린다.

## 무료로 할 수 있는 것 (크레딧 0)

| 상황 | 방법 |
|---|---|
| 댓글 30개짜리 이슈의 결론만 알고 싶다 | 요약 기능 |
| JQL 문법이 기억 안 난다 | Ask AI로 물어보고 생성된 JQL 확인 |
| 이 프로젝트에서 쓰는 용어가 뭔지 모르겠다 | 용어 정의(Definitions) |
| 여러 도구에 흩어진 문서를 찾아야 한다 | Rovo Search |

## MCP로 하면 좋은 것

| 상황 | 흐름 |
|---|---|
| 이슈 읽고 바로 구현 | AI가 이슈를 읽고 저장소에서 작업 |
| 릴리스 노트 작성 | 완료 이슈 조회 → 사용자 관점으로 정리 |
| 버그 분류(트리아지) | 새 버그를 읽고 우선순위·담당자 제안 |
| 회의록 → 이슈 | 회의록에서 할 일을 뽑아 이슈로 생성 |

## AI에게 맡기면 안 되는 것

- **스토리 포인트 추정** — [3편](/Jira/jira-team.html)에서 봤듯 추정의 목적은 숫자가 아니라 **팀의 이해 차이를 발견하는 것**이다. AI가 대신 하면 그 대화가 사라진다
- **우선순위 결정** — 비즈니스 맥락은 AI가 모른다
- **완료 판정** — Definition of Done 충족 여부는 사람이 본다
- **검토 없는 이슈 생성** — AI가 만든 이슈를 그대로 두면 백로그만 늘어난다

정리
=====
-----

| 하고 싶은 것 | 방법 | 비용 |
|---|---|---|
| 자연어로 이슈 검색 | Ask AI | 무료 |
| 긴 스레드 요약 | 요약 기능 | 무료 |
| 통합 검색 | Rovo Search | 무료 |
| 대화하며 이슈 조작 | Rovo Chat | 10크레딧 |
| 개발 도구에서 JIRA 조작 | MCP 서버 | 무료 플랜 포함 |
| 스크립트로 자동화 | REST API | 무료 |

시작 순서를 추천하면 이렇다.

1. **Ask AI로 JQL 배우기** — 무료이고, 2편의 JQL 학습에도 도움이 된다
2. **요약 기능 습관화** — 긴 이슈를 읽기 전에 한 번 요약
3. **MCP 연결** — 개발자라면 여기가 실질적인 이득이 가장 크다
4. **Chat·Agent는 나중에** — 크레딧 소모를 파악한 뒤에

마지막으로, AI 기능은 **JIRA에 적힌 내용이 정확할 때만 쓸모가 있다.** 3편에서 말한 "보드가 현실과 일치한다"는 원칙이 지켜지지 않으면, AI가 요약해주는 것도 결국 틀린 내용이다. 도구를 먼저 붙이기보다 운영을 먼저 정리하는 편이 순서상 맞다.

## 참고 문서

- [Rovo 소개](https://support.atlassian.com/rovo/docs/what-is-rovo/)
- [Rovo 사용량 한도](https://support.atlassian.com/rovo/docs/rovo-usage-limits/)
- [Rovo MCP Server 시작하기](https://developer.atlassian.com/cloud/rovo-mcp/guides/getting-started/)
- [Jira Cloud REST API v3](https://developer.atlassian.com/cloud/jira/platform/rest/v3/)
- [REST API Basic 인증](https://developer.atlassian.com/cloud/jira/platform/basic-auth-for-rest-apis/)
