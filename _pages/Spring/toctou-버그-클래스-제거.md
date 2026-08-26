---
title:  "TOCTOU 한 건을 고치는 대신 버그 클래스를 없앴다"

categories:
  - Spring
tags:
  - AI
  - Claude Code
  - 동시성
  - Spring

date: 2026-05-10
thumbnail: "/assets/img/thumbnail/spring_thumbnail.webp"
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
// 원격 디렉토리는 셸 mkdir -p 로 원자적으로 보장한다.
// SFTP 의 stat/mkdir 루프는 동시 업로드 시 TOCTOU race 가 발생하므로 사용 금지.
String remoteDir = remoteFilePath.substring(0, remoteFilePath.lastIndexOf('/'));
if (!remoteDir.isEmpty()) {
    createRemoteDirectory(session, remoteDir);
}
```

- `mkdir -p` → "없으면 만들고 있으면 성공"을 커널이 원자적으로 처리
- check와 use 사이의 틈이 애초에 존재하지 않음
- 동시 호출이 몇 개가 들어오든 race 발생 불가
- 35줄 → 20줄, 그중 중요한 건 삭제된 15줄

<div class="diagram" role="img" aria-label="예외로 감싸는 방식과 틈 자체를 없애는 방식의 대비">
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
// 영향받은 행 수가 1이면 락 획득, 0이면 다른 스레드가 이미 진입했음을 의미한다.
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
| 원자적 위임 | 연산이 한 문장으로 표현될 때 (`mkdir -p`, 조건부 UPDATE) | 표현 가능한 연산이 제한적 |
| 비관락 | 여러 문장을 하나의 임계 구역으로 묶어야 할 때 | 락 대기, 데드락 가능성 |

- 첫 번째 코드의 시도: 사실상 낙관적 재시도 — 실패하면 다시 확인하는 방식
- 그러나 SFTP 디렉토리 생성은 훨씬 싼 원자적 연산으로 표현 가능
- 결론: 재시도 로직을 정교하게 다듬는 건 처음부터 잘못된 방향

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
