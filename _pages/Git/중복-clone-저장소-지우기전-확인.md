---
title:  "git status 가 깨끗하다고 지워도 되는 게 아니었다"

categories:
  - Git
tags:
  - Git
  - 브랜치

date: 2026-09-09
thumbnail: "/assets/img/thumbnail/github_thumbnail.png"
card_thumbnail: "/assets/img/thumbnail/github_card.png"
---
## 같은 저장소가 로컬에 두 벌 있었다

여러 머신 설정을 만지다가 블로그 저장소를 열었는데, 같은 저장소가 두 곳에 clone 돼 있었다.

```
/Users/<user>/dmstjd1024.github.io                    마지막 커밋 2026-09-07 17:50
/Users/<user>/eunseong-project/dmstjd1024.github.io   마지막 커밋 2026-09-08 14:36
```

둘 다 `origin` 이 같은 GitHub 저장소다. 실제로 쓰는 건 뒤쪽이었고, 앞쪽은 언제 만들었는지
기억나지 않았다. 그래서 앞쪽을 지우기로 했다.

## 지우기 전에 본 것 — 깨끗했다

먼저 상태를 봤다.

```
$ git status -sb
## main...origin/main
?? assets/.DS_Store
```

`main` 은 원격과 같고, 미추적 파일은 macOS 가 만든 `.DS_Store` 하나뿐이다. 여기까지만 보면
지워도 되는 폴더다.

## 그런데 원격에 없는 커밋이 다섯 개 있었다

지우기 전에 한 번 더 봤다. 이번엔 브랜치 전체에서 원격에 없는 커밋을 셌다.

```
$ git log --branches --not --remotes --oneline
f71affe chore: 익명화 (5/5)
372ae9c chore: 익명화 (4/5)
17a7d40 chore: 익명화 (3/5)
f6f8ceb chore: 익명화 (2/5)
3580454 WIP: 익명화 작업 (재정리 예정)
```

다섯 개가 나왔다.

### 왜 갈렸나

`git status` 는 **현재 체크아웃된 브랜치만** 본다. 워킹 디렉터리와 인덱스, 그리고 지금
올라타 있는 브랜치와 그 업스트림의 차이를 말해줄 뿐이다. 체크아웃돼 있지 않은 다른 브랜치에
쌓인 커밋은 그 관찰 범위 밖이다.

당시 체크아웃된 건 `main` 이었고, `main` 은 실제로 원격과 같았다. 그래서 깨끗하다고 나왔다.
커밋들은 다른 브랜치에 있었다.

```
$ git branch -vv
* main       [origin/main]
  redact-a   [origin/redact-a: ahead 1]
  redact-b   [origin/redact-b: ahead 1]
  redact-c   [origin/redact-c: ahead 1]
  redact-d   [origin/redact-d: ahead 1]
  redact-e   [origin/redact-e: ahead 2]
```

브랜치 다섯 개에 하나씩, 하나는 둘씩 흩어져 있었다.

`git log --branches --not --remotes` 는 범위가 다르다. `--branches` 로 로컬 브랜치 전부를
모으고, `--not --remotes` 로 원격 추적 브랜치에서 닿을 수 있는 것을 빼므로, **어느 브랜치에
있든 원격에 없는 커밋**이 남는다.

## 다른 clone 에 같은 커밋이 있는지 확인

같은 저장소를 두 벌 갖고 있으니 저쪽에 이미 있을 수도 있다. 있으면 그냥 지워도 된다.
커밋 해시로 직접 조회했다.

```
$ cd /Users/<user>/eunseong-project/dmstjd1024.github.io
$ for c in f71affe 372ae9c 17a7d40 f6f8ceb 3580454; do
    git cat-file -e "$c^{commit}" 2>/dev/null && echo "$c 있음" || echo "$c 없음"
  done
f71affe 없음
372ae9c 없음
17a7d40 없음
f6f8ceb 없음
3580454 없음
```

다섯 개 다 없었다. 그 폴더를 지웠으면 복구할 수 있는 곳이 없는 상태였다.

`git cat-file -e <해시>^{commit}` 은 그 해시의 커밋 객체가 이 저장소에 있는지만 확인하고
종료 코드로 답한다. 브랜치 이름이 서로 달라도 되고, 로그를 눈으로 훑을 필요도 없다.

## 하필 내용이 이랬다

다섯 개가 전부 같은 갈래였다. 공개 블로그에서 회사 정보를 걷어내는 익명화 작업이고,
하나에는 `WIP: 재정리 예정` 이 붙어 있다.

(이 글에서는 브랜치 이름과 커밋 메시지를 일반화해 적었다. 무엇을 가렸는지가 그대로
드러나면 가린 의미가 없기 때문이다. 명령과 절차는 실제 그대로다.)

끝나지 않은 채로 로컬에만 있던 작업이었다.

## 푸시하고, 대조하고, 그 다음에 지웠다

브랜치를 원격에 올렸다.

```
$ for b in redact-a redact-b redact-c redact-d redact-e; do
    git push origin "$b"
  done
 * [new branch]      redact-a -> redact-a
 * [new branch]      redact-b -> redact-b
 * [new branch]      redact-c -> redact-c
 * [new branch]      redact-d -> redact-d
 * [new branch]      redact-e -> redact-e
```

`push` 출력이 성공이라고 해서 그대로 믿지 않고, 원격에 다시 물어 해시를 대조했다.

```
$ git ls-remote origin "refs/heads/redact-a"
3580454...   로컬 3580454 와 일치
```

다섯 개 전부 일치했다. 그리고 미푸시 커밋을 다시 셌다.

```
$ git log --branches --not --remotes --oneline
(출력 없음)
```

0건이 되고 나서 폴더를 지웠다. 61MB 였다.

## clone 을 지우기 전에 볼 것

다음에 같은 상황이 오면 이 순서로 본다.

**1. 원격에 없는 커밋이 있는지 — 브랜치 전체 기준으로 본다**

```
git log --branches --not --remotes --oneline
```

`git status` 로는 부족하다. 그건 지금 체크아웃된 브랜치만 본다.

**2. 어느 브랜치에 있는지 확인한다**

```
git branch -vv
```

`ahead N` 이 붙은 브랜치가 대상이다.

**3. 다른 clone 에 이미 있는지 해시로 조회한다**

```
git cat-file -e <해시>^{commit} && echo 있음 || echo 없음
```

있으면 지워도 되고, 없으면 아래로 간다.

**4. 원격에 올린다**

```
git push origin <브랜치>
```

**5. 원격에서 다시 조회해 해시를 대조한다**

```
git ls-remote origin "refs/heads/<브랜치>"
```

push 출력이 아니라 원격의 답을 근거로 삼는다.

**6. 미푸시 커밋이 0건인 것을 확인하고 지운다**

```
git log --branches --not --remotes --oneline
```

여기서 아무것도 안 나와야 지운다.

덧붙여, 스태시와 태그는 위 명령에 안 잡힌다. `git stash list` 와 `git tag` 도 같이 본다.
