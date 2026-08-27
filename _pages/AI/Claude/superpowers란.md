---
title:  "Superpowers 란 — Claude Code 에 절차 규율을 심는 플러그인"

categories:
  - AI
tags:
  - AI
  - Claude Code
  - Superpowers
  - 개발환경

date: 2026-08-27
thumbnail: "/assets/img/thumbnail/claude_thumbnail.png"
card_thumbnail: "/assets/img/thumbnail/claude_card.png"
---
## 한 줄로

**AI 에게 "바로 코딩하지 말고 이 절차를 밟아라" 를 강제하는 플러그인**이다. Anthropic 공식
마켓플레이스(`claude-plugins-official`)에서 받는다.

기능을 더해주는 게 아니라 **일하는 순서를 바꾼다**. 그래서 설치해도 새 명령어가 늘지 않고,
대신 Claude 가 작업에 들어가는 방식이 달라진다.

## 무엇이 들어 있나

스킬 14개다. 지금 깔린 5.0.6 기준으로 전부 나열하면 이렇다.

| 스킬 | 언제 |
|---|---|
| `brainstorming` | 기능을 만들기 전 — 요구사항과 설계를 먼저 캐묻는다 |
| `writing-plans` | 요구사항이 정해진 뒤 계획 문서를 쓴다 |
| `executing-plans` | 그 계획을 별도 세션에서 실행한다 |
| `subagent-driven-development` | 계획을 서브에이전트에게 나눠 실행한다 |
| `dispatching-parallel-agents` | 독립적인 일 2개 이상을 동시에 던진다 |
| `test-driven-development` | 구현 전에 테스트부터 쓴다 |
| `systematic-debugging` | 버그를 만나면 고치기 전에 원인을 좁힌다 |
| `requesting-code-review` | 작업을 마치고 리뷰를 요청한다 |
| `receiving-code-review` | 받은 리뷰를 맹목적으로 따르지 않고 검증한다 |
| `verification-before-completion` | "다 됐다" 고 말하기 전에 실제로 돌려본다 |
| `using-git-worktrees` | 작업을 격리된 워크트리에서 한다 |
| `finishing-a-development-branch` | 브랜치를 어떻게 정리할지 결정한다 |
| `writing-skills` | 스킬 자체를 만들거나 고칠 때 |
| `using-superpowers` | 위 스킬들을 언제 부를지 정하는 진입점 |

## 핵심은 게이트다

이 플러그인의 성격은 `brainstorming` 스킬의 설명 한 줄에 다 들어 있다.

```
You MUST use this before any creative work — creating features,
building components, adding functionality, or modifying behavior.
```

"권장" 이 아니라 **MUST** 다. 그리고 본문에는 `<HARD-GATE>` 라는 태그로 감싼 구간이 있다.

무슨 뜻이냐면, "로그인 기능 만들어줘" 라고 하면 바로 코드를 쓰지 않고 **요구사항을 되묻는
단계로 먼저 들어간다.** 세션이 마음대로 건너뛰지 못하게 문장 강도로 막아둔 것이다.

- 얻는 것 — 잘못된 전제로 코드가 쌓이는 일이 줄어든다
- 잃는 것 — 간단한 일에도 질문이 붙는다

## 강제력의 정체

여기서 짚어둘 게 있다. 이 게이트는 **훅이 아니라 문장**이다.

- 훅 — 스크립트가 도구 호출을 실제로 막는다. 모델의 협조가 필요 없다
- 스킬의 MUST — 모델에게 강하게 말하는 것이다. 대체로 지켜지지만 보장은 아니다

같은 구분을 [훅은 언제 막고 언제 못 막나](/AI/Claude/훅은-언제-막고-언제-못-막나.html)
에서 실측으로 다뤘다. 도구 권한을 좁히는 옵션이 강제되지 않은 반면 `PreToolUse` 훅은
실제로 막혔다.

Superpowers 는 후자가 아니라 전자다. **절차를 코드로 막는 게 아니라 규율로 세운다.**
그래서 "이번엔 건너뛰자" 가 가능하고, 실제로 그렇게 쓴다.

## 내가 쓰는 방식

전역 규칙에 라우팅을 적어뒀다. 상황별로 어느 스킬을 쓸지 미리 정해둔 것이다.

| 상황 | 사용 |
|---|---|
| 새 기능 (대화형) | brainstorming → writing-plans → subagent-driven-development |
| 버그 수정 | systematic-debugging |
| 완료 검증 | verification-before-completion **1회만** |

마지막 줄에 "1회만" 이 붙은 이유가 있다. 다른 플러그인(OMC)에도 검증 단계가 있어서, 둘 다
돌리면 같은 일을 두 번 한다. 이 조합 문제는 다음 글에서 다룬다.

## 정리

- **무엇** — 절차 규율을 스킬 14개로 심는 공식 플러그인
- **성격** — 기능 추가가 아니라 순서 변경
- **강제력** — 훅이 아니라 문장. 강하게 말하지만 물리적 차단은 아니다
- **주의** — 다른 오케스트레이션 플러그인과 검증 단계가 겹칠 수 있다

같이 읽을 글:
[Claude Code 설정을 맥 4대에 나눠 담기](/AI/Claude/claude-code-셋업-계층과-플러그인.html)
