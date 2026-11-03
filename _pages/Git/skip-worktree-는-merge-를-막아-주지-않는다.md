---
title:  "skip-worktree 는 merge 를 막아 주지 않는다"
subtitle: "dotfiles 자동 동기화가 stash 를 쌓던 원인은 install.sh 가 심링크된 공유 settings.json 을 실행할 때마다 고치던 것이었다"
description: "dotfiles 자동 동기화가 stash 를 쌓던 원인은 install.sh 가 심링크된 공유 settings.json 을 실행할 때마다 고치던 것이었다"

categories:
  - Git
tags:
  - Git
  - skip-worktree
  - dotfiles
  - Claude Code
  - stash

date: 2026-11-03
---
## 한 줄로

skip-worktree 는 `git status` 에서만 로컬 변경을 가린다. merge 할 때는 git 이 그 변경을 그대로 보고 `local changes would be overwritten` 으로 거부한다. dotfiles 자동 동기화에 stash 가 계속 쌓이던 이유가 이것이었다. 근본 원인은 `install.sh` 가 실행될 때마다 공유 설정 파일을 고치던 것이었다.

## skip-worktree 가 가리는 범위

skip-worktree 는 git 이 특정 파일의 로컬 변경을 못 본 척하게 만드는 플래그다.

핵심은 "못 본 척"이 어디까지냐다. 가려지는 곳은 `git status` 하나다. 원격에서 같은 파일이 바뀌어 merge 해야 하면 git 은 로컬 변경을 그대로 본다. 그리고 그 변경을 덮어쓰지 않으려고 merge 를 거부한다.

text
local changes would be overwritten


이 동작은 격리 레포를 따로 만들어 재현해 확인했다.

## 처음 세운 전제가 틀렸다

처음에는 "skip-worktree 를 걸었는데 왜 stash 가 생기나"를 물었다. skip-worktree 가 걸린 파일이면 로컬 변경이 동기화를 방해하지 않을 거라고 생각했기 때문이다.

실제로는 이렇게 흘러간다.

1. 자동 동기화가 merge 를 시도한다.
2. skip-worktree 가 걸린 파일에 로컬 변경이 있어서 merge 가 `local changes would be overwritten` 으로 거부된다.
3. 무인 AI 해소가 지시받은 대로 로컬 변경을 stash 에 넣는다.

stash 가 생기는 것 자체는 설계대로 돌아간 결과다. 그러니 찾아야 할 것은 "왜 stash 가 생기나"가 아니었다. "누가 그 파일을 계속 바꾸나"였다.

## 진짜 원인: install.sh 가 공유본을 고치고 있었다

`install.sh` 에 `claude plugins enable -s user` 가 들어 있었다. 이 명령은 Claude Code 사용자 설정 파일인 `settings.json` 을 고친다. 그런데 이 파일은 dotfiles 레포의 공유본을 가리키는 심링크(원본을 가리키는 바로가기 파일)다. 그래서 install.sh 가 돌 때마다 공유본이 바뀌었다.

게다가 이 쓰기는 아무 효과도 없었다. `company-mac` 프로파일이 `document-skills` 를 `false` 로 덮어쓰고 있었기 때문이다. `company-pro` 에는 `true` 로 되어 있다. 이 플러그인을 도입한 커밋 `9557c64` 도 프로파일마다 켠다고 적어 두었다. 그러니 `company-mac` 의 `false` 는 잘못 적힌 값이다.

정리하면 이렇다. install.sh 는 효과도 없는 설정을 공유 파일에 매번 쓰고 있었다. 그 쓰기가 로컬 변경으로 남아 merge 를 막았다. merge 가 막히면 무인 AI 해소가 stash 를 하나 더 만들었다.

## 무인 동기화 기록에 남은 흔적

회사 머신에서 13:10 에 돈 무인 동기화 기록을 보면 이 흐름이 그대로 드러난다.

- `scripts/weekly-report*.sh` 의 미커밋 변경은 stash 했다가 다시 꺼내 되돌렸다.
- `settings.json` 에 자동으로 들어간 값(herdr hook, `model: "opus"`, `document-skills`)은 `stash@{0}` 에 넣어 두었다.
- 그 상태에서 `f9a969e` 까지 fast-forward 했다.

## 고친 것 (`a4ede58`)

- `company-mac/settings.local.json`: `false` → `true`
- `install.sh`: `plugins enable -s user` 를 지우고 설치 단계만 남겼다
- `CLAUDE.md`: "skip-worktree 는 status 만 가린다, merge 는 거부한다"를 적어 두었다

검증은 install.sh 를 두 번 연달아 실행하는 방식으로 했다. 두 번 다 공유본이 바뀌지 않았다. 드리프트(공유본과 로컬 값이 어긋난 상태) 키는 2개에서 1개로 줄었다. 이 커밋은 push 했다.

## 남은 하나: herdr 가 넣는 절대경로 훅

남은 드리프트 키 하나는 herdr 가 넣는 절대경로 훅이다.

로컬 전용 값이니 `settings.local.json` 으로 옮기면 될 것처럼 보인다. 하지만 실제로 해 보니 훅만 `settings.local.json` 으로 옮기면 실행되지 않았다. `advisorModel`·`theme` 같은 값은 local 에 있어도 적용된다. 반면 훅 배열은 두 파일 사이에서 병합되지 않는다.

그래서 원격에서 `settings.json` 이 바뀌는 날에는 stash 가 다시 생길 수 있다. 그래도 pull 은 정상으로 끝나므로, 피해는 stash 가 쌓이는 것에 그친다.

선택지는 세 가지였다. 파일을 미추적으로 바꾸기, herdr 연동 끊기, 그대로 두기다. 결국 그대로 두기로 했고, 지금은 손댈 것이 없다.

## 정리

- skip-worktree 는 `git status` 만 가린다. merge 는 로컬 변경을 보고 거부한다.
- 자동 동기화가 stash 를 쌓는 것은 증상이다. 원인은 그 파일에 계속 쓰는 쪽에 있다. 이번에는 심링크를 거쳐 공유본을 고치던 `install.sh` 였다.
- 훅처럼 병합되지 않는 설정은 `settings.local.json` 으로 옮겨도 동작하지 않는다. 그런 값은 공유본에 남아 드리프트가 된다.
