---
title:  "Istio 를 깔지만 트래픽은 안 보낸다 — 스키마가 요구해서 남은 필드"

categories:
  - Kubernetes
tags:
  - Kubernetes
  - Istio
  - Hyperledger Fabric
  - 폐쇄망

date: 2026-08-28
thumbnail: "/assets/img/thumbnail/kubernetes_thumbnail.png"
card_thumbnail: "/assets/img/thumbnail/kubernetes_card.png"
---
## 한 줄로

**Istio 를 설치는 하는데, 실제 트래픽은 Istio 를 통과하지 않는다.**

Fabric 배포 스크립트 주석이 그걸 명시하고 있다.

```
# Orderer/Peer의 istio.port 설정 (Kind 클러스터에서는 Istio 대신 직접 포트 사용)
```

이 글은 왜 이런 상태가 됐는지에 대한 이야기다.

## Istio 가 왜 후보에 올랐나

Istio 는 **서비스 메시**다. 서비스 사이 통신을 대신 처리해주는 층이라고 보면 된다.
암호화, 라우팅, 관측을 애플리케이션 코드를 안 고치고 얻을 수 있다.

Fabric 에서 이게 필요해 보이는 지점이 있다. **오더러**(트랜잭션 순서를 정하는 노드)를
클러스터 밖에 노출해야 하는데, 프로토콜이 gRPC 이고 TLS 를 쓴다.

실제로 이 프로젝트가 쓰는 **hlf-operator** 는 Istio 를 전제로 설계돼 있다. 오더러와 피어
CRD 에 `istio` 필드가 아예 들어 있다.

```bash
kubectl hlf ordnode create ... --istio-port=7050
```

그래서 클러스터를 만들 때 Istio 를 같이 깐다.

## 그런데 트래픽은 안 지나간다

문제는 이 시스템이 **kind** 위에서 돈다는 점이다. kind 는 도커 컨테이너 안에 쿠버네티스를
띄우는 방식이라, 외부 노출을 **호스트 포트 매핑**으로 해결한다.

[클러스터 글](/Kubernetes/회사마다-클러스터-하나씩-띄운다.html)에서 봤듯 회사마다 포트를
10개 떼어주고, 컨테이너를 만들 때 그 포트를 호스트에 직접 연결해둔다.

즉 **밖으로 내보내는 통로가 이미 있다.** Istio 게이트웨이를 한 겹 더 태울 이유가 없다.

그래서 `--istio-port=7050` 의 `7050` 은 Istio 포트가 아니라 **오더러의 gRPC 포트 그 자체**다.
스크립트 주석이 그걸 설명한다.

```
# 7050: orderer GRPC 포트, 채널 config에 이 포트가 포함되어 peer가 orderer에 연결
```

## 그러면 왜 값을 채우나

지울 수가 없기 때문이다.

CRD(사용자 정의 리소스)에는 **스키마**가 있다. 오퍼레이터가 정한 필드 구조를 따라야 하고,
필수 필드를 비우면 리소스 생성 자체가 거부된다.

`istio` 필드가 그런 경우다. 실제로 Istio 를 쓰지 않아도 **필드는 채워야 한다.** 그래서
오더러의 실제 포트를 그 자리에 넣었다.

게다가 이 값이 그냥 버려지지도 않는다. 스크립트에 이런 주석이 있다.

```
# spec.istio.hosts + port: addanchorpeer가 anchor peer 주소를 여기서 읽음
```

**앵커 피어**(조직을 대표해 다른 조직과 통신하는 피어) 주소를 등록할 때, 오퍼레이터가
이 `istio` 필드를 읽어 주소를 만든다. 이름은 Istio 인데 **실제로는 일반 주소 설정 필드로
쓰이고 있다.**

## 그럼 Istio 는 아무것도 안 하나

설치는 `minimal` 프로파일로 한다.

```yaml
profile: minimal
components:
  pilot:        # 설정 배포 담당
    enabled: true
  ingressGateways:
    - name: istio-ingressgateway
      enabled: true
```

`minimal` 은 **pilot 과 게이트웨이만** 깐다. 사이드카 자동 주입 같은 무거운 기능은 빠진다.
자원도 제한해뒀다 — pilot 이 CPU 500m, 메모리 512Mi 상한이다.

즉 **최소한으로 깔아두고 실제로는 거의 안 쓰는 상태**다. 오퍼레이터가 Istio 리소스를
만들려 할 때 실패하지 않도록 받쳐주는 역할에 가깝다.

## 폐쇄망 설치 방식

Istio 는 다른 컴포넌트와 설치 방식이 다르다. Helm 이 아니라 전용 CLI 를 쓴다.

```bash
ISTIO_IMAGE="localhost:${LOCAL_REGISTRY_PORT}/istio"
istioctl operator init --hub "${ISTIO_IMAGE}" --tag="${ISTIO_TAG}"
```

`--hub` 가 이미지를 받아올 **저장소 주소**다. 기본값은 Docker Hub 인데, 폐쇄망이라
로컬 레지스트리로 바꾼다.

Helm 의 `--set image.repository=...` 를 컴포넌트마다 반복하는 것과 달리, Istio 는
**hub 하나만 바꾸면** 하위 이미지가 전부 그 아래에서 해결된다. 이 점은 편하다.

대신 `istioctl` 이라는 바이너리가 서버에 미리 있어야 한다.

```bash
if ! command -v istioctl &> /dev/null; then
  echo "❌ istioctl command not found"
```

없으면 명확히 알려준다.

## 여기서 걸린 것 — 게이트웨이 설정 실패가 묻힌다

게이트웨이 설정을 적용하는 대목이다.

```bash
kubectl apply -f "${ISTIO_GATEWAY_CONFIG}" || {
  echo "⚠️  Failed to apply istio-gateway config (non-critical)"
}
```

**"non-critical" 이라고 스스로 적어뒀다.** 실제로 트래픽이 Istio 를 안 지나가니 맞는 판단이다.

다만 이게 **"지금은 안 쓰니까 괜찮다"** 는 뜻인지, **"원래 안 중요하다"** 는 뜻인지 코드만
봐서는 구분이 안 된다. 나중에 Istio 로 트래픽을 태우기로 결정하면, 이 줄은 조용히 위험해진다.

설치 자체도 상위 스크립트에서 `|| { … continuing }` 로 감싸여 있어서, **Istio 가 통째로
안 깔려도 클러스터는 `ACTIVE`** 로 기록된다. 지금 구조에서는 실제로 별 문제가 없는데,
그게 오히려 **문제를 오래 숨긴다.**

## 남는 생각

이건 결함이라기보다 **설계 흔적**에 가깝다.

오퍼레이터가 Istio 를 전제하니 깔긴 해야 하고, kind 의 포트 매핑이 이미 노출을 해결하니
실제로 태울 이유는 없다. 그 사이에서 나온 절충이다.

다만 **"왜 깔려 있는가" 가 코드 어디에도 정리돼 있지 않다.** 주석 두 줄이 흩어져 있을 뿐이다.
새로 온 사람은 Istio 가 트래픽 경로에 있다고 오해하기 쉽고, 그 상태로 디버깅을 시작하면
한참을 헤맨다.

**쓰지 않는 것을 지우지 못할 때는, 왜 남겨두는지를 적어두는 게 유일한 방어다.**

## 정리

- Istio 를 깔지만 **실제 트래픽은 통과하지 않는다.** kind 의 호스트 포트 매핑이 이미
  노출을 해결하기 때문
- `--istio-port=7050` 의 값은 Istio 포트가 아니라 **오더러의 gRPC 포트**다
- 그래도 필드를 채우는 이유는 **CRD 스키마가 요구**하고, 앵커 피어 주소 계산에 쓰이기 때문
- 설치는 `minimal` 프로파일 — **pilot 과 게이트웨이만**, 자원도 제한
- 폐쇄망 대응은 **`--hub` 하나**로 끝난다. Helm 보다 간결한 지점
- ⚠️ 게이트웨이 설정 실패가 "non-critical" 로 묻힌다. **지금은 맞지만, Istio 를 실제로
  쓰기 시작하면 조용히 위험해지는 줄이다**

같이 읽을 글:
[회사마다 클러스터 하나씩 띄운다](/Kubernetes/회사마다-클러스터-하나씩-띄운다.html) ·
[Fabric 네트워크는 어떻게 생기나](/BlockChain/Infra/fabric-네트워크는-어떻게-생기나.html) ·
[Ingress 로 포트 3개를 1개로 줄였다](/Kubernetes/ingress로-포트-3개를-1개로-줄였다.html)
