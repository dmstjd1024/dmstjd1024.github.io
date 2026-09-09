---
title:  "SSH 로는 되는데 Herdr 만 못 찾는다 — .zshrc 가 아니라 .zshenv 였던 이유"

categories:
  - Linux
tags:
  - Herdr
  - Tailscale
  - SSH
  - zsh

date: 2026-09-08
---

## 한 줄로

`~/.local/bin` 을 `.zshrc` 에 넣었는데도 원격 도구가 바이너리를 못 찾았다.
**비대화식(non-interactive) SSH 에서 zsh 는 `.zshrc` 를 읽지 않는다.** `.zshenv` 에 넣어야 했다.

"내가 SSH 로 직접 들어가면 멀쩡한데 프로그램만 못 찾는다"는 상태가 여기서 나온다.
내가 들어갈 때는 대화형 셸이라 `.zshrc` 가 읽히고, 프로그램이 붙을 때는 안 읽히기 때문이다.

---

## 무엇을 하려던 것인가

Herdr(코딩 에이전트용 터미널 멀티플렉서) 0.9.0 에 다중 머신(SSH) 통합이 들어왔다.
로컬 세션과 SSH 로 붙은 원격 머신을 한 창에서 관리하는 기능이다.

이걸 Tailscale 로 연결해 둔 개인 맥미니에 붙였다.

| 항목 | 값 |
|---|---|
| 클라이언트 | 회사 맥 (macOS, arm64), Herdr 0.9.0 |
| 원격 | 개인 맥미니 (macOS, arm64) |
| 연결 | Tailscale, `active; direct` (릴레이 경유 아님) |
| 인증 | macOS 원격 로그인 + 공개키 |

한 가지 짚어둘 것 — **Tailscale 의 SSH 기능은 꺼져 있다**(`TailscaleSSHEnabled: None`).
Tailscale 은 네트워크 경로만 뚫어주고, 실제 접속은 macOS 기본 원격 로그인이 받는다.

그리고 이 편이 Herdr 에 맞다. Herdr 는 끊기면 배경에서 다시 붙는데,
그 재접속이 **비대화식**이라 비밀번호를 물어볼 창구가 없다. 키 인증이 필요하다.
(공식 문서도 passphrase 걸린 키는 `ssh-add` 를 먼저 하라고 적어 뒀다. 같은 이유다.)

---

## 설치 — 첫 줄 에러는 에러가 아니었다

```
$ herdr machine add <맥미니> --label "맥미니"
could not inspect the running remote herdr server on <맥미니> (session default)
before installing: could not parse remote server status JSON from ``: EOF while parsing a value at line 1 column 0
continue installing the remote herdr binary? [y/N] y
matching herdr 0.9.0 is not installed on <맥미니> (session default) for macos-aarch64.
Install the current local herdr binary to "$HOME/.local/bin/herdr"? [Y/n] y
herdr: installed remote binary to ~/.local/bin/herdr, but the remote shell does not resolve `herdr` to that path
Saved SSH machine <ID>. Remote server is ready.
```

첫 줄의 `could not parse remote server status JSON from ``` 는 빈 문자열(``` `` ```)을
JSON 으로 파싱하려다 난 것이다. **원격에 Herdr 가 아예 없어서 상태를 되돌려줄 서버가 없었다.**
그래서 바로 다음 줄에서 설치 여부를 물어본다. 정상 흐름이고, 마지막 줄도 `Remote server is ready` 다.

설치가 대화형 프롬프트로 물어보는 것도 설계다. 문서에 따르면 설치·교체는 **대화형 터미널에서만**
물어보고, 배경 연결은 절대 스스로 설치하지 않는다. 자고 있는 사이에 바이너리가 갈리지 않는다는 뜻이다.

문제는 마지막에서 두 번째 줄이다.

```
installed remote binary to ~/.local/bin/herdr, but the remote shell does not resolve `herdr` to that path
```

설치는 됐는데 **`herdr` 라는 이름으로는 해석이 안 된다.**

---

## 본론 — 왜 `.zshrc` 가 아니라 `.zshenv` 인가

Herdr 가 접속할 때와 같은 조건, 즉 비대화식으로 직접 확인해 봤다.

```
$ ssh -o BatchMode=yes <맥미니> 'echo $PATH; command -v herdr'
PATH=/usr/local/bin:/System/Cryptexes/App/usr/bin:/usr/bin:/bin:/usr/sbin:/sbin:...
which: NOT_FOUND
```

`~/.local/bin` 이 PATH 에 없다. 그런데 `.zshrc` 에는 넣어 뒀다.

### zsh 는 셸 종류마다 다른 파일을 읽는다

zsh 가 시작할 때 무엇을 읽는지는 셸이 **어떤 종류로 켜졌는가**에 달려 있다.

| 셸 종류 | 언제 | `.zshenv` | `.zshrc` |
|---|---|---|---|
| 로그인 + 대화형 | 터미널을 열고 SSH 로 들어감 | 읽음 | 읽음 |
| 비로그인 + 대화형 | 셸 안에서 `zsh` 를 또 실행 | 읽음 | 읽음 |
| **비대화식** | **`ssh 호스트 '명령'`, 스크립트, 프로그램의 원격 실행** | **읽음** | **안 읽음** |

`.zshrc` 는 이름 그대로 **rc — 대화형 셸 설정**이다.
프롬프트 모양, 별칭, 자동완성처럼 사람이 앞에 앉아 있을 때만 의미가 있는 것들의 자리다.
사람이 없는 비대화식 셸에서는 읽을 이유가 없으니 zsh 가 건너뛴다.

`.zshenv` 는 **env — 환경변수**다. 어떤 종류로 켜지든 항상 읽힌다.
PATH 는 프롬프트와 달리 사람이 있든 없든 필요하므로 원래 여기 있어야 했다.

### 이게 만드는 증상

이 차이가 특히 헷갈리는 이유는 **사람이 확인하는 경로와 프로그램이 쓰는 경로가 다르기** 때문이다.

- 내가 `ssh <맥미니>` 로 들어가서 `herdr --version` → **된다.** 대화형이라 `.zshrc` 가 읽혔다.
- Herdr 가 배경에서 붙어 명령을 실행 → **못 찾는다.** 비대화식이라 안 읽혔다.

들어가서 확인해 보면 멀쩡하니 "설정은 맞는데 프로그램이 이상하다"로 결론이 나기 쉽다.
확인 자체를 같은 조건에서 해야 보인다. 그래서 위에서 `ssh -o BatchMode=yes <호스트> '명령'` 형태로 쟀다.

### 조치

맥미니에서 한 줄이다.

```
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshenv
```

검증은 다시 **같은 비대화식 조건**으로 했다.

```
which: /Users/<user>/.local/bin/herdr
ver: herdr 0.9.0
```

---

## 그런데 왜 연결은 처음부터 됐나

경고가 떴는데도 `Remote server is ready` 였고, 실제로 원격 세션이 붙었다.

Herdr 가 머신 프로필에 **절대경로**를 기억해 두고 그걸로 실행하기 때문이다.
`~/.local/bin/herdr` 를 통째로 알고 있으면 PATH 탐색이 필요 없다.

즉 이 경고는 **"지금 안 된다"가 아니라 "이름으로 찾는 경로만 안 된다"** 는 뜻이다.
당장은 굴러가지만, 원격 셸에서 `herdr` 를 직접 치거나 절대경로가 아닌 방식으로 부르는
자리에서는 걸린다. 고쳐두는 게 맞다.

---

## 세션 공유 실험 — 서버는 둘, 세션은 하나

붙이고 나니 궁금해졌다. **SSH 로 붙은 Herdr 와 맥미니에서 직접 켠 Herdr 는 같은 것인가?**

맥미니 서버에 `공유테스트` 라는 워크스페이스를 만들고 양쪽에서 조회해 봤다.

| 어디서 조회 | 결과 |
|---|---|
| 맥미니 서버 | `['~', '공유테스트']` — 보임 |
| 회사 맥(로컬) 서버 | 기존 12개 그대로. `공유테스트` 없음 |

**서버가 두 개이고 각자 자기 것만 갖는다.** 합쳐지는 게 아니다.

ID 도 서로 겹친다. 양쪽 다 `w2` 가 있는데 서로 다른 워크스페이스다.
공식 문서도 못을 박아 뒀다 — *"Workspace, tab, pane IDs … are scoped to one server"*.
`w2` 라는 ID 는 어느 서버에서 부르는가에 따라 다른 것을 가리킨다.

그럼 무엇이 공유되는가. **세션이다.**

맥미니의 `default` 세션에 회사 맥이 창을 하나 더 붙여서 보는 구조다.
맥미니 앞에서 직접 `herdr` 를 켜도 같은 `default` 세션(같은 소켓)에 붙는다.
맥미니에서 돌리던 에이전트를 회사 맥에서 그대로 이어 보게 되는데,
정확히는 세션이 "이어지는" 게 아니라 **애초에 끊긴 적이 없다.**

0.9.0 에서 `--no-session` 모드가 삭제되고 모든 실행이 배경 서버에 붙게 된 것과 같은 방향이다.
붙는 창이 로컬이든 SSH 너머든, 세션은 서버에 남는다.

---

## 알고 있어야 할 제약

**프로필은 한 세션만 겨냥한다.** 위 출력에도 `(session default)` 가 찍혀 있다.
맥미니에서 `herdr --session 딴이름` 으로 켜면 그 세션은 회사 맥에서 안 보인다.

**CLI 는 사이드바 선택을 따라가지 않는다.** 로컬에서 `herdr workspace list` 를 치면
사이드바가 원격 머신을 보고 있어도 **로컬 것**이 나온다.
화면이 원격을 보고 있다고 명령어까지 원격으로 가지는 않는다.

여기에 실험용으로 만든 `공유테스트` 워크스페이스는 지워 원상복구했다.

---

## 정리

- 원격 도구가 바이너리를 못 찾으면 **같은 비대화식 조건으로 다시 재본다.**
  `ssh -o BatchMode=yes <호스트> 'echo $PATH; command -v <명령>'`
- zsh 에서 PATH 는 `.zshrc` 가 아니라 `.zshenv` 다. `.zshrc` 는 사람이 앞에 있을 때만 읽힌다.
- 절대경로를 기억하는 도구는 이 문제가 있어도 일단 동작한다. 경고를 무시하기 쉬운 구조다.
- 다중 머신은 서버를 합치는 게 아니라 **각 서버의 세션에 창을 더 붙이는 것**이다. ID 는 서버마다 따로 논다.
