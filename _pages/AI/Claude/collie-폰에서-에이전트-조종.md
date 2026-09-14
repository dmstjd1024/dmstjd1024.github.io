---
title:  "폰에서 에이전트를 조종했다 — Collie 로 승인 대기를 풀어낸 3일"

categories:
  - AI
tags:
  - AI
  - Claude Code
  - Herdr
  - Collie
  - Tailscale
  - 개발환경

date: 2026-09-14
thumbnail: "/assets/img/thumbnail/herdr_thumbnail.png"
card_thumbnail: "/assets/img/thumbnail/herdr_card.png"
---

## 한 줄로

에이전트를 오래 돌려보면 **일하는 시간보다 승인을 기다리는 시간이 길다.**
자리를 비우면 그 대기가 전부 멈춤이 된다.

Collie 는 그 판에 **폰을 붙인다.** 밖에서 승인 번호를 누르고, 답을 보내고,
`/compact` 를 친다. 3일 동안 폰에서 39번 입력을 보냈고, 그중 **10번이
승인 대화상자 응답**이었다.

---

## 무엇이 병목이었나

[Herdr](/AI/Claude/herdr란.html) 로 판을 여러 개 띄우면 에이전트가 동시에 돈다.
그런데 동시에 돈다고 시간이 줄지 않는다. 이유가 하나 있다.

에이전트는 혼자 끝까지 못 간다. 중간에 **묻는다.** 파일을 지워도 되는지,
이 명령을 실행해도 되는지. Herdr 는 그 상태를 `blocked` 로 알아본다.
알아보기만 한다 — 답은 사람이 해야 한다.

그래서 이런 상태가 된다.

```
$ herdr workspace list
4  블로그    pane 1  blocked   ← 3분 전부터 여기서 멈춰 있다
```

3분이면 괜찮다. 문제는 **점심 먹으러 나갔을 때**다. 1시간을 나가면 1시간이 통째로
날아간다. 에이전트가 느려서가 아니라 **답할 사람이 자리에 없어서**다.

판을 아무리 늘려도 이건 안 풀린다. 오히려 판이 많을수록 멈춤이 겹친다.
풀리려면 **자리를 비운 채로 답할 수 있어야** 한다.

---

## Collie 는 무엇인가

터미널에서 도는 에이전트에 **폰용 웹 UI를 붙이는 브리지**다.
`herdr.collie` 라는 이름으로 launchd 에 등록되어 배경에 떠 있다.

구조는 네 층이라고 문서가 밝히고 있다.

| 층 | 하는 일 |
|---|---|
| Web | 폰에서 여는 PWA. 자기를 내려준 브리지와 대화한다 |
| Crew | 여러 머신을 한 URL 뒤에 묶는 선택적 연결 |
| Bridge | 머신 위의 서비스. PWA 를 내려주고 폰의 요청에 답한다 |
| Mux adapter | 이 설치가 비추는 멀티플렉서 하나 — Herdr · tmux · zellij |

내 경우 mux 는 Herdr 다. `COLLIE_MUX=herdr` 이고,
`~/.config/herdr/herdr.sock` 으로 붙는다.

여기서 **Herdr 와 역할이 갈리는 지점**을 짚어둔다.

- Herdr — 판을 나누고, 그 안에서 뭐가 도는지 안다
- Collie — 그 앎을 **밖에서 열람하고 조작하게** 한다

Collie 는 에이전트를 새로 띄우지 않는다. **이미 돌고 있던 판에 붙는다.**
그래서 폰에서 보내는 것은 새 질문이 아니라 **아까 그 대화의 다음 줄**이다.

---

## 폰에서 누른 키가 판에 닿기까지

<div class="diagram">
{% include diagrams/collie--phone-path.svg %}
</div>

네 칸이지만 실제로 봐야 할 건 **강조된 칸 하나**다. 나머지는 통로다.

`tailscale serve` 로 프론트도어를 하나 연다. 내 경우는 이 주소다.

```
https://<내-머신>.<내-테일넷>.ts.net → http://127.0.0.1:8787
```

**포트를 여는 게 아니다.** 브리지는 `127.0.0.1` 에만 바인딩되고,
tailnet 안에서만 닿는다. 문서가 이 지점에 경고를 박아 뒀다.

> 🚫 **Never use `tailscale funnel` with Collie.** Funnel routes traffic to the
> public internet, whereas `tailscale serve` restricts access to your private tailnet.

`funnel` 은 공개 인터넷으로 낸다. `serve` 는 내 tailnet 안에서만 닿는다.
글자 하나 차이인데 **한쪽은 인터넷 전체에 셸을 여는 것**이다.

---

## 실제로 무엇을 했나 — 3일치 기록

Collie 는 들어온 쓰기를 전부 `audit.log` 에 남긴다.
추정이 아니라 **파일에 적힌 것**을 센다.

```bash
$ wc -l < ~/.local/state/collie/audit.log
59
```

2026-09-10 ~ 09-13, 59줄이다. 갈래를 세면 이렇다.

| 행위 | 횟수 |
|---|---:|
| `reply` — 텍스트를 보냄 | 39 |
| `keys` — 키를 직접 누름 | 10 |
| 페어링 · crew · 기기 회수 | 9 |
| 탭 닫기 | 1 |

`reply` 39번 중 **실제 텍스트가 실린 건 21번**이고 나머지 18번은
텍스트 없이 submit 만 간 것이다. 입력과 전송이 따로 기록되기 때문이라
**내가 폰에서 문장을 보낸 횟수는 21번**으로 읽는 게 맞다.

판별로는 이렇게 갈렸다.

| 판 | 횟수 | 무엇이 돌고 있었나 |
|---|---:|---|
| `wS:p2` | 31 | Collie 자체를 손보던 판 |
| `wE:p1` | 11 | 주간보고 자동화 |
| `wE:p2` | 4 | 옵시디언 볼트 정리 |
| `wS:p3` | 3 | 요약 받던 판 |

실제로 밖에서 보낸 문장 몇 개를 그대로 옮긴다.

```
주간보고 잘 썻어?
지금 옵시디언은 어때?? 잘 돌아가?
/compact
```

`/compact` 가 섞여 있는 게 이 도구의 성격을 잘 보여준다.
폰에서 한 게 **읽기만이 아니라 세션 관리**였다는 뜻이다.
실제로 그 판은 컨텍스트가 차서 밖에서 `ctrl+k` 로 입력줄을 비우고
다시 `/compact` 를 쳐 넣어야 했다.

---

## 승인 번호를 폰에서 누른다

`keys` 10번이 이 글의 핵심이다. 기록을 보면 대부분 이 모양이다.

```json
{"action":"keys","paneId":"wE:p1","device":"마이폰",
 "detail":{"keys":["5","Enter"]}}
```

Claude 가 띄운 번호 선택 대화상자에 **폰에서 5번을 누른 것**이다.
앞서 말한 `blocked` 가 여기서 풀린다. 자리에 없어도 풀린다.

10번 중 8번에는 `promptBinding` 이라는 필드가 같이 붙어 있다.

```json
"promptBinding": {
  "checked": true,
  "passed": true,
  "expected": "  결론 3줄   1. 주간보고 못 썼습니다. 09:07에 돌긴 했는데 …"
}
```

**내 폰 화면에 보이던 프롬프트가 무엇이었는지를 같이 보낸다.**
`checked: true, passed: true` 는 그게 판의 현재 화면과 대조되어 통과했다는 뜻이다.
8번 전부 통과했다.

왜 이게 필요한지는 이 도구를 써 보면 바로 안다. 폰 화면은 **과거**다.
1500ms 폴링이고, 지하철에서는 더 늦는다. 내가 "5번" 을 누를 때
그 판은 이미 다음 질문으로 넘어가 있을 수 있다. 그러면 **다음 질문에
엉뚱한 답이 들어간다.** 삭제 확인에 "예" 가 꽂히는 사고가 이 구조다.

`promptBinding` 은 그걸 막는다. 보낼 때 화면을 같이 실어서,
**달라졌으면 안 넣는다.**

나머지 2번은 이 필드가 없다. 둘 다 `ctrl+k`·`Backspace`·`Enter` 였다 —
번호 선택이 아니라 편집 키다. 고를 선택지가 없으니 대조할 프롬프트도 없다.
**대조가 붙는 건 선택지를 고르는 순간뿐**이라는 뜻으로 읽었다.

⚠️ 다만 `promptBinding` 은 공식 문서에 없는 필드다.
`collie docs --all` 어디에도 안 나온다. **위는 로그에 찍힌 값에서 읽어낸 것**이고,
설계 의도를 내가 확인한 것은 아니다.

---

## 알림이 조용히 죽어 있었다

밖에서 답하려면 **멈췄다는 걸 알아야** 한다. 판을 계속 들여다볼 거면
폰을 붙인 의미가 없다. 그래서 Web Push 를 켰다 — 정확히는, **켠 줄 알았다.**

09-11 에 폰에서 이 문장을 보냈다.

```
서버에 VAPID 키가 구성되지 않아 푸시 알림이 비활성화되었습니다 이건 머야
```

로그를 열어보니 브리지가 뜰 때마다 같은 줄을 찍고 있었다.

```
[push] disabled (no VAPID keys configured)
```

VAPID 는 Web Push 를 보낼 때 **"이 알림은 이 서버가 보낸 게 맞다"** 를
증명하는 키 쌍이다. 없으면 브라우저가 알림을 안 받는다.

문제는 **이게 에러로 안 뜬다는 것**이다. 브리지는 정상 기동했고,
폰 UI 도 멀쩡했고, 알림만 안 왔다. 알림이 안 오는 건 조용한 증상이다 —
**안 왔다는 걸 알려면 와야 했던 순간을 알아야 하는데, 그걸 알려주는 게
알림이다.** `collie push-keys` 로 키를 만들고 나서야 바뀌었다.

```
[push] enabled (0 saved subscription(s))
```

지금은 폰 하나가 구독에 올라와 있다.

```json
{"endpoint":"https://web.push.apple.com/QEMZ…",
 "userAgent":"Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 …)"}
```

알림은 세 가지를 켜 뒀다.

```json
{"blocked": true, "done": true, "updates": true}
```

`blocked` 가 이 글의 그 `blocked` 다. **에이전트가 물어보는 순간 폰이 울린다.**
`done` 은 [Herdr 글](/AI/Claude/herdr란.html)에서 정리한 대로
"내가 안 보는 사이에 끝났다" 는 뜻이고, 밖에 있을 때는 항상 그 경우다.

---

## 폰이 곧 셸이다 — 페어링을 먼저 한다

문서 첫 줄이 이렇게 시작한다.

> **Collie provides remote shell access to your machine by design.**
> Treat the URL as a root login.

과장이 아니다. 이 URL 에 닿는 기기는 **판에 키를 넣을 수 있다.**
샌드박스도 없고 명령 화이트리스트도 없다 — 걸면 도구가 죽으니 안 건다고
문서가 밝히고 있다.

그래서 기기를 짝지었다. 호스트에서 `collie pair` 를 치면 8자 코드와 QR 이 나오고,
10분 안에 폰에서 넣으면 토큰을 받는다. **호스트에는 해시만 남는다.**

```json
{"label":"마이폰",
 "tokenHash":"4f1a2cfad794…",
 "createdAt":1789032340091}
```

짝지은 기기는 하나다. 09-10 에 "내 핸드폰" 으로 한 번 짝짓고,
09-11 에 회수한 뒤 "마이폰" 으로 다시 짝지었다. 회수는 즉시 먹는다 —
재시작이 필요 없다고 문서에 적혀 있고, 실제로 그랬다.

## 관문을 하나 더 세웠다가 도로 내렸다

브리지가 뜰 때마다 찍는 경고가 하나 있다.

```
[bridge] WARNING: COLLIE_TRUSTED_USER is empty —
any tailnet device/user that reaches the bridge gets full write access.
```

관문이 둘인데 하나만 세워 뒀다는 뜻이다. 둘은 **서로 다른 것을 묻는다.**

| 관문 | 묻는 것 |
|---|---|
| 페어링 | 이 기기가 **내가 발급한 토큰**을 갖고 있나 |
| `COLLIE_TRUSTED_USER` | 이 요청이 **내 tailnet 로그인**으로 들어왔나 |

페어링만으로도 쓰기는 막힌다. 다만 문서가 짚어두듯 **읽기는 남는다** —
`read operations remain accessible`. tailnet 안의 다른 기기가 URL 을 알면
토큰 없이도 판 출력을 볼 수 있다는 뜻이다.

그래서 켜 봤다. `tailscale status --json` 이 알려주는 내 로그인 이름이다.

```bash
COLLIE_TRUSTED_USER=<내-계정>@github
```

고치고 `collie restart` 를 했다. 앞서 crew 에서 겪은 그대로,
파일만 고치면 도는 프로세스는 부팅 때 읽은 값을 계속 들고 있다.

재시작하니 경고 줄이 사라졌다. 그런데 **경고가 사라진 건 값이 읽혔다는 증거일 뿐,
차단된다는 증거가 아니다.** 직접 찔러 봤다.

```bash
$ curl … /api/snapshot                                    # 헤더 없음
403  identity required
$ curl -H "Tailscale-User-Login: <내-계정>@github" …     # 내 계정
200  {"bridge":"connected","agents":[…
$ curl -H "Tailscale-User-Login: someone@else" …          # 남의 계정
403  identity not trusted
```

제대로 막혔다. 폰도 확인했다 — 헤더는 `tailscale serve` 가 넣어주는 것이라
그게 안 되면 내 폰까지 잠긴다.

```bash
$ curl https://<내-머신>.<내-테일넷>.ts.net/api/snapshot
200
```

**막혔고, 폰은 살아 있다.** 여기까지는 성공이었다.

### 그런데 doctor 가 눈이 멀었다

`collie doctor` 를 돌려보니 이렇게 나왔다.

```
skipped: agent-sessions   the bridge did not answer `/api/snapshot`,
                          so no pane can be checked
```

**doctor 도 헤더 없이 자기 브리지를 호출한다.** 그래서 자기가 세운 관문에
자기가 막힌다. 브리지는 멀쩡한데 진단 도구만 아무것도 못 본다.

문서에 `COLLIE_TRUSTED_USER_OPTIONAL=1` 이 있지만 그건 **헤더 없는 요청을
전부 통과**시키는 스위치다. 방금 막은 걸 도로 여는 것이라 쓰지 않았다.

그래서 실제 위협이 뭔지를 다시 봤다. 문서가 경고한 건 **"모든 로컬 UID 가
포트에 닿는다"** 였다. 이 맥에서 그게 성립하는지 센다.

```bash
$ dscl . -list /Users UniqueID | awk '$2>=500 && $2<1000'
jeon-eunseong  501          # 일반 사용자는 나 하나뿐

$ lsof -nP -iTCP:8787 -sTCP:LISTEN
collie … TCP 127.0.0.1:8787 (LISTEN)   # 루프백에만
```

tailnet 쪽도 셌다. `tailscale status` 에 노드 5개가 있고 **전부 내 계정
소유의 내 기기**다. 남이 없다.

즉 이 관문이 막아주는 시나리오가 **이 머신에는 지금 존재하지 않는다.**
반면 doctor 가 못 도는 건 매번 겪는 실질적 손해다. 되돌렸다.

```bash
$ curl … /api/snapshot     # 다시 200
$ collie doctor            # 판을 다시 읽는다
```

⚠️ **이건 "안 해도 된다"가 아니라 "이 머신에서는 지금 이득이 없다"이다.**
tailnet 에 남의 기기가 들어오는 순간, 또는 이 맥에 계정이 하나 더 생기는
순간 판단이 뒤집힌다. 그때는 doctor 를 포기하고 관문을 세우는 게 맞다.

💡 헛다리를 하나 짚었던 것도 적어둔다. 처음엔 `/api/state` 로 찔러보고
셋 다 200 이 나와서 "설정이 안 먹었나" 했는데, **그런 경로가 없었다.**
PWA 라 없는 경로는 전부 `index.html` 을 200 으로 돌려준다.
차단을 확인하려면 **진짜 있는 엔드포인트**로 찔러야 한다.

---

## crew 는 포기했다

머신이 둘이다 — 회사 맥과 개인 맥미니. Collie 에는 **crew** 라는 게 있어서
여러 머신을 한 URL 뒤에 묶을 수 있다. 폰 앱 하나로 양쪽을 보는 그림이다.

09-10 에 붙였다. 로그상 10분 만에 들어왔다.

```
09:10:46  crew.enroll  jeon-eunseong-ui-macmini-local
09:21:41  crew.remove  jeon-eunseong-ui-macmini-local
```

**11분 만에 뺐다.** 붙는 중에 이미 다른 문제가 하나 드러났다.

```
[crew] the trust store changed under this running process —
       it still holds the roster it read at boot.
[crew] this machine is now a lead, but the process is still running as a solo
```

**등록은 파일에 됐는데 도는 프로세스는 예전 명부를 들고 있다.**
`collie restart` 전까지는 반영이 안 된다. 설정을 고쳤는데 안 먹는 상황이
여기서 나온다 — 흔한 함정이고, Collie 는 이걸 로그로 말해준다.

09-12 에 다시 붙였다. 이번엔 다른 데서 막혔다.

```
[crew] jeon-eunseong-ui-macmini-local: unreachable (snapshot: timed out after 5000ms)
[crew] jeon-eunseong-ui-macmini-local: dropped a stale hello reply, dial 104 of 105
[crew] jeon-eunseong-ui-macmini-local: dropped a stale hello reply, dial 113 of 114
```

**114번을 걸어서 붙지 못했다.** lead 가 member 를 불러서(dial) 가져오는 구조라
member 쪽이 안 받으면 방법이 없다. 그날 폰에서 이렇게 물었다.

```
차라리 맥미니를 중심으로 회사 머신에 붙도록 바꾸는건 어때?
```

방향을 뒤집어도 같은 벽이었다. 그래서 이렇게 끝냈다.

```
그냥 따로따로 해서 앱 2개 만들게
```

**머신마다 Collie 를 따로 띄우고 폰에 PWA 를 두 개 깔았다.**
한 URL 로 묶는 편의를 버리고 확실히 붙는 쪽을 골랐다.
지금 `mode` 는 `solo` 이고 명부는 비어 있다.

```json
{"mode":"solo","roster":[]}
```

돌아보면 crew 는 **내 상황에 필요한 기능이 아니었다.** 두 머신을 동시에
보는 일이 거의 없다. 회사 맥을 볼 때와 맥미니를 볼 때가 애초에 다른 시간대다.
붙이느라 쓴 이틀은 **기능이 있어서 붙인 것**이지 필요해서 붙인 게 아니었다.

---

## doctor 가 말해주는 것

앞에서 두 번 나왔으니 정리해 둔다. `doctor` 는
**조용히 실패하는 것들을 잡아주는 명령**이다. 지금 돌리면 하나가 빨간색으로 뜬다.

```
error: agent-sessions  10 agent pane(s) … 2 report NO session: w9:p2 (claude), wS:p2 (claude)
       — their History link and icon are hidden, and the pane looks otherwise normal
```

`w9:p2` 는 **지금 이 글을 쓰는 판**이다. 훅이 깔리기 전에 시작한 세션이라
Herdr 에 자기 세션 ID 를 보고하지 못했다. 그래서 폰에서 이 판의 History 를
못 연다.

주목할 건 뒷부분이다 — **"the pane looks otherwise normal"**.
판은 멀쩡해 보인다. 목록에도 뜨고 출력도 보이고 키도 들어간다.
History 만 조용히 없다. `doctor` 를 안 돌리면 모를 종류의 고장이다.

고치는 법도 같이 알려준다 — **새 세션을 시작하면 된다.** 훅은 세션 시작 때
로드되므로 이미 도는 세션에는 못 붙는다.

---

## 정리

- 에이전트 여러 개를 돌릴 때 진짜 병목은 처리 속도가 아니라 **승인 대기**다.
  자리를 비우면 그 대기가 전부 멈춤이 된다
- Collie 는 그 판에 폰을 붙인다. **에이전트를 새로 띄우는 게 아니라
  돌고 있던 대화에 이어 붙는다**
- 3일간 폰에서 문장 21번, 키 10번. **키 10번이 승인 대화상자 응답**이고
  여기서 멈춤이 풀렸다
- 폰 화면은 과거다. `promptBinding` 이 **보낼 때 화면을 같이 실어 대조**한다.
  8번 다 통과 — 다만 이 필드는 문서에 없고 로그에서 읽어낸 것이다
- ⚠️ VAPID 키가 없으면 **푸시가 조용히 죽는다.** 에러가 안 뜨고 알림만 안 온다.
  알림이 안 온 걸 알려주는 게 알림이라 스스로는 못 알아챈다
- ⚠️ `funnel` 이 아니라 `serve` 다. 한 글자 차이로 **인터넷 전체에 셸이 열린다**
- URL 은 root 로그인이다. 관문은 **둘이고 묻는 게 다르다** — 페어링은 토큰을,
  `COLLIE_TRUSTED_USER` 는 tailnet 로그인을 묻는다. 페어링만 세우면
  **쓰기는 막히고 읽기는 남는다**
- 두 번째 관문은 켰다가 **되돌렸다.** `doctor` 도 헤더 없이 호출하므로
  자기가 세운 관문에 자기가 막힌다. 이 맥은 사용자가 나 하나, tailnet 도 내 기기뿐이라
  **막아주는 시나리오가 없는데 진단만 잃는** 거래였다.
  ⚠️ 조건이 바뀌면 판단도 뒤집힌다
- ⚠️ **경고가 사라진 건 차단됐다는 증거가 아니다.** 값이 읽혔다는 것뿐이다.
  없는 경로는 200 을 돌려주므로, **진짜 엔드포인트로 403 을 직접 확인**해야 한다
- crew 는 114번 dial 끝에 포기하고 **앱 2개로 갔다.** 두 머신을 동시에 볼 일이
  애초에 없었다 — 기능이 있어서 붙인 것이었다
- 설정 파일을 고쳐도 **도는 프로세스는 부팅 때 읽은 걸 들고 있다.**
  `restart` 전까지 반영 안 된다
- `doctor` 는 **멀쩡해 보이는 고장**을 잡는다. 내 판 하나가 History 만 조용히 없다

같이 읽을 글:
[Herdr 란](/AI/Claude/herdr란.html) ·
[SSH 로는 되는데 Herdr 만 못 찾는다](/Linux/zshenv-비대화식-ssh-path.html) ·
[내가 돌리는 워크플로우 설계](/AI/Claude/내가-돌리는-워크플로우-설계.html)
