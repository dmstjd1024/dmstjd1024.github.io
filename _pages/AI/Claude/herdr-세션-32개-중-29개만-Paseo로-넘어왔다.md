---
title:  "herdr 세션 32개 중 29개만 Paseo로 넘어왔다"
subtitle: "데몬 네 대를 Tailscale IP에서만 듣게 묶었다. 남은 3개는 모두 Codex 세션이었다"
description: "데몬 네 대를 Tailscale IP에서만 듣게 묶었다. 남은 3개는 모두 Codex 세션이었다"

categories:
  - AI
tags:
  - Paseo
  - herdr
  - Tailscale
  - Codex
  - Claude Code

date: 2026-11-25
---
## 한 줄로

여러 머신의 에이전트 세션을 관리하던 도구를 herdr 에서 Paseo 로 바꿨다. 네 대의 Paseo 데몬이 Tailscale IP 에서만 접속을 받게 설정했고, herdr 세션 32개 중 29개를 옮겼다. 못 옮긴 3개는 모두 Codex 세션이다. 2개는 herdr pane 이 아직 열고 있어서 거부됐고, 1개는 세션 ID 가 없었다.

## Paseo 와 herdr

두 도구 모두 데몬(머신에서 계속 떠 있는 백그라운드 프로세스)과 그 데몬에 붙는 클라이언트로 나뉜다. 그래서 herdr 에서 쓰던 방식을 Paseo 에서도 거의 그대로 쓸 수 있다.

Paseo 는 에이전트가 CLI 로 다른 에이전트를 띄우는 오케스트레이션(여러 에이전트에게 일을 나눠 맡기는 것)을 공식 문서에서 다룬다. 다만 Claude 는 터미널 화면(TUI)이 아니라 Agent SDK 로 돌린다. 이 점은 아래 「감수할 점」에서 다시 나온다.

## 후보 넷 중 Paseo 를 고른 이유

후보는 t3code, herdr+collie, Paseo, Orca 넷이었다. Opus 로 다시 조사했을 때는 Orca 가 1순위로 나왔다. Orca 는 실제 `claude` TUI 를 띄우기 때문에 mod·훅·CLAUDE.md 가 그대로 살아 있다.

선택을 좁힌 조건은 두 가지다.

- Claude Remote Control 은 쓰지 않는다.
- Claude 말고 Codex·OpenCode 도 함께 쓰고 싶다.

마지막에는 t3code 와 Paseo 중 하나를 골라야 했고, **Paseo** 로 정했다. 데몬·클라이언트 구조가 herdr 와 같고, 에이전트 오케스트레이션을 공식 문서에서 다룬다는 점이 컸다.

t3code 를 뺀 이유는 네 가지다.

- 권한 기본값이 `Full access` 다.
- 텔레메트리(사용 데이터 수집) 논란이 있었다.
- 오케스트레이션 V2 에 동시 실행 상한이 없다.
- 병렬 위임 버그가 아직 열려 있다.

감수할 점도 두 가지다.

- Paseo 는 Claude 를 Agent SDK 로 돌린다. 그래서 TUI 화면에 붙는 mod(tessera 등)는 보이지 않을 가능성이 크다.
- 사실상 1인 프로젝트다.

## 데몬 네 대를 Tailscale 로 묶기

Tailscale 은 내 기기끼리만 통하는 사설망을 만들어 주는 VPN 이다. 네 대 모두 아래처럼 맞췄다.

- 데몬은 각 머신의 Tailscale IP 에서만 듣는다.
- 포트는 6767 이고 SSL 은 끈다.
- 비밀번호는 맥미니의 해시를 복사했다. 그래서 네 대의 비밀번호가 같다.

| 머신 | 한 일 |
|---|---|
| 맥미니 | 설정 파일 `config.json` 의 기존 `listen` 값을 그대로 둠 |
| 회사 맥 | `listen` 을 `127.0.0.1` 에서 Tailscale IP 로 바꾸고 비밀번호 설정 |
| 맥북프로 | LaunchAgent `sh.paseo.daemon.plist` 로 로그인할 때 자동 시작 |
| 맥북에어 | `brew install --cask paseo` 뒤 같은 설정과 LaunchAgent 적용 |

LaunchAgent 는 macOS 가 사용자 로그인 때 프로그램을 띄워 주는 설정이다. 원래 설정 파일은 `config.json.bak-20261125` 로 백업했다.

### localhost 로 붙으면 1006 으로 끊긴다

같은 머신에서 `localhost` 로 접속하면 아래 오류가 난다.

```text
Transport closed (code 1006)
```

데몬이 Tailscale IP 에서만 듣고 있으니 `localhost` 로 들어오는 접속은 받지 않는다. `0.0.0.0` 으로 열면 이 오류는 사라진다. 하지만 같은 와이파이처럼 Tailscale 밖에서도 접속할 수 있게 되므로 바꾸지 않았다.

다른 머신의 앱에서 붙을 때도 같다. 앱의 Host 칸에는 접속할 데몬의 Tailscale IP 를 넣어야 한다. 예를 들어 맥북프로에서 맥미니로 붙으려면 맥미니의 Tailscale IP 를 넣는다.

## herdr 세션 옮기기

32개 중 29개를 Paseo 로 가져왔다.

| 머신 | 가져온 세션 |
|---|---|
| 맥미니 | 17 / 19 |
| 회사 맥 | 7 / 8 |
| 맥북프로 | 5 / 5 |

같은 폴더를 쓰던 워크스페이스는 하나로 합쳤고, 빈 워크스페이스는 보관 처리했다.

### 넘어오지 않은 3개

- **Codex 2개:** herdr pane 에 아직 열려 있어서 아래 오류로 거부됐다. 한 세션에 쓰는 쪽은 하나만 허용되기 때문이다.

```text
already has an active writer
```

- **auto-trading-v2 의 Codex 1개:** 세션 ID 가 없어서 가져올 수 없었다.

이전에 쓴 스크립트는 `herdr_sessions2paseo.py` 다. 임시 폴더에 있어서 지워질 수 있다. 가져온 세션에는 라벨 `herdr_session=<ID>` 를 붙이고, 이 라벨이 있는 세션은 다시 돌릴 때 건너뛴다. 그래서 pane 을 닫은 뒤 스크립트를 다시 돌려도 이미 옮긴 세션이 중복으로 생기지 않는다.

### 목록의 `closed` 는 보관이 아니다

Paseo 세션 목록의 `closed` 는 보관됐다는 뜻이 아니다. 프로세스가 꺼져 있다는 뜻이다. 실제로 `closed` 세션을 열어 보면 `Archived: false` 로 나온다. 보관된 세션은 하나뿐이었다.

## 아직 조심할 것

- **Claude 세션이 양쪽에 다 살아 있다.** 가져온 Claude 세션은 herdr 에도 남아 있다. 두 곳에서 번갈아 쓰면 대화가 꼬이므로 세션마다 한쪽에서만 이어 쓴다.
- **TUI mod 가 안 보일 수 있다.** Agent SDK 로 돌리기 때문이다. Orca 를 고르지 않으면서 감수한 부분이다.
- **유지보수 위험.** 사실상 1인 프로젝트다.
