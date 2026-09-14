---
title:  "문서에 없는 API 를 바이너리에서 꺼냈다 — Herdr 소켓 API 와 플러그인"

categories:
  - AI
tags:
  - AI
  - Claude Code
  - Herdr
  - api
  - 플러그인
  - 개발환경

date: 2026-09-14
thumbnail: "/assets/img/thumbnail/herdr_thumbnail.png"
card_thumbnail: "/assets/img/thumbnail/herdr_card.png"
---

## 한 줄로

Herdr 공식 문서의 API 페이지는 **엔드포인트를 하나도 적어두지 않았다.**
`server` · `client` · `update` 세 개와 "CLI 와 소켓 API 는 같은 표면"이라는 한 문장이 전부다.

그런데 `herdr api schema --json` 을 치면 **275KB** 가 쏟아진다.
그 안에 **메서드 102개, 타입 정의 121개**가 들어 있다.

이 글은 그걸 꺼내서 읽고, 실제로 찔러보고, 그 API 를 쓰는 플러그인을 하나 만든 기록이다.

## 문서를 번역하려다 그만둔 이야기

원래는 herdr.dev 문서를 한국어로 옮겨볼 생각이었다. 옮기기 전에 원문을 다 읽었는데,
**옮길 게 없었다.**

- `Connecting Machines` — `herdr machine add <name>` 한 줄. 나머지는 "클라우드 곧 나옴"
- `API` — 위에 적은 그대로. 스펙이 없다

문서가 얇다는 게 이 도구가 부실하다는 뜻은 아니었다. 뒤에서 보겠지만 **구현은 문서보다
훨씬 앞서 있었다.** 적어두지 않았을 뿐이다.

그래서 방향을 바꿨다. 문서가 안 알려주는 걸 직접 알아내기로.

## 스키마는 바이너리 안에 있었다

`herdr api` 에 하위 명령이 둘 있다.

```
Commands:
  snapshot  Print the live session snapshot
  schema    Print or write the bundled API schema
```

`bundled` — **번들된** 스키마다. 서버에 물어보는 게 아니라 바이너리가 들고 있다.
그냥 치면 요약 6줄만 나온다.

```
Herdr API schema
protocol: 22
schema_version: 1
schemas: error_response, event, request, subscription_event, success_response
```

243바이트. 여기서 멈추면 아무것도 못 얻는다. 실물은 `--json` 뒤에 있다.

```bash
herdr api schema --json > schema.json
# 275,126 bytes
```

⚠️ `--json` 과 `--output` 은 **같이 못 쓴다.** 둘 다 주면
`usage: herdr api schema [--json | --output PATH]` 로 거절당한다.
파일로 받고 싶으면 위처럼 리다이렉트하거나 `--output` 만 쓴다.

### 파싱이 한 번 막힌다

그대로 `json.load()` 하면 깨진다.

```
JSONDecodeError: Invalid control character at: line 7627 column 109
```

설명문 안에 **원시 개행이 그대로** 들어 있어서다. 엄격 모드가 이걸 거부한다.
`strict=False` 로 읽으면 통과한다.

```python
d = json.load(open("schema.json"), strict=False)
```

## 메서드 102개

요청은 JSON-RPC 꼴이다. 최상위에 `id` 가 필수고, `oneOf` 아래 각 변형이
`method` 상수와 `params` 참조를 들고 있다.

```json
{"properties": {"method": {"const": "ping", ...},
                "params": {"$ref": "#/schemas/request/$defs/PingParams"}},
 "required": ["method", "params"]}
```

`method` 상수만 전부 뽑아 계열별로 세면 이렇다.

| 계열 | 개수 | 대표 메서드 |
|---|---|---|
| `pane.*` | 36 | `split` · `send_keys` · `read` · `wait_for_output` |
| `agent.*` | 12 | `start` · `prompt` · `wait` · `explain` |
| `plugin.*` | 11 | `link` · `action.invoke` · `pane.open` |
| `workspace.*` | 9 | `create` · `move_block` · `report_metadata` |
| `tab.*` | 7 | `create` · `move` · `focus` |
| `server.*` | 5 | `stop` · `live_handoff` · `reload_config` |
| 나머지 13계열 | 22 | `worktree` · `layout` · `integration` · `events` … |

**102개다.** 공식 문서가 이 중 적어둔 것은 0개다.

<div class="diagram">
{% include diagrams/herdr--api-surface.svg %}
</div>

## 직접 찔러본다

소켓은 `herdr status` 가 알려준다.

```
socket: /Users/…/.config/herdr/herdr.sock
```

권한은 `srw-------` — 내 계정만 읽고 쓴다. 프로토콜 번호(22)가
클라이언트·서버 양쪽에 같이 찍혀 있어서, 버전이 어긋나면 바로 드러나는 구조다.

핸드셰이크는 없다. **한 줄 JSON 을 던지면 한 줄 JSON 이 돌아온다** (JSON Lines).

```python
import socket, json, os

def call(method, params=None):
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.settimeout(10)
    s.connect(os.path.expanduser("~/.config/herdr/herdr.sock"))
    s.sendall((json.dumps({"id": "probe-1",
                           "method": method,
                           "params": params or {}}) + "\n").encode())
    buf = b""
    while b"\n" not in buf:
        chunk = s.recv(65536)
        if not chunk:
            break
        buf += chunk
    s.close()
    return json.loads(buf.split(b"\n")[0].decode())
```

`ping` 부터.

```json
{"id":"probe-1","result":{"type":"pong","version":"0.9.0","protocol":22,
 "capabilities":{"live_handoff":true,"detached_server_daemon":true,
                 "endpoint_protocol_generation":1,
                 "surface_interest":true,"health_check":true}}}
```

💡 **`capabilities` 5개는 스키마에 없던 정보다.** `PingParams` 를 아무리 읽어도
안 나온다. 응답 쪽에만 있으니 **실제로 한 번 쳐봐야** 알 수 있다.
스키마를 읽는 것과 찔러보는 것은 서로를 대체하지 못한다.

## 판 상태가 그대로 나온다

`agent.list` 를 부르면 지금 돌고 있는 것들이 전부 나온다.

```
  wE:p1    claude   idle     JIRA(주간보고)
  wE:p2    claude   idle     옵시디언 내용 정리
  w4:p1    claude   idle     dotfiles
  w9:p2    claude   working  Herdr collie 포스트 작성
  wA:p2    claude   working  Claude 세션 내용 확인
  w2:p3    claude   done     Runcat 메모리 사용량 분석
  wG:p1    claude   idle     광명 9월달 주간보고서 월간계획서

분포: {'idle': 4, 'working': 2, 'done': 1}
```

`w9:p2` 가 `working` 으로 잡혀 있다. **이 글을 쓰고 있는 판이다.**
API 로 나를 관측한 셈이 됐다.

### `agent_session` — 판이 아니라 대화를 가리킨다

각 항목에 이런 필드가 붙어 온다.

```json
"agent_session": {"source":"herdr:claude", "agent":"claude",
                  "kind":"id", "value":"875967a8-…"}
```

Claude Code 의 **세션 UUID** 다. Herdr 가 판 번호만 들고 있는 게 아니라
**그 안에서 돌던 대화를 식별**하고 있다.

앞 글에서 "새로 띄우는 것이 아니라 아까 그 대화에 그대로 이어 붙는다"고 썼는데,
그때는 화면을 보고 쓴 문장이었다. 이 필드가 그 문장의 실제 근거다.

## 핵심은 `agent.wait` 이었다

`agent` 계열에서 눈에 띄는 건 세 개 조합이다 — `start` · `prompt` · `wait`.
에이전트가 다른 에이전트를 띄우고, 프롬프트를 넣고, 기다린다.

파라미터를 보면 `wait` 이 특이하다.

```
### agent.wait  (AgentWaitParams)
  *target        string
   timeout_ms    ['integer','null']
   until         array
```

`until` 이 **배열**이다. 뭐가 들어가는지 따라가면 `AgentStatus` 가 나온다.

```json
{"enum": ["idle", "working", "blocked", "done", "unknown"], "type": "string"}
```

다섯 개. 앞서 [Herdr 글](/AI/Claude/herdr란.html)에서 화면을 보고 적었던 상태와 정확히 같다.
이제는 스키마가 같은 값을 확인해준다.

그리고 이 조합의 의미가 여기서 드러난다.

```python
call("agent.wait", {"target": "w4:p1", "until": ["blocked"]})
```

**상대 에이전트가 승인을 기다리며 막힐 때까지 기다린다.**
"일이 끝날 때까지"가 아니라 "사람 손이 필요해질 때까지"다.

### 폴링이 아니라 블로킹이다

실제로 재봤다.

| 호출 | 결과 | 걸린 시간 |
|---|---|---|
| 이미 `idle` 인 판에 `until:["idle"]` | 즉시 `agent_info` | **0.030초** |
| 아무도 `blocked` 아닌데 `until:["blocked"]`, 4초 제한 | `{"code":"timeout"}` | **4.062초** |

조건을 이미 만족하면 즉시 돌려주고, 아니면 **붙잡고 있다가** 타임아웃으로 끝낸다.
반복 조회로 흉내 낸 게 아니다. 0.030 과 4.062 — 스키마만 읽어서는 알 수 없고
직접 재야 나오는 숫자다.

실패는 예외가 아니라 **에러 코드**로 온다.

```json
{"id":"probe-1","error":{"code":"timeout","message":"timed out waiting for agent status"}}
```

## 이 API 를 쓰는 플러그인을 만든다

읽기만 하면 반쪽이다. 같은 API 를 쓰는 플러그인을 하나 만들어봤다.
하는 일은 하나 — **막힌 에이전트를 찾아준다.**

문서가 알려주는 매니페스트 규칙은 이렇다.

- 필수 필드 4개: `id` · `name` · `version` · `min_herdr_version`
- 섹션 6종: `build` · `startup` · `actions` · `events` · `panes` · `link_handlers`
- ⚠️ `command` 는 **argv 배열**이고 **셸을 거치지 않는다** — 파이프도 `~` 확장도 없다

```toml
id = "local.blocked-watch"
name = "Blocked Watch"
version = "0.1.0"
min_herdr_version = "0.9.0"
description = "막힌 에이전트를 소켓 API 로 찾아낸다"
platforms = ["macos", "linux"]

[[actions]]
id = "list-blocked"
title = "막힌 에이전트 찾기"
contexts = ["workspace"]
command = ["python3", "blocked.py"]
```

스크립트는 위의 `call()` 과 거의 같다. 딱 한 군데만 다르다.

```python
sock_path = os.environ.get("HERDR_SOCKET_PATH")
if not sock_path:
    sys.exit("HERDR_SOCKET_PATH 가 없다 — Herdr 가 띄운 게 맞나?")
```

**소켓 경로를 박아 넣지 않는다.** Herdr 가 실행할 때 환경변수로 주입한다.
같이 들어오는 것이 `HERDR_BIN_PATH` · `HERDR_PLUGIN_ID` ·
`HERDR_PLUGIN_CONFIG_DIR` · `HERDR_PLUGIN_STATE_DIR` 이다.
설정은 `CONFIG_DIR`, 런타임 상태는 `STATE_DIR` 에 두고 **플러그인 루트에는 쓰지 말라**고
문서가 명시한다.

### 마켓에 올리지 않고 붙인다

```bash
herdr plugin link ./herdr-blocked-plugin
```

```json
{"result":{"plugin":{"enabled":true,"plugin_id":"local.blocked-watch",
 "source":{"kind":"local"},"version":"0.1.0", …},"type":"plugin_linked"}}
```

`link` 는 빌드 단계를 건너뛰고 로컬 디렉터리를 그대로 등록한다.
GitHub 에 올리고 토픽을 달고 인덱싱 30분을 기다릴 필요가 없다.

## 실행하다 만난 함정

액션을 부르려는데 세 번 틀렸다. 헬프는 이렇게 적혀 있다.

```
Usage: herdr plugin action invoke [OPTIONS] <ACTION_ID>
Options:
      --plugin <ID>
```

그래서 이렇게 쳤다 — 전부 실패했다.

```bash
herdr plugin action invoke local.blocked-watch list-blocked   # unknown option
herdr plugin action invoke --plugin local.blocked-watch list-blocked   # unknown option
herdr plugin action invoke --plugin=local.blocked-watch list-blocked   # unknown option
```

정답은 **가장 단순한 형태**였다.

```bash
herdr plugin action invoke list-blocked
```

💡 **`--plugin` 은 헬프에 적혀 있지만 파서가 받지 않는다** (0.9.0 실측).
같은 플러그인 ID 를 콜론으로 붙이면(`local.blocked-watch:list-blocked`)
`plugin_action_not_found` 가 난다. 액션 ID 만 준다.

헬프를 믿고 세 번 틀린 셈인데, 이건 문서가 얇아서 생긴 문제가 아니다.
**헬프와 구현이 어긋나 있다.** 문서가 두꺼웠어도 똑같이 틀렸을 것이다.

### 부르지 않은 정보가 딸려온다

성공 응답에 `context` 가 붙어 있었다.

```json
"context": {"focused_pane_id":"w9:p2", "focused_pane_status":"working",
            "focused_pane_agent":"claude",
            "workspace_id":"w9", "workspace_label":"블로그",
            "tab_label":"블로그", "invocation_source":"cli"}
```

인자로 아무것도 안 줬는데 **어느 판에서 불렀는지**를 Herdr 가 채워 넣는다.
플러그인이 자기 위치를 스스로 알 필요가 없다는 뜻이다.

## 결과

```bash
herdr plugin log list
```

```json
{"action_id":"list-blocked","exit_code":0,"status":"succeeded",
 "started_unix_ms":1789371091510, "finished_unix_ms":1789371091629,
 "stderr":"", "stdout":"전체 7개 중 막힌 것 0개\n  - wE:p1 idle …"}
```

`exit_code: 0`. 소켓까지 닿아 7개를 읽어왔다.
시작과 끝 타임스탬프 차이가 **119ms** — 파이썬 프로세스 기동까지 포함한 값이다.

`HERDR_SOCKET_PATH` 가 진짜로 주입된다는 것도 같이 증명됐다.
없으면 죽게 짜놨는데 정상 종료했으니까.

## 알고 쓸 것

⚠️ **이 API 는 공식 문서에 없는 표면이다.** 스키마에 `protocol: 22`,
`schema_version: 1` 이 박혀 있는데, 문서화되지 않았다는 것은 **예고 없이 바뀔 수 있다**는
뜻이다. 버전을 확인하지 않고 스크립트를 짜두면 업데이트 한 번에 조용히 깨진다.

앞 글에서 Collie 의 `promptBinding` 을 다룰 때와 같은 처리를 한다 —
쓰되, 무엇에 기대고 있는지 적어둔다.

그리고 이 글에서 알아낸 것 중 **설계 의도를 개발자에게 확인한 것은 하나도 없다.**
전부 스키마와 실측에서 나온 관찰이다. `agent.wait` 이 왜 블로킹인지,
`--plugin` 이 왜 안 받는지는 추측일 뿐 확인된 바 없다.

## 정리

- 공식 문서의 API 페이지는 엔드포인트 **0개**. `herdr api schema --json` 은 **275KB**
- 그 안에 메서드 **102개**, 타입 정의 **121개**
- 소켓은 JSON Lines, 핸드셰이크 없음. 권한은 `600` 으로 내 계정 전용
- `AgentStatus` 는 `idle` · `working` · `blocked` · `done` · `unknown` **5종**
- `agent.wait` 은 폴링이 아니라 **블로킹** — 즉시 0.030초 / 타임아웃 4.062초
- `agent_session` 이 판이 아니라 **대화 UUID** 를 들고 있다
- 플러그인은 `herdr plugin link` 로 마켓 없이 붙는다. 액션 실행 **119ms**
- 함정: `--json`+`--output` 동시 불가 / 스키마에 원시 개행 / `--plugin` 은 헬프에만 있다

문서가 얇았던 게 오히려 나았다. 번역했으면 반 페이지를 옮기고 끝났을 것이고,
**이 102개는 영영 못 봤을 것이다.**

---

같이 읽을 글:
[Herdr 란](/AI/Claude/herdr란.html) ·
[폰에서 에이전트를 조종했다 — Collie](/AI/Claude/collie-폰에서-에이전트-조종.html) ·
[SSH 로는 되는데 Herdr 만 못 찾는다](/Linux/zshenv-비대화식-ssh-path.html)
