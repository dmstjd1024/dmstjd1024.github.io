---
title: "도커 교과서 2장"

categories:
 - Docker
tags:
 - docker

date: 2025-05-28
thumbnail: "/assets/img/thumbnail/docker_thumbnail.png"
---

# 도커의 기본적인 사용법
### 컨테이너 실행
- 컨테이너로 애플리케이션 실행 명령어
- 애플리케이션은 미리 도커로 실행되도록 패킹돼 누구나 사용되도록 공유된 것
```docker
docker container run diamol/ch02-hello-diamol
```
애플리케이션을 컨테이너에서 실행할 수 있도록 패키징(빌드) -> 다른사람들과 공유(공유) -> 패키지 내려받은 사람이 컨테이너를 통해 애플리케이션 실행(실행)
### 컨테이너란 무엇인가?
- 애플리케이션이 한 컴퓨팅 환경에서 다른 컴퓨팅 환경으로 빠르고 안정적으로 실행될 수 있도록 코드와 모든 종속성을 패키징 하는 표준 소프트웨어 단위입니다. 
가상머신 : 호스트 컴퓨터의 운영체제를 공유하지 않음
 컨테이너 : 호스트 컴퓨터의 운영체제 공유
### 컨테이너를 원격 컴퓨터처럼 사용하기

`--tty` : 터미널 세션을 통해 컨테이너 조작
`--ìnteractive` : 컨테이너에 접속된 상태
`docker container run —interactive —ty diamol/base`

#### 실행중인 모든 컨테이너 정보
`docker container ls`

#### 컨테이너에서 실행중인 프로세스 목록
`docker container top [컨테이너 ID prefix]`

#### 컨테이너에서 수집된 모든 로그 출력
`docker container logs [컨테이너 ID prefix]`

#### 컨테이너의 상세한 정보
`docker container inspect [컨테이너 ID prefix]`

### 컨테이너 사용해 웹사이트 호스팅하기
#### 상태 상관없이 모든 컨테이너의 목록 확인
`docker container ls —all`

컨테이너 실행하고 백그라운드에서 계속 동작하게 하려면
#### 간단한 웹사이트 호스팅
`docker container run —detach —publish 8088:80 diamol/ch02-hello-diamol-web`
- `--detach` : 컨테이너 백그라운드에서 실행
- `--publish` : 컨테이너의 포트를 호스트 컴퓨터에 공개

#### 컨테이너의 상태 확인
`docker container stats [컨테이너 ID prefix]`

### 도커가 컨테이너를 실행하는 원리
#### 도커엔진
- 도커의 관리 기능을 맡은 컴포넌트 -> 이미지 pull, 도커 리소스 만드는 일도 담당
- API 통해 맡은 기능 수행 (도커 API)
- 도커 명령행 인터페이스 : 도커 API의 클라이언트 (docker 호출하도록 도와주는 CLI)
