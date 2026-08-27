---
title:  "Superpowers 란 — 코드를 쓰기 전에 멈추게 만드는 플러그인"

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

**AI 에게 "바로 코딩하지 말고 이 절차를 밟아라" 를 강제하는 플러그인**이다.

기능을 더해주는 게 아니라 **일하는 순서를 바꾼다**. 그래서 설치해도 새 명령어가 늘지 않고,
대신 Claude 가 작업에 들어가는 방식이 달라진다.

만든 사람은 Jesse Vincent(obra), MIT 라이선스다. Anthropic 공식
마켓플레이스에 올라와 있어 한 줄로 깔린다.

```
/plugin install superpowers@claude-plugins-official
```

## 무엇이 들어 있나

스킬 14개다. 내 머신에 깔린 6.3.0 기준으로 전부 나열하면 이렇다.

| 스킬 | 언제 |
|---|---|
| `brainstorming` | 기능을 만들기 전 — 요구사항과 설계를 먼저 캐묻는다 |
| `writing-plans` | 요구사항이 정해진 뒤 계획 문서를 쓴다 |
| `executing-plans` | 그 계획을 순차 실행한다 |
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

이름만 봐도 성격이 보인다. **테스트·리뷰·검증이 절반**이다. 코드를 더 빨리 쓰게 하는
스킬은 하나도 없다.

## 핵심은 게이트다

`brainstorming` 스킬 안에 이런 태그가 있다. 원문 그대로다.

```
<HARD-GATE>
Do NOT invoke any implementation skill, write any code, scaffold any project,
or take any implementation action until you have presented a design and
the user has approved it. This applies to EVERY project regardless of
perceived simplicity.
</HARD-GATE>
```

"설계를 제시하고 승인받기 전에는 **어떤 구현 행위도 하지 말라**" 는 것이다. 그리고 마지막
문장이 빠져나갈 구멍을 막는다 — **"간단해 보이든 말든 모든 프로젝트에 적용된다."**

바로 다음 절 제목이 아예 이렇다.

```
## Anti-Pattern: "This Is Too Simple To Need A Design"
```

본문 요지는 이렇다. 할 일 목록 하나, 함수 하나짜리 유틸리티, 설정 변경 — 전부 이 과정을
거친다. **"간단한" 프로젝트야말로 검토되지 않은 가정이 헛일을 가장 많이 만드는 곳**이라는
것이다. 설계가 몇 문장으로 짧아도 되지만, 제시하고 승인은 받아야 한다.

TDD 스킬에도 비슷한 문장이 있다. 절 제목이 **"The Iron Law"** 다.

```
NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST
```

## 순서가 정해져 있다

스킬 14개가 흩어져 있는 게 아니라 흐름을 이룬다. 대략 이런 순서다.

```
brainstorming        설계를 캐묻고 승인받는다      ← 여기서 막힌다
      ↓
using-git-worktrees  격리된 작업 공간을 만든다
      ↓
writing-plans        구현 계획을 잘게 쪼갠다
      ↓
subagent-driven-development / executing-plans
      ↓
test-driven-development   RED → GREEN → REFACTOR
      ↓
requesting-code-review    리뷰를 받는다
      ↓
finishing-a-development-branch   병합·PR·보류·폐기 중 선택
```

계획을 쪼개는 단위도 정해져 있다. `writing-plans` 는 **한 작업이 2~5분** 안에 끝나게
쪼개라고 하고, `TBD`·`TODO` 같은 자리표시자를 금지한다.

## 강제력의 정체

여기서 짚어둘 게 있다. 이 게이트는 **훅이 아니라 문장**이다.

- 훅 — 스크립트가 도구 호출을 실제로 막는다. 모델의 협조가 필요 없다
- 스킬의 MUST — 모델에게 강하게 말하는 것이다. 대체로 지켜지지만 보장은 아니다

같은 구분을 [훅은 언제 막고 언제 못 막나](/AI/Claude/훅은-언제-막고-언제-못-막나.html)
에서 실측으로 다뤘다. 도구 권한을 좁히는 옵션이 강제되지 않은 반면 `PreToolUse` 훅은
실제로 막혔다.

Superpowers 는 후자가 아니라 전자다. **절차를 코드로 막는 게 아니라 규율로 세운다.**
문장 강도를 극단까지 올려 그 격차를 메우는 방식이고, `using-superpowers` 에는 이런
기준까지 적혀 있다.

```
If you think there is even a 1% chance a skill might apply to what you are doing,
you ABSOLUTELY MUST invoke the skill.
```

1% 라도 해당될 것 같으면 무조건 부르라는 것이다. 판단 재량을 최대한 좁힌다.

## 안 맞는 경우도 있다

솔직히 쓰자면 이 게이트가 늘 이득은 아니다.

- **빠른 프로토타입** — 버릴 코드를 짜는데 설계 승인부터 받는 건 과하다
- **한 줄 수정** — 오타 고치는 데 브레인스토밍이 붙으면 방해다

그래서 전역 규칙에 라우팅을 적어뒀다. 상황별로 어느 스킬을 쓸지 미리 정해둔 것이다.

| 상황 | 사용 |
|---|---|
| 새 기능 (대화형) | brainstorming → writing-plans → subagent-driven-development |
| 버그 수정 | systematic-debugging |
| 완료 검증 | verification-before-completion **1회만** |

마지막 줄에 "1회만" 이 붙은 이유가 있다. 다른 플러그인(OMC)에도 검증 단계가 있어서, 둘 다
돌리면 같은 일을 두 번 한다. 이 조합 문제는 다음 글에서 다룬다.

## 정리

- **무엇** — 절차 규율을 스킬 14개로 심는 공식 플러그인 (MIT, obra)
- **성격** — 기능 추가가 아니라 순서 변경. 테스트·리뷰·검증이 절반
- **강제력** — 훅이 아니라 문장. 강하게 말하지만 물리적 차단은 아니다
- **핵심** — `HARD-GATE`. 설계 승인 전에는 코드를 쓰지 않는다
- **주의** — 프로토타입·사소한 수정에는 과할 수 있고, 다른 플러그인과 검증이 겹칠 수 있다

같이 읽을 글:
[Claude Code 설정을 맥 4대에 나눠 담기](/AI/Claude/claude-code-셋업-계층과-플러그인.html)
