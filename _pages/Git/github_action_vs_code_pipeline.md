---
title:  "Github Action VS Code Pipeline"

categories:
  - git
tags:
  - git 
  - github
  - github action
  - code Pipeline

date: 2025-05-27
thumbnail: "/assets/img/thumbnail/github_thumbnail.png"
---


# Github action 이란
- Github에서 공식적으로 제공하는 CI / CD 툴
- 코드 변경 문제사항 검사
- 소프트웨어 빌드, 상용서버 배포
- 통계 데이터 수집

# 코어 개념

- **Workflow**
자동화된 전체 프로세스. 하나 이상의 Job으로 구성되고, Event에 의해 예약되거나 트리거될 수 있는 자동화된 절차를 말한다. ex) deploy.yml
Workflow 파일은 YAML으로 작성되고, Github Repository의 .github/workflows 폴더 아래에 저장된다. Github에게 YAML 파일로 정의한 자동화 동작을 전달하면, Github Actions는 해당 파일을 기반으로 그대로 실행시킨다.
- **Event**
Workflow를 트리거(실행)하는 특정 활동이나 규칙. ex) pull request, push 시 event 실행
- **Job**
- Job은 여러 Step으로 구성되고, 단일 가상 환경에서 실행된다. 다른 Job에 의존 관계를 가질 수도 있고, 독립적으로 병렬로 실행
- **Step**
Job 안에서 순차적으로 실행되는 프로세스 단위. step에서 명령을 내리거나, action을 실행할 수 있다.
- **Action**
job을 구성하기 위한 step들의 조합으로 구성된 독립적인 명령. workflow의 가장 작은 빌드 단위이다. workflow에서 action을 사용하기 위해서는 action이 step을 포함해야 한다. action을 구성하기 위해서 레포지토리와 상호작용하는 커스텀 코드를 만들 수도 있다. 사용자가 직접 커스터마이징하거나, 마켓플레이스에 있는 action을 가져다 사용할 수도 있다.
- **Runner**
Gitbub Action Runner 어플리케이션이 설치된 머신으로, Workflow가 실행될 인스턴스

ex)
```yaml
name: dmstjd1024-github-actions              # WorkFlow 이름
on:                                     # 트리거 하는 이벤트 명시
  push:                               # push 이벤트일때
    branches: [ master, dev ]         # 어떤 브랜치들
  pull_request:                       # 어떤 풀리퀘일때
    branches: [ master ]
    paths:                            # 특정 패턴을 설정하여 변경되었을 때 이벤트 실행
      - "**.js"
    schedule:
        - cron: '0 01 * * *'              # 새벽 1시 (https://crontab.guru 참조)
jobs:
  build:
    strategy:
      matrix:                           # 테스트 배포를 위한 빌드 matrix 구성
        node-version: [10.x, 12.x]

    runs-on: ubuntu-latest              # 어떤 OS로 실행
    steps:                              # Job이 가질 수 있는 동작 나열 step 독립적 프로세스
      - name: Checkout source code      # Step 이름
        uses: actions/checkout@v2       # Step에서 사용할 액션 (Github 마켓플레이스 action 사용가능)

      - name: My First Step             # step 이름
        run:                            # job에 할당된 자원 shell 이용하여 커맨드 라인 실행
          npm install
          npm test
          npm build
      - name: Cache yarn dependencies
uses: actions/cache@v1
id: yarn-cache
with:                           # action에 정의되는 input 파라미터 (환경 변수)
path: node_modules
key: ${{ runner.os }}-yarn-${{ hashFiles('**/yarn.lock') }}
restore-keys: |               
${{ runner.os }}-yarn-
Code Pipeline
```

## 가격 비교

 
|                | Github Action(Teams 플랜) | Code Pipeline                                                                                |
|----------------|-------------------------|----------------------------------------------------------------------------------------------|
|갯수별 비용| X| 활성 파이프라인(사용기간 30일 이상, 코드 1회 변경)<br/> 개당 1.00 USD(생성 후 첫 30일간 무료) <br/>※ 월별 무료 활성 파이프라인 1개 지원 |
|패키지 스토리지| 2GB| X|
|분(월별)| 3,000분| X|
|분당 요금| vCPU 2개 기준 $0.008 (약 10.80원)| X|
|월별 총 비용| $4 (연 결제 기준 $3.67)| Resource 에 따라 다양한 비용 발생 (측정 불가) <br/> ※ 월별 명세서로 측정 예정|


추가) CodeDeploy 비용
AWS 답변 : AWS CodeDeploy를 통해 Amazon EC2 인스턴스에 코드를 배포하는 데는 추가 비용이 부과되지 않습니다.