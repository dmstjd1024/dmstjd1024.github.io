---
title: "도커 교과서 4장"

categories:
 - Docker
tags:
 - docker

date: 2025-07-06
thumbnail: "/assets/img/thumbnail/docker_thumbnail.png"
---

## 애플리케이션 소스 코드에서 도커 이미지까지

## Dockerfile 가 있는데 빌드서버가 필요할까?
- 빌드 툴 체인을 통해 한번에 패키징해서 공유하면 편리
- 도커만 갖춰진다면 컨테이너를 통해 어떤 환경에서든 애플리케이션 빌드, 실행 가능
- 도커허브를 통해 빌드도구가 내장된 공식 이미지 제공

## 애플리케이션 빌드 실전 예제

```dockerfile
FROM diamol/maven AS builder

WORKDIR /usr/src/iotd
COPY pom.xml .
RUN mvn -B dependency:go-offline

COPY . .
RUN mvn package

# app
FROM diamol/openjdk

WORKDIR /app
COPY --from=builder /usr/src/iotd/target/iotd-service-0.1.0.jar .

EXPOSE 80
ENTRYPOINT ["java", "-jar", "/app/iotd-service-0.1.0.jar"]
```
FROM 인스트럭션 이 여러개 있으므로 멀티 스테이지 빌드 적용된 스크립트빌드 절차가 정의

#### builder 하는 일
- diamol/maven 메이븐 OpenJDK 포함
- 이미지에 작업 디렉토리 만든 다음 pom.xml 파일 복사하며 시작. 메이븐 수행할 빌드절차 정의
- 첫번쨰 RUN 인스트럭션에서 메이븐이 실행돼 필요한 의존 모듈 다운.
  - 상당한 시간이 걸리기에 별도 단계 분리하여 레이어 캐시 활용
  - 새로운 의존 모듈이 추가될 경우, 이 단계 다시 실행, 없으면 이미지 캐시 재사용
- COPY . . 인스트럭션 통해 소스 코드 복사 => 도커 빌드가 실행중인 디렉터리에 포함된 모든 파일과 서브 디렉터리를 현재 이미지 내 작업 디렉토리로 복사
- mvn package 명령어 실행. 

#### builder 단계 이후
- 작업 디렉터리 만든 후, builder 단계에서 만든 JAR 파일 복사
- 80포트를 주시하는 애플리케이션 -> EXPOSE 인스트럭션을 통해 외부로 공개
- ENTRYPOINT 인스트럭션 : CMD 인스트럭션 같은 기능 

## 멀티 스테이지 Dockerfile 스크립트 이해하기(왜 유용한지)
- 표준화 : 버전 차이로 인한 실패 감소
- 성능 향상 : 캐싱
- 빌드과정을 조정해 이미지를 가능 한 작게 유지
- 