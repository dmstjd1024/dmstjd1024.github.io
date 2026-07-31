---
title:  "kubectl exec은 왜 멈추는가 — 셸 스크립트에 타임아웃과 재시도 넣기"

categories:
  - AI
tags:
  - AI
  - Claude Code
  - Kubernetes
  - 셸스크립트

date: 2026-05-11
thumbnail: "/assets/img/thumbnail/sample.png"
---

# 문제: 스크립트가 멈춘다

이 프로젝트에서 Fabric 네트워크를 올리는 일은 결국 bash 스크립트가 `kubectl`을 순서대로 호출하는 것이다. 그런데 이 스크립트가 간헐적으로 **멈췄다.** 에러가 나는 게 아니라 그냥 멈춰 있는다. 폐쇄망에 kind 다중 클러스터 환경이라 네트워크 계층이 순탄하지 않은 것도 한몫했다.

`kubectl`은 기본적으로 요청 타임아웃이 없다. `kubectl exec`은 API 서버와 스트리밍 연결을 맺는데, 이 연결이 어딘가에서 끊기면 클라이언트는 그 사실을 모른 채 계속 기다린다. 스크립트는 그 앞에서 무한정 대기하고, 애플리케이션은 그 스크립트가 끝나기를 기다린다.

# 어떻게 고쳤나

## 1. 재시도 래퍼

`kubectl` 호출을 감싸는 함수를 만들었다.

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

핵심은 `"$@"`다. 명령을 문자열로 받아 `eval`하면 인자 안의 공백이나 따옴표가 깨진다. 앞의 두 인자를 `shift`로 걷어내고 나머지를 배열 그대로 실행하면, 원본 명령의 인자 경계가 그대로 유지된다.

## 2. 모든 호출에 타임아웃

재시도만으로는 부족하다. 첫 호출이 영원히 안 끝나면 두 번째 시도는 오지 않는다. **재시도의 전제 조건이 타임아웃이다.** 모든 호출에 `--request-timeout`을 붙이되, 작업 성격에 따라 다르게 줬다.

| 작업 | 타임아웃 |
|---|---|
| 채널 조인 여부 확인 | 30s |
| MSP 생성, cert/key 복사, 권한 설정 | 60s |
| peer의 채널 조인 | 90s |

일괄로 하나를 주면 짧은 쪽은 실패를 늦게 알고 긴 쪽은 정상 작업을 죽인다.

## 3. heredoc이 범인이었다

가장 뜻밖의 발견은 이거였다. pod 안에 설정 파일을 만드느라 `kubectl exec`에 heredoc을 쓰고 있었다.

```bash
kubectl exec ... -- sh -c "
  cat > /tmp/admin-msp/config.yaml << 'CONFIGEOF'
NodeOUs:
  Enable: true
  ...
CONFIGEOF
"
```

`kubectl exec`의 stdin 스트리밍과 heredoc이 맞물리면 hang이 발생할 수 있다. heredoc은 종료 마커를 만날 때까지 stdin을 읽는데, 원격 셸이 그 stdin 스트림을 언제 닫을지가 보장되지 않는다.

`printf` 한 줄로 바꿨다.

```bash
printf 'NodeOUs:\n  Enable: true\n  ClientOUIdentifier:\n    Certificate: cacerts/cacert.pem\n ...' > /tmp/admin-msp/config.yaml
```

가독성은 확실히 나빠졌다. 하지만 stdin을 전혀 쓰지 않으므로 hang의 여지가 사라진다. 스크립트가 멈추는 것보다는 한 줄이 긴 게 낫다.

## 4. 재시도에 검증을 붙였다

여기가 이 작업의 핵심이다. 재시도는 "명령의 종료 코드가 0이 될 때까지"만 보장한다. `kubectl cp`가 0을 반환했는데 파일이 실제로 없는 상황은 얼마든지 가능하다 — 특히 부분적으로 끊긴 연결에서 그렇다.

그래서 권한 설정 단계 뒤에 필수 파일 존재 검증을 넣었다. `cert.pem`, `priv_sk`, `cacert.pem` 셋 중 하나라도 없으면 그 자리에서 실패시킨다.

**검증 없는 재시도는 "성공했다고 주장하는 실패"를 세 번 반복하는 것에 불과하다.** 오히려 나쁘다. 재시도 로직이 있다는 사실이 안심을 주기 때문에, 뒤쪽 단계에서 알 수 없는 이유로 터졌을 때 여기를 의심하지 않게 된다.

같은 이유로 인접한 버그도 하나 잡았다. `kubectl wait`는 매칭되는 Pod가 0개면 타임아웃을 기다리지 않고 **즉시** `no matching resources found`를 반환한다. CRD 생성 직후에는 오퍼레이터가 아직 Pod를 안 만든 상태라 여기 걸렸다. Pod가 생길 때까지 최대 60초 폴링한 뒤에 readiness를 기다리도록 바꿨다. "기다리는 명령"이 사실은 안 기다린다는 걸 알아야 쓸 수 있는 도구다.

# 별건: helm uninstall --wait가 만든 연쇄

같은 종류의 무한 대기가 삭제 경로에도 있었다. `helm uninstall --wait`가 PV finalizer 때문에 끝나지 않았다.

연쇄는 이렇게 흘렀다.

```
PV finalizer 잔존
  → helm uninstall --wait 무한 대기
  → 삭제 스크립트 중단
  → 애플리케이션이 응답을 못 받음
  → 네트워크 상태 DELETE_FAILED
```

그런데 이 스크립트는 helm 뒤에서 **직접** Pod/PVC/PV finalizer를 강제 정리하는 로직을 이미 갖고 있었다. helm이 따로 기다릴 이유가 없었던 것이다. `--wait`를 빼고 `--timeout 60s`를 줬다.

# 남는 교훈

**모든 원격 호출에는 타임아웃이 있어야 한다.** 기본값이 "무한 대기"인 도구는 생각보다 많다. 그리고 무한 대기는 실패보다 나쁘다 — 실패는 다음 단계로 넘어가지만 대기는 아무것도 진행시키지 않으면서 자원을 붙잡고 있다.

**재시도와 검증은 세트다.** 하나만 있으면 재시도는 거짓 성공을 반복하고, 검증은 일시적 장애를 영구 실패로 만든다.

**"기다린다"고 이름 붙은 도구가 정말 기다리는지 확인한다.** `kubectl wait`도, `helm --wait`도 이름이 약속하는 것과 실제 동작이 달랐다. 앞의 것은 안 기다렸고 뒤의 것은 너무 기다렸다.
