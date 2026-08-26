---
title:  "오픈소스 오퍼레이터 버그를 CRD 스키마 패치로 우회하기"

categories:
  - Infra
tags:
  - AI
  - Claude Code
  - Kubernetes
  - Hyperledger Fabric

date: 2026-05-08
thumbnail: "/assets/img/thumbnail/kubernetes_thumbnail.png"
---
## 문제: 체인코드 상태가 FAILED에서 안 나온다

구조:

- 체인코드 배포 시 Kubernetes에 `FabricChaincode` 커스텀 리소스 생성
- hlf-operator가 이 리소스를 보고 실제 체인코드 pod 기동

증상:

- 배포는 실제로 성공
- `kubectl get fabricchaincodes`의 STATUS가 **FAILED로 고착**
- 한 번 FAILED가 되면 갱신 불가
- 애플리케이션이 이 상태를 읽어 노출 → 정상 체인코드가 화면에서 실패로 표시

## 원인: 오퍼레이터가 자기 스키마를 못 지킨다

hlf-operator v1.9.2의 문제.

- CRD 정의: `status` 하위 `conditions`, `message`가 **required**
- 실제 동작: 오퍼레이터가 status 업데이트 시 이 필드들 누락

결과의 연쇄:

```
오퍼레이터가 status 업데이트 시도
  → conditions/message 누락
  → API 서버가 스키마 validation 거부
  → status 업데이트 실패
  → 오퍼레이터가 이걸 에러로 판단해 FAILED 기록 시도
  → 그 기록도 같은 이유로 실패
  → STATUS는 FAILED에 머문 채 영원히 갱신 불가
```

- 상태 갱신 경로 자체가 봉쇄 → 어떤 값으로도 탈출 불가
- 스스로 만든 스키마를 스스로 못 지키는 상황

<div class="diagram" role="img" aria-label="required 필드 누락으로 status 갱신이 막혀 FAILED 에 고착되는 구조">
{% include diagrams/crd--schema-workaround.svg %}
</div>

## 선택지를 따져봤다

우리 코드가 아니므로 직접 수정 불가. 선택지 세 가지:

| 선택지 | 장점 | 단점 |
|---|---|---|
| 포크해서 패치 | 근본 수정, 상류 기여 가능 | Go 빌드 파이프라인·이미지 레지스트리 필요, 폐쇄망에서 부담. 업스트림 추적 비용이 영구히 발생 |
| 버전 다운그레이드 | 간단 | 이 버전에서만 되는 다른 기능을 잃을 수 있고, 옛 버전에 다른 버그가 있는지 모름 |
| CRD 스키마 패치 | 설치 스크립트 몇 줄, 오퍼레이터 이미지 그대로 | 스키마를 느슨하게 만듦, 업그레이드 시 다시 적용 필요 |

포크 기각 사유:

- 폐쇄망 — 커스텀 이미지 빌드·반입 파이프라인 신설 필요
- 이후 업스트림 릴리스마다 리베이스 관리 필요
- 버그 하나에 대한 대가로는 과함

다운그레이드 기각 사유:

- 버그 없는 버전을 찾아도 다른 기능의 무결성 미보장
- 확인하려면 전체 배포 시나리오 재실행 필요

**세 번째를 골랐다.** 오퍼레이터가 required를 못 지킨다면, required를 걷어내면 된다.

## 어떻게 고쳤나

- 시점: 오퍼레이터 설치 직후
- 조치: CRD `status.required`에서 `conditions`, `message` 제거
- 위치: 설치 스크립트

```bash
kubectl wait --timeout=30s \
  --for=condition=established \
  crd/fabricchaincodes.hlf.kungfusoftware.es 2>/dev/null || true

kubectl patch crd fabricchaincodes.hlf.kungfusoftware.es \
  --type='json' \
  -p='[{"op": "replace", "path": "/spec/versions/0/schema/openAPIV3Schema/properties/status/required", "value": ["status"]}]'
```

- `required`를 `["status"]`만 남기고 축소
- 오퍼레이터가 `conditions` 없이 업데이트해도 API 서버가 수용
- 상태 갱신 경로가 뚫리므로 FAILED 고착 해소

패치 전 `kubectl wait --for=condition=established` 배치가 필수:

- helm 설치 완료 ≠ CRD의 API 서버 등록 완료
- 즉시 patch 시 "리소스 없음"으로 실패

### sleep 20을 kubectl wait로 바꿨다

같은 커밋에서 인접한 문제도 정리. 체인코드 pod 대기 코드의 원래 모습:

```bash
log_info "Waiting for chaincode pod to be ready..."
sleep 20
```

문제점:

- 20초 후 아무 확인 없음
- 느린 환경 — 20초 부족
- 빠른 환경 — 20초 낭비
- **20초 뒤 pod 미기동 상태여도 스크립트는 그대로 진행**

실제 readiness 기준으로 교체:

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

- 준비 완료 시 즉시 진행
- 120초 초과 시 pod 목록 + 로그 30줄 출력 후 실패

요점: 실패 시 조사에 필요한 정보를 그 자리에서 확보 — 나중에 다시 보면 pod가 이미 재시작된 뒤

판단 기준의 이동: CRD STATUS → **실제 pod readiness**

- 앞의 버그 탓에 CRD STATUS는 애초에 신뢰 불가한 신호
- 알고 싶은 것은 "체인코드가 실제로 동작하는가" → pod에 직접 질의

## 남는 교훈

**업스트림 버그를 만났을 때 기본값은 포크가 아니다.** 포크는 가장 근본적으로 보이지만 유지 비용이 영구히 발생한다.

- 우회로가 몇 줄 + 영향 범위 협소 → 우회가 합리적인 경우 다수

**우회 조치에는 우회라는 표시를.**

- 스크립트에 버전(v1.9.2)과 증상을 주석으로 기록
- 오퍼레이터 업그레이드 후 이 패치는 불필요해짐
- 존재 이유를 모르면 아무도 삭제 불가 → 이번엔 이 패치가 부채로 전환

**믿을 수 없는 신호에 의존하는 대기를 계속 정교하게 만들 필요는 없다.**

- CRD STATUS → pod readiness 전환 시점에 문제 대폭 단순화
- 대기 조건 정교화보다 "무엇을 근거로 기다리는가"가 선행 질문
