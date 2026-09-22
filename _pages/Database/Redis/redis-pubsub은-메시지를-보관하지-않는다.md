---
title:  "Redis Pub/Sub 은 메시지를 보관하지 않는다"

categories:
 - Database
tags:
  - Redis
  - messaging
  - Backend
  - 자료구조

date: 2026-09-22
thumbnail: "/assets/img/thumbnail/redis_thumbnail.png"
card_thumbnail: "/assets/img/thumbnail/redis_card.png"
---
Redis 로 메시지를 나르는 방법은 세 가지다. Pub/Sub, List, Streams.
셋 다 "A 가 보내고 B 가 받는다"를 하지만, 고르는 기준은 성능도 문법도 아니다.

공식 문서에는 [자료구조 선택 가이드](https://redis.io/docs/latest/develop/data-types/compare-data-types/)
가 따로 있는데, 거기서 Pub/Sub 은 다뤄지지 않는다. **Pub/Sub 은 자료구조가 아니기 때문이다.**
키 공간에 아무것도 만들지 않는다. 이 사실 하나가 셋의 차이를 거의 다 설명한다.

## 결론부터

**갈림길은 "서버가 이 메시지를 기억하는가" 하나다.**

| | Pub/Sub | List | Streams |
|---|---|---|---|
| 키 공간에 남는가 | 안 남는다 | 남는다 | 남는다 |
| 받는 사람이 없으면 | 사라진다 | 쌓인다 | 쌓인다 |
| 꺼낸 뒤 처리 실패하면 | 알 방법이 없다 | 그 1건은 증발 | PEL 에 남는다 |
| 한 메시지를 여럿이 받나 | 구독자 전원 | 한 명만 | 그룹별로 전원 |
| 지난 메시지 다시 읽기 | 불가 | 불가 | 가능 |

전달 보장(at-most-once / at-least-once)이라는 용어 자체가 낯설다면
[비동기 메시징 입문](/Messaging/messaging-basic.html) 을 먼저 보는 게 빠르다.
여기서는 그 개념이 Redis 안에서 어떻게 갈리는지만 다룬다.

## Pub/Sub 은 at-most-once 다 — 문서가 그렇게 쓰여 있다

이건 해석이 아니라 공식 문서의 명시다.

> Redis' Pub/Sub exhibits *at-most-once* message delivery semantics. (...)
> If the subscriber is unable to handle the message (for example, due to an error
> or a network disconnect) **the message is forever lost.**
> — [Redis 공식 문서, Pub/sub](https://redis.io/docs/latest/develop/pubsub/)

`forever lost` 라는 표현을 문서가 직접 쓴다. 완곡어법이 아니다.

구체적으로 이런 일이 벌어진다.

- **구독자가 0명일 때 `PUBLISH` 하면** 메시지는 그냥 없어진다. 에러도 나지 않고 `PUBLISH` 는 0을 반환한다
- **구독자가 처리 중에 죽으면** 그 메시지는 되찾을 방법이 없다. 서버가 보낸 뒤 기억하지 않기 때문이다
- **네트워크가 끊겼다 붙으면** 끊겨 있던 동안의 메시지는 못 받는다. 재구독은 "지금부터"다

재시도 로직을 짤 수가 없다는 게 핵심이다. 무엇을 다시 보낼지 아는 주체가 아무도 없다.

### 직접 확인해보기

`redis-cli` 두 개를 띄우면 유실을 눈으로 볼 수 있다. 터미널 A 에서 먼저 발행한다.

```
127.0.0.1:6379> PUBLISH room:1 "first"
(integer) 0
```

**반환값 0 이 "메시지를 받은 구독자 수"다.** 아무도 없었고, 에러도 나지 않았고,
그 메시지는 이제 어디에도 없다. 이제 터미널 B 에서 구독한다.

```
127.0.0.1:6379> SUBSCRIBE room:1
1) "subscribe"
2) "room:1"
3) (integer) 1
```

구독한 뒤 터미널 A 에서 다시 발행하면 이번엔 `(integer) 1` 이 돌아오고 B 에 즉시 뜬다.
**B 를 끄고 발행한 뒤 다시 켜도 그 메시지는 오지 않는다.** 구독은 언제나 "지금부터"다.

Streams 로 같은 걸 해보면 차이가 분명해진다.

```
127.0.0.1:6379> XADD room:2 '*' msg "first"      # 구독자가 없는 상태에서 넣어도
"1758500000000-0"
127.0.0.1:6379> XLEN room:2                      # 남아 있다
(integer) 1
```

나중에 붙은 소비자가 `0` 부터 읽으면 아까 그 메시지를 받는다. Pub/Sub 과 갈리는 지점이다.

### 그런데 이게 단점만은 아니다

키 공간에 안 남는다는 건 **메모리를 안 먹고, 정리할 것도 없다**는 뜻이다.
Streams 처럼 `MAXLEN` 으로 트리밍을 고민할 일이 없고, List 처럼 소비자가
멈췄을 때 키가 무한정 부풀 걱정도 없다.

문서가 짚는 또 하나 — Pub/Sub 은 **DB 번호와 무관**하다.

> Publishing on db 10, will be heard by a subscriber on db 1.

스코프가 필요하면 채널 이름에 `prod:`, `staging:` 같은 접두사를 직접 붙이라고 문서가 권한다.
이걸 모르고 DB 번호로 환경을 갈라놨다가 개발 채널 메시지가 운영 구독자에게 가는 사고가 가능하다.

## List 는 큐인데, 꺼낸 순간 책임이 넘어온다

List 를 큐로 쓰는 건 Redis 의 오래된 관용구다. 문서도 이걸 정식 패턴으로 설명하고,
Ruby 의 resque·sidekiq 같은 잡 큐 라이브러리가 이 위에 만들어졌다.

```
LPUSH bikes:repairs bike:1     # 왼쪽으로 넣고
RPOP  bikes:repairs            # 오른쪽에서 꺼낸다 → FIFO
```

넣는 쪽과 꺼내는 쪽을 반대로 두면 먼저 넣은 것이 먼저 나온다. 이게 전부다.

폴링을 피하려면 `BRPOP` 을 쓴다. 메시지가 올 때까지 블로킹으로 기다리다가
들어오면 즉시 꺼낸다. 1초마다 `RPOP` 을 때리는 루프보다 낫다.

**문제는 꺼낸 다음이다.** `RPOP` 은 메시지를 리스트에서 제거한다. 그 직후
워커가 죽으면 그 1건은 메모리에도 Redis 에도 없다. 앞서 본 Pub/Sub 의 유실과
범위만 다를 뿐 같은 종류의 구멍이다.

그래서 문서는 `LMOVE` 를 권한다.

> Atomic transfer: Use LMOVE to move elements between lists in a single operation
> when you need to transfer items without race conditions
> — [Redis 공식 문서, Lists](https://redis.io/docs/latest/develop/data-types/lists/)

꺼내면서 동시에 "처리중" 리스트로 옮긴다. 원자적 연산이라 그 사이에 죽을 수 없다.
처리가 끝나면 처리중 리스트에서 지우고, 안 지워진 채 오래 남아 있는 것은
죽은 워커가 쥐고 있던 일로 보고 회수한다.

이 방식이 동작하기는 하는데, **회수 로직을 직접 짜야 한다.** 얼마나 오래 남았으면
죽은 것으로 볼지, 누가 그걸 주기적으로 검사할지를 전부 애플리케이션이 정한다.
그리고 그건 Streams 가 내장으로 갖고 있는 기능이다.

## Streams 는 그 회수 로직을 내장했다

Streams 는 append-only 로그다. `XADD` 로 넣으면 지우기 전까지 남아 있고,
소비자가 읽어도 사라지지 않는다. 읽은 위치만 따로 기록된다.

핵심은 **컨슈머 그룹(Consumer Group)** 이다. 문서는 이걸 Kafka 에 빗대 설명한다.

> it is possible to scale the message processing across different consumers,
> without single consumers having to process all the messages (...)
> **This is basically what Kafka (TM) does with consumer groups.**
> — [Redis 공식 문서, Streams](https://redis.io/docs/latest/develop/data-types/streams/)

그룹 안에서 메시지가 나뉘고(큐처럼), 그룹이 다르면 같은 메시지를 각자 받는다(Pub/Sub 처럼).
앞의 두 방식이 각각 하던 일을 한 구조에서 한다.

<div class="diagram" role="img" aria-label="소비자가 처리 도중 죽었을 때 Pub/Sub은 메시지가 사라지고 List는 꺼낸 1건만 사라지며 Streams는 PEL에 남아 다른 소비자가 인수하는 구조">
{% include diagrams/redis-msg--delivery-paths.svg %}
</div>

### PEL — 꺼냈지만 아직 안 끝난 것들의 목록

`XREADGROUP` 으로 메시지를 읽으면 그 메시지는 **PEL(Pending Entries List)** 에 등록된다.
"이 소비자가 가져갔는데 아직 완료 신호를 안 보냈다"는 기록이다.

```
XREADGROUP GROUP mygroup consumer1 STREAMS race:france >   # 읽으면 PEL 에 등록
XACK race:france mygroup 1692632086370-0                   # 처리 끝나면 PEL 에서 제거
```

`XACK` 을 보내야 비로소 완료로 친다. 워커가 처리 도중 죽으면 `XACK` 이 안 오고,
그 메시지는 PEL 에 미처리로 남는다. **List 에서 직접 짜야 했던 "처리중 목록"이
서버 쪽 기본 기능으로 있는 것이다.**

남은 것을 회수하는 명령도 있다.

```
XAUTOCLAIM race:france mygroup consumer2 3600000 0-0
```

"1시간(3600000ms) 넘게 PEL 에 방치된 메시지를 consumer2 가 인수한다"는 뜻이다.
죽은 워커의 일을 산 워커가 넘겨받는 과정이 명령 하나다.

### 대신 지워줄 사람이 필요하다

로그가 계속 쌓인다는 건 **메모리를 계속 먹는다**는 뜻이다. Pub/Sub 에 없던
숙제가 여기서 생긴다. `XADD` 에 `MAXLEN` 을 걸어 오래된 것부터 버린다.

```
XADD race:france MAXLEN 100 * rider Castilla speed 30.2   # 100건까지만 유지
XTRIM race:france MAXLEN ~ 1000                           # ~ 는 근사 트리밍 — 더 싸다
```

`~` 를 붙이면 정확히 1000건이 아니라 "대략 그쯤"에서 멈춘다. 내부 노드 단위로
잘라내서 비용이 싸다. 정확한 개수가 중요한 게 아니라면 이쪽을 쓴다.

**트리밍을 안 걸면 스트림이 무한히 자란다.** Streams 를 쓰기로 했다면
`MAXLEN` 을 같이 정하는 것까지가 한 세트다.

## Spring 에서는 어떻게 붙나

`spring-boot-starter-data-redis` 하나면 셋 다 된다. 붙이는 모양이 꽤 다르다.

### Pub/Sub — 리스너 컨테이너에 등록한다

보내는 쪽은 한 줄이다.

```java
@Service
@RequiredArgsConstructor
public class RoomNotifier {

    private final StringRedisTemplate redisTemplate;

    public void notify(String roomId, String message) {
        // 반환값은 받은 구독자 수. 0 이어도 예외가 아니다 — 그냥 아무도 못 받은 것이다
        redisTemplate.convertAndSend("room:" + roomId, message);
    }
}
```

받는 쪽은 컨테이너에 리스너를 얹는다. `@KafkaListener` 처럼 애너테이션 하나로 끝나지 않는다.

```java
@Configuration
public class RedisPubSubConfig {

    @Bean
    public RedisMessageListenerContainer container(RedisConnectionFactory cf,
                                                   RoomSubscriber subscriber) {
        RedisMessageListenerContainer container = new RedisMessageListenerContainer();
        container.setConnectionFactory(cf);
        // PatternTopic 은 news.* 같은 glob 패턴. 정확한 채널만 받으려면 ChannelTopic 을 쓴다
        container.addMessageListener(subscriber, new PatternTopic("room:*"));
        return container;
    }
}

@Component
public class RoomSubscriber implements MessageListener {

    @Override
    public void onMessage(Message message, byte[] pattern) {
        String channel = new String(message.getChannel());
        String body = new String(message.getBody());
        // 여기서 예외가 나면 그 메시지는 끝이다. 재시도할 원본이 서버에 없다
        log.info("received {} on {}", body, channel);
    }
}
```

**`onMessage` 안에서 던진 예외는 아무도 받아주지 않는다.** 로그에 남을 뿐
메시지는 복구되지 않는다. 이 메서드 안에서 DB 를 건드린다면 그 실패를
스스로 감당하는 코드가 있어야 한다.

### Streams — 소비자를 등록하고 ack 을 보낸다

```java
@Service
@RequiredArgsConstructor
public class OrderStreamProducer {

    private final StringRedisTemplate redisTemplate;

    public RecordId publish(String orderId, String amount) {
        return redisTemplate.opsForStream()
                .add(StreamRecords.newRecord()
                        .in("orders")
                        .ofMap(Map.of("orderId", orderId, "amount", amount)));
    }
}
```

받는 쪽은 `StreamListener` 를 구현하고 컨테이너에 그룹·소비자 이름을 준다.

```java
@Component
@RequiredArgsConstructor
public class OrderStreamConsumer
        implements StreamListener<String, MapRecord<String, String, String>> {

    private final StringRedisTemplate redisTemplate;

    @Override
    public void onMessage(MapRecord<String, String, String> record) {
        process(record.getValue());
        // XACK 을 보내야 PEL 에서 빠진다. 이 줄을 빼면 처리는 됐는데 미처리로 남는다
        redisTemplate.opsForStream().acknowledge("order-group", record);
    }
}
```

```java
@Bean(destroyMethod = "stop")
public StreamMessageListenerContainer<String, MapRecord<String, String, String>> streamContainer(
        RedisConnectionFactory cf, OrderStreamConsumer consumer) {

    var options = StreamMessageListenerContainer.StreamMessageListenerContainerOptions
            .builder()
            .pollTimeout(Duration.ofSeconds(1))
            .build();

    var container = StreamMessageListenerContainer.create(cf, options);
    // ReadOffset.lastConsumed() 가 ">" 다 — 이 그룹이 아직 안 가져간 것부터
    container.receive(Consumer.from("order-group", "consumer-1"),
                      StreamOffset.create("orders", ReadOffset.lastConsumed()),
                      consumer);
    container.start();
    return container;
}
```

`receive()` 대신 `receiveAutoAck()` 도 있는데, **이건 읽는 즉시 ack 을 보낸다.**
처리 중 죽어도 PEL 에 안 남으므로 Streams 를 쓰는 이유가 사라진다.
유실이 곤란해서 Streams 를 골랐다면 `receive()` 를 쓰고 직접 `acknowledge()` 한다.

⚠️ **그룹은 먼저 만들어져 있어야 한다.** 없는 그룹으로 `receive()` 하면
`NOGROUP` 에러가 난다. 애플리케이션 기동 시 한 번 만들어 준다.

```java
try {
    redisTemplate.opsForStream().createGroup("orders", ReadOffset.from("0"), "order-group");
} catch (RedisSystemException e) {
    // BUSYGROUP — 이미 있으면 그대로 쓴다
}
```

### List — 가장 코드가 적다

```java
// 넣는 쪽
redisTemplate.opsForList().leftPush("jobs", payload);

// 꺼내는 쪽 — 최대 5초 기다리다 없으면 null
String job = redisTemplate.opsForList().rightPop("jobs", Duration.ofSeconds(5));
```

`rightPop` 에 `Duration` 을 주면 `BRPOP` 이 된다. 앞서 말한 유실이 걱정되면
`LMOVE` 에 해당하는 `move()` 로 처리중 리스트에 옮긴다.

```java
String job = redisTemplate.opsForList().move(
        "jobs", RedisListCommands.Direction.RIGHT,
        "jobs:processing", RedisListCommands.Direction.LEFT,
        Duration.ofSeconds(5));
// 처리가 끝나면 jobs:processing 에서 지운다. 안 지워진 채 남은 것이 죽은 워커의 일이다
```

**세 방식의 코드량 차이가 곧 책임의 차이다.** List 가 짧은 건 회수 로직이
아직 안 쓰였기 때문이고, Streams 가 긴 건 그걸 서버가 대신 해주는 대가다.

## 그럼 Kafka 는 이제 안 쓰나

Streams 가 컨슈머 그룹을 갖고 있다고 해서 Kafka 를 대체하지는 않는다.
문서가 "basically what Kafka does" 라고 쓴 건 컨슈머 그룹이라는 **개념**이 같다는 말이지,
운영 특성이 같다는 말이 아니다.

- **Redis 는 기본이 인메모리다.** 메시지 보관 기간이 디스크 용량이 아니라 RAM 에 묶인다. 며칠치 이벤트를 쌓아두고 재처리하는 용도와는 맞지 않는다
- **파티션 개념이 없다.** Kafka 는 파티션 단위로 순서를 보장하며 수평 확장하는데, Streams 의 확장 단위는 그와 다르다
- **이미 Redis 가 떠 있는가**가 실제 판단 기준이 된다. 캐시나 세션 때문에 Redis 를 이미 쓰고 있다면, 가벼운 큐 하나 때문에 Kafka 를 새로 세우는 건 운영 대상만 늘린다

반대로 Kafka 가 이미 있다면 Redis Streams 를 굳이 겹쳐 쓸 이유도 없다.
**"뭐가 더 좋은가"가 아니라 "지금 뭐가 떠 있는가"로 갈린다.**

## 클러스터에서 Pub/Sub 이 비싸지는 지점

단일 노드에서는 안 보이다가 클러스터로 가면 드러나는 문제가 있다.
일반 Pub/Sub 은 **메시지를 클러스터의 모든 노드로 전파한다.** 구독자가 어느 노드에
붙어 있을지 모르기 때문이다. 노드를 늘릴수록 클러스터 버스를 지나는 트래픽이 늘어난다.

Redis 7.0 이 이걸 위해 sharded Pub/Sub 을 넣었다.

> Sharded Pub/Sub helps to scale the usage of Pub/Sub in cluster mode.
> It restricts the propagation of messages to be within the shard of a cluster.

`SSUBSCRIBE` / `SPUBLISH` 를 쓰면 채널이 키처럼 슬롯에 할당돼서, 전파 범위가
그 샤드 안으로 제한된다. 클러스터에서 Pub/Sub 을 본격적으로 쓸 계획이라면
이쪽을 먼저 본다.

## 그래서 언제 뭘 쓰나

| 상황 | 고른다 | 이유 |
|---|---|---|
| 실시간 알림 — 지금 접속한 사람에게만 | Pub/Sub | 못 받은 사람에게 나중에 줄 이유가 없다 |
| 서버 간 캐시 무효화 신호 | Pub/Sub | 한 건 놓쳐도 다음 신호가 덮는다 |
| WebSocket 브로드캐스트 (다중 인스턴스) | Pub/Sub | 연결이 끊긴 클라이언트는 어차피 못 받는다 |
| 간단한 백그라운드 잡 큐 | List | `BRPOP` 하나로 끝난다. 유실을 감당할 수 있을 때 |
| 유실이 곤란한 잡 큐 | Streams | PEL + `XAUTOCLAIM` 이 재처리를 대신한다 |
| 여러 소비자가 같은 이벤트를 각자 처리 | Streams | 그룹을 나누면 Pub/Sub 처럼 되면서 유실은 없다 |
| 며칠치 이벤트를 쌓고 재처리 | Redis 가 아닌 것 | 인메모리에 묶인 용도가 아니다 |

한 줄로 줄이면 이렇다. **못 받아도 되면 Pub/Sub, 못 받으면 곤란하면 Streams.**
List 는 그 사이에서 "지금 당장 간단히"가 필요할 때의 선택지다.

## 직접 확인하지 않은 것

이 글은 공식 문서를 1차 출처로 정리한 것이다. **성능 수치는 넣지 않았다.**
직접 재보지 않았기 때문이다.

- Pub/Sub 과 Streams 의 처리량 차이 — 재본 적 없다. 워크로드마다 다를 것이라 인용도 하지 않았다
- `XAUTOCLAIM` 의 실제 운영 동작 — 명령의 의미는 문서로 확인했지만, 소비자가 실제로 죽는 상황을 만들어 인수까지 돌려보지는 않았다
- sharded Pub/Sub 의 전파 비용 감소 폭 — 문서가 "제한된다"고 한 것까지만 확인했다
- **위 Spring 코드는 이 글을 위해 쓴 것이고 프로젝트에서 돌려본 것이 아니다.** API 시그니처는 Spring Data Redis 문서 기준이며, 버전에 따라 다를 수 있다. 붙일 때는 자기 버전의 문서를 확인하는 게 맞다

이 블로그의 [Redis 로 동시 접속 기기를 제한한 글](/Database/Redis/장부만-지우고-세션은-살려뒀다.html)
에서 Pub/Sub 으로 세션 종료 알림을 보냈다. 거기서 알림을 먼저 보내고 `Thread.sleep(200)` 을
넣은 직접적인 이유는 세션을 먼저 지우면 SSE 연결이 같이 끊겨 알림이 도착하지 못해서였다.
다만 **"전송이 끝났는지 확인하고 넘어가는" 경로가 없어 시간으로 때울 수밖에 없었던 것**은
이 글에서 본 성질과 같은 자리다. 확인을 받으려면 ack 경로를 따로 만들어야 하고,
그건 Pub/Sub 이 주지 않는 것이다.

## 정리

- **Pub/Sub 은 자료구조가 아니다.** 키 공간에 아무것도 만들지 않고, 그래서 공식 자료구조 비교 문서에도 없다
- 문서가 명시한 보장은 **at-most-once** 다. 구독자가 없거나 처리에 실패하면 `the message is forever lost`
- **List 는 꺼낸 뒤가 문제다.** `RPOP` 한 1건은 워커가 죽으면 증발한다. `LMOVE` 로 처리중 목록을 만들 수 있지만 회수 로직은 직접 짠다
- **Streams 는 그 회수 로직이 내장이다.** PEL 에 미처리가 남고 `XAUTOCLAIM` 으로 다른 소비자가 인수한다. 대신 `MAXLEN` 트리밍이 숙제로 붙는다
- 컨슈머 그룹이 Kafka 와 개념이 같다고 대체재는 아니다. **인메모리라는 제약이 보관 기간을 정한다**
- 판단 기준은 하나다 — **서버가 이 메시지를 기억해야 하는가.** 기억하지 않는 쪽을 골랐다면 재시도라는 선택지를 같이 버린 것이다
