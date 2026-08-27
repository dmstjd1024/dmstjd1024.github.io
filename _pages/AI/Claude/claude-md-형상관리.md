---
title:  "CLAUDE.md 를 git 으로 관리하기 — 설정 파일이 내 것이 아닐 때"

categories:
  - AI
tags:
  - AI
  - Claude Code
  - dotfiles
  - 개발환경

date: 2026-08-27
thumbnail: "/assets/img/thumbnail/github_thumbnail.png"
card_thumbnail: "/assets/img/thumbnail/github_card.png"
---
## 왜 git 에 넣나

맥 4대(회사 2 · 개인 2)를 오간다. 한쪽에서 고친 규칙이 다른 쪽에 없으면 같은 지시를 두 번
해야 한다. 그래서 저장소 하나를 진실 공급원으로 두고 각 머신이 **심링크**(원본을 가리키는
바로가기 파일)로 그 파일을 본다.

```
~/.claude/CLAUDE.md  →  ~/dotfiles/claude/CLAUDE.md
~/.claude/skills/*   →  ~/dotfiles/claude/skills/*
```

`install.sh` 609줄이 이 연결을 만든다. 지금 커밋 256개가 쌓였다.

여기까지는 흔한 dotfiles 구성이다. **문제는 그다음이었다.**

## 설정 파일이 내 것이 아니었다

`settings.json` 을 저장소에 넣었더니 매일 `pull` 이 충돌로 막혔다. 원인이 셋이었고, 셋 다
**나 아닌 것들이 그 파일을 고치고 있었다.**

| 누가 | 무엇을 쓰나 |
|---|---|
| 외부 도구 | 머신 로컬 절대경로(`/Users/...`)가 박힌 훅을 자동 주입 |
| Claude Code 자신 | `theme`·`editorMode` 같은 UI 상태를 되받아 씀 |
| `git config --global` | `~/.gitconfig` 가 심링크라 공유 파일에 `[user]` 블록을 씀 |

세 번째가 특히 고약하다. `~/.gitconfig` 를 저장소 파일로 심링크해뒀는데,
`git config --global user.email ...` 을 한 번 치면 **회사 이메일이 공유 파일에 박힌다.**
그 상태로 개인 머신에 퍼지면 곤란하다.

## skip-worktree 로 흡수한다

해법은 "고치지 못하게" 가 아니라 **"고쳐도 git 이 안 보게"** 였다.

```bash
for _swt in claude/settings.json git/.gitconfig; do
  git -C "$DOTFILES" update-index --skip-worktree "$_swt"
done
```

`install.sh` 주석에 이유가 적혀 있다.

```
skip-worktree 로 로컬 변경만 무시한다
(파일은 계속 트래킹되므로 다른 머신은 정상적으로 최신본을 받는다).
```

이게 핵심이다. **파일은 여전히 저장소에 있어서 다른 머신은 최신본을 받는다.** 다만 이
머신에서 생긴 로컬 변경만 git 이 무시한다. 자동 주입은 흡수되고 동기화는 살아 있다.

주석에 함정도 같이 적어뒀다.

```
주의: 이 파일을 의도적으로 수정해 커밋하려면 먼저 플래그를 풀어야 한다.
  git update-index --no-skip-worktree claude/settings.json
```

플래그를 걸어두면 **내가 고친 것도 안 보인다.** `git status` 가 깨끗한데 파일은 바뀌어
있는 상태가 되므로, 의도적 수정 전에는 풀어야 한다.

### 그럼 진짜 설정값은 어디에 두나

`settings.json` 을 그렇게 봉인하면 확정값은 어디 쓰나. **프로파일별 로컬 파일로 망명시켰다.**

```
~/.claude/settings.local.json
  → dotfiles/claude/profiles/<프로파일>/settings.local.json
```

이쪽은 `skip-worktree` 대상이 아니다. deep-merge 로 공유 파일을 이기므로, 앱이 공유 파일에
다시 뭘 써도 실제 동작은 흔들리지 않는다.

즉 같은 자동 주입이라도 **노이즈와 의미 있는 변경을 구분**한 것이다.

## pull 만으로는 부족하다

두 번째로 배운 것. **파일 내용이 최신이어도 설정이 적용되지 않는 경우가 있다.**

| 대상 | pull 로 전파되나 |
|---|---|
| 파일 내용 (`CLAUDE.md`) | 된다 |
| 심볼릭 링크 | **안 된다** — 링크는 내용이 아니다 |
| `skip-worktree` 플래그 | **안 된다** — 인덱스에 있고 커밋 대상이 아니다 |
| LaunchAgent 등록 주기 | **안 된다** — launchd 가 들고 있다 |

"최신 파일을 받았다" 와 "설정이 적용됐다" 는 다른 사건이다. 그래서 pull 이 성공하면
`install.sh` 를 자동으로 실행해 **시스템 상태까지** 맞춘다.

이 구분에서 파생된 문제들(자기 자신을 죽이는 스크립트, TCC 팝업, API 키 유출)은
[별도 글](/Infra/맥-4대-설정-동기화-자동화.html)에 따로 정리했다.

## 문서에 목록을 적지 않는다

마지막으로 하나. 처음엔 README 에 "어떤 파일이 어디로 심링크되는지" 표를 만들어뒀다.
그걸 지웠고, 지운 이유를 커밋에 남겼다.

```
심링크 표 2개: install.sh 의 link 호출이 원본이라 표는 중복이었고,
스크립트가 바뀌면 문서만 조용히 낡는다. 포인터로 대체.
```

대신 이렇게 바꿨다.

```
생성되는 심링크의 전체 목록은 install.sh 의 link 호출을 읽는다.
여기에 표로 옮겨두면 스크립트가 바뀔 때 조용히 어긋난다.
```

**진실이 두 곳에 있으면 한쪽은 반드시 낡는다.** 그리고 낡은 쪽이 문서일 때가 더 위험하다.
코드는 안 돌면 티가 나지만 문서는 조용히 틀린 채로 남는다.

## 정리

- 저장소 하나 + 심링크로 맥 4대가 같은 `CLAUDE.md` 를 본다
- `settings.json` 은 **외부 도구·Claude 자신·git config** 셋이 함께 더럽힌다
- 해법은 `skip-worktree` — 파일은 트래킹하되 로컬 변경만 무시한다
- 확정값은 프로파일별 `settings.local.json` 으로 망명시킨다 (deep-merge 로 이긴다)
- **pull 은 파일 내용만 옮긴다.** 심링크·플래그·등록 주기는 `install.sh` 재실행이 필요하다
- 문서에 목록을 복사하지 않는다. 포인터만 남긴다

같이 읽을 글:
[CLAUDE.md 에 무엇을 썼나](/AI/Claude/claude-md에-무엇을-썼나.html) ·
[pull 은 됐는데 설정이 반만 적용된다](/Infra/맥-4대-설정-동기화-자동화.html)
