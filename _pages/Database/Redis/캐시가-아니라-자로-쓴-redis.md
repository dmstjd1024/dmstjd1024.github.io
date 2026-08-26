---
title: "캐시가 아니라 자로 쓴 Redis"

categories:
 - Database
tags:
  - Redis
  - Spring
  - Backend
  - 모니터링

date: 2026-08-26
thumbnail: "/assets/img/thumbnail/redis_thumbnail.png"
---
관리자 화면에 "통계 API 평균 응답시간" 을 띄워야 했다. 통계 API 는 집계 쿼리가 무거워
느려지면 먼저 티가 나는 쪽이라, 지금 얼마나 걸리는지를 화면에서 보고 싶었다.

APM 을 붙이는 선택지가 있었지만 그러지 않았다. 알고 싶은 것은 **특정 URL 접두사 하나의 평균**
이었고, 이미 Redis 가 떠 있었다.

## 어디에 쌓을 것인가

세 가지를 두고 골랐다.

| 방식 | 문제 |
|---|---|
| DB 테이블 | 매 요청 INSERT. 재고 있는 것도 아닌데 쓰기가 늘어난다 |
| 애플리케이션 메모리 | 서버가 여러 대면 각자 다른 값을 본다. 재시작하면 사라진다 |
| Redis List | 이미 떠 있고, 서버가 몇 대든 한 곳에 모인다 |

Redis 를 골랐지만 **캐시로 쓴 게 아니다.** 여기서 Redis 는 값을 빨리 돌려주는 저장소가 아니라
샘플을 담아두는 자다. 읽는 쪽은 관리자 한 명이고, 쓰는 쪽이 매 요청이다. 캐시와 정반대 비율이다.

자료구조는 List 를 썼다. 평균만 필요하면 합계와 개수 두 숫자를 `INCR` 로 굴려도 된다.
그런데 그러면 나중에 **분포를 볼 수 없다.** p95 가 궁금해지는 순간 다시 만들어야 한다.
샘플을 그대로 들고 있으면 평균이든 백분위든 나중에 정한다.

```java
private static final String RESPONSE_TIME_KEY_PREFIX = "api:response-time:";
private static final int MAX_SAMPLES = 1000;
private static final Duration TTL = Duration.ofDays(1);
```

키는 날짜별이다. `api:response-time:2026-08-26` 하나에 그날 샘플이 쌓인다.

## 무한히 쌓이지 않게

샘플을 그대로 들고 있기로 했으면 **어디서 끊을지**를 정해야 한다.
끝에 넣고, 넘치면 앞에서 뺀다.

```java
stringRedisTemplate.opsForList().rightPush(key, String.valueOf(responseTimeMs));

Long size = stringRedisTemplate.opsForList().size(key);
if (size != null && size > MAX_SAMPLES) {
    stringRedisTemplate.opsForList().leftPop(key);
}
```

최신 1000개만 남는 슬라이딩 윈도우다. 오래된 것부터 밀려난다.

여기에 TTL 을 걸어 날짜가 지난 키가 스스로 사라지게 했다.

```java
if (size != null && size <= 1) {
    stringRedisTemplate.expire(key, TTL);   // 키가 새로 생긴 첫 요청에서만
}
```

## 그런데 이 TTL 이 안 걸릴 수 있다

`size <= 1` 은 "방금 이 키를 처음 만들었다" 는 뜻으로 쓴 조건이다.
그런데 이 코드는 서블릿 필터에서 **매 요청** 호출된다. 즉 동시에 들어온다.

날이 바뀌고 첫 두 요청이 겹치면 이렇게 된다.

```
요청 A: RPUSH → (아직 size 안 읽음)
요청 B: RPUSH → (아직 size 안 읽음)
요청 A: LLEN → 2   →  2 <= 1 이 아니므로 EXPIRE 안 함
요청 B: LLEN → 2   →  2 <= 1 이 아니므로 EXPIRE 안 함
```

**둘 다 남에게 미루고 아무도 안 건다.** 그날 키는 TTL 없이 영원히 남는다.

로컬 Redis 를 따로 띄워 이 순서를 그대로 재현했다.

```
=== 1) 순차 호출 (요청이 겹치지 않는 경우) ===
  LLEN=3  TTL=86400

=== 2) 첫 두 push 가 겹친 경우 ===
  A가 본 size=2, B가 본 size=2
  LLEN=2  TTL=-1        ← 만료가 걸리지 않았다
```

`TTL=-1` 은 만료 시각이 없다는 뜻이다. 순차로 부르면 `86400`(1일)이 정상으로 걸린다.
같은 코드가 **호출이 겹치느냐 아니냐로 갈린다.**

키가 하루에 하나씩 생기고 각각 최대 1000개씩 들고 있으니 폭증하지는 않는다.
그래서 지금까지 드러나지 않았다. 하지만 지워질 근거가 없는 데이터가 남는 것은 맞다.

## 고친다면

읽고 나서 쓰는 두 번의 왕복 사이에 남이 끼어드는 것이 원인이다. **읽지 않고 정하면 된다.**

```java
Long size = stringRedisTemplate.opsForList().rightPush(key, value);  // 반환값이 push 후 길이
if (size != null && size > MAX_SAMPLES) {
    stringRedisTemplate.opsForList().leftPop(key);
}
if (size != null && size == 1) {
    stringRedisTemplate.expire(key, TTL);
}
```

`RPUSH` 는 넣은 뒤의 길이를 돌려준다. 그 값을 쓰면 **내가 넣은 결과**를 보게 되어,
정확히 한 요청만 `size == 1` 을 본다. `LLEN` 을 따로 부를 필요도 없어져 왕복도 하나 준다.

더 확실히 하려면 키를 만들 때 만료를 함께 정하는 방법도 있다. 다만 그건 스크립트를 하나
쓰게 되므로, 지금 규모에서는 위 한 줄이면 충분하다고 봤다.

## 자기 자신은 재지 않는다

이 지표를 보여주는 API 도 `/api/v1/admin/statistics` 아래에 있다. 그대로 두면
**조회할 때마다 자기 응답시간이 샘플에 섞인다.**

```java
private boolean isStatisticsApi(String uri) {
    return uri != null && uri.startsWith(STATISTICS_API_PREFIX)
        && !uri.contains("data-collection-performance");   // 자기 자신 제외
}
```

관리자가 화면을 자주 새로고침할수록 평균이 그쪽으로 끌려간다. 측정 대상 안에 측정 도구가
들어가 있으면 재는 행위가 값을 바꾼다.

## 계측이 서비스를 막지 않게

기록도 조회도 전부 `try-catch` 로 감싸고, 실패하면 로그만 남긴다.

```java
} catch (Exception e) {
    log.warn("Failed to record API response time: {}", e.getMessage());
}
```

조회 실패 시에는 `0.0` 을 돌려준다. 응답시간을 못 쟀다고 API 가 실패하면 주객이 뒤바뀐다.
Redis 가 죽어도 서비스는 그대로 동작하고 이 지표만 비는 것이 맞다.

다만 `0.0` 을 돌려주는 건 **"0ms 였다" 와 "못 쟀다" 가 구분되지 않는** 선택이다.
화면에 0 이 뜨면 빠른 건지 고장난 건지 알 수 없다. 지금은 샘플 수를 함께 내려
`getSampleCount()` 가 0 이면 데이터가 없는 것으로 읽게 해두었다.

## 안 한 것

- **p95·p99 를 계산하지 않았다.** 샘플을 그대로 들고 있으므로 나중에 List 를 정렬하면 된다.
  화면이 평균만 요구해서 거기까지만 만들었다.
- **URL 별로 나누지 않았다.** 키 하나에 통계 API 전체가 섞인다. 어느 API 가 느린지는 알 수 없다.
  접두사 단위로 "느려지고 있는가" 만 보는 것이 목적이었다.
- **위에 적은 `RPUSH` 반환값 수정을 아직 반영하지 않았다.** 재현으로 확인만 한 상태다.

## 남는 교훈

Redis 를 캐시로만 생각하면 "읽기가 빨라졌는가" 만 묻게 된다. 여기서는 **읽는 쪽이 하루 몇 번,
쓰는 쪽이 매 요청**이라 그 질문 자체가 맞지 않았다. 자료구조를 고르는 기준도 속도가 아니라
"나중에 다른 걸 묻고 싶어질까" 였다.

그리고 `read → 판단 → write` 를 두 번의 왕복으로 나눠 쓰면 그 사이는 항상 열려 있다.
이번에는 그 틈으로 TTL 하나가 빠져나갔다. 명령 하나가 이미 돌려주는 값이 있다면
**다시 물어보지 않는 편**이 짧고 안전하다.
