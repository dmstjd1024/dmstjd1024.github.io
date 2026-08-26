---
title: "JIRA 활용 - JQL 심화와 자동화, 그리고 연동"

categories:
 - Jira
tags:
  - Jira
  - atlassian
  - jql
  - 자동화
  - 협업

date: 2026-08-20
thumbnail: "/assets/img/thumbnail/jira_thumbnail.png"
---
> [JIRA 입문 - 개념부터 기본 사용법까지](/Jira/jira-basic.html)에서 이어지는 글이다.
> 1편이 "JIRA가 무엇이고 어떻게 쓰는가"였다면, 이 글은 "손으로 하던 일을 어떻게 줄이는가"에 대한 글이다.

들어가며
=====
-----
JIRA를 며칠 써보면 반복 작업이 눈에 띄기 시작한다.
- 매일 아침 내 이슈를 찾으려고 같은 필터를 다시 만든다
- PR을 머지하고 나서 JIRA에 들어가 상태를 `완료`로 바꾼다
- 스프린트가 끝나면 완료된 이슈를 손으로 정리해 릴리스 노트를 만든다

이 글에서 다루는 세 가지가 그 반복을 줄인다.
1. **JQL** — 원하는 이슈를 정확히 뽑아내는 검색 문법
2. **자동화(Automation)** — 조건이 맞으면 JIRA가 알아서 처리하게 만드는 규칙
3. **연동(Integration)** — GitHub, Slack과 붙여서 JIRA에 들어가지 않고도 흐름이 이어지게 만들기

JQL 심화
=====
-----
JQL(Jira Query Language)은 이슈를 조건으로 걸러내는 검색 문법이다. SQL의 `WHERE` 절과 비슷하지만, `SELECT`나 `FROM`은 없다. **조건과 정렬만 쓴다.**

```sql
project = SHOP AND status = "In Progress" ORDER BY created DESC
```

검색창의 **기본(Basic)** 모드에서 **JQL** 모드로 전환하면 직접 입력할 수 있다.

## 기본 구조

```
필드  연산자  값  [AND/OR  ...]  [ORDER BY  필드  ASC/DESC]
```

- 필드명과 값에 **공백이 있으면 큰따옴표**로 감싼다 → `status = "In Progress"`
- 대소문자는 구분하지 않지만, 값에 한글이 들어가면 따옴표를 쓰는 편이 안전하다

## 연산자

| 연산자 | 의미 | 예시 |
|---|---|---|
| `=` / `!=` | 같다 / 다르다 | `status = Done` |
| `>` `<` `>=` `<=` | 크다 / 작다 (날짜, 숫자) | `created >= -7d` |
| `IN` / `NOT IN` | 목록 중 하나 | `status IN (Done, Closed)` |
| `~` / `!~` | 포함한다 / 포함하지 않는다 (텍스트) | `summary ~ "결제"` |
| `IS EMPTY` / `IS NOT EMPTY` | 비어 있다 / 값이 있다 | `assignee IS EMPTY` |
| `WAS` / `WAS NOT` | 과거에 그 값이었다 | `status WAS "Rejected"` |
| `CHANGED` | 값이 바뀐 적 있다 | `status CHANGED AFTER -1d` |

`~`는 **부분 일치 검색**이다. `summary ~ "결제"`는 제목에 "결제"가 들어간 이슈를 모두 찾는다.

`WAS`와 `CHANGED`가 JQL의 진짜 강점이다. 현재 상태가 아니라 **이력**을 검색한다.

```sql
-- 한 번이라도 반려된 적 있는 이슈 (지금은 완료여도 잡힌다)
status WAS "Rejected"

-- 어제 이후 담당자가 바뀐 이슈
assignee CHANGED AFTER -1d
```

## 날짜 표현

상대적인 시간을 문자로 쓴다.

| 표기 | 의미 |
|---|---|
| `-1d` | 1일 전 |
| `-1w` | 1주 전 |
| `-30m` | 30분 전 |
| `startOfDay()` | 오늘 0시 |
| `startOfWeek()` | 이번 주 시작 |
| `endOfMonth()` | 이번 달 말 |

```sql
-- 오늘 생성된 이슈
created >= startOfDay()

-- 이번 주에 완료된 이슈
resolutiondate >= startOfWeek()

-- 마감일이 지났는데 아직 안 끝난 이슈
duedate < now() AND status != Done
```

## 자주 쓰는 함수

| 함수 | 의미 |
|---|---|
| `currentUser()` | 지금 로그인한 사용자 |
| `openSprints()` | 진행 중인 스프린트 |
| `closedSprints()` | 종료된 스프린트 |
| `futureSprints()` | 아직 시작 안 한 스프린트 |
| `membersOf("그룹명")` | 특정 그룹에 속한 사용자들 |
| `linkedIssues("KEY")` | 특정 이슈에 연결된 이슈들 |
| `now()` | 현재 시각 |

`currentUser()`를 쓰면 **필터 하나를 팀 전체가 공유**할 수 있다. 각자 자기 이슈만 보이기 때문이다.

## 실전 쿼리 모음

바로 복사해서 쓸 수 있는 것들이다.

```sql
-- 1. 내가 오늘 할 일
assignee = currentUser() AND status != Done AND sprint IN openSprints()
ORDER BY priority DESC

-- 2. 내가 리뷰해야 할 이슈
status = "In Review" AND assignee != currentUser()
AND sprint IN openSprints()

-- 3. 담당자가 없어서 방치된 이슈
project = SHOP AND assignee IS EMPTY AND status = "To Do"
ORDER BY created ASC

-- 4. 3일 넘게 진행 중인 이슈 (막혀 있을 가능성)
status = "In Progress" AND status CHANGED BEFORE -3d
ORDER BY updated ASC

-- 5. 이번 스프린트에서 새로 들어온 이슈 (스프린트 중간 추가분)
sprint IN openSprints() AND created >= startOfWeek()

-- 6. 이번 릴리스에 포함될 미완료 이슈
fixVersion = "v2.1.0" AND status != Done

-- 7. 최근 일주일간 생성된 버그
project = SHOP AND issuetype = Bug AND created >= -1w
ORDER BY priority DESC

-- 8. 오래 방치된 백로그 (한 달 넘게 업데이트 없음)
project = SHOP AND sprint IS EMPTY AND updated <= -30d

-- 9. 내가 보고했는데 아직 안 끝난 이슈
reporter = currentUser() AND resolution = Unresolved

-- 10. 우리 팀 이슈 중 마감 임박
assignee IN membersOf("backend-team") AND duedate <= 3d AND status != Done
```

4번 쿼리가 특히 쓸모 있다. `status CHANGED BEFORE -3d`는 "3일 전에 이미 진행 중으로 바뀌었고 아직 그대로"라는 뜻이라, **막혀 있는 작업**을 찾아준다.

## 필터로 저장하기

매번 입력하지 않고 저장해서 쓴다.

1. JQL로 검색 실행
2. **다른 이름으로 저장(Save as)** 클릭
3. 이름 지정 → 저장

저장한 필터로 할 수 있는 것

- **공유**: 팀·프로젝트 단위로 공개 범위 설정
- **구독(Subscription)**: 정해진 주기로 결과를 메일로 받기 (예: 매일 아침 9시)
- **대시보드에 올리기**: 아래에서 설명
- **보드 만들기**: 필터 결과를 그대로 보드로 사용

## 대시보드 구성

여러 필터 결과를 한 화면에 모아 보는 곳이다. **대시보드 → 대시보드 만들기**로 생성하고, **가젯(Gadget)** 을 추가해 채운다.

자주 쓰는 가젯

| 가젯 | 용도 |
|---|---|
| 필터 결과(Filter Results) | 저장한 필터의 이슈 목록을 표로 표시 |
| 원형 차트(Pie Chart) | 담당자별·상태별 비율 |
| 생성 대 해결(Created vs Resolved) | 새로 생기는 속도 vs 처리하는 속도 |
| 스프린트 번다운 | 스프린트 잔여 작업량 추이 |
| 할당된 작업(Assigned to Me) | 내 이슈 |

**생성 대 해결** 차트는 팀 상태를 판단하는 데 유용하다. 생성 곡선이 해결 곡선보다 계속 위에 있으면 일이 쌓이고 있다는 뜻이다.

자동화(Automation)
=====
-----
반복 작업을 규칙으로 만들어 JIRA가 대신 처리하게 한다. **코드 없이 화면에서 설정**한다.

**프로젝트 설정 → 자동화(Automation)** 에서 규칙을 만든다.

## 규칙의 3단 구조

<div class="diagram" role="img" aria-label="자동화 규칙이 트리거, 조건, 액션 세 단계로 흐르는 구조">
{% include diagrams/jira--automation-rule.svg %}
</div>

- **트리거**: 규칙이 실행되는 시점 (이슈 생성됨, 상태 변경됨, 매일 오전 9시 ...)
- **조건**: 실행할지 말지 판단 (이슈 타입이 버그일 때만, 우선순위가 High일 때만 ...)
- 조건은 **생략 가능**하다. 트리거되면 무조건 실행한다는 뜻이다
- **액션**: 실제 수행 (필드 변경, 댓글 달기, 하위 이슈 생성, Slack 알림 ...)

## 주요 트리거

| 트리거 | 언제 실행되나 |
|---|---|
| 이슈 생성됨(Issue created) | 새 이슈가 만들어질 때 |
| 이슈 전환됨(Issue transitioned) | 상태가 바뀔 때 |
| 필드 값 변경됨(Field value changed) | 특정 필드가 수정될 때 |
| 예약(Scheduled) | 정해진 시각·주기마다 |
| 이슈에 댓글 달림 | 댓글이 추가될 때 |
| 수동 트리거(Manual) | 사용자가 버튼을 눌렀을 때 |

**예약 트리거**는 JQL과 함께 쓴다. "매일 9시에 이 JQL에 걸리는 이슈들에 대해 실행" 형태다.

## 실전 규칙 예시

### 1. 하위 작업이 모두 끝나면 부모 이슈 완료

```
트리거: 이슈 전환됨 (→ 완료)
조건: 이슈 타입 = 서브태스크
조건: 같은 부모의 모든 서브태스크가 완료 상태
액션: 부모 이슈를 완료로 전환
```

서브태스크를 다 끝내고도 부모 이슈를 안 닫아서 보드에 남아 있는 상황을 막는다.

### 2. 작업 시작하면 담당자 자동 지정

```
트리거: 이슈 전환됨 (→ 진행 중)
조건: 담당자가 비어 있음
액션: 담당자를 = 방금 상태를 바꾼 사람
```

### 3. 막힌 이슈 매일 알림

```
트리거: 예약 (매일 오전 10시)
       JQL: status = "In Progress" AND status CHANGED BEFORE -3d
액션: Slack 메시지 전송
      "3일 넘게 진행 중: {{issue.key}} {{issue.summary}}"
```

앞에서 만든 4번 JQL을 그대로 쓴다. **JQL과 자동화는 이렇게 붙여 쓸 때 위력이 나온다.**

### 4. 긴급 버그는 우선순위 자동 설정 + 팀 알림

```
트리거: 이슈 생성됨
조건: 이슈 타입 = Bug AND 우선순위 = Highest
액션: 담당자를 QA 리드로 지정
액션: 댓글 추가 "긴급 버그로 등록되었습니다."
액션: Slack #alert 채널로 전송
```

### 5. 마감일 임박 알림

```
트리거: 예약 (매일 오전 9시)
       JQL: duedate <= 2d AND status != Done
액션: 담당자에게 이메일 발송
```

### 6. 스프린트 종료 시 미완료 이슈 백로그로

```
트리거: 스프린트 완료됨
조건: 상태 != 완료
액션: 이슈를 백로그로 이동
액션: 댓글 추가 "이전 스프린트에서 완료되지 않아 백로그로 이동했습니다."
```

## 스마트 값(Smart Values)

액션 안에서 `{{ }}` 문법으로 이슈 정보를 꺼내 쓴다. 템플릿 변수라고 생각하면 된다.

| 스마트 값 | 의미 |
|---|---|
| `{{issue.key}}` | 이슈 키 (SHOP-101) |
| `{{issue.summary}}` | 제목 |
| `{{issue.assignee.displayName}}` | 담당자 이름 |
| `{{issue.status.name}}` | 현재 상태 |
| `{{issue.url}}` | 이슈 링크 |
| `{{now}}` | 현재 시각 |
| `{{initiator.displayName}}` | 규칙을 발동시킨 사람 |

## 자동화 만들 때 주의할 점

- **규칙이 규칙을 부르는 무한 루프**를 조심한다. "이슈가 수정되면 → 필드를 수정한다" 같은 규칙은 자기 자신을 다시 발동시킨다. 설정에 *다른 규칙 실행 허용* 옵션이 있는데, 켤 때 특히 주의한다
- **감사 로그(Audit log)** 를 먼저 본다. 규칙이 안 도는 것 같으면 여기에 실행 이력과 실패 원인이 남는다
- **실행 횟수 제한**이 요금제별로 있다. 예약 규칙을 너무 잦은 주기로 만들면 금방 소진된다
- **처음엔 알림만 하는 규칙부터** 만든다. 상태를 바꾸거나 이슈를 옮기는 규칙은 잘못 만들면 되돌리기 번거롭다

Git 연동
=====
-----
1편에서 커밋 메시지에 이슈 키를 넣으면 연결된다고 했다. 여기서는 그 이상을 다룬다.

## 스마트 커밋(Smart Commits)

커밋 메시지에 **명령어를 넣어 JIRA를 조작**할 수 있다.

```
<이슈키> #<명령어> <인자>
```

| 명령어 | 동작 |
|---|---|
| `#comment` | 이슈에 댓글 추가 |
| `#time` | 작업 시간 기록 |
| `#<전환이름>` | 상태 전환 (예: `#done`) |

```bash
git commit -m "SHOP-101 #comment PG사 연동 완료, 테스트 대기 #time 3h"

git commit -m "SHOP-102 #time 2h 30m #comment 리팩터링 완료 #done"
```

- 여러 명령어를 한 줄에 이어 쓸 수 있다
- 상태 전환 이름에 공백이 있으면 하이픈으로 바꾼다 (`In Review` → `#in-review`)
- **동작하려면 JIRA 계정과 Git 호스팅 계정의 이메일이 같아야 한다.** 안 되는 대부분의 원인이 이것이다

## 브랜치 전략과 이슈 키

브랜치명에 이슈 키를 넣으면 이슈 화면에서 브랜치·PR 상태를 볼 수 있다.

```bash
git switch -c feature/SHOP-101-card-payment
git switch -c bugfix/SHOP-205-order-status
```

이슈 화면의 **개발(Development)** 영역에서 연결된 브랜치, 커밋, PR, 빌드 상태가 한 번에 보인다.

<div class="diagram" role="img" aria-label="이슈 키가 브랜치와 커밋을 거쳐 지라 이슈로 연결되는 흐름">
{% include diagrams/jira--git-link.svg %}
</div>

## 이슈 키 강제하기

팀에서 이슈 키 붙이기를 깜빡하는 경우가 많다. Git 훅으로 막을 수 있다.

`.git/hooks/commit-msg` 파일:

```bash
#!/bin/sh
# 커밋 메시지에 이슈 키(예: SHOP-123)가 있는지 검사

if ! grep -qE '[A-Z]+-[0-9]+' "$1"; then
  echo "커밋 메시지에 JIRA 이슈 키가 없습니다. (예: SHOP-101 결제 연동)"
  exit 1
fi
```

```bash
chmod +x .git/hooks/commit-msg
```

- `exit 1`로 종료하면 커밋이 취소된다
- `.git/hooks/`는 git으로 공유되지 않으므로, 팀 전체 적용은 husky 같은 도구나 서버 훅을 쓴다

## GitHub Actions로 상태 자동 변경

PR이 머지되면 이슈를 완료로 바꾸는 것은 JIRA 자동화보다 GitHub Actions 쪽이 편할 때가 있다.

```yaml
name: JIRA 이슈 완료 처리

on:
  pull_request:
    types: [closed]

jobs:
  transition:
    if: github.event.pull_request.merged == true
    runs-on: ubuntu-latest
    steps:
      - name: JIRA 로그인
        uses: atlassian/gajira-login@master
        env:
          JIRA_BASE_URL: ${{ secrets.JIRA_BASE_URL }}
          JIRA_USER_EMAIL: ${{ secrets.JIRA_USER_EMAIL }}
          JIRA_API_TOKEN: ${{ secrets.JIRA_API_TOKEN }}

      - name: 브랜치명에서 이슈 키 추출
        id: issue
        run: |
          KEY=$(echo "${{ github.event.pull_request.head.ref }}" \
            | grep -oE '[A-Z]+-[0-9]+' | head -1)
          echo "key=$KEY" >> "$GITHUB_OUTPUT"

      - name: 이슈를 완료로 전환
        if: steps.issue.outputs.key != ''
        uses: atlassian/gajira-transition@master
        with:
          issue: ${{ steps.issue.outputs.key }}
          transition: "완료"
```

- `JIRA_API_TOKEN`은 Atlassian 계정 설정에서 발급받아 GitHub Secrets에 등록한다
- `transition` 값은 **워크플로우에 정의된 전환 이름과 정확히 일치**해야 한다

Slack 연동
=====
-----
개발자가 하루 종일 보는 곳은 JIRA가 아니라 Slack이다. 알림을 Slack으로 보내면 확인율이 올라간다.

## 공식 앱 설치

Slack 앱 디렉터리에서 **Jira Cloud for Slack**을 설치하면 아래가 가능하다.

- 채널에 프로젝트·필터를 구독해 이슈 변경 알림 받기
- Slack에서 바로 이슈 생성
- JIRA 링크를 붙여넣으면 이슈 요약이 자동으로 펼쳐짐(언퍼링)

## 자동화 + 웹훅으로 원하는 형태로 보내기

공식 앱의 알림 형식이 마음에 안 들면, 자동화 규칙의 **웹 요청 보내기(Send web request)** 액션으로 직접 만든다.

Slack에서 Incoming Webhook URL을 발급받고, 자동화 액션에 아래처럼 설정한다.

```json
{
  "text": ":rotating_light: 긴급 버그 등록",
  "blocks": [
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": "*<{{issue.url}}|{{issue.key}}: {{issue.summary}}>*\n담당자: {{issue.assignee.displayName}}"
      }
    }
  ]
}
```

- 스마트 값이 그대로 들어간다
- `<URL|텍스트>` 는 Slack의 링크 문법이다

## 알림 설계 원칙

알림은 많을수록 좋은 게 아니다. **너무 많으면 아무도 안 본다.**

- 개인에게 필요한 알림(내 이슈 할당, 내 이슈에 댓글)은 JIRA 개인 알림 설정으로
- 팀 전체가 알아야 하는 것(긴급 버그, 배포 완료)만 채널로
- 정기 요약(매일 아침 오늘 할 일)은 하루 1회로 묶어서

정리
=====
-----

| 하고 싶은 것 | 도구 |
|---|---|
| 원하는 이슈만 골라 보기 | JQL + 저장된 필터 |
| 팀 상태 한눈에 보기 | 대시보드 + 가젯 |
| 반복 작업 없애기 | 자동화 규칙 |
| 상태 변경 자동화 | 스마트 커밋 또는 GitHub Actions |
| 알림 받기 | Slack 연동 + 자동화 웹훅 |

시작하는 순서를 추천하자면 이렇다.

1. **JQL부터** — 위 실전 쿼리 10개 중 필요한 것을 저장된 필터로 만든다
2. **대시보드 구성** — 만든 필터를 올려서 매일 보는 화면을 만든다
3. **알림 규칙 하나** — 막힌 이슈 알림처럼 읽기만 하는 규칙부터
4. **상태 변경 규칙** — 익숙해진 뒤에 손댄다

자동화는 한 번에 다 만들 필요 없다. **손으로 두 번 이상 반복한 일이 생기면 그때 규칙으로 만든다.**
