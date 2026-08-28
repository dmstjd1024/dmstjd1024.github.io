---
title:  "사설 레지스트리(registry:2) 란? — 이름이 둘이라 클러스터가 이미지를 못 받았다"

categories:
  - Docker
tags:
  - Docker
  - Registry
  - Kubernetes
  - 폐쇄망

date: 2026-08-28
thumbnail: "/assets/img/thumbnail/docker_thumbnail.png"
card_thumbnail: "/assets/img/thumbnail/docker_card.png"
---
## 한 줄로

폐쇄망(인터넷이 끊긴 망)에서 이미지를 공급하려고 띄운 **사설 레지스트리**다.

이미지 이름은 `registry:2`. Docker 가 공식 배포하는 레지스트리 서버다.

그리고 **이 레지스트리가 담고 있는 이미지 목록에 `registry:2` 자신이 들어 있다.**
이 글은 그게 왜 필요한지에 대한 이야기다.

## 왜 필요한가

이 시스템은 인터넷이 차단된 망에서 돈다. `docker pull nginx` 가 안 된다.

그런데 [회사마다 쿠버네티스 클러스터를 하나씩 띄우는](/Kubernetes/회사마다-클러스터-하나씩-띄운다.html)
구조라, 클러스터를 만들 때마다 수십 개 이미지가 필요하다.

그래서 **서버 안에 이미지 저장소를 하나 세워두고** 거기서 받아 쓴다. 그게 `registry:2` 다.

## 어떻게 띄우나

```bash
docker run -d \
  --restart=always \
  --name kind-registry \
  -p "0.0.0.0:5001:5000" \
  -e REGISTRY_STORAGE_DELETE_ENABLED=true \
  registry:2
```

옵션 네 개가 각각 이유가 있다.

| 옵션 | 이유 |
|---|---|
| `--restart=always` | 서버가 재부팅돼도 살아나야 한다. 이게 죽으면 **모든 클러스터가 이미지를 못 받는다** |
| `-p 0.0.0.0:5001:5000` | 컨테이너 안은 5000, 밖은 **5001** |
| `REGISTRY_STORAGE_DELETE_ENABLED` | 이미지 **삭제 허용**. 기본값은 삭제 불가다 |
| 이름 `kind-registry` | 클러스터가 이 이름으로 찾는다 |

포트가 5000 이 아니라 **5001** 인 게 눈에 띈다. macOS 에서 5000 번은 AirPlay 가 쓰는 등
충돌이 잦아, 관례적으로 한 칸 옆으로 비켜 쓴다.

`REGISTRY_STORAGE_DELETE_ENABLED=true` 도 기본값이 아니다. Docker Registry 는 **기본적으로
삭제를 막아둔다.** 실수로 이미지를 지우면 복구할 방법이 없기 때문이다. 여기서는 디스크가
한정적이라 정리할 수 있게 열어뒀다.

## 클러스터 밖에 있다

헷갈리기 쉬운 지점이다. 레지스트리는 **쿠버네티스 안이 아니라 그냥 도커 컨테이너**다.

```
[ 서버 ]
   ├─ kind-registry            ← 도커 컨테이너 (쿠버 밖)
   ├─ 회사A-control-plane      ← 도커 컨테이너 안의 쿠버 클러스터
   ├─ 회사B-control-plane
   └─ 회사C-control-plane
```

클러스터가 회사마다 따로 뜨는데 **레지스트리는 하나뿐**이다. 같은 이미지를 회사 수만큼
중복 저장할 이유가 없다.

대신 클러스터 안에서 이 컨테이너에 닿을 수 있어야 한다. 그래서 같은 도커 네트워크에 붙인다.

```bash
docker network connect kind kind-registry
```

## 이름이 두 개다

클러스터 안쪽에서는 주소가 달라진다. 여기가 이 구조에서 가장 헷갈리는 대목이다.

| 어디서 | 주소 |
|---|---|
| 서버(호스트)에서 | `localhost:5001` |
| **클러스터 안에서** | `kind-registry:5000` |

이미지 이름에는 `localhost:5001/...` 이 박혀 있는데, 정작 그 이미지를 받는 건 클러스터
안의 파드다. 파드 입장에서 `localhost` 는 **자기 자신**이니 그대로면 못 찾는다.

그래서 클러스터 안 컨테이너 런타임(containerd)에 매핑을 심는다.

```
localhost:5001  →  kind-registry:5000
```

**HTTP 평문 접근을 허용**하는 설정도 같이 들어간다. 원래 레지스트리는 HTTPS 를 요구하는데,
사설망이고 인증서를 발급할 방법도 마땅치 않아 예외로 열어둔 것이다. 외부에 노출되지 않는다는
전제 위에서만 성립하는 선택이다.

## 겪은 이슈 — 이름을 잘못 알려줘서 이미지를 못 받았다

앞 절의 "이름이 두 개" 가 **실제로 사고를 냈다.**

```
fix(cluster): containerd registry 설정 보완 및 mirrors 추가   (2026-04-19)
```

무엇이 틀렸는지는 변경 내용에 그대로 남아 있다.

```diff
- server = "http://localhost:5001"
+ server = "http://kind-registry:5000"
```

**클러스터 안에서 `localhost:5001` 을 가리키고 있었다.**

이게 왜 안 되는지는 `localhost` 의 의미를 생각하면 명확하다. `localhost` 는 절대 주소가
아니라 **"말하는 사람 자신"** 이다. 서버에서 치면 서버이고, 클러스터 노드 안에서 해석하면
**그 노드 자신**이다. 레지스트리는 노드 안이 아니라 옆 컨테이너에 있으니 닿을 리가 없다.

```
[ 서버 ]              localhost:5001  →  레지스트리 ✅
[ 클러스터 노드 ]      localhost:5001  →  노드 자신   ❌
```

같은 문자열이 어디서 해석되느냐에 따라 다른 곳을 가리킨다. **이미지 이름에 박힌
`localhost:5001` 은 그대로 두되, 노드 안에서는 `kind-registry:5000` 으로 바꿔 부르도록**
매핑을 고친 것이 해결책이다.

`mirrors` 설정을 함께 넣은 것도 같은 맥락이다. 두 이름을 **모두** 등록해서 어느 쪽으로
불러도 같은 곳에 닿게 했다.

```toml
[plugins."...".registry.mirrors."localhost:5001"]
  endpoint = ["http://kind-registry:5000"]
[plugins."...".registry.mirrors."kind-registry:5000"]
  endpoint = ["http://kind-registry:5000"]
```

### 고치면서 검증을 붙였다

이 커밋에서 더 눈여겨볼 건 **확인 절차를 새로 넣었다**는 점이다.

```bash
# 3. hosts.toml 기록 검증
if ! docker exec ... cat .../hosts.toml | grep -q "kind-registry"; then
  echo "❌ hosts.toml write failed"; exit 1
fi

# 4. Kind 노드에서 레지스트리 접근 확인
if ! docker exec ... curl -sf "http://kind-registry:5000/v2/_catalog" > /dev/null; then
  echo "❌ Cannot reach kind-registry:5000 from Kind node"; exit 1
fi
```

**설정 파일을 썼다는 것과 그게 실제로 동작한다는 것은 다르다.** 그래서 두 가지를 나눠서
확인한다 — 파일이 제대로 쓰였는지, 그리고 **노드에서 실제로 레지스트리에 닿는지**.

이 검증이 없으면 증상이 한참 뒤에 나타난다. 클러스터는 정상으로 만들어지고, 나중에 파드가
뜰 때 `ImagePullBackOff` 로 실패한다. 그때는 원인이 레지스트리 설정이라는 걸 알기 어렵다.

**설치 시점에 확인할 수 있는 것은 설치 시점에 확인하는 게 낫다.** 실패를 뒤로 미룰수록
원인과 증상의 거리가 멀어진다.

## 자기 자신을 담고 있다

이미지 시딩(레지스트리 채우기) 목록의 마지막 줄이 이렇다.

```bash
["registry:2"]="registry:2"
```

**레지스트리가 자기 자신의 이미지를 담고 있다.**

처음 보면 이상한데, 폐쇄망을 생각하면 필연이다. 레지스트리 컨테이너가 죽어서 다시 만들어야
할 때, `registry:2` 이미지를 **어디서 받나?** 인터넷은 없고, 그걸 갖고 있어야 할 레지스트리는
지금 죽어 있다.

닭과 달걀 문제다. 해법은 두 가지다.

1. 이미지를 **오프라인 번들**(`docker save` 로 만든 tar)로 따로 보관한다
2. 서버의 로컬 도커에 이미지가 **캐시로 남아 있길** 기대한다

실제로 이 프로젝트는 1번을 했다. 번들 스크립트가 `registry:2` 와 `kindest/node` 를
따로 챙긴다. **레지스트리를 재건할 씨앗은 레지스트리 밖에 있어야 한다.**

## 담기는 것은 38개

시딩 스크립트에 원본 → 로컬 매핑이 38개 정의돼 있다.

| 묶음 | 예 |
|---|---|
| Fabric | `fabric-peer`, `fabric-ca`, `fabric-orderer` 등 6개 |
| Besu | `hyperledger/besu`, `quorum-k8s-hooks` |
| 모니터링 | `grafana`, `prometheus`, `alertmanager`, `node-exporter` … |
| Istio | `operator`, `pilot`, `proxyv2` |
| 체인코드 빌드 | `node:18-alpine`, `golang:1.21-alpine`, `eclipse-temurin` |
| 기타 | `couchdb`, `postgres`, `busybox`, **`registry:2`** |

원본 출처가 제각각인 게 흥미롭다 — `gcr.io`, `quay.io`, `ghcr.io`, `registry.k8s.io`,
Docker Hub. 이걸 전부 `localhost:5001` 아래로 **평평하게** 모은다.

즉 폐쇄망 레지스트리는 저장소인 동시에 **이름 공간을 통일하는 장치**이기도 하다.

## 여기서 걸린 것 — 목록이 두 벌인데 서로 다르다

이미지를 다루는 스크립트가 둘이다.

| 스크립트 | 역할 |
|---|---|
| `07-setup-images-to-registry.sh` | 원본에서 받아 **레지스트리에 채운다** |
| `save-images.sh` | 레지스트리에서 받아 **tar 로 백업한다** |

문제는 **두 목록이 어긋나 있다**는 점이다.

- 시딩에만 있고 백업에 없는 것 — `fabric-tools`, `fabric-ccenv`, `fabric-baseos`,
  `ingress-nginx/controller` 등
- 백업에만 있고 시딩에 없는 것 — `kube-webhook-certgen:v1.1.1`(시딩은 더 최신 태그),
  `prometheus:v2.41.0`, `kubernetesui/dashboard:v2.6.1`

즉 **백업본으로 복원해도 시딩 목록과 같은 상태가 되지 않는다.** 두 파일을 각각 손으로
관리하다 보니 벌어진 일로 보인다.

덧붙여 `fabric-ccenv` 와 `fabric-baseos` 는 시딩 목록에 있지만 **다른 어느 스크립트에서도
참조되지 않는다.** 예전에 쓰다 만 것으로 보이는데, 지금은 용량만 차지한다.

## 정리

- 폐쇄망이라 서버에 **사설 레지스트리**를 띄운다. 이미지는 `registry:2`
- 클러스터는 회사마다 따로지만 **레지스트리는 하나**를 공유한다
- 주소가 두 개다 — 호스트에서 `localhost:5001`, **클러스터 안에서 `kind-registry:5000`**.
  containerd 매핑으로 이어붙인다
- ⚠️ 이 매핑을 **틀리게 적어 사고가 났다.** 노드 안에서 `localhost` 는 노드 자신이라
  레지스트리에 닿지 않는다. `mirrors` 로 두 이름을 모두 등록해 해결
- 고치면서 **검증 두 단계**를 붙였다 — 설정 파일이 쓰였는지, 노드에서 실제로 닿는지.
  **설치 시점에 확인 안 하면 나중에 `ImagePullBackOff` 로 뒤늦게 터진다**
- `REGISTRY_STORAGE_DELETE_ENABLED=true` 는 기본값이 아니다. 디스크가 한정적이라 연 것
- **레지스트리가 자기 자신을 담고 있다.** 재건할 씨앗은 오프라인 번들로 따로 보관해야 한다
- ⚠️ **시딩 목록과 백업 목록이 어긋나 있다.** 백업으로 복원해도 원래 상태가 안 된다
- ⚠️ `fabric-ccenv`·`fabric-baseos` 는 **아무 데서도 안 쓰인다**

같이 읽을 글:
[회사마다 클러스터 하나씩 띄운다](/Kubernetes/회사마다-클러스터-하나씩-띄운다.html) ·
[couchdb — 피어마다 붙는 상태 DB](/Docker/couchdb-피어마다-붙는-상태-db.html) ·
[busybox — 1초 살고 사라지는 컨테이너](/Docker/busybox-1초-살고-사라지는-컨테이너.html)
