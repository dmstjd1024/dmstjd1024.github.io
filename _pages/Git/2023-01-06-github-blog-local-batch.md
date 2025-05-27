---
title:  "깃허브 블로그 로컬로 돌리기"

categories:
  - git
tags:
  - git
  - github
  - jekyll

date: 2023-01-06
thumbnail: "/assets/img/thumbnail/github_thumbnail.png"
---

# 깃허브 블로그 실행 파일
---
 처음엔 남들 github.io에 개발 관련 블로그가 많이 보이길래 저건 어떻게 만들지 하며
  찾아보니깐 깃허브로 무료 호스팅을 제공하는거라 한다.  
  나는 이런 글을 쓰는 것이 좀 어색하지만 차츰 글의 양을 늘려보도록 하겠다.  
  
  
  일단 jekyll 설치, 실행 방식은 구글링을 통해서 쉽게 접할 수 있다.  
  근데 ruby를 켜서 실행할 때 마다 일일히 루비 명령 프롬프트를 켜서 진행을 해야한다.
  
  ## 실행 파일 생성
  
  일단 메모장 파일을 생성하고 다음과 같은 코드를 입력한다.

## 코드
```sh
cd C:\Ruby26-x64\bin\setrbvars.cmd
call setrbvars.cmd
cd 클론해온 리포지터리경로\리포지터리 이름
bundle exec jekyll serve
```
  
## 다른 이름으로 저장
  <img src="/img/posts/github-blog-local-batch/save.png" width="800" height="400">

이렇게 저장하면 bat 파일이 생성된다.

  <img src="/img/posts/github-blog-local-batch/bat.png">
  
실행하면 http://localhost:4000 포트에서 돌아가고 있는 것을 확인할 수 있다.
