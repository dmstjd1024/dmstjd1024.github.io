---
title:  "depth < 10 방어 코드가 버그를 감추고 있었다"

categories:
  - AI
tags:
  - AI
  - Claude Code
  - Java
  - 리팩터링

date: 2026-03-25
thumbnail: "/assets/img/thumbnail/sample.png"
---

## 문제의 코드

- 대상: 계층형 조직 트리 서비스의 조상 조직 ID 수집 메서드
- 원래 구현의 핵심 — 아래 한 줄


```java
while (currentId != null && depth < 10) {
    ancestorIds.add(0, currentId);
    OrganizationDto parent = organizationDao.selectOrganizationById(currentId);
    if (parent == null) break;
    currentId = parent.getParentOrgId();
    depth++;
}
```

- 하는 일: 부모를 따라 위로 올라가는 평범한 루프
- `depth < 10`의 목적: 순환 참조 발생 시 무한루프 방지
- 실제 효과: 방어가 아니라 **은폐**

- 의도 자체는 좋음. 문제는 이게 방어가 아니라는 점

## 왜 은폐인가

- `depth < 10`이 실제로 하는 일을 정확히 서술하면 아래와 같음

> 조상을 10개까지 모은 뒤, 아무 말 없이 멈춤

<div class="diagram" role="img" aria-label="깊이 제한이 문제를 감지하지 않고 조용히 잘라내는 구조">
{% include diagrams/depth10--concealment.svg %}
</div>

- 호출자가 받는 정보

- 반환 타입 — 그냥 `List<Long>`
- 예외 — 없음
- 경고 로그 — 없음
- 플래그 — 없음

즉 조건에 걸려 끝났는지, 루트에 도달해 정상 종료했는지 **호출자가 구분할 방법이 없음**

- 결과: 서로 다른 두 상황이 하나로 뭉개짐

| 상황 | 실제로 일어난 일 | 반환값 |
|---|---|---|
| 조직 깊이가 12단계 | 조상 2개가 조용히 누락 | 불완전한 목록 |
| A → B → A 순환 참조 | 같은 ID를 반복 수집하다 10에서 절단 | 중복이 섞인 쓰레기 목록 |
| 깊이 5, 정상 | 정상 종료 | 정상 목록 |

- 세 경우 모두 결과물의 겉모습

- 정상적인 리스트처럼 생긴 값
- 이 목록의 용도 — 권한 범위 계산, 상위 조직 조회
- 조상 누락 시 증상 — 보여야 할 데이터가 안 보이거나, 없어야 할 권한이 생김
- 로그 — 아무것도 안 남음

무한루프는 최소한 시끄럽다. CPU가 튀고 요청이 안 끝나니 누군가 알아챈다. 조용히 틀린 답을 주는 것은 알아채기까지 훨씬 오래 걸린다.

## 두 개의 문제가 하나의 숫자에 뭉개져 있었다

- `10`이라는 숫자 하나가 답하려던 두 질문

1. **순환 참조가 있는가?** — 예외 상황. 데이터가 망가졌다는 뜻이고 반드시 기록돼야 함
2. **조직 계층이 얼마나 깊을 수 있는가?** — 정상 범위의 도메인 제약. 조직이 12단계인 건 버그 아님

- 1번의 성격 — 고쳐야 할 데이터
- 2번의 성격 — 허용할 범위
- 같은 조건문에 섞인 결과 — 어느 쪽이 발생했는지 알 수 없음

이 둘은 대응 방식이 다르다. 그런데 하나의 숫자가 둘 다를 맡고 있었다.

## 어떻게 고쳤나

- 커밋 `642845d`에서 둘을 분리

```java
Long currentId = org.getParentOrgId();
Set<Long> visited = new HashSet<>();
while (currentId != null) {
    if (!visited.add(currentId)) {
        log.warn("[조직 서비스] getAncestorOrgIds 순환 참조 감지 - orgId={}, cycleAt={}",
                 orgId, currentId);
        break;
    }
    if (visited.size() > MAX_ORG_DEPTH) {
        log.warn("[조직 서비스] getAncestorOrgIds 최대 깊이({}) 초과 - orgId={}",
                 MAX_ORG_DEPTH, orgId);
        break;
    }
    ancestorIds.add(0, currentId);
    OrganizationDto parent = organizationDao.selectOrganizationById(currentId);
    if (parent == null) break;
    currentId = parent.getParentOrgId();
}
```

- 바뀐 점 셋

- **`Set<Long> visited`로 순환을 실제로 검출** — `add()`가 `false`면 이미 방문한 노드로 되돌아온 것. 깊이를 세는 게 아니라 순환 그 자체를 포착
- **경고 로그 추가** — 순환일 때와 깊이 초과일 때 메시지 분리. 사후에 로그만 봐도 구분 가능하고, `cycleAt`으로 순환 지점 노드까지 확인
- **`MAX_ORG_DEPTH = 50`을 별도 상수로 분리** — 순환 검출이 `visited`로 넘어가면서 깊이 한도는 순환 방어 역할에서 해방. 이제 "이 정도 깊이는 정상이 아니다"라는 도메인 판단만 표현하므로 10보다 훨씬 넉넉한 50도 안전

### 근본 원인 쪽도 함께 손봤다

- 같은 커밋에 포함된 마이그레이션 — `V169__fix_null_org_paths.sql`
- 메서드의 조상 조회 경로

- 1순위 — `org_path`(`"/1/5/12"` 형태 경로 문자열) 파싱해서 바로 조상 획득
- 폴백 — `org_path`가 없을 때만 부모를 따라 올라가는 루프
- 즉 위험한 루프 진입 조건 — `org_path`가 NULL인 데이터의 존재
- V169의 역할 — 그 NULL 경로를 실제로 채워 넣는 데이터 교정

- 한 커밋에서 함께 한 일 — 방어 코드 수정 + 방어할 일 자체를 없애기
- 폴백은 유지 — 데이터를 한 번 고쳤다고 앞으로 영원히 NULL이 안 생긴다는 보장은 없음

## 남는 교훈

**루프 한도 상수를 보면 그게 무엇을 막고 있는지 물어야 한다.**

- 대개 둘 중 하나 — 비정상 상태 감지 또는 정상 범위의 상한
- 하나의 숫자가 둘 다 담당 시 — 둘 다 제대로 못 함

그리고 **조용히 `break` 하는 방어 코드는 방어가 아니다.**

- 예상 못 한 경로로 루프 이탈 — 그 자체가 정보
- 필요한 것 — 로그든 예외든 메트릭이든 어떤 형태로든 밖으로 노출
- 안 하면 — "가끔 상위 조직이 안 보인다"는 제보를 받고 몇 시간 헤매기

- `depth < 10`의 성격 — 코드 리뷰에서 지적받기 어려운 종류
- 이유: 무한루프를 막고 있고, 짧고, 의도가 명백해 보임

그런데 그 명백해 보이는 의도가 실제 동작과 달랐다.
