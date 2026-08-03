---
title:  "오픈소스 오퍼레이터 버그를 CRD 스키마 패치로 우회하기"

categories:
  - AI
tags:
  - AI
  - Claude Code
  - Kubernetes
  - Hyperledger Fabric

date: 2026-05-08
thumbnail: "/assets/img/thumbnail/sample.png"
---

## 문제: 체인코드 상태가 FAILED에서 안 나온다

이 플랫폼에서 체인코드를 배포하면 Kubernetes에 `FabricChaincode`라는 커스텀 리소스가 만들어진다. hlf-operator가 이 리소스를 보고 실제 체인코드 pod를 띄운다.

그런데 배포가 실제로는 잘 됐는데도 `kubectl get fabricchaincodes`의 STATUS가 **FAILED로 고착**됐다. 한 번 FAILED가 되면 다시는 안 바뀐다. 애플리케이션은 이 상태를 읽어 사용자에게 보여주므로, 정상 동작하는 체인코드가 화면에서는 실패로 표시됐다.

## 원인: 오퍼레이터가 자기 스키마를 못 지킨다

hlf-operator v1.9.2의 문제였다. CRD 정의에는 `status` 하위에 `conditions`와 `message`가 **required**로 선언돼 있다. 그런데 오퍼레이터가 status를 업데이트할 때 이 필드들을 빠뜨리고 보낸다.

결과는 이렇게 흘러간다.

```
오퍼레이터가 status 업데이트 시도
  → conditions/message 누락
  → API 서버가 스키마 validation 거부
  → status 업데이트 실패
  → 오퍼레이터가 이걸 에러로 판단해 FAILED 기록 시도
  → 그 기록도 같은 이유로 실패
  → STATUS는 FAILED에 머문 채 영원히 갱신 불가
```

상태를 갱신하는 경로 자체가 막혀 있으니 어떤 값으로도 빠져나올 수 없다. 스스로 만든 스키마를 스스로 못 지키는 상황이다.

## 선택지를 따져봤다

우리 코드가 아니므로 고칠 수 없다. 세 가지 선택지가 있었다.

| 선택지 | 장점 | 단점 |
|---|---|---|
| 포크해서 패치 | 근본 수정, 상류 기여 가능 | Go 빌드 파이프라인·이미지 레지스트리 필요, 폐쇄망에서 부담. 업스트림 추적 비용이 영구히 발생 |
| 버전 다운그레이드 | 간단 | 이 버전에서만 되는 다른 기능을 잃을 수 있고, 옛 버전에 다른 버그가 있는지 모름 |
| CRD 스키마 패치 | 설치 스크립트 몇 줄, 오퍼레이터 이미지 그대로 | 스키마를 느슨하게 만듦, 업그레이드 시 다시 적용 필요 |

포크는 이 환경에서 비용이 컸다. 폐쇄망이라 커스텀 이미지를 빌드해 밀어 넣는 파이프라인을 새로 만들어야 하고, 그 이후로 업스트림 릴리스마다 리베이스를 관리해야 한다. 버그 하나에 대한 대가로는 과했다.

버전 다운그레이드는 검증 비용이 문제였다. 이 버그가 없는 버전을 찾더라도 그 버전에서 다른 게 깨지지 않는다는 보장이 없고, 확인하려면 전체 배포 시나리오를 다시 돌려야 한다.

**세 번째를 골랐다.** 오퍼레이터가 required를 못 지킨다면, required를 걷어내면 된다.

## 어떻게 고쳤나

오퍼레이터 설치 직후에 CRD의 `status.required`에서 `conditions`와 `message`를 뺀다. 설치 스크립트에 넣었다.

```bash
kubectl wait --timeout=30s \
  --for=condition=established \
  crd/fabricchaincodes.hlf.kungfusoftware.es 2>/dev/null || true

kubectl patch crd fabricchaincodes.hlf.kungfusoftware.es \
  --type='json' \
  -p='[{"op": "replace", "path": "/spec/versions/0/schema/openAPIV3Schema/properties/status/required", "value": ["status"]}]'
```

`required`를 `["status"]`만 남기고 좁혔다. 이제 오퍼레이터가 `conditions` 없이 업데이트를 보내도 API 서버가 받아준다. 상태 갱신 경로가 뚫리므로 FAILED 고착이 풀린다.

패치 전에 `kubectl wait --for=condition=established`를 두는 게 중요하다. helm 설치가 끝나도 CRD가 API 서버에 등록되기까지는 시간이 걸린다. 바로 patch를 때리면 "리소스 없음"으로 실패한다.

### sleep 20을 kubectl wait로 바꿨다

같은 커밋에서 인접한 문제도 정리했다. 체인코드 pod를 기다리는 코드가 이랬다.

```bash
log_info "Waiting for chaincode pod to be ready..."
sleep 20
```

20초 자고 나서 아무것도 확인하지 않는다. 느린 환경에서는 20초로 부족하고, 빠른 환경에서는 20초를 낭비한다. 무엇보다 **20초 뒤에 pod가 안 떠 있어도 스크립트는 그냥 다음으로 넘어간다.**

실제 readiness를 기준으로 바꿨다.

```bash
if ! kubectl wait --for=condition=ready pod \
    -l "app=${CC_RESOURCE_NAME}" \
    -n "${K8S_NAMESPACE}" \
    --timeout=120s; then
    log_error "Chaincode pod did not become ready within 120s"
    kubectl get pods -n "${K8S_NAMESPACE}" -l "app=${CC_RESOURCE_NAME}"
    kubectl logs -n "${K8S_NAMESPACE}" -l "app=${CC_RESOURCE_NAME}" --tail=30 || true
    exit 1
fi
```

준비되면 즉시 진행하고, 120초를 넘기면 pod 목록과 로그 30줄을 남기고 실패한다. 실패했을 때 조사에 필요한 정보를 그 자리에서 확보하는 게 요점이다 — 나중에 다시 들어가서 보려고 하면 pod가 이미 재시작돼 있을 수 있다.

여기서 판단 기준을 CRD STATUS가 아니라 **실제 pod readiness**로 옮긴 것도 의미가 있다. 앞의 버그 때문에 CRD STATUS는 애초에 믿을 수 없는 신호였다. 어차피 알고 싶은 것은 "체인코드가 실제로 동작하는가"이고, 그건 pod에 물어보면 된다.

## 남는 교훈

**업스트림 버그를 만났을 때 기본값은 포크가 아니다.** 포크는 가장 근본적으로 보이지만 유지 비용이 영구히 발생한다. 우회로가 몇 줄이고 그 영향 범위가 좁다면, 우회가 합리적인 선택일 때가 많다.

**우회 조치는 우회라고 적어둔다.** 스크립트에 버전(v1.9.2)과 증상을 주석으로 남겼다. 오퍼레이터가 업그레이드되고 버그가 고쳐지면 이 패치는 불필요해지는데, 왜 있는지 모르면 아무도 못 지운다. 그러면 이번엔 이 패치가 부채가 된다.

**믿을 수 없는 신호에 의존하는 대기를 계속 정교하게 만들 필요는 없다.** CRD STATUS 대신 pod readiness를 보기로 한 순간 문제가 훨씬 단순해졌다. 대기 조건을 다듬기 전에 "무엇을 근거로 기다리고 있는가"를 먼저 묻는 게 낫다.
