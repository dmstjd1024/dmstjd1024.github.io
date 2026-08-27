---
title:  "OMC 란 — 에이전트 19개를 부리는 오케스트레이션 층"

categories:
  - AI
tags:
  - AI
  - Claude Code
  - OMC
  - 개발환경

date: 2026-08-27
thumbnail: "/assets/img/thumbnail/claude_thumbnail.png"
card_thumbnail: "/assets/img/thumbnail/claude_card.png"
---
## 한 줄로

**하나의 요청을 여러 에이전트에게 나눠 실행시키는 플러그인**이다. oh-my-claudecode, 줄여서
OMC. MIT 라이선스이고 [Yeachan-Heo/oh-my-claudecode](https://github.com/Yeachan-Heo/oh-my-claudecode)
에서 받는다.

[Superpowers](/AI/Claude/superpowers란.html) 가 **절차**를 세운다면 OMC 는 **인력**을
나눈다. 층이 달라서 둘을 같이 쓴다.

지금 깔린 5.0.0 기준으로 규모는 이렇다.

| 항목 | 수 |
|---|---:|
| 스킬 | 31 |
| 에이전트 | 19 |
| MCP 도구 | 54 |
| 브리지 코드 | 31,928줄 |

## 뼈대는 4단계다

31개 스킬이 흩어져 있는 게 아니라 정식 흐름이 하나 있다.

```
plan  →  execute  →  review  →  verify
```

각 스킬 문서에 "canonical" 이라고 못박혀 있다. `execute` 문서에는 이런 문장이 있다.

```
This is the canonical execution workflow.
autopilot, ralph, ultrawork, ultragoal, ultrapilot, pipeline,
and swarm route here.
```

즉 `ralph` 든 `autopilot` 이든 결국 같은 실행 경로를 탄다. 겉으로 보이는 이름이 여럿일 뿐
안쪽은 하나다.

## 자기 승인을 못 하게 막아뒀다

이 도구에서 제일 눈여겨본 설계다. **각 단계가 자기 일을 스스로 통과시키지 못한다.**

| 단계 | 금지된 것 |
|---|---|
| `plan` | 실행 금지 — "planning modes ... produce plans/specs/proposals **only**" |
| `execute` | 자기 승인 금지 — "do not self-approve; hand off to `review` or `verify`" |
| `review` | 자기 작성물 심사 금지 — "Review never authors the change it is judging" |

`plan` 은 파일을 고치거나 커밋·푸시·PR 을 할 수 없게 명시돼 있고, 산출물에 `pending
approval` 을 붙여야 한다. `review` 는 "리뷰어가 작성자와 같은 컨텍스트여서는 안 된다" 고
못박는다.

AI 에게 일을 맡길 때 제일 위험한 게 **스스로 "다 됐다" 고 판정하는 것**인데, 그걸 구조로
막은 셈이다.

## 에이전트 19개와 모델 핀

에이전트마다 쓸 모델이 파일에 박혀 있다.

| 티어 | 수 | 예 |
|---|---:|---|
| opus | 7 | analyst, architect, critic, code-reviewer, security-reviewer, planner, code-simplifier |
| sonnet | 10 | executor, debugger, test-engineer, verifier, git-master, tracer … |
| haiku | 2 | explore, writer |

설계 의도는 명확하다 — **판단이 필요한 일에 opus, 실행에 sonnet, 단순 조회에 haiku.**
README 는 이 라우팅으로 토큰을 30~50% 아낀다고 주장한다.

### 그런데 함정이 있다

`/model` 로 세션을 sonnet 으로 낮춰도 **위임 에이전트는 자기 핀을 따른다.** OMC 지침에
그대로 적혀 있다.

```
The session model set via /model governs the main loop only;
delegated agents run on their pinned tier
```

즉 세션을 가볍게 해뒀어도 `ralph` 나 `team` 을 돌리면 **opus 핀 7개가 그대로 호출된다.**
그래서 내 전역 규칙에는 이런 경고를 넣어뒀다.

```
토큰 주의: ralph/team 은 여러 Opus 에이전트를 써 토큰 소비가 크다.
한 줄 수정·질문·단일 파일 작업에는 절대 자동 실행하지 않는다.
```

## 실행 모드 넷

이름이 비슷해서 헷갈리는데 성격이 다르다.

| 모드 | 핵심 | 상태 저장 |
|---|---|---|
| `ralph` | PRD 의 모든 항목이 통과할 때까지 **반복** | `prd.json` (세션 안) |
| `team` | N 개 에이전트가 **공유 목록**을 나눠 처리 | 공유 task list |
| `autopilot` | 아이디어 2~3줄에서 **전 생애주기** 자율 실행 | 단계별 진행상태 |
| `ultragoal` | **세션을 넘어** 지속되는 원장 | `.omc/ultragoal/` |

`ralph` 의 완료 판정이 인상적이다.

```
Completion is NEVER inferred from PR/branch/merge status alone;
git state is a warning signal only.
```

PR 이 머지됐다고 끝났다고 보지 않는다. PRD 항목이 전부 `passes: true` 이고 검증자가 확인해야
끝이다. `autopilot` 에는 무한루프 방지도 있다 — QA 를 최대 5회 돌리되, **같은 에러가 3회
반복되면 멈추고 보고**한다.

`ultragoal` 만 성격이 다르다. 루프를 돌지 않고 **세션 간 상태 보존**이 목적이다. Claude Code
자체의 `/goal` 이 세션 스코프라 상태를 잃는다는 문제를 메우려는 것이다.

## 절반이 기억 도구다

MCP 브리지가 제공하는 도구 54개를 범주로 나누면 이렇다.

| 범주 | 수 |
|---|---:|
| LSP (코드 탐색) | 12 |
| wiki | 7 |
| notepad | 6 |
| state | 5 |
| shared_memory | 5 |
| project_memory | 4 |
| 그 외 | 15 |

**wiki + notepad + state + shared_memory + project_memory = 27개.** 절반이 코드를 만지는
도구가 아니라 **세션을 넘어 맥락을 유지하는 도구**다.

여러 에이전트가 일을 나눠 하려면 서로 뭘 했는지 알아야 하고, 세션이 끊겨도 이어져야 한다.
그 요구가 도구 구성에 그대로 드러난다.

## 5.0.0 이 표면적을 깎았다

이전 버전(4.15.10)에는 스킬이 41개였다. 5.0.0 에서 **31개로 줄었다.**

CHANGELOG 의 표현이 단호하다.

```
removes 17 legacy names outright
rather than keeping them as compatibility aliases
```

호환 별칭조차 안 남기고 지웠다는 것이다. `ultrawork`, `ultraqa`, `deep-dive`, `sciomc` 등이
사라졌다.

### 줄이는 과정이 부채를 남겼다

여기서 실제로 확인한 게 있다. **지운 이름들이 문서 곳곳에 살아 있다.**

| 어디 | 무엇 |
|---|---|
| `cancel` 스킬 설명 | 없는 모드 4개(`ultrawork`·`swarm`·`ultrapilot`·`pipeline`)를 나열 |
| `ralph` 스킬 본문 | "직접 제어하려면 `ultrawork` 를 쓰라" — 없는 스킬로 안내 |
| `execute` 스킬 | retired 된 이름들이 "route here" 목록에 그대로 |
| MCP 브리지 | `merge-readiness` 스킬은 지웠는데 도구 5개는 남음 |

**그리고 내 설정도 마찬가지였다.** 전역 규칙의 모드 선택 문장이 이렇게 돼 있다.

```
완료 시점을 직접 판단하면→ultrawork, 완주·검증까지 맡기면→ralph
```

`ultrawork` 는 5.0.0 에 없다. 규칙은 2026년 7월 7일에 만든 뒤 개정하지 않았고, 그 사이
플러그인이 버전을 올리며 그 이름을 지웠다. **글을 쓰려고 조사하다 발견했다.**

## 정리

- **무엇** — 에이전트 19개에 일을 나눠 실행시키는 오케스트레이션 층 (MIT)
- **뼈대** — `plan → execute → review → verify`. 각 단계가 자기 승인을 못 한다
- **비용** — 모델 핀으로 아끼지만, **위임 에이전트는 세션 모델을 무시한다**
- **성격** — MCP 도구 54개 중 27개가 기억 계열
- **주의** — 5.0.0 이 스킬을 41→31 로 줄였고, 옛 이름을 가리키는 문서가 곳곳에 남아 있다

다음 글에서는 이 도구의 긴 과정을 어떻게 줄였는지를 다룬다.

같이 읽을 글:
[Superpowers 란](/AI/Claude/superpowers란.html)
