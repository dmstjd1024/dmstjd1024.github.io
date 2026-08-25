---
title: "쿠버네티스 - 디플로이먼트(Deployment), 서비스(Service)"

categories:
 - Kubernetes
tags:
  - Kubernetes

date: 2026-08-19
thumbnail: "/assets/img/thumbnail/kubernetes_thumbnail.png"
---
디플로이먼트(Deployment) 란?
=====
-----
**파드(Pod)를 관리해주는 것**

앞에서 파드를 직접 매니페스트로 만들어 띄웠다.
그런데 파드만 쓰면 불편한 점이 있다.

- 서버를 3개 띄우려면 매니페스트 파일을 3개 만들어야 한다
- 파드가 죽으면 아무도 다시 살려주지 않는다
- 새로운 버전으로 바꾸려면 직접 지우고 다시 만들어야 한다

디플로이먼트는 이걸 대신 해준다.
**몇 개를 띄울지 선언해두면, 그 상태를 계속 유지시켜준다.**

## [예제] 디플로이먼트를 활용해 백엔드(Spring Boot) 서버 3개 띄워보기

```yaml
apiVersion: apps/v1
kind: Deployment

metadata:
  name: spring-deployment

spec:
  replicas: 3                # 파드를 몇 개 띄울지
  selector:
    matchLabels:
      app: spring-app        # 이 라벨을 가진 파드를 내가 관리한다
  template:                  # 파드를 만들 때 쓸 설계도
    metadata:
      labels:
        app: spring-app      # selector와 반드시 같아야 한다
    spec:
      containers:
        - name: spring-container
          image: spring-server
          ports:
            - containerPort: 8080
          imagePullPolicy: IfNotPresent
```

`template` 아래 부분을 보면, 앞에서 작성했던 **파드 매니페스트와 똑같다.**
디플로이먼트는 그 파드 설계도를 들고 있다가 `replicas` 개수만큼 찍어내는 역할이다.

### 라벨(label)과 셀렉터(selector)

쿠버네티스는 리소스끼리 **이름이 아니라 라벨로 연결된다.**

- `template.metadata.labels` : 만들어질 파드에 붙는 이름표
- `spec.selector.matchLabels` : 그 이름표를 가진 파드를 찾아서 관리

이 둘이 서로 다르면 매니페스트 적용 자체가 안 된다. **자주 하는 실수다.**

<div class="diagram">
{% include diagrams/k8s--deploy-service.svg %}
</div>

### 실행

```bash
kubectl apply -f spring-deployment.yaml
kubectl get deployments        # 축약: kubectl get deploy
kubectl get pods
```

파드 이름이 `spring-deployment-xxxxx-yyyyy` 형태로 3개 생성된다.
파드를 하나씩 만들지 않아도 되고, 이름도 알아서 붙여준다.

서비스(Service) 란?
=====
-----
**여러 개의 파드에 접근할 수 있는 하나의 고정된 주소를 만들어주는 것**

디플로이먼트로 파드를 3개 띄웠다. 그런데 여기에 어떻게 접속할까?

- 파드는 **각각 IP가 다르다** → 3개 중 어디로 보내야 하지?
- 파드는 죽었다 살아나면 **IP가 바뀐다** → 주소를 적어둘 수가 없다

그래서 파드 앞에 **서비스**를 두고, 서비스 주소로 요청을 보낸다.
서비스가 알아서 뒤에 있는 파드들에게 요청을 나눠준다. (로드 밸런싱)

## [예제] 서비스(Service)를 활용해 백엔드(Spring Boot) 서버와 통신해보기

```yaml
apiVersion: v1
kind: Service

metadata:
  name: spring-service

spec:
  selector:
    app: spring-app      # 이 라벨을 가진 파드로 요청을 보낸다
  ports:
    - port: 8080         # 서비스가 열어두는 포트
      targetPort: 8080   # 파드(컨테이너)의 포트
```

여기서도 연결 고리는 **라벨**이다.
디플로이먼트에서 파드에 붙여준 `app: spring-app` 을 서비스가 셀렉터로 찾는다.

```bash
kubectl apply -f spring-service.yaml
kubectl get services      # 축약: kubectl get svc
```

### 포트 포워딩으로 접속해보기

서비스도 기본적으로는 **클러스터 내부 주소**라 로컬에서 바로 접속되지 않는다.
파드 때와 마찬가지로 포트 포워딩을 걸면 된다.

```bash
kubectl port-forward service/spring-service 8080:8080
```

파드에 직접 걸었을 때와 다른 점은, **파드가 죽었다 살아나도 그대로 동작한다**는 것이다.
서비스는 파드가 바뀌어도 같은 주소를 유지해주기 때문이다.

### 포트 2개가 헷갈릴 때

```
요청 ──▶ port(8080) ──▶ targetPort(8080) ──▶ 컨테이너
          서비스 포트        파드의 포트
```

- `port` : 서비스 자신이 열어둔 포트
- `targetPort` : 실제 컨테이너가 듣고 있는 포트 (`containerPort` 와 맞춰야 한다)

디플로이먼트를 활용한 서버 개수 조절 방법
=====
-----

서버를 늘리거나 줄이는 방법은 두 가지다.

### 1. 매니페스트 파일 수정

`replicas` 값만 바꾸고 다시 적용한다.

```yaml
spec:
  replicas: 5
```

```bash
kubectl apply -f spring-deployment.yaml
```

### 2. 명령어로 바로 변경

```bash
kubectl scale deployment/spring-deployment --replicas=5
```

`kubectl get pods` 로 보면 파드가 5개로 늘어나 있다.
줄일 때도 똑같이 숫자만 낮추면 된다.

> 파드를 직접 만들었다면 파일을 5개 만들고 5번 apply 해야 했을 일이다.

서버가 죽었을 때 자동으로 복구하는 기능 (Self-Healing)
=====
-----

디플로이먼트는 **`replicas` 에 적힌 개수를 계속 지킨다.**
파드가 죽으면 죽은 걸 감지하고 새로 하나 만들어낸다.

직접 확인해보자.

```bash
kubectl get pods              # 파드 3개 확인
kubectl delete pod [파드 이름] # 하나를 일부러 지운다
kubectl get pods              # 잠시 후 다시 3개
```

지운 파드는 사라지지만, **이름이 다른 새 파드가 하나 생겨 있다.**
서버가 예기치 않게 죽어도 사람이 개입하지 않고 원래 개수로 돌아온다.

앞에서 쿠버네티스의 장점으로 이야기한 **셀프 힐링**이 바로 이것이다.

> 파드를 직접 만들었을 때 `kubectl delete pod` 를 하면 그냥 없어졌다.
> 관리해주는 주체(디플로이먼트)가 있느냐 없느냐의 차이다.

새로운 버전의 서버로 업데이트 시키기
=====
-----

서버 코드를 수정해서 새 이미지를 만들었다고 하자.
이걸 반영하려면 이미지 태그를 바꾸고 다시 적용하면 된다.

```yaml
    spec:
      containers:
        - name: spring-container
          image: spring-server:v2    # v1 -> v2
```

```bash
kubectl apply -f spring-deployment.yaml
```

### 한 번에 다 바꾸지 않는다

디플로이먼트는 파드를 **전부 지우고 새로 만들지 않는다.**
하나씩 새 버전으로 갈아끼우면서 기존 파드를 지운다. (롤링 업데이트)

그래서 업데이트 중에도 **서비스가 멈추지 않는다.**

```bash
kubectl get pods -w    # -w 옵션으로 변화 과정을 지켜볼 수 있다
```

### 이전 버전으로 되돌리기

새 버전에 문제가 있으면 되돌린다.

```bash
kubectl rollout undo deployment/spring-deployment
```

배포 이력도 확인할 수 있다.

```bash
kubectl rollout status deployment/spring-deployment    # 진행 상황
kubectl rollout history deployment/spring-deployment   # 이력
```

[요약] 지금까지 나온 명령어 정리
=====
-----

```bash
# 디플로이먼트
kubectl apply -f [파일명].yaml
kubectl get deployments                                  # 축약: get deploy
kubectl delete deployment [디플로이먼트명]

# 서비스
kubectl get services                                     # 축약: get svc
kubectl delete service [서비스명]
kubectl port-forward service/[서비스명] 8080:8080

# 개수 조절
kubectl scale deployment/[디플로이먼트명] --replicas=5

# 업데이트 / 롤백
kubectl rollout status deployment/[디플로이먼트명]
kubectl rollout history deployment/[디플로이먼트명]
kubectl rollout undo deployment/[디플로이먼트명]

# 전체 조회
kubectl get all
```

[요약] 파드(Pod), 디플로이먼트(Deployment), 서비스(Service) 개념 정리
=====
-----

```
디플로이먼트 ──관리──▶ 파드 ◀──연결── 서비스
 (개수 유지)          (실행 단위)      (고정 주소)
```

| 리소스 | 역할 | 한 줄 정리 |
|---|---|---|
| 파드(Pod) | 프로그램을 실행하는 가장 작은 단위 | 컨테이너를 감싼 것 |
| 디플로이먼트(Deployment) | 파드를 몇 개 띄울지 관리 | 개수 유지, 셀프 힐링, 무중단 업데이트 |
| 서비스(Service) | 파드에 접근할 고정 주소 제공 | IP가 바뀌어도 같은 주소, 로드 밸런싱 |

- 실무에서 **파드를 직접 만드는 일은 거의 없다.** 대부분 디플로이먼트를 쓴다
- 디플로이먼트와 서비스는 **라벨(label)로 연결된다**
- 셋을 묶으면 "서버 N개를 띄우고, 죽으면 살리고, 하나의 주소로 접근한다"가 완성된다
