---
title:  "Ingress 로 포트 3개를 1개로 줄였다 — 경로 재작성이 필요한 이유"

categories:
  - Kubernetes
tags:
  - Kubernetes
  - Ingress
  - nginx
  - 멀티테넌시

date: 2026-08-28
thumbnail: "/assets/img/thumbnail/nginx_thumbnail.png"
card_thumbnail: "/assets/img/thumbnail/nginx_card.png"
---
## 한 줄로

**회사 하나가 쓸 수 있는 포트가 10개뿐이라, 관측 도구 3종을 포트 하나에 몰아넣었다.**

그 대가로 **경로 재작성**(rewrite)이 필요해졌다. 이 글은 왜 그게 필요한지에 대한 이야기다.

## 포트가 왜 모자라나

[앞 글](/Kubernetes/회사마다-클러스터-하나씩-띄운다.html)에서 봤듯, 이 시스템은 회사마다
쿠버네티스 클러스터를 통째로 하나씩 띄운다. 서버는 한 대다.

그래서 회사마다 **포트를 10개씩** 떼어준다. 그런데 노출해야 할 게 그보다 많다.

| 오프셋 | 용도 |
|---:|---|
| +0 | API 서버 |
| +1 | **Ingress HTTP** |
| +2 | Ingress HTTPS |
| +3~5 | 대시보드 · Grafana · Prometheus |
| +6~9 | Besu RPC · WS · Blockscout · Fabric Explorer |

블록체인 쪽(+6~9)은 프로토콜이 제각각이라 포트를 따로 써야 한다. 줄일 수 있는 건
**관측 도구 3종**뿐이었다.

## NodePort 대신 Ingress

쿠버네티스에서 서비스를 밖으로 여는 방법은 크게 둘이다.

| | NodePort | Ingress |
|---|---|---|
| 방식 | 서비스마다 포트 하나 | **경로로 갈라 하나의 포트 공유** |
| 3종 노출 시 | 포트 3개 | **포트 1개** |
| 필요한 것 | 없음 | Ingress 컨트롤러 |

Ingress 는 **HTTP 레벨에서 경로를 보고 뒤로 넘겨주는** 문지기다. 웹(HTTP)이라 가능한 방식이고,
그래서 관측 도구 3종에는 되지만 블록체인 RPC 에는 안 맞는다.

결과적으로 이렇게 들어간다.

```
{Ingress포트}/grafana      → grafana-svc:80
{Ingress포트}/prometheus   → prometheus-svc:9090
{Ingress포트}/kube-dashboard/
```

**포트 3개가 1개가 됐다.** 남은 2개는 블록체인 쪽으로 갔다.

## 경로를 떼어내지 않으면 깨진다

여기서 흔히 걸리는 함정이 있다. 위 설정만으로는 **안 된다.**

`{포트}/grafana/foo` 로 요청이 오면 Ingress 는 Grafana 에게 넘긴다. 그런데 **경로를 그대로**
넘기면 Grafana 는 `/grafana/foo` 라는 주소를 받는다. Grafana 입장에서 자기 앱에 그런 경로는
없다. 404 다.

Grafana 는 자기가 `/` 아래 있다고 생각한다. `/grafana` 라는 접두어는 **바깥 사정**이다.
그래서 넘기기 전에 떼어줘야 한다.

```yaml
annotations:
  nginx.ingress.kubernetes.io/rewrite-target: /$2
spec:
  rules:
  - http:
      paths:
      - path: /grafana(/|$)(.*)
        pathType: ImplementationSpecific
```

정규식 괄호가 두 개다.

| 괄호 | 잡는 것 | 예 (`/grafana/d/abc`) |
|---|---|---|
| `(/|$)` — `$1` | 구분자 | `/` |
| `(.*)` — `$2` | **나머지 전부** | `d/abc` |

`rewrite-target: /$2` 는 **두 번째 괄호만 남긴다**는 뜻이다. `/grafana/d/abc` 가
`/d/abc` 로 바뀌어 Grafana 에 도착한다.

`(/|$)` 가 `/` 뿐 아니라 **문자열 끝**(`$`)도 허용하는 게 포인트다. 이게 없으면
`/grafana` (뒤에 슬래시 없이)로 들어온 요청이 매칭되지 않는다.

`pathType: ImplementationSpecific` 인 이유도 여기 있다. 표준 타입인 `Prefix` 나 `Exact` 는
**정규식을 해석하지 않는다.** 정규식을 쓰려면 "구현체(nginx)에 맡긴다" 고 선언해야 한다.

## 타임아웃을 1시간으로 늘렸다

같은 설정에 이런 줄도 있다.

```yaml
nginx.ingress.kubernetes.io/proxy-read-timeout: "3600"
nginx.ingress.kubernetes.io/proxy-send-timeout: "3600"
```

nginx 의 기본 타임아웃은 60초다. 그런데 Grafana 는 **연결을 오래 붙잡는 요청**을 쓴다.
대시보드가 실시간으로 갱신되려면 서버와 연결을 유지해야 하기 때문이다.

60초에서 끊기면 화면이 멈춘 것처럼 보이고, 원인을 찾기 어렵다. 에러 화면이 뜨는 게 아니라
그냥 갱신이 안 되기 때문이다. **1시간(3600초)** 은 그걸 피하려는 값이다.

## Ingress 컨트롤러 자체는 어떻게 깔리나

Ingress 는 규칙일 뿐이고, 그 규칙을 실행할 **컨트롤러**가 따로 필요하다. 여기서는 nginx 를 쓴다.

```bash
--set controller.image.registry=localhost:5001
--set controller.image.image=ingress-nginx/controller
--set controller.image.tag=v1.9.4
```

폐쇄망이라 이미지 출처를 로컬 레지스트리로 바꿔 지정한다. 이 패턴은 부가 컴포넌트 전부에
공통이다.

설치 스크립트는 96줄로, 부가 컴포넌트 중 가장 짧다. 표준 Helm 차트를 이미지 경로만 바꿔
그대로 쓰기 때문이다.

## 여기서 걸린 것 — 실패해도 넘어간다

설치 호출부가 이렇게 돼 있다.

```bash
bash "$SCRIPT_DIR/12-install-ingress-controller.sh" ... || {
  echo "⚠️ ... non-critical, continuing..."
}
```

**Ingress 컨트롤러가 안 깔려도 클러스터는 `ACTIVE` 로 기록된다.**

그런데 이건 다른 부가 컴포넌트가 실패한 것과 무게가 다르다. Ingress 가 없으면
**Grafana·Prometheus·대시보드 3개가 전부 접근 불가**가 된다. 이 셋은 자기 포트가 없기 때문이다.

포트를 아끼려고 셋을 하나에 몰았더니, **그 하나가 무너지면 셋이 같이 무너지는** 구조가 됐다.
자원 절약과 장애 격리는 이런 식으로 맞바꿔진다.

## 정리

- 포트가 회사당 10개뿐이라 **관측 도구 3종을 Ingress 경로로 몰았다** — 포트 3개 → 1개
- 블록체인 RPC 는 HTTP 가 아니라 이 방식을 못 쓴다. 그래서 포트를 따로 갖는다
- **경로 재작성이 필수다.** 뒷단 앱은 자기가 `/` 아래 있다고 생각하기 때문
- `(/|$)` 로 **슬래시 없는 요청**까지 받고, `pathType: ImplementationSpecific` 이라야
  정규식이 해석된다
- 타임아웃을 60초 → **3600초**로 늘렸다. Grafana 의 긴 연결이 끊기지 않도록
- ⚠️ 실패해도 `ACTIVE` 다. 그런데 Ingress 는 **혼자 죽으면 셋이 같이 죽는다**

같이 읽을 글:
[모니터링은 한 덩어리로 깔린다](/Kubernetes/모니터링은-한-덩어리로-깔린다.html) ·
[Grafana 대시보드를 파일로 심는다](/Kubernetes/grafana-대시보드를-파일로-심는다.html) ·
[회사마다 클러스터 하나씩 띄운다](/Kubernetes/회사마다-클러스터-하나씩-띄운다.html)
