---
title: "도커 교과서 3장"

categories:
 - Docker
tags:
  - Docker

date: 2025-05-28
thumbnail: "/assets/img/thumbnail/docker_thumbnail.png"
---
## 도커 이미지 만들기

## 도커 허브에 공유된 이미지 사용하기
**web-ping** 어플리케이션 이미지 pull 명령어
`docker image pull diamol/ch03-web-ping`

도커 이미지를 다운받을 때 각각의 파일을 이미지 레이어 라고 부른다.

### 환경변수
도커 컨테이너도 별도의 환경변수를 가질 수 있다.
컨테이너의 호스트명, IP 주소처럼 Docker 가 부여해준다.

#### 환경변수를 사용한 docker 명령어

```docker
docker rm -f web-ping
docker container run --env TARGET=google.com diamol/ch03-web-ping
# google 도메인을 타겟으로 요청 보내는 명령어
```

## Dockerfile 작성하기
web-ping 애플리케이션 Dockerfile 스크립트
```docker
FROM diamol/node -- 이미지 시작점 (web-ping 어플리케이션 실행위한 런타임 Node.js)

ENV TARGET="도메인" -- 환경 변수 값을 지정하기 위한 인스크럭션
ENV METHOD="HEAD"
ENV INTERVAL="3000"

WORKDIR /web-ping -- 해당 디렉터리를 작업 디렉토리로 지정
COPY app.js . -- 로컬 파일 시스템의 파일 혹은 디렉터리를 컨테이너 이미지로 복사하는 인스트럭션

CMD ["node", "/web-ping/app.js"] -- 컨테이너가 시작될 때 실행할 명령어를 지정하는 인스트럭션
```

## 컨테이너 이미지 빌드하기
이미지 빌드를 위해선, 이미지 이름, 파일 경로 추가 지정해줘야함
```docker
docker image build --tag web-ping .
-- tag 옵션은 이미지 이름을 지정하는 옵션
-- .은 현재 디렉터리에서 Dockerfile을 찾겠다는 의미
```
※문제 발생 시, 도커 엔진 -> 현재 작업 디렉토리 -> build 명령어 정확한지 확인

이미지 목록 확인
```docker
docker image ls 'w*' -- w로 시작하는 이미지 목록
```

## 도커 이미지와 이미지 레이어 이해하기

```docker
#이미지 히스토리 확인하기
docker image history web-ping
```
- 도커 이미지는 이미지 레이어가 모인 논리적 대상
- 레이어는 도커 엔진의 캐시에 물리적으로 저장된 파일
- 이미지 레이어는 여러 이미지와 컨테이너에서 공유

docker 에서는 이미지가 비슷한 용량을 가진 것으로 보이지만, 
Node.js 런타임을 포함한 이미지가 런타임을 공유하였을 때, 
각 Image의 실제 용량은 `image ls`로 호출한 SIZE 값아랑 다르다. 
(`system df`로 확인 가능)

따라서 공유되는 레이어는 수정할 수 없어야 한다. (읽기전용으로 구현)

<div class="diagram" role="img" aria-label="여러 이미지가 레이어를 공유하는 구조">
{% include diagrams/docker2--layer-share.svg %}
</div>

## 이미지 레이어 캐시를 이요한 Dockerfile 스크립트 최적화
 
```docker
# 이미지의 파일을 수정 후 다시 빌드 시, 새로운 이미지 레이어 생성.
docker image build -t web-ping:v2 .
```
- Docker 스크립트 인스트럭션은 각 하나의 이미지 레이어와 1:1 연결
- 결과가 이전과 같다면 이전 캐시된 레이어 사용
따라서 잘 수정하지 않는 인스트럭션이 앞으로 오도록 작성하는 것이 좋다.

<div class="diagram" role="img" aria-label="인스트럭션 순서에 따른 캐시 재사용 차이">
{% include diagrams/docker2--layer-cache.svg %}
</div>

#### 최적화 한 스크립트 (핵심)

```docker
FROM diamol/node 

CMD ["node", "/web-ping/app.js"] 

ENV TARGET="도메인"
    METHOD="HEAD"
    INTERVAL="3000"

WORKDIR /web-ping
COPY app.js . ## 현재 명령어 빼고 모든 레이어를 캐시에서 재사용
```