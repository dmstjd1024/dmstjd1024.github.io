---
title:  "Grafana 대시보드를 파일로 심는다 — ConfigMap 라벨 하나로"

categories:
  - Kubernetes
tags:
  - Kubernetes
  - Grafana
  - ConfigMap
  - 모니터링

date: 2026-08-28
thumbnail: "/assets/img/thumbnail/grafana_thumbnail.png"
card_thumbnail: "/assets/img/thumbnail/grafana_card.png"
---
## 한 줄로

**Grafana 에 API 를 한 번도 호출하지 않고 대시보드를 등록한다.**

JSON 파일을 ConfigMap 으로 만들고 **라벨 하나(`grafana_dashboard=1`)** 를 붙이면 끝이다.
나머지는 Grafana 옆에 붙은 보조 컨테이너가 알아서 한다.

## 왜 손으로 만들면 안 되나

Grafana 대시보드는 화면에서 클릭으로 만들 수 있다. 문제는 **어디에 저장되느냐**다.

기본 설정에서 대시보드는 Grafana 내부 DB 에 들어간다. 이 시스템에서는 그게 곤란하다.

- 회사마다 클러스터가 따로 뜬다 → **회사 수만큼 똑같은 대시보드를 손으로 만들어야 한다**
- 클러스터를 지우고 다시 만드는 일이 잦다 → **그때마다 사라진다**

그래서 대시보드를 **코드처럼 파일로** 두고 설치할 때 같이 심는다. 지금 2개가 들어 있다 —
파드 개요, 컨테이너 자원.

## 사이드카가 감시한다

`kube-prometheus-stack` 으로 깔린 Grafana 에는 **사이드카**(같은 파드에 붙는 보조 컨테이너)가
하나 따라온다. 이 컨테이너가 하는 일이 딱 하나다.

> 특정 라벨이 붙은 ConfigMap 을 감시하다가, 발견하면 그 내용을 대시보드 폴더에 써준다.

그 라벨이 `grafana_dashboard=1` 이다. 그래서 이렇게만 하면 된다.

```bash
kubectl create configmap "grafana-dashboard-${name}" \
  --from-file="${name}.json=${file}" \
  --namespace monitoring --dry-run=client -o yaml | \
kubectl label --local -f - grafana_dashboard="1" -o yaml | \
kubectl apply -f -
```

파이프가 세 단계인 게 눈에 띈다. **`--dry-run=client` 로 YAML 만 만들고 → 라벨을 붙이고 →
그제야 적용한다.**

`kubectl create configmap` 에는 라벨을 붙이는 옵션이 없어서, 만들어진 YAML 을 중간에서
가로채 라벨을 주입하는 방식이다. `--local` 은 "서버에 묻지 말고 이 파일만 고쳐라" 는 뜻이다.

## 왜 API 호출이 아니라 이 방식인가

Grafana 에는 대시보드를 등록하는 REST API 가 있다. 그걸 안 쓴 이유가 있다.

| | API 호출 | ConfigMap + 사이드카 |
|---|---|---|
| 필요한 것 | Grafana 주소·인증 토큰 | **없음** |
| 순서 | Grafana 가 **먼저 떠 있어야** | 순서 무관 |
| 재설치 | 스크립트를 다시 돌려야 | **ConfigMap 이 남아 있으면 자동** |
| 상태 | Grafana DB 안 (안 보임) | **쿠버 리소스로 보임** |

핵심은 **선언적**이라는 점이다. "이 ConfigMap 이 존재한다" 는 상태만 선언하면, Grafana 가
언제 뜨든 그걸 따라온다. 순서를 맞출 필요가 없다.

인증도 필요 없다. 쿠버네티스 리소스를 만들 권한만 있으면 된다. **비밀번호를 스크립트에 넣지
않아도 되는 것**이 폐쇄망 환경에서는 특히 값지다.

## 이미 있으면 replace 로 간다

같은 스크립트에 이런 대비가 있다.

```bash
kubectl apply -f - 2>/dev/null || {
  echo "  ⚠️  ConfigMap ${configmap_name} already exists, updating..."
  ... | kubectl replace -f -
}
```

`apply` 가 실패하면 `replace` 로 다시 시도한다. 재설치할 때 기존 ConfigMap 과 충돌하는
경우를 넘기려는 것이다.

다만 `2>/dev/null` 로 **에러 메시지를 버린다**는 게 아쉽다. 권한 문제로 실패한 것과
이미 존재해서 실패한 것을 구분하지 않고 똑같이 `replace` 를 시도한다.

## 재시작을 시킨다

마지막 줄이 흥미롭다.

```bash
kubectl rollout restart deployment -n monitoring -l app.kubernetes.io/name=grafana
```

사이드카가 알아서 감지한다면서 **Grafana 를 재시작한다.**

사이드카의 감지에는 주기가 있다. 설치 스크립트가 끝난 직후 사용자가 접속했는데 대시보드가
아직 안 보이면 "안 깔렸다" 고 오해할 수 있다. 그걸 피하려고 즉시 반영시키는 것으로 보인다.

절충이 하나 있다. **이미 Grafana 를 보고 있던 사용자는 이 순간 연결이 끊긴다.**
설치 직후에만 도는 코드라 실제 피해는 거의 없겠지만, 재설치 상황에서는 얘기가 다르다.

주석에 "즉시 반영을 위해" 같은 한 줄이 있었으면 좋았을 대목이다. 지금은 왜 재시작하는지
코드만 봐서는 알 수 없다.

## 대시보드 폴더가 없으면 조용히 넘어간다

```bash
if [ -d "${DASHBOARD_DIR}" ]; then
  ... 대시보드 등록 ...
fi
```

`else` 가 없다. 폴더가 없으면 **아무 말 없이 넘어간다.**

앞의 [Prometheus 편](/Kubernetes/모니터링은-한-덩어리로-깔린다.html)에서 본 차트 파일 확인은
`exit 1` 로 명확히 실패했는데, 여기는 다르다.

Grafana 는 떴는데 대시보드만 비어 있는 상태가 되고, 로그에는 단서가 없다. 대시보드가 없다는
걸 사람이 화면을 보고 알아채야 한다.

**"없으면 안 하고 넘어간다" 는 판단 자체는 맞다** — 대시보드가 없다고 설치를 실패시킬 이유는
없다. 다만 `echo "대시보드 폴더 없음, 건너뜀"` 한 줄이면 나중에 원인을 찾는 시간이 크게 줄어든다.

## 정리

- 대시보드를 **JSON 파일로 두고** 설치 때 심는다. 클러스터가 회사마다 뜨고 자주 재생성되기 때문
- 방식은 **ConfigMap + 라벨 `grafana_dashboard=1`**. Grafana 사이드카가 감시하다 읽어간다
- **API 호출이 아니라 선언적**이라, 인증도 필요 없고 Grafana 기동 순서와도 무관하다
- `kubectl create` 에 라벨 옵션이 없어 **`--dry-run` → `label --local` → `apply`** 로 우회한다
- 사이드카 감지 주기를 기다리지 않으려고 **Grafana 를 롤아웃 재시작**한다.
  보고 있던 사용자는 끊긴다
- ⚠️ 대시보드 폴더가 없으면 **아무 메시지 없이 넘어간다.** 빈 Grafana 의 원인을 찾기 어렵다

같이 읽을 글:
[Prometheus 는 한 덩어리로 깔린다](/Kubernetes/모니터링은-한-덩어리로-깔린다.html) ·
[Ingress 로 포트 3개를 1개로 줄였다](/Kubernetes/ingress로-포트-3개를-1개로-줄였다.html) ·
[쿠버네티스 대시보드란](/Kubernetes/쿠버네티스-대시보드란.html)
