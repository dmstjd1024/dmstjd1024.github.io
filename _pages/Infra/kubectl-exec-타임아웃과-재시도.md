---
title:  "kubectl exec은 왜 멈추는가 — 셸 스크립트에 타임아웃과 재시도 넣기"

categories:
  - Infra
tags:
  - AI
  - Claude Code
  - Kubernetes
  - 셸스크립트

date: 2026-05-11
thumbnail: "/assets/img/thumbnail/sample.png"
---
## 문제: 스크립트가 멈춘다

- Fabric 네트워크 기동 = bash 스크립트가 `kubectl`을 순서대로 호출
- 증상 — 스크립트가 간헐적으로 **멈춤**. 에러가 아니라 그냥 정지
- 환경 — 폐쇄망 + kind 다중 클러스터. 네트워크 계층이 순탄하지 않음

원인 구조:

- `kubectl`은 기본적으로 요청 타임아웃 없음
- `kubectl exec`은 API 서버와 스트리밍 연결 수립
- 이 연결이 끊기면 클라이언트는 그 사실을 모른 채 계속 대기
- 스크립트는 그 앞에서 무한정 대기, 애플리케이션은 그 스크립트 종료를 대기

<div class="diagram" role="img" aria-label="연결이 끊겨도 모른 채 대기하는 구조와 그 전파">
{% include diagrams/kubectl--hang.svg %}
</div>

## 어떻게 고쳤나

### 1. 재시도 래퍼

- 조치: `kubectl` 호출을 감싸는 함수 추가

```bash
# 사용: kubectl_with_retry <max_retry> <sleep_sec> kubectl exec ...
kubectl_with_retry() {
  local max_retry=$1; shift
  local sleep_sec=$1; shift
  local attempt=1
  while [ ${attempt} -le ${max_retry} ]; do
    if "$@"; then
      return 0
    fi
    log "    ⚠️ kubectl 명령 실패 (attempt ${attempt}/${max_retry}), ${sleep_sec}s 후 재시도..."
    sleep ${sleep_sec}
    attempt=$((attempt + 1))
  done
  log "    ❌ kubectl 명령 ${max_retry}회 모두 실패"
  return 1
}
```

- 핵심은 `"$@"`
- 명령을 문자열로 받아 `eval` 시 → 인자 안의 공백·따옴표 파손
- 앞 두 인자를 `shift`로 제거하고 나머지를 배열 그대로 실행 → 원본 명령의 인자 경계 유지

### 2. 모든 호출에 타임아웃

- 재시도만으로는 부족 — 첫 호출이 안 끝나면 두 번째 시도 자체가 없음
- 즉 **재시도의 전제 조건이 타임아웃**

- 모든 호출에 `--request-timeout` 부착
- 작업 성격에 따라 값 차등

| 작업 | 타임아웃 |
|---|---|
| 채널 조인 여부 확인 | 30s |
| MSP 생성, cert/key 복사, 권한 설정 | 60s |
| peer의 채널 조인 | 90s |

- 일괄 단일값의 문제: 짧은 쪽은 실패 인지 지연, 긴 쪽은 정상 작업 중단

### 3. heredoc이 범인이었다

- 가장 뜻밖의 발견 — pod 안 설정 파일 생성을 위해 `kubectl exec`에 heredoc 사용 중

```bash
kubectl exec ... -- sh -c "
  cat > /tmp/admin-msp/config.yaml << 'CONFIGEOF'
NodeOUs:
  Enable: true
  ...
CONFIGEOF
"
```

- `kubectl exec`의 stdin 스트리밍 + heredoc 조합 → hang 발생 가능
- heredoc은 종료 마커를 만날 때까지 stdin을 읽음
- 원격 셸이 그 stdin 스트림을 언제 닫을지 미보장

- 조치: `printf` 한 줄로 변경

```bash
printf 'NodeOUs:\n  Enable: true\n  ClientOUIdentifier:\n    Certificate: cacerts/cacert.pem\n ...' > /tmp/admin-msp/config.yaml
```

- 대가: 가독성 저하
- 이득: stdin 미사용 → hang 여지 소멸

스크립트가 멈추는 것보다는 한 줄이 긴 게 낫다.

### 4. 재시도에 검증을 붙였다

- 이 작업의 핵심 지점

- 재시도가 보장하는 것 — "명령의 종료 코드가 0이 될 때까지"뿐
- `kubectl cp`가 0을 반환했는데 파일이 실제로 없는 상황 가능 — 특히 부분적으로 끊긴 연결
- 조치 — 권한 설정 단계 뒤에 필수 파일 존재 검증. `cert.pem`, `priv_sk`, `cacert.pem` 중 하나라도 없으면 즉시 실패

**검증 없는 재시도는 "성공했다고 주장하는 실패"를 세 번 반복하는 것에 불과하다.**

- 오히려 해로운 이유: 재시도 로직의 존재 자체가 안심을 줌
- 결과: 뒤쪽 단계가 터졌을 때 이 지점을 의심 대상에서 제외

같은 이유로 잡은 인접 버그:

- `kubectl wait`는 매칭 Pod가 0개면 타임아웃을 기다리지 않고 **즉시** `no matching resources found` 반환
- CRD 생성 직후 — 오퍼레이터가 아직 Pod 미생성 상태라 여기 걸림
- 조치 — Pod가 생길 때까지 최대 **60초** 폴링 후 readiness 대기

- 전제 지식: "기다리는 명령"이 사실은 안 기다린다는 점

## 별건: helm uninstall --wait가 만든 연쇄

- 삭제 경로에도 같은 종류의 무한 대기 존재
- 원인: PV finalizer로 `helm uninstall --wait` 미종료

```
PV finalizer 잔존
  → helm uninstall --wait 무한 대기
  → 삭제 스크립트 중단
  → 애플리케이션이 응답을 못 받음
  → 네트워크 상태 DELETE_FAILED
```

- 이 스크립트는 helm 뒤에서 **직접** Pod/PVC/PV finalizer를 강제 정리하는 로직을 이미 보유
- 즉 helm이 따로 기다릴 이유가 없었음
- 조치 — `--wait` 제거, `--timeout 60s` 부여

## 남는 교훈

**모든 원격 호출에는 타임아웃이 있어야 한다.** 기본값이 "무한 대기"인 도구는 생각보다 많다.

- 무한 대기가 실패보다 나쁜 이유: 실패는 다음 단계로 진행, 대기는 자원만 점유

**재시도와 검증은 세트다.**

- 재시도만 있을 때 — 거짓 성공 반복
- 검증만 있을 때 — 일시적 장애가 영구 실패로 전환

**"기다린다"고 이름 붙은 도구가 정말 기다리는지 확인한다.**

- `kubectl wait` — 안 기다림
- `helm --wait` — 너무 기다림
- 공통점: 이름의 약속과 실제 동작 불일치
