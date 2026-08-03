---
title:  "TOCTOU 한 건을 고치는 대신 버그 클래스를 없앴다"

categories:
  - AI
tags:
  - AI
  - Claude Code
  - 동시성
  - Spring

date: 2026-05-10
thumbnail: "/assets/img/thumbnail/sample.png"
---

## 문제: SFTP 업로드가 동시에 들어오면 터졌다

이 프로젝트는 사용자가 웹에서 버튼을 누르면 Hyperledger Fabric·Besu 네트워크를 Kubernetes 클러스터에 올려주는 플랫폼이다. 인프라 계층은 JSch로 원격 서버에 SSH/SFTP 접속해 bash 스크립트를 밀어 넣고 실행한다.

그 업로드 코드가 원격 디렉토리를 이렇게 만들고 있었다.

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

전형적인 TOCTOU(Time-of-check to time-of-use)다. `stat`으로 확인한 시점과 `mkdir`로 만드는 시점 사이에 다른 스레드가 끼어들 수 있다. 이미 catch 안에 catch를 겹쳐 "동시 생성이면 무시" 처리를 해뒀는데도 동시 업로드에서 실패가 났다. 예외 처리를 한 겹 더 두르면 잡히긴 하겠지만, 그건 race를 없앤 게 아니라 race의 증상만 막는 것이다.

## 원인 조사를 방해한 두 번째 결함

더 곤란했던 건 실패 원인을 못 봤다는 점이다. `ScriptResult`에 `exception`은 담겨 있는데 `errors` 리스트는 비어 있었다. 로그로 올라오는 건 errors 쪽이라, 실패한 결과 객체를 받아도 **왜 실패했는지가 어디에도 남지 않았다.**

`@Setter`가 붙어 있는 평범한 필드라서 예외를 설정해도 아무 부수 효과가 없던 게 원인이었다.

## 어떻게 고쳤나

### 1. 루프를 지우고 셸에 위임했다

개별 예외 처리를 보강하는 대신 루프 자체를 삭제했다. 원격 디렉토리 생성을 `mkdir -p`에 넘긴다.

```java
// 원격 디렉토리는 셸 mkdir -p 로 원자적으로 보장한다.
// SFTP 의 stat/mkdir 루프는 동시 업로드 시 TOCTOU race 가 발생하므로 사용 금지.
String remoteDir = remoteFilePath.substring(0, remoteFilePath.lastIndexOf('/'));
if (!remoteDir.isEmpty()) {
    createRemoteDirectory(session, remoteDir);
}
```

`mkdir -p`는 "없으면 만들고 있으면 성공"을 커널이 원자적으로 처리한다. check와 use 사이의 틈이 애초에 존재하지 않으므로, 동시 호출이 몇 개가 들어오든 race가 발생할 수 없다. 35줄이 20줄로 줄었고 그중 중요한 건 삭제된 15줄이다.

### 2. 예외 설정에 부수 효과를 심었다

`@Setter`를 떼고 setter를 직접 구현했다.

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

이제 예외를 담는 모든 호출부가 자동으로 errors에도 흔적을 남긴다. 호출부를 하나하나 고치는 대신 진입점 하나를 막아 "빈 errors로 실패 결과가 반환되는" 상태를 구조적으로 불가능하게 만든 것이다.

### 3. 같은 클래스를 상위 계층에서도 막았다

SFTP 사건을 정리하고 나서 같은 모양의 결함이 위쪽에도 있다는 걸 확인했다. 네트워크 생성 버튼을 빠르게 두 번 누르면 비동기 작업이 두 번 진입한다. 여기에는 두 가지 다른 도구를 썼다.

**중복 진입은 원자적 UPDATE로.** `INSTALLING` 상태를 새로 만들고, `CREATED → INSTALLING` 전환을 UPDATE 한 방으로 처리한다.

```java
// status = CREATED → INSTALLING 원자적 UPDATE.
// 영향받은 행 수가 1이면 락 획득, 0이면 다른 스레드가 이미 진입했음을 의미한다.
int markInstalling(@Param("id") String id);
```

영향 행 수가 0이면 즉시 return한다. DB가 UPDATE의 원자성을 보장하므로 별도 락이 필요 없다.

**검증-저장 구간의 TOCTOU는 비관락으로.**

```java
@Lock(LockModeType.PESSIMISTIC_WRITE)
@Query("SELECT a FROM Agency a WHERE a.id = :id AND a.delYn = false")
Optional<Agency> findByIdForUpdate(@Param("id") String id);
```

"이미 진행 중인 네트워크가 있는지 검증 → 새 레코드 저장" 사이에 다른 요청이 끼어드는 걸 막아야 하는데, 이건 UPDATE 한 문장으로 표현되지 않는다. 여러 문장을 하나의 임계 구역으로 묶어야 하므로 비관락이 맞다.

## 세 가지 도구의 선택 기준

| 방식 | 쓸 때 | 비용 |
|---|---|---|
| 낙관적 재시도 | 충돌이 드물고 재시도가 안전(멱등)할 때 | 충돌이 잦으면 재시도 폭풍 |
| 원자적 위임 | 연산이 한 문장으로 표현될 때 (`mkdir -p`, 조건부 UPDATE) | 표현 가능한 연산이 제한적 |
| 비관락 | 여러 문장을 하나의 임계 구역으로 묶어야 할 때 | 락 대기, 데드락 가능성 |

첫 번째 코드가 시도한 게 사실상 낙관적 재시도였다. 실패하면 다시 확인해보는 방식. 그런데 SFTP 디렉토리 생성은 그보다 훨씬 싼 원자적 연산으로 표현할 수 있었으므로, 재시도 로직을 정교하게 다듬는 건 처음부터 잘못된 방향이었다.

## 남는 교훈

**버그 하나를 고칠 때 "이 버그의 클래스가 뭔가"를 먼저 묻는 게 이득일 때가 있다.** SFTP 한 건에 예외 처리를 덧대는 데는 5분이면 됐다. 대신 "check-then-act 패턴이 어디에 또 있나"를 물었더니 네트워크 생성 경로에서 같은 모양이 나왔다.

**예외 처리를 겹겹이 두르고 있다면, 그건 설계가 잘못됐다는 신호일 가능성이 높다.** catch 안의 catch는 "여기서 뭔가 근본적으로 잘못되고 있다"는 냄새였는데, 첫 작성 시점에는 그게 방어 코드처럼 보였을 것이다.

**진단 가능성은 기능이다.** 실패를 못 고치게 만든 건 race가 아니라 빈 errors 리스트였다. 실패 경로가 자기 원인을 남기지 않으면, 그 위의 모든 수정은 추측이 된다.
