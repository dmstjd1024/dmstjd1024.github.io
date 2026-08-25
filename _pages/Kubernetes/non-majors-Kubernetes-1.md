---
title: "쿠버네티스"

categories:
 - Kubernetes, Docker
tags:
  - Kubernetes
  - Docker

date: 2025-05-28
thumbnail: "/assets/img/thumbnail/kubernetes_thumbnail.png"
---
## 쿠버네티스란,
다수의 컨테이너를 효율적으로 배포, 확장 및 관리 하기 위한 오픈소스 시스템
Docker Compose의 확장판이라고 생각
## 쿠버네티스 장점
- 컨테이너 관리 자동화(배포, 확장, 업데이트)
- 부하 분산 (로드 밸런싱)
- 쉬운 스케일링
- 셀프 힐링

## 파드(Pod) 란?,
하나의 프로그램을 실행시키는 단위
- 쿠버네티스에서 가장 작은 단위
- 일반적으로 하나의 파드가 하나의 컨테이너를 가진다. (예외로 여러 컨테이너를 가지는 경우도 있다.)

## Nginx 파드 예시

```yaml
apiVersion: v1
kind: Pod

metadata:
  name: nginx-pod

spec:
  containers:
    - name: nginx-container
      image: nginx
      ports:
        - containerPort: 80 # 컨테이너가 사용하는 포트
```
- 파드 조회 명령어 `kubectl get pods`
매니페스트 파일(Manifest File) 이라고 부른다.
`kubectl apply -f nginx-pod.yaml` 명령어로 파드를 생성할 수 있다.

## 파드(Pod)로 띄운 프로그램에 접속이 안 되는 이유
- 도커에 대해서 공부했을 때는 컨테이너 내부와 컨테이너 외부의 네트워크가 서로 독립적으로 분리
쿠버네티스에서는 파드(Pod) 내부의 네트워크를 컨테이너가 공유해서 같이 사용
- 파드(Pod) 네트워크는 로컬 컴퓨터의 네트워크와 독립적 분리 -> 외부에서 접근 불가
### 2가지 접근 방법
1. 파드 내부로 들어가서 접근
`kubectl exec -it nginx-pod -- bash`
2. 파드 의 내부네트워크를 외부에서도 접속할 수 있도록 포트 포워딩 활용
`sudo kubectl port-forward pod/nginx-pod 80:80`

<div class="diagram" role="img" aria-label="파드 네트워크가 분리되어 있어 접속이 안 되는 구조">
{% include diagrams/k8s--pod-network.svg %}
</div>

파드 삭제
`kubectl delete pod nginx-pod`

## 백앤드 서버 파드로 띄우기
Spring boot 서버에 Dockerfile 작성
```dockerfile
FROM openjdk:17-jdk

COPY build/libs/*SNAPSHOT.jar app.jar
LABEL authors="jeon-eunseong"

ENTRYPOINT ["java","-jar","/app.jar"]
```
쿠버네티스 파드 매니페스트 파일 작성
```yaml
apiVersion: v1
kind: Pod

metadata:
  name: spring-pod
  labels:
    app: spring-app

spec:
  containers:
    - name: spring-container
      image: spring-server
      ports:
        - containerPort: 8080
```
등록 명령어
`kubectl apply -f spring-pod.yaml`
조회 명령어
`kubectl get pods`
ImagePullBackOff 오류 발생
## 이미지가 없다고 에러가 뜨는 이유
이미지 풀 정책(Image pull Policy) 때문에 발생
### 이미지 풀 정책
yaml 을 읽어서 Pod 생성 시, 이미지를 어떻게 Pull 할 지에 대한 정책
- `Always`: 로컬 말고, 무조건 레지스트리(Dockerhub, ECR(원격 이미지 저장소)) 에서 가져온다.
- `IfNotPresent`: 로컬에 이미지 먼저 가져오고, 없으면 레지스트리에서 가져온다.
- `Never`: 로컬에서만 이미지를 가져온다.

`image` 뒤에 `version`을 명시하지 않거나, latest 태그를 사용하는 경우 `Always` 가 기본값
`lastest` 태그를 사용하지 않는다면 `IfNotPresent` 가 기본값

<div class="diagram" role="img" aria-label="이미지 풀 정책과 태그에 따른 기본값">
{% include diagrams/k8s--image-pull-policy.svg %}
</div>

### 해결 방법
이미지 풀 정책을 `IfNotPresent` 로 변경
```yaml
...
      ports:
        - containerPort: 8080
      imagePullPolicy: IfNotPresent  
```


