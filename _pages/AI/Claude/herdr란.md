---
title:  "Herdr 란 — 에이전트가 자기 옆자리를 알아보는 터미널"

categories:
  - AI
tags:
  - AI
  - Claude Code
  - Herdr
  - 개발환경

date: 2026-09-10
thumbnail: "/assets/img/thumbnail/herdr_thumbnail.png"
card_thumbnail: "/assets/img/thumbnail/herdr_card.png"
---
## 한 줄로

**터미널 판(pane) 안에 무엇이 돌고 있는지를 아는** 멀티플렉서다.

tmux 는 판을 나눠주고 끝난다. 그 안에서 도는 게 셸인지 에이전트인지,
답을 기다리는 중인지 일하는 중인지는 모른다. Herdr 는 그걸 안다.

그래서 **에이전트가 다른 에이전트를 부릴 수 있다.** 이 글을 쓰는 지금 이 Claude 도
Herdr 판 안에서 돌고 있다.

## 왜 필요한가 — tmux 로는 안 되는 것

에이전트를 여러 개 띄워 놓고 일해 본 사람이면 아는 상황이 있다.

창이 8개 열려 있는데 **어느 게 내 답을 기다리고 있는지 모른다.** 하나씩 들어가서
확인해야 한다. 돌아와 보면 3개는 벌써 끝나 있고 1개는 30분째 승인 대화상자 앞에서
멈춰 있다.

tmux 가 이걸 못 도와주는 건 버그가 아니다. **tmux 는 프로세스가 살아 있는지까지만
안다.** 살아 있는 셸과, 승인을 기다리며 멈춘 에이전트는 tmux 입장에서 똑같다.

| | tmux | Herdr |
|---|---|---|
| 아는 것 | 창·판의 **위치** | 위치 + **그 안의 에이전트** |
| 상태 | 프로세스가 살아 있는가 | `idle` · `working` · `blocked` · `done` |
| 붙는 법 | 사람이 붙는다 | 사람도 붙고 **에이전트도 붙는다** |

## 구조 — 서버 하나, 그 아래 계층

<div class="diagram">
{% include diagrams/herdr--hierarchy.svg %}
</div>

위 세 칸(워크스페이스·탭·판)은 tmux 도 하는 일이다. **아래 강조된 칸이 Herdr 의 존재
이유다.**

판은 에이전트 없이도 존재한다. 그냥 셸이 도는 터미널일 수 있다. 하지만
`idle`/`working`/`blocked` 같은 상태는 **에이전트에만 붙는다.** 그래서 Herdr 의
명령어도 두 갈래다 — 평범한 프로세스는 `pane` 명령으로, 에이전트는 `agent` 명령으로
다룬다.

ID 는 `w9`(워크스페이스), `w9:t1`(탭), `w9:p2`(판) 처럼 계층이 그대로 보인다.
지금 이 판의 ID 를 환경변수로 확인할 수 있다.

```bash
$ printf '%s\n' "$HERDR_WORKSPACE_ID" "$HERDR_TAB_ID" "$HERDR_PANE_ID"
w9
w9:t1
w9:p2
```

`HERDR_ENV=1` 도 같이 들어온다. 스킬이 제어 명령을 내리기 전에 이 값을 먼저 확인하게
되어 있다 — **Herdr 밖에서 남의 세션을 조종하지 않기 위해서**다.

## 실제로 무엇이 보이는가

말로 하면 추상적이니 지금 내 머신에서 그대로 찍어 본다.

```bash
$ herdr workspace list
```

```
1  홈                 pane 2  idle
2  dotfiles 환경설정    pane 1  idle
3  기존 엔비온          pane 2  idle
4  블로그              pane 1  working   ← 지금 이 글
5  POPLE              pane 1  idle
...
10 pople              pane 2  done
```

(원본은 JSON 이다. 읽기 좋게 줄인 것이고 워크스페이스는 10개다.)

여기서 눈여겨볼 건 **워크스페이스마다 `agent_status` 가 붙어 있다**는 점이다.
들어가 보지 않아도 4번이 일하는 중이고 10번은 끝났다는 걸 목록에서 안다.
아까 말한 "8개 창을 하나씩 열어보는" 문제가 여기서 사라진다.

에이전트만 따로 세면 이렇다.

| 항목 | 값 |
|---|---|
| 살아 있는 에이전트 | 14 |
| 종류 | 전부 `claude` |
| 상태 | `idle` 12 · `working` 1 · `done` 1 |
| 이름 붙은 것 | `dotfiles` · `envion-gh` · `esg` · `gm-report` |

이름은 붙여도 되고 안 붙여도 된다. 붙이면 `w9:p2` 대신 `dotfiles` 로 부를 수 있다.
다만 **그 이름은 판이 아니라 지금 그 판에 있는 에이전트를 따라간다.** 에이전트가
빠지면 이름도 같이 사라진다.

## `done` 은 `idle` 과 같은 상태다

상태가 다섯 개인데, 이 중 둘은 **내부적으로 같은 것**이다.

`idle` 도 "입력을 기다리는 중", `done` 도 "입력을 기다리는 중"이다. 무엇이 다른가.
**내가 봤느냐**가 다르다.

- `idle` — 준비됐고, 그 탭을 **내가 이미 봤다**
- `done` — 준비됐는데, 내가 **안 보는 사이에** 끝났다

즉 `done` 은 "완료"라기보다 **"네가 안 볼 때 끝났어"** 라는 알림에 가깝다.
탭을 열어보면 그 순간 `idle` 로 내려간다.

여기서 실용적으로 중요한 게 하나 있다. **CLI 로 읽는 건 '봤다'로 치지 않는다.**
`herdr agent read` 로 출력을 아무리 읽어도 `done` 은 `done` 으로 남는다.
사람이 화면에서 그 탭을 봐야 내려간다. 에이전트가 대신 읽어주는 것과
사람이 확인하는 것을 Herdr 가 구분한다는 뜻이다.

나머지 둘도 짚어둔다.

- `blocked` — 승인·질문 대화상자를 Herdr 가 알아본 상태. **여기에 프롬프트를 밀어넣으면
  거부된다.** 열려 있는 대화상자를 먼저 봐야 한다
- `unknown` — 에이전트는 있는데 상태를 분류하지 못한 것. ⚠️ **완료가 아니다.**
  `unknown` 을 끝난 걸로 읽으면 아직 도는 작업을 끝났다고 보고하게 된다

## 에이전트가 에이전트를 부린다

이게 tmux 와 갈리는 지점이다. 흐름은 세 단계다.

```bash
# 1. 옆에 판을 하나 만든다 (내 포커스는 그대로 둔다)
herdr pane split --current --direction right --cwd "$PWD" --no-focus

# 2. 그 판에 에이전트를 띄운다
herdr agent start reviewer --kind codex --pane <위에서 받은 판 ID>

# 3. 일을 시키고 끝날 때까지 기다린다
herdr agent prompt reviewer "현재 diff 를 리뷰해줘" --wait --timeout 120000
```

`--kind` 로 고를 수 있는 에이전트가 22종이다 — `claude`, `codex`, `gemini`, `cursor`,
`copilot`, `droid`, `amp` 등. **Claude 가 Codex 를 띄워서 리뷰를 시키는 것**이 되는 셈이다.
같은 모델끼리 서로 검토하는 것보다 낫다는 판단이면 이렇게 가를 수 있다.

`agent start` 는 **판을 만들지 않는다.** 이미 있는 빈 셸 판에만 붙는다. 그래서 1번이
따로 있다. 레이아웃을 건드리는 일과 에이전트를 띄우는 일을 분리해 둔 것이다.

### Task 서브에이전트와 무엇이 다른가

Claude Code 자체에도 서브에이전트가 있다. 겹치는 것 아닌가 싶지만 성격이 다르다.

| | Task 서브에이전트 | Herdr 에이전트 |
|---|---|---|
| 어디서 도나 | 내 프로세스 안 | **진짜 터미널** |
| 종류 | Claude | 22종 (Codex·Gemini…) |
| 끝나면 | 사라진다 | **판에 남는다** — 이어서 대화 가능 |
| 내가 볼 수 있나 | 결과만 | **도는 걸 화면으로 본다** |

남는다는 게 실제로 크다. 서브에이전트는 보고서 하나를 던지고 사라지지만, Herdr 로 띄운
쪽은 판에 그대로 있어서 **"방금 그거 왜 그렇게 판단했어"** 를 이어서 물을 수 있다.

## 붙는 자리가 셋 — CLI · 스킬 · 훅

[Aside 글](/AI/Claude/aside란.html)에서 도구 하나가 세 군데로 들어온다는 얘기를 했는데,
Herdr 도 똑같이 셋이다. 그리고 **설치 주체가 갈리는 것도 똑같다.**

| 자리 | 실체 | 누가 설치하나 |
|---|---|---|
| CLI | `~/.local/bin/herdr` | Herdr 자신 |
| 스킬 | `~/.claude/skills/herdr` → `~/.agents/skills/herdr` | Herdr 자신 |
| 훅 | `~/.claude/hooks/herdr-agent-state.sh` | `herdr integration install claude` |

스킬은 심링크인데 **dotfiles 가 아니라 `~/.agents/skills/` 를 가리킨다.**
dotfiles 관리 밖이라는 뜻이고, 곧 **맥 4대에 자동으로 퍼지지 않는다**는 뜻이다.
Herdr 를 깐 머신에만 있다.

훅 파일은 첫 줄부터 못을 박아 뒀다.

```sh
# installed by herdr
# managed by herdr; reinstalling or updating the integration overwrites this file.
# add custom hooks beside this file instead of editing it.
```

**고치지 말고 옆에 새로 만들라**는 것이다. 업데이트하면 덮어쓰기 때문이다.
내 `settings.json` 의 훅들과 달리 이 파일은 내가 관리하는 대상이 아니다.

## 훅이 하는 일 — 상태를 추측하지 않게 만든다

훅을 열어보면 하는 일이 하나다. **Claude 세션이 시작될 때 "나 여기 있다"고 Herdr 에
직접 알려준다.**

```python
request = {
    "method": "pane.report_agent_session",
    "params": {
        "pane_id": pane_id,
        "source": "herdr:claude",
        "agent": "claude",
        "agent_session_id": agent_session_id,   # Claude 세션 ID
        "agent_session_path": agent_session_path # 트랜스크립트 파일 경로
    },
}
```

유닉스 소켓(`$HERDR_SOCKET_PATH`)으로 이 JSON 한 줄을 던지고 끝난다.
0.5초 타임아웃이고, 실패하면 조용히 넘어간다 — **훅이 죽어도 Claude 는 안 죽는다.**

왜 이게 필요한가. 훅이 없으면 Herdr 는 **화면에 찍힌 글자를 보고 추측**해야 한다.
그것도 되긴 하는데, 알려주는 편이 정확하다.

실제로 두 경로가 섞여 있는 게 데이터로 보인다. 아까 그 14개를 출처별로 세면:

| 탐지 경로 | 개수 |
|---|---:|
| `herdr:claude` (훅이 알려줌) | 11 |
| 출처 없음 (화면 보고 알아냄) | 3 |

3개는 훅을 깔기 전에 띄운 세션이다. **훅 없이도 인식은 된다.** 다만 세션 ID 와
트랜스크립트 경로까지는 못 얻는다.

한 가지 걸러내는 조건이 훅에 박혀 있는데 짚어둘 만하다.

```python
is_subagent = bool(hook_input.get("agent_id"))
if is_subagent:
    raise SystemExit(0)
```

**서브에이전트는 보고하지 않는다.** 서브에이전트가 뜰 때마다 보고하면 판 하나에
에이전트가 여러 개인 것처럼 보인다. 판과 에이전트를 1:1 로 유지하려는 것이다.

## 알고 있어야 할 것

**서버가 살아 있는 한 세션도 산다.** 창을 닫아도, SSH 가 끊겨도 판의 프로세스는 계속
돈다. 이게 장점인데 함정도 된다 — `herdr server stop` 은 **판에서 돌던 것까지 같이
멈춘다.** 스킬에도 "명시적으로 의도한 게 아니면 절대 실행하지 말 것"으로 적혀 있다.

**ID 는 서버 단위다.** 다중 머신으로 원격에 붙어도 서버가 합쳐지지 않는다. 양쪽에
`w2` 가 있으면 **서로 다른 워크스페이스**다. 이건 실제로 실험해 보고
[다른 글](/Linux/zshenv-비대화식-ssh-path.html)에 정리해 뒀다.

**화면이 원격을 봐도 CLI 는 로컬로 간다.** 사이드바에서 원격 머신을 보고 있어도
`herdr workspace list` 는 로컬 것을 뱉는다. 보는 것과 명령이 가는 곳이 다르다.

**닫힌 ID 는 재사용되지 않는다.** 판을 다른 워크스페이스로 옮기면 새 ID 를 받는다.
그래서 스킬이 "ID 를 예측하지 말고 JSON 응답에서 읽으라"고 반복해 말한다.

## 정리

- **판 안에 무엇이 도는지를 아는** 멀티플렉서다. tmux 는 위치까지, Herdr 는 그 안까지
- 상태가 목록에 붙어 있어서 **창을 하나씩 열어볼 필요가 없다**
- `done` 은 `idle` 과 **같은 상태**다. 다른 건 "내가 봤느냐"뿐이고,
  **CLI 로 읽는 건 봤다로 치지 않는다**
- ⚠️ `unknown` 은 완료가 아니다. 끝난 걸로 읽으면 안 된다
- 에이전트가 에이전트를 부린다 — **22종 중에 고를 수 있어서** Claude 가 Codex 에게
  리뷰를 시킬 수 있다
- Task 서브에이전트와 달리 **일이 끝나도 판에 남는다.** 이어서 물어볼 수 있다
- 붙는 자리는 셋(CLI·스킬·훅). 스킬은 **dotfiles 밖이라 다른 맥에 안 퍼진다**
- 훅은 상태를 **추측 대신 통보**로 바꾼다. 내 14개 중 11개가 훅 경로다
- `herdr server stop` 은 판의 프로세스까지 죽인다. 함부로 치지 않는다

같이 읽을 글:
[폰에서 에이전트를 조종했다 — Collie](/AI/Claude/collie-폰에서-에이전트-조종.html) ·
[SSH 로는 되는데 Herdr 만 못 찾는다](/Linux/zshenv-비대화식-ssh-path.html) ·
[Aside 란](/AI/Claude/aside란.html) ·
[내가 돌리는 워크플로우 설계](/AI/Claude/내가-돌리는-워크플로우-설계.html)
