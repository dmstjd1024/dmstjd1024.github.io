---
title: "Alias 명령어 처리"

categories:
  - linux
tags:
  - linux
  - ubuntu

date: 2025-07-06
thumbnail: "/assets/img/thumbnail/linux_thumbnail.jpg"
---

## Alias 명령어 처리
bash 접근
```shell
nano ~/.bashrc
```
alias 명령어 추가
```bash
alias log="tail -f /{프로젝트 경로}/logs/{로그파일명}.log"
```