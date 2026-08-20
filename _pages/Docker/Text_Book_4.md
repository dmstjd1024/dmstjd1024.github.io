---
title: "도커 교과서 5장"

categories:
 - Docker
tags:
 - docker

date: 2026-08-19
thumbnail: "/assets/img/thumbnail/docker_thumbnail.png"
---

도커 허브 등 레지스트리에 이미지 공유하기
=====
-----

4장까지는 내 컴퓨터 안에서만 이미지를 만들었다.
빌드한 이미지를 다른 사람도 쓰게 하려면 **레지스트리**에 올려야 한다.

## 레지스트리, 리포지터리, 이미지 태그 다루기

세 가지 용어가 헷갈리는데, 이미지 이름 하나를 뜯어보면 정리된다.

```docker
docker.io/diamol/node:latest
```

| 조각 | 이름 | 의미 |
|---|---|---|
| `docker.io` | 레지스트리 도메인 | 이미지를 보관하는 서버. 생략하면 도커 허브(`docker.io`) |
| `diamol` | 계정 이름 | 도커 허브의 사용자/조직 계정 |
| `node` | 리포지터리 이름 | 같은 애플리케이션의 이미지들을 모아둔 저장소 |
| `latest` | 태그 | 리포지터리 안의 특정 버전. 생략하면 `latest` |

- **레지스트리(registry)**: 이미지를 보관하는 서버 (도커 허브, ECR, 하버 등)
- **리포지터리(repository)**: 레지스트리 안에서 한 애플리케이션의 이미지들을 모아둔 단위
- **태그(tag)**: 리포지터리 안의 개별 버전 이름표

즉 `이미지 참조 = 레지스트리/계정/리포지터리:태그` 구조다.
평소에 `docker pull nginx` 라고 쳐도 되는 건, 앞뒤가 생략된 것뿐이다.

## 도커 허브에 직접 빌드한 이미지 푸시하기

### 1. 로그인

```docker
docker login --username [도커 허브 계정명]
```

### 2. 이미지에 새 이름(태그) 붙이기

내가 빌드한 로컬 이미지 이름에는 계정 정보가 없다.
푸시하려면 **내 계정 이름이 포함된 참조**를 하나 더 붙여야 한다.

```docker
docker image tag image-gallery [계정명]/image-gallery:v1
```

### 태그는 복사가 아니다

`tag` 명령은 이미지를 복사하는 게 아니라 **같은 이미지에 이름표를 하나 더 다는 것**이다.
직접 확인해보면 명확하다.

```docker
docker image tag diamol/node myaccount/verify-demo:v1
docker image ls
```

```
REPOSITORY              TAG       IMAGE ID       SIZE
myaccount/verify-demo   v1        8e0eeb0a11b3   75.5MB
diamol/node             latest    8e0eeb0a11b3   75.5MB
```

**IMAGE ID가 똑같다.** 목록에는 2개로 보이고 SIZE도 각각 75.5MB로 찍히지만,
실체는 하나다. `docker system df` 로 보면 디스크 사용량이 늘지 않은 걸 알 수 있다.
(3장에서 본 이미지 레이어 이야기와 같은 맥락이다.)

### 3. 푸시

```docker
docker image push [계정명]/image-gallery:v1
```

푸시도 **레이어 단위**로 이뤄진다.
레지스트리에 이미 있는 레이어는 `Layer already exists` 로 건너뛴다.
이미지 레이어 공유가 네트워크 전송량 절약으로 이어지는 지점이다.

> 푸시 권한은 **계정 이름이 일치할 때만** 생긴다.
> 남의 계정 이름으로 태그를 달면 인증 오류가 난다.

## 나만의 도커 레지스트리 운영하기

회사 내부망처럼 도커 허브를 쓸 수 없는 환경에서는 레지스트리를 직접 띄운다.
레지스트리조차 컨테이너로 실행한다.

```docker
docker container run -d -p 5000:5000 --restart always diamol/registry
```

### ※ macOS 에서 5000번 포트가 안 열릴 때

```
docker: Error response from daemon: ports are not available:
exposing port TCP 0.0.0.0:5000 -> 127.0.0.1:0: listen tcp 0.0.0.0:5000:
bind: address already in use
```

맥에서는 **AirPlay 수신 기능(ControlCenter)이 5000번 포트를 이미 쓰고 있다.**
`lsof -nP -iTCP:5000 -sTCP:LISTEN` 로 확인할 수 있다.

해결은 둘 중 하나다.
- `시스템 설정 > 일반 > AirDrop 및 Handoff > AirPlay 수신 모드` 끄기
- 다른 포트를 쓰기 (`-p 5001:5000`)

아래 예제는 5001번을 쓴 것이다.

### 푸시하고 다시 받아보기

```docker
docker image tag diamol/node localhost:5001/gallery/ui:v1
docker image push localhost:5001/gallery/ui:v1
```

```
0a6a364b44af: Pushed
20e8cfeb051c: Pushed
6d626da635fc: Pushed
0c7669bfb3ce: Pushed
v1: digest: sha256:6467efe6481aace... size: 1158
```

로컬 이미지를 지우고 다시 받아오면, 레지스트리가 제대로 동작하는 걸 확인할 수 있다.

```docker
docker image rm localhost:5001/gallery/ui:v1
docker image pull localhost:5001/gallery/ui:v1
```

### HTTPS 문제

도커는 레지스트리에 **HTTPS로 접속하려고 한다.**
그런데 위 예제는 인증서가 없는데도 푸시가 됐다.
**`localhost` 는 도커가 예외적으로 신뢰하기 때문이다.**

도메인 이름을 쓰면 이야기가 달라진다.

```docker
docker image push registry.local:5001/gallery/ui:v1
```

```
Get "https://registry.local:5001/v2/": ...
```

에러 메시지에서 보이듯 **`https://` 로 접속을 시도**한다.
그래서 도메인으로 접근하려면 두 가지가 필요하다.

1. `hosts` 파일에 도메인 등록 (`registry.local` → `127.0.0.1`)
2. 도커 엔진에 예외 등록

```json
{
  "insecure-registries": ["registry.local:5001"]
}
```

도커 데스크톱은 `Settings > Docker Engine`, 리눅스는 `/etc/docker/daemon.json` 에
넣고 엔진을 재시작한다.

## 이미지 태그를 효율적으로 사용하기

태그에는 아무 문자열이나 넣을 수 있다. 그래서 **규칙을 정하는 것이 중요**하다.
보통 `[주.부.패치]` 형태의 버전 번호를 쓴다.

```docker
docker image tag image-gallery [계정명]/image-gallery:2.1.106
```

핵심은 **얼마나 구체적인 태그를 쓰느냐가 곧 안정성과 최신성의 트레이드오프**라는 점이다.

| 사용한 태그 | 의미 | 특징 |
|---|---|---|
| `2.1.106` | 정확히 그 빌드 | 항상 같은 이미지. 가장 안정적 |
| `2.1` | 2.1의 최신 패치 | 버그 수정은 따라감 |
| `2` | 2의 최신 부 버전 | 기능 추가까지 따라감 |
| `latest` | 그때그때 최신 | 무엇이 올지 알 수 없음 |

- 이미지를 **사용하는 쪽**은 안정성이 중요하니 구체적인 태그를 쓴다
- **운영 배포에서 `latest` 는 쓰지 않는다** — 언제 무엇으로 바뀔지 통제할 수 없다

> 2장에서 본 쿠버네티스 이미지 풀 정책도 같은 맥락이다.
> `latest` 를 쓰면 풀 정책 기본값이 `Always` 가 된다.

## 공식 이미지에서 골든 이미지로 전환하기

### 공식 이미지를 그대로 믿어도 될까

도커 허브의 이미지는 크게 세 가지로 나뉜다.

- **공식 이미지(Official Images)**: 도커가 검수하고 관리. Dockerfile이 공개돼 있음
- **인증 이미지(Verified Publisher)**: 소프트웨어 제조사가 직접 배포
- **일반 이미지**: 누구나 올린 것. 내용을 보장하지 않음

공식 이미지라도 조직의 보안 정책, 사내 인증서, 로깅 설정까지 맞춰주지는 않는다.

### 골든 이미지

그래서 **공식 이미지를 기반으로 조직 표준을 입힌 이미지**를 만들어 두고,
사내의 모든 애플리케이션이 그것을 `FROM` 으로 삼게 한다. 이를 골든 이미지라고 한다.

```docker
FROM diamol/node

LABEL maintainer="jeon-eunseong"
LABEL version="1.0.0"

# 조직 표준: 인증서, 공통 설정, 보안 패치 등을 여기서 한 번에 적용
```

이제 각 애플리케이션은 공식 이미지가 아니라 골든 이미지를 기반으로 빌드한다.
(`[계정명]` 자리에는 조직의 도커 허브 계정이나 사내 레지스트리 주소가 들어간다.)

```docker
FROM [계정명]/golden-node

CMD ["node", "/app/index.js"]
```

**장점**

- 기반 이미지의 보안 패치를 한 곳에서 적용하면 전체에 반영된다
- 조직 표준(라벨, 인증서, 설정)이 강제된다
- 어떤 이미지가 무엇을 기반으로 하는지 추적할 수 있다

`LABEL` 로 넣은 메타데이터는 아래 명령으로 확인한다.

```docker
docker image inspect --format='{{.Config.Labels}}' golden-node:1.0.0
```

```
map[maintainer:jeon-eunseong version:1.0.0]
```

라벨이 없는 이미지라면 `map[]` 이 출력된다.

## 정리

- 이미지 참조는 `레지스트리/계정/리포지터리:태그` 구조다
- `docker image tag` 는 복사가 아니라 **이름표를 더 다는 것** (IMAGE ID가 같다)
- 푸시는 레이어 단위라, 이미 있는 레이어는 다시 올리지 않는다
- 사설 레지스트리는 `localhost` 면 그냥 되지만, **도메인을 쓰면 HTTPS 설정이 필요**하다
- 태그가 구체적일수록 안정적이고, `latest` 는 운영에서 쓰지 않는다
- 공식 이미지를 그대로 쓰기보다 **골든 이미지**로 조직 표준을 한 번에 관리한다
