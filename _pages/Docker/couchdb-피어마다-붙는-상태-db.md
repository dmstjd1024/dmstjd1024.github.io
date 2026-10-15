---
title:  "CouchDB 를 고른 대가는 피어마다 컨테이너 하나였다"
subtitle: "Fabric 상태 DB 를 LevelDB 대신 CouchDB 로"
description: "Fabric 상태 DB 를 LevelDB 대신 CouchDB 로"
categories:
  - Docker
tags:
  - Docker
  - CouchDB
  - Hyperledger Fabric
  - Kubernetes

date: 2026-08-28
thumbnail: "/assets/img/thumbnail/docker_thumbnail.png"
card_thumbnail: "/assets/img/thumbnail/docker_card.png"
---
## 한 줄로

Hyperledger Fabric 피어가 **현재 상태를 저장하는 DB** 다.

기본값이 아니다. 일부러 골랐고, 그 대가로 **피어 수만큼 DB 가 늘어난다.**

## 블록체인인데 DB 가 왜 필요한가

헷갈리기 쉬운 지점이라 먼저 푼다.

블록체인은 **거래 기록(원장)** 을 이어붙인 사슬이다. "A가 B에게 10을 보냈다" 같은 기록이
순서대로 쌓인다. 그런데 여기서 **"지금 A의 잔액은 얼마인가"** 를 알려면 처음부터 전부
다시 계산해야 한다.

그래서 Fabric 은 **현재 상태만 따로 저장하는 DB** 를 둔다. 이걸 **상태 DB**(state database)
라고 부른다.

```
원장(블록)      : 거래 기록 전체. 절대 안 바뀜
상태 DB         : "지금 값은 이것" 만. 계속 갱신됨
```

상태 DB 가 날아가도 원장으로 다시 만들 수 있다. **원본이 아니라 캐시에 가깝다.**

## LevelDB 대신 CouchDB 를 골랐다

Fabric 은 상태 DB 를 두 가지 중에 고를 수 있다.

| | LevelDB (기본) | **CouchDB** |
|---|---|---|
| 형태 | 피어에 내장된 키-값 저장소 | **별도 컨테이너로 뜨는 문서 DB** |
| 조회 | 키로만 찾을 수 있음 | **값의 내용으로도 검색 가능** |
| 컨테이너 | 없음 (피어 안) | **피어마다 하나씩 추가** |

이 프로젝트는 CouchDB 를 골랐다.

```bash
kubectl hlf peer create --statedb=couchdb \
  --couchdb-repository=${COUCHDB_IMAGE} \
  ...
```

`--statedb=couchdb` 가 그 선택이다. 안 적으면 LevelDB 로 간다.

## 왜 골랐나 — 리치 쿼리

CouchDB 를 쓰는 이유는 사실상 하나다. **값의 내용으로 검색**할 수 있기 때문이다.
Fabric 문서에서는 이걸 **리치 쿼리**(rich query)라고 부른다.

LevelDB 는 키-값 저장소라 "키가 `car-001` 인 것" 은 찾아도, **"소유자가 홍길동인 자동차
전부"** 는 못 찾는다. 값 안을 들여다볼 수 없기 때문이다.

CouchDB 는 값을 JSON 문서로 저장해서, 그 안의 필드로 조회할 수 있다. 체인코드에서
이런 질의가 가능해진다.

```json
{"selector": {"owner": "홍길동"}}
```

**앱을 만들 때 이 차이가 크다.** 목록 화면, 검색, 필터가 필요하면 사실상 CouchDB 를
골라야 한다. 나중에 바꾸려면 네트워크를 다시 세워야 하므로, 처음에 정해야 하는 선택이다.

## 대가 — 피어 수만큼 늘어난다

CouchDB 는 피어 안에 들어가지 않는다. **별도 컨테이너**로 뜬다. 그것도 피어마다 하나씩이다.

피어 생성이 이중 반복문 안에 있다.

```bash
for ((org=1; org<=ORG_CNT; org++)); do
  for ((peer=1; peer<=PEER_CNT; peer++)); do
    kubectl hlf peer create --statedb=couchdb ...
```

조직 × 피어 수만큼 피어가 생기고, **그 수만큼 CouchDB 도 생긴다.**

| 조직 | 피어/조직 | 피어 | **CouchDB** | 피어·DB 컨테이너 합계 |
|---:|---:|---:|---:|---:|
| 2 | 1 | 2 | 2 | 4 |
| 2 | 2 | 4 | **4** | **8** |
| 3 | 2 | 6 | **6** | **12** |

피어·DB 컨테이너 합계는 피어 수의 두 배다. 이 프로젝트의 **hlf-operator v1.9.2는 같은 피어 파드 안에
CouchDB 컨테이너를 붙이므로 파드 수는 늘지 않는다.** [회사마다 클러스터를 하나씩 띄우는](/Kubernetes/회사마다-클러스터-하나씩-띄운다.html)
구조에서 추가 컨테이너가 쓰는 자원은 회사 수만큼 늘어난다.

[모니터링 편](/Kubernetes/모니터링은-한-덩어리로-깔린다.html)에서 본 자원 제한이
왜 그렇게 빡빡한지도 여기서 이해된다. 쓸 수 있는 자원이 애초에 넉넉하지 않다.

## 저장소와 태그를 따로 받는다

CouchDB 이미지 지정이 두 군데 있지만, 저장소 주소와 태그는 구분해서 읽어야 한다.

| 어디 | 값 |
|---|---|
| 시딩 목록 | `couchdb:3.1.1` (태그 명시) |
| Fabric 배포 스크립트 | 저장소 `localhost:5001/couchdb`, 별도 태그 기본값 `3.1.1` |

**hlf-operator v1.9.2의 CLI는 `--couchdb-repository`와 `--couchdb-tag`를 따로 받는다.**
태그를 생략하면 `--couchdb-tag` 기본값인 `3.1.1`을 쓴다. 따라서 이 경우 시딩 버전과 일치한다.
저장소 인자에 태그가 없다는 이유만으로 `latest`를 사용한다고 판단하면 안 된다.

## 안 쓰는 형제가 하나 있다

시딩 목록에 이런 줄도 있다.

```bash
["gesellix/couchdb-prometheus-exporter:v30.0.0"]="couchdb-prometheus-exporter:v30.0.0"
```

CouchDB 지표를 Prometheus 로 보내주는 **exporter** 다. 그런데 **다른 어느 스크립트에서도
참조되지 않는다.**

CouchDB 를 모니터링하려던 시도의 흔적으로 보인다. [Prometheus 편](/Kubernetes/모니터링은-한-덩어리로-깔린다.html)
에서 본 모니터링 스택은 이 exporter 를 설치하지 않는다.

즉 **CouchDB 전용 지표는 지금 수집하지 않는다.** 피어마다 DB 컨테이너가 추가되지만 전용 exporter는 깔리지 않는다.

## 정리

- CouchDB 는 Fabric 피어의 **상태 DB** — "지금 값" 만 담는다. 원장이 아니라 캐시에 가깝다
- 기본값(LevelDB)이 아니라 **일부러 고른 것**이다. 이유는 **값 내용으로 검색**(리치 쿼리)
- 네트워크를 세운 뒤엔 바꾸기 어려우므로 **처음에 정해야 하는 선택**이다
- 대가는 **피어마다 컨테이너 하나 추가** — hlf-operator v1.9.2는 같은 파드에 붙이므로 파드 수는 그대로다
- CLI는 저장소와 태그를 따로 받는다. v1.9.2의 태그 기본값은 `3.1.1`로 시딩과 일치한다
- ⚠️ `couchdb-prometheus-exporter` 는 시딩만 되고 **안 쓰인다.** CouchDB 는 관측 밖이다

같이 읽을 글:
[registry:2 — 자기 자신을 담고 있는 레지스트리](/Docker/registry-2-자기-자신을-담고-있는-레지스트리.html) ·
[Fabric 네트워크는 어떻게 생기나](/BlockChain/Infra/fabric-네트워크는-어떻게-생기나.html) ·
[postgres — Explorer 전용 DB](/Docker/postgres-explorer-전용-db.html)
