---
title:  "SFTP 동시성 오류를 고치다 같은 패턴을 상위 계층에서 둘 더 찾았다"
description: "SFTP 한 건이 아니라 check-then-act 패턴 전체를"

categories:
  - Spring
tags:
  - AI
  - Claude Code
  - 동시성
  - Spring

date: 2026-05-10
thumbnail: "/assets/img/thumbnail/spring_thumbnail.webp"
card_thumbnail: "/assets/img/thumbnail/spring_card.webp"
---
## 문제: SFTP 업로드가 동시에 들어오면 터졌다

- 프로젝트: 웹 버튼 클릭 → Hyperledger Fabric·Besu 네트워크를 Kubernetes 클러스터에 배포하는 플랫폼
- 인프라 계층: JSch로 원격 서버에 SSH/SFTP 접속 → bash 스크립트 전송 후 실행

- 해당 업로드 코드의 원격 디렉토리 생성 방식

```java
for (String dir : dirs) {
    currentPath.append("/").append(dir);
    try {
        sftpChannel.stat(currentPath.toString());   // 있나?
    } catch (Exception statEx) {
        try {
            sftpChannel.mkdir(currentPath.toString());  // 없으니 만들자
        } catch (Exception mkdirEx) {
            sftpChannel.stat(currentPath.toString());   // 남이 먼저 만들었나?
        }
    }
}
```

- 전형적인 TOCTOU(Time-of-check to time-of-use)
- `stat` 확인 시점과 `mkdir` 생성 시점 사이에 다른 스레드 진입 가능
- catch 안에 catch로 "동시 생성이면 무시" 처리를 해뒀는데도 동시 업로드에서 실패

- 예외 처리를 한 겹 더 두르면 포착은 가능
- 단 그건 race 제거가 아니라 race 증상 차단

<div class="diagram" role="img" aria-label="확인과 생성 사이의 틈에 다른 스레드가 끼어드는 구조">
{% include diagrams/toctou--race-window.svg %}
</div>

## 원인 조사를 방해한 두 번째 결함

- 더 곤란했던 점: 실패 원인 미확인

- `ScriptResult`에 `exception`은 담김
- `errors` 리스트는 비어 있음
- 로그로 올라오는 건 errors 쪽
- 결과: 실패한 결과 객체를 받아도 **왜 실패했는지가 어디에도 남지 않음**

- 원인: `@Setter`가 붙은 평범한 필드 → 예외를 설정해도 아무 부수 효과 없음

## 어떻게 고쳤나

### 1. 루프를 지우고 셸에 위임했다

- 개별 예외 처리 보강 대신 루프 자체를 삭제
- 원격 디렉토리 생성을 `mkdir -p`에 위임

```java
// 원격 디렉토리 생성과 이미 존재하는 디렉토리 처리는 mkdir -p 에 위임한다.
// SFTP 의 stat/mkdir 루프는 동시 업로드 시 TOCTOU race 가 발생하므로 사용 금지.
String remoteDir = remoteFilePath.substring(0, remoteFilePath.lastIndexOf('/'));
if (!remoteDir.isEmpty()) {
    createRemoteDirectory(session, remoteDir);
}
```

- `mkdir -p`는 부모 디렉토리를 순서대로 만들며, 이미 존재하는 디렉토리는 성공으로 처리한다
- 전체 경로 생성이 단일 시스템 호출인 것은 아니다. 애플리케이션의 `stat → mkdir` 루프와 동시 생성 처리를 검증된 도구에 위임한 것이다
- 다른 작업이 경로를 삭제·교체하는 경쟁까지 막는 것은 아니다
- 35줄 → 20줄, 그중 중요한 건 삭제된 15줄

<div class="diagram" role="img" aria-label="직접 예외 처리를 겹치는 방식과 디렉토리 생성을 도구에 위임하는 방식의 대비">
{% include diagrams/toctou--class-vs-instance.svg %}
</div>

### 2. 예외 설정에 부수 효과를 심었다

- `@Setter` 제거 후 setter 직접 구현

```java
public void setException(Exception exception) {
    this.exception = exception;
    if (exception != null) {
        String msg = exception.getMessage();
        addError("[" + exception.getClass().getSimpleName() + "] "
            + (msg == null ? "(no message)" : msg));
    }
}
```

- 효과: 예외를 담는 모든 호출부가 자동으로 errors에도 흔적을 남김
- 방식: 호출부를 하나하나 수정하는 대신 진입점 하나를 차단
- 효과: "빈 errors로 실패 결과가 반환되는" 상태를 구조적으로 불가능화

### 3. 같은 클래스를 상위 계층에서도 막았다

- SFTP 사건 정리 후, 같은 모양의 결함이 상위 계층에도 존재함을 확인
- 재현: 네트워크 생성 버튼을 빠르게 두 번 클릭 → 비동기 작업 2회 진입
- 사용한 도구: 두 가지

**중복 진입 → 원자적 UPDATE**

- `INSTALLING` 상태 신설
- `CREATED → INSTALLING` 전환을 UPDATE 한 방으로 처리

```java
// status = CREATED → INSTALLING 원자적 UPDATE.
// 영향받은 행 수가 1이면 상태 선점 성공, 0이면 CREATED 조건을 만족하는 행이 없음을 의미한다.
int markInstalling(@Param("id") String id);
```

- 영향 행 수 0 → 즉시 return
- DB가 UPDATE의 원자성을 보장 → 별도 락 불필요

**검증-저장 구간의 TOCTOU → 비관락**

```java
@Lock(LockModeType.PESSIMISTIC_WRITE)
@Query("SELECT a FROM Agency a WHERE a.id = :id AND a.delYn = false")
Optional<Agency> findByIdForUpdate(@Param("id") String id);
```

- 막아야 할 구간: "진행 중 네트워크 검증 → 새 레코드 저장" 사이의 타 요청 진입
- UPDATE 한 문장으로 표현 불가
- 여러 문장을 하나의 임계 구역으로 묶어야 하므로 비관락이 적합

## 세 가지 도구의 선택 기준

| 방식 | 쓸 때 | 비용 |
|---|---|---|
| 낙관적 재시도 | 충돌이 드물고 재시도가 안전(멱등)할 때 | 충돌이 잦으면 재시도 폭풍 |
| 검증된 도구·원자적 연산에 위임 | 디렉토리 생성은 `mkdir -p`, 상태 선점은 조건부 UPDATE로 맡길 때 | 도구마다 보장 범위가 다름 |
| 비관락 | 여러 문장을 하나의 임계 구역으로 묶어야 할 때 | 락 대기, 데드락 가능성 |

- 첫 번째 코드의 시도: 사실상 낙관적 재시도 — 실패하면 다시 확인하는 방식
- 이 디렉토리 생성 경로에서는 `mkdir -p`로 이미 존재하는 경우의 처리를 위임할 수 있었다
- 결론: 직접 만든 재시도 루프를 늘리기 전에 기존 도구의 보장 범위를 확인한다

## 남는 교훈

**버그 하나를 고칠 때 "이 버그의 클래스가 뭔가"를 먼저 묻는 게 이득일 때가 있다.**

- SFTP 한 건에 예외 처리 덧대기: 5분 소요
- 대신 던진 질문 — "check-then-act 패턴이 어디에 또 있나"
- 결과: 네트워크 생성 경로에서 동일 형태 발견

**예외 처리를 겹겹이 두르고 있다면, 그건 설계가 잘못됐다는 신호일 가능성이 높다.**

- catch 안의 catch = "여기서 뭔가 근본적으로 잘못되고 있다"는 냄새
- 첫 작성 시점의 인상: 방어 코드

**진단 가능성은 기능이다.**

- 실패를 못 고치게 만든 진짜 원인: race가 아니라 빈 errors 리스트
- 실패 경로가 자기 원인을 남기지 않으면 그 위의 모든 수정은 추측
