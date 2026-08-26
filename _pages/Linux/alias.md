---
title: "Alias 명령어 처리"

categories:
  - Linux
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

<div class="diagram" role="img" aria-label="alias 가 실행 전에 원래 명령으로 펼쳐지는 과정">
{% include diagrams/alias--expansion.svg %}
</div>