---
title:  "busybox — 1초 살고 사라지는 컨테이너가 하는 일"

categories:
  - Docker
tags:
  - Docker
  - Kubernetes
  - busybox
  - Hyperledger Besu

date: 2026-08-28
thumbnail: "/assets/img/thumbnail/docker_thumbnail.png"
card_thumbnail: "/assets/img/thumbnail/docker_card.png"
---
## 한 줄로

Besu 노드가 뜨기 **직전에** 잠깐 떠서 **폴더 주인을 바꾸고 사라지는** 컨테이너다.

하는 일은 명령 한 줄이다.

```bash
chown -R 1000:1000 /data
```

이 한 줄 때문에 이미지 하나가 필요하다.

## 초기화 컨테이너란

쿠버네티스에는 **초기화 컨테이너**(init container)라는 게 있다. 본 컨테이너가 뜨기 전에
먼저 실행되고, **끝나야 본 컨테이너가 시작**된다.

```
[ 파드 ]
  1. busybox      → chown 실행 → 종료
  2. besu         → 그제서야 시작
```

준비 작업 전용이다. 실패하면 본 컨테이너는 아예 안 뜬다.

Besu 차트에서는 이렇게 정의돼 있다.

```yaml
initContainers:
  - name: volume-permission-besu
    image: "localhost:5001/busybox:latest"
    command: ["sh", "-c", "chown -R 1000:1000 /data"]
    securityContext:
      runAsUser: 0
```

## 무슨 문제를 푸나

Besu 는 블록 데이터를 디스크에 쓴다. 그 디스크는 쿠버네티스가 붙여주는 **볼륨**이다.

문제는 **볼륨이 처음 만들어질 때 주인이 root** 라는 점이다. 그런데 Besu 프로세스는
보안상 root 가 아닌 **일반 사용자(UID 1000)** 로 돈다.

```
볼륨 주인 : root (UID 0)
Besu 실행 : UID 1000
결과      : 쓰기 권한 없음 → 기동 실패
```

그래서 **root 권한을 가진 컨테이너가 먼저 떠서** 폴더 주인을 1000 으로 바꿔준다.
그게 busybox 가 하는 전부다.

`runAsUser: 0` 이 붙은 이유가 여기 있다. **이 컨테이너만 root 로 돈다.** 본 컨테이너는
계속 일반 사용자다. 필요한 순간에만 권한을 빌려 쓰는 셈이다.

## 왜 하필 busybox 인가

`chown` 하나 돌리는 데 왜 이미지가 필요한가 싶지만, 컨테이너는 **뭐라도 이미지가 있어야**
뜬다. 그러면 가장 작은 걸 고르는 게 맞다.

busybox 는 리눅스 기본 명령 수백 개를 **하나의 실행 파일**에 몰아넣은 도구다. 원래 임베디드
기기용으로 만들어졌고, 이미지 크기가 **수 MB 수준**이다.

| 이미지 | 대략 크기 |
|---|---|
| busybox | **~5MB** |
| alpine | ~8MB |
| ubuntu | ~80MB |

`chown` 만 쓸 건데 ubuntu 를 받으면 80MB 를 낭비한다. 게다가 폐쇄망이라 **그 용량이 그대로
레지스트리 저장 공간**이다.

## 조건부로 뜬다

이 컨테이너는 항상 뜨지 않는다. 차트에 조건이 걸려 있다.

```yaml
{{- if has .Values.cluster.provider .Values.volumePermissionsFix }}
```

`volumePermissionsFix` 목록에 현재 provider 가 있을 때만 넣는다.

```yaml
volumePermissionsFix:
  - local
  - aws
```

그리고 이 프로젝트 설정은 `provider: local` 이다. **목록에 있으니 실제로 뜬다.**

`azure` 가 빠진 게 흥미롭다. 클라우드마다 볼륨을 붙일 때 권한을 처리하는 방식이 달라서,
어떤 환경에서는 이 우회가 필요 없다.

차트 주석에 원인 링크까지 달려 있다.

```
# fix for minikube and PVC's only writable as root
# https://github.com/kubernetes/minikube/issues/1990
```

즉 이건 **로컬 쿠버네티스 환경의 알려진 문제를 우회**하는 코드다. kind 도 같은 계열이라
그대로 해당된다.

## 태그가 latest 다

한 가지 걸리는 점.

```yaml
busybox:
  repository: localhost:5001/busybox
  tag: latest
```

**`latest` 로 고정돼 있다.** 다른 이미지들은 대부분 버전이 박혀 있는데 여기만 다르다.

폐쇄망이라 위험이 크진 않다. 레지스트리에 올라간 그 이미지가 계속 쓰이고, 밖에서 새 버전이
들어올 경로가 없기 때문이다.

다만 **레지스트리를 다시 채울 때** 그 시점의 최신 busybox 가 들어온다. 그래서 재구축
전후로 이미지가 조용히 바뀔 수 있다. `chown` 만 쓰니 실제로 깨질 일은 거의 없지만,
**"버전을 고정한다" 는 원칙에서 예외**인 것은 맞다.

## 정리

- 본 컨테이너 전에 잠깐 떠서 **볼륨 폴더 주인을 바꾸는** 초기화 컨테이너다
- 이유는 **볼륨 초기 주인이 root, Besu 실행 계정은 UID 1000** 이라 쓰기가 안 되기 때문
- `runAsUser: 0` — **이 컨테이너만 root** 로 돈다. 필요한 순간에만 권한을 빌린다
- busybox 를 고른 이유는 **가장 작아서**(~5MB). 폐쇄망에서는 용량이 곧 레지스트리 비용이다
- `provider` 가 `local`/`aws` 일 때만 뜬다 — **로컬 쿠버네티스의 알려진 문제 우회**다
- ⚠️ 태그가 **`latest`** 다. 레지스트리 재구축 시 조용히 다른 버전이 들어올 수 있다

같이 읽을 글:
[registry:2 — 자기 자신을 담고 있는 레지스트리](/Docker/registry-2-자기-자신을-담고-있는-레지스트리.html) ·
[Besu 네트워크는 어떻게 생기나](/BlockChain/Infra/besu-네트워크는-어떻게-생기나.html) ·
[couchdb — 피어마다 붙는 상태 DB](/Docker/couchdb-피어마다-붙는-상태-db.html)
