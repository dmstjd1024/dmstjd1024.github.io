---
title:  "Ingress 란? — 포트 3개를 1개로 줄이고 무한 리다이렉트를 만났다"

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

## 겪은 이슈 ① — 양쪽이 경로를 다루면 무한 루프가 난다

경로 재작성에서 실제로 사고가 났다.

```
fix(monitoring): Prometheus 무한 리다이렉트 및 Grafana 로그인 루프 수정   (2026-04-19)

Prometheus: routePrefix=/prometheus 제거 → Ingress rewrite(/$2)와의 충돌 해결
  routePrefix 설정 시 /prometheus/graph → Ingress가 /graph로 rewrite →
  Prometheus 미인식 → /prometheus/graph 재리다이렉트 무한 반복 발생
```

원인이 명확하다. **Ingress 와 Prometheus 가 둘 다 경로를 손대고 있었다.**

Prometheus 에는 `routePrefix` 라는 설정이 있다. "나는 `/prometheus` 아래에 있다" 고
알려주는 값이다. 하위 경로에 앱을 붙일 때 흔히 쓴다.

그런데 Ingress 도 같은 일을 하고 있었다. 접두어를 **떼어내서** 넘기고 있었으니, 앱은
접두어가 없는 요청을 받는다. 그 상태에서 앱이 "나는 `/prometheus` 아래 있어야 해" 라고
믿으면 이렇게 된다.

```
브라우저 → /prometheus/graph
Ingress  → 접두어 떼고 /graph 로 전달
Prometheus → "이건 내 경로가 아닌데?" → /prometheus/graph 로 리다이렉트
브라우저 → /prometheus/graph        ← 처음으로 돌아옴
```

**끝나지 않는다.** 브라우저는 리다이렉트를 계속 따라가다 결국 에러를 낸다.

해법은 둘 중 하나를 포기하는 것이다. Ingress 가 떼어내든지, 앱이 접두어를 알든지.
여기서는 **`routePrefix` 를 없애고 Ingress 쪽에 맡겼다.**

배운 것은 이거다. **경로를 다루는 주체는 하나여야 한다.** 프록시와 앱이 각자 옳은 일을
해도, 합쳐지면 순환이 된다.

같은 커밋에 Grafana **로그인 루프**도 함께 고쳤는데 원인은 조금 다르다. Grafana 의
`root_url` 이 `localhost` 를 가리키고 있어서, 로그인 후 돌아갈 주소를 잘못 만들고 있었다.
외부에서 접근하는 실제 주소를 설정 체인으로 넘겨 해결했다.

**하위 경로에 앱을 붙일 때는 그 앱이 "자기 주소" 를 어떻게 아는지 확인해야 한다.**
Prometheus 는 `routePrefix`, Grafana 는 `root_url` 이었다.

## 타임아웃을 1시간으로 늘렸다

같은 설정에 이런 줄도 있다.

```yaml
nginx.ingress.kubernetes.io/proxy-read-timeout: "3600"
nginx.ingress.kubernetes.io/proxy-send-timeout: "3600"
```

이 값은 처음부터 이랬던 게 아니다. **실제로 겪고 나서 올린 값**이다.

```
fix(proxy): Grafana WebSocket 장시간 연결 끊김 방지   (2026-04-19)

nginx proxy_read/send_timeout과 Ingress proxy-read/send-timeout을
120s → 3600s로 변경하여 Grafana 라이브 대시보드(/api/live/ws)
WebSocket 연결이 유휴 시 끊기는 문제 수정.
```

증상이 까다로운 종류였다. Grafana 라이브 대시보드는 **WebSocket**(연결을 열어둔 채 서버가
값을 밀어주는 방식)으로 갱신된다. 그런데 값이 안 바뀌는 동안에는 **트래픽이 흐르지 않는다.**

nginx 입장에서는 그게 "놀고 있는 연결" 로 보인다. 그래서 120초가 지나면 끊는다.

```
사용자: 화면을 열어둠
  ↓ 2분간 지표 변화 없음 → 데이터 오감 없음
nginx: 유휴 연결로 판단 → 끊음
사용자: 갱신이 멈췄는데 에러는 안 뜸
```

**에러 화면이 안 뜨는 게 진단을 어렵게 한다.** 페이지는 멀쩡히 떠 있고 숫자만 안 바뀐다.
새로고침하면 잠깐 되살아나니 "가끔 이상하다" 로 넘어가기 쉽다.

고친 방식은 타임아웃을 **1시간(3600초)** 으로 늘린 것이다. 근본 해법은 아니다 —
WebSocket 을 유휴로 판정하지 않게 하거나 주기적으로 신호를 보내는 방법도 있다. 다만
사내용 화면이고 연결 수가 많지 않아 **가장 단순한 쪽**을 택했다.

한 가지 더 눈에 띄는 건 **두 군데를 같이 고쳤다**는 점이다. Ingress 애노테이션만 고치면
안 됐다. 그 앞에 nginx 가 한 겹 더 있어서, **경로 위의 모든 프록시가 같은 값을 가져야**
연결이 유지된다.

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
- ⚠️ **경로를 다루는 주체는 하나여야 한다.** Ingress 와 Prometheus 가 둘 다 손대서
  **무한 리다이렉트**가 났다 (`routePrefix` 제거로 해결)
- 타임아웃 **120초 → 3600초** — Grafana 라이브 대시보드의 WebSocket 이 유휴로 판정돼
  끊기던 문제. **경로 위의 모든 프록시**를 같이 고쳐야 했다
- ⚠️ 실패해도 `ACTIVE` 다. 그런데 Ingress 는 **혼자 죽으면 셋이 같이 죽는다**

같이 읽을 글:
[모니터링은 한 덩어리로 깔린다](/Kubernetes/모니터링은-한-덩어리로-깔린다.html) ·
[Grafana 대시보드를 파일로 심는다](/Kubernetes/grafana-대시보드를-파일로-심는다.html) ·
[회사마다 클러스터 하나씩 띄운다](/Kubernetes/회사마다-클러스터-하나씩-띄운다.html)
