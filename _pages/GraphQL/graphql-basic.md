---
title: "GraphQL 입문 - REST와 무엇이 다른가"

categories:
 - GraphQL
tags:
 - graphql
 - api
 - spring
 - backend

date: 2026-08-22
thumbnail: "/assets/img/thumbnail/empty.jpg"
---

GraphQL 이란
=====
-----
**API 를 통해 데이터를 주고받기 위한 쿼리 언어(Query Language, 원하는 데이터를 문장으로 적어 요청하는 문법)**
- 클라이언트가 "무엇이 필요한지"를 직접 적어서 보내면, 서버가 딱 그만큼만 돌려준다
- 2012년 페이스북이 사내에서 만들어 2015년에 공개했다. 지금은 GraphQL Foundation 이 관리하는 오픈 스펙이다
- **데이터베이스가 아니다.** 이름에 Query 가 들어가서 자주 오해받는데, GraphQL 은 저장소가 아니라 API 를 설계하고 호출하는 방식이다

## 왜 만들어졌나
페이스북이 웹에서 모바일 앱으로 넘어가면서 겪은 문제에서 출발했다.

모바일 화면 하나를 그리려면 사용자 정보, 그 사람이 쓴 글 목록, 각 글의 댓글 수가 필요하다. 그런데 REST 로 짜인 서버에서는 이게 API 3번 호출이 된다. 게다가 사용자 정보 API 는 화면에 안 쓰는 주소·가입일까지 전부 실어 보낸다.

- 네트워크가 느리고 불안정한 환경에서는 **왕복 횟수 자체가 비용**이다
- 화면마다 필요한 데이터 모양이 다른데, 서버 응답 모양은 고정돼 있다
- 그래서 화면이 바뀔 때마다 서버에 새 엔드포인트를 추가하게 된다

GraphQL 은 이 셋을 "요청하는 쪽이 응답 모양을 정한다"는 한 가지 원칙으로 풀었다.

REST 와 무엇이 다른가
=====
-----
가장 큰 차이는 **엔드포인트(Endpoint, 요청을 받는 주소)의 개수**다.

| | REST | GraphQL |
|---|---|---|
| 엔드포인트 | 리소스마다 하나씩 (`/users`, `/posts`, ...) | 보통 `/graphql` 하나 |
| 응답 모양 | 서버가 정한다 | 클라이언트가 요청에 적는다 |
| 화면 하나에 필요한 호출 | 여러 번일 때가 많다 | 한 번에 묶을 수 있다 |
| HTTP 메서드 | GET/POST/PUT/DELETE 로 의미 구분 | 대부분 POST 하나 |
| 타입 정보 | 문서(Swagger 등)로 따로 관리 | 스키마가 곧 명세이자 검증기 |

## 오버페칭과 언더페칭
REST 에서 자주 나오는 두 단어다. 둘 다 "응답 모양이 고정돼 있어서" 생긴다.

- **오버페칭(Over-fetching)**: 안 쓰는 필드까지 받는 것. 이름만 필요한데 주소·전화번호·가입일이 같이 온다
- **언더페칭(Under-fetching)**: 한 번으로 부족해 또 부르는 것. 글 목록을 받았더니 작성자 이름이 없어서 작성자 API 를 또 부른다

언더페칭이 반복되면 목록 10건에 작성자 조회 10번이 붙는다. 클라이언트 쪽에서 벌어지는 N+1 문제다.

<div class="diagram" role="img" aria-label="REST 는 화면 하나를 그리려고 세 번 왕복하고 안 쓰는 필드까지 받는 반면 GraphQL 은 한 번 왕복으로 필요한 필드만 받는 구조">
{% include diagrams/graphql--rest-vs-graphql.svg %}
</div>

## 그럼 REST 는 이제 안 쓰나
그렇지 않다. 바뀌는 건 문제의 종류지 난이도가 아니다.

- REST 가 공짜로 주던 것들(HTTP 캐싱, 상태 코드, 파일 업로드/다운로드)을 GraphQL 에서는 직접 챙겨야 한다
- 왕복이 줄어드는 대신, 서버는 어떤 쿼리가 올지 미리 알 수 없게 된다

무엇을 얻고 무엇을 잃는지는 이 글 끝의 [언제 쓰고, 언제 쓰지 않나](#언제-쓰고-언제-쓰지-않나)
에서 정리한다. 그 전에 GraphQL 이 실제로 어떻게 생겼는지부터 본다.

스키마와 타입
=====
-----
GraphQL 서버는 **스키마(Schema)** 로 시작한다. "이 API 에 어떤 데이터가 있고 어떤 모양인지"를 적은 문서이자, 서버가 요청을 검증하는 실제 규칙이다.

스키마는 **SDL(Schema Definition Language)** 이라는 문법으로 쓴다.

```graphql
type User {
  id: ID!
  name: String!
  email: String
  posts: [Post!]!
}

type Post {
  id: ID!
  title: String!
  content: String
  author: User!
}
```

읽는 법:
- `type User { ... }` — User 라는 타입에 어떤 필드가 있는지 정의
- `String`, `ID` 등은 **스칼라 타입(Scalar Type, 더 쪼갤 수 없는 값)**. 기본으로 `Int`, `Float`, `String`, `Boolean`, `ID` 다섯 개가 있다
- `User`, `Post` 처럼 필드를 가진 타입은 **오브젝트 타입(Object Type)**
- `!` 는 **널이 될 수 없다(non-null)** 는 뜻. `name: String!` 이면 서버는 name 을 반드시 채워야 한다
- `[ ]` 는 리스트. `[Post!]!` 는 "리스트 자체도 널이 아니고, 안에 든 Post 도 널이 아니다"

`!` 를 어디에 붙이냐가 계약이 된다. `email: String` 은 널일 수 있다고 명시한 것이므로, 클라이언트는 없을 경우를 처리해야 한다. 타입 정보가 문서가 아니라 스키마에 있으니 서버와 클라이언트가 같은 것을 본다.

## 스키마는 그래프다
`User.posts` 가 `[Post!]!` 이고 `Post.author` 가 `User!` 다. 타입들이 서로를 참조하면서 그래프(Graph, 점과 선으로 이어진 구조)를 이룬다. GraphQL 이라는 이름이 여기서 나왔다.

클라이언트의 쿼리는 이 그래프 위를 걸어 내려가는 경로가 된다.

세 가지 진입점 - Query, Mutation, Subscription
=====
-----
스키마에는 특별한 타입 셋이 있다. 클라이언트가 그래프에 처음 발을 딛는 지점이다.

| 타입 | 하는 일 | REST 에 비유하면 |
|---|---|---|
| Query | 데이터를 읽는다 | GET |
| Mutation | 데이터를 바꾼다 | POST / PUT / DELETE |
| Subscription | 변경을 실시간으로 받는다 | WebSocket 등 |

## Query - 읽기
```graphql
type Query {
  user(id: ID!): User
  posts(limit: Int = 10): [Post!]!
}
```
- `user(id: ID!)` — 인자를 받는다. `limit: Int = 10` 처럼 기본값도 줄 수 있다

클라이언트가 보내는 쿼리:
```graphql
query {
  user(id: "1") {
    name
    posts {
      title
    }
  }
}
```

응답:
```json
{
  "data": {
    "user": {
      "name": "전은성",
      "posts": [
        { "title": "GraphQL 입문" }
      ]
    }
  }
}
```
- **요청 모양과 응답 모양이 같다.** 이게 GraphQL 을 처음 볼 때 가장 눈에 띄는 특징이다
- `email` 을 안 적었으므로 응답에도 없다. 필요한 필드만 골라 받는다는 게 이 뜻이다

## Mutation - 쓰기
```graphql
type Mutation {
  createPost(title: String!, content: String): Post!
}
```
```graphql
mutation {
  createPost(title: "새 글", content: "본문") {
    id
    title
  }
}
```
- 바꾸는 동시에 **바뀐 결과에서 필요한 필드를 골라 받는다**. 생성 후 조회를 또 하지 않아도 된다
- Query 의 여러 필드는 병렬로 실행되지만, Mutation 의 최상위 필드는 **적힌 순서대로** 실행된다. 쓰기 작업이 서로 간섭하지 않게 하려는 규칙이다

## Subscription - 실시간
```graphql
type Subscription {
  postAdded: Post!
}
```
- 서버가 이벤트를 밀어주는 방식. 보통 WebSocket 위에서 동작한다
- 입문 단계에서는 "이런 게 있다" 정도로 알아두면 된다. Query·Mutation 없이 Subscription 부터 쓸 일은 없다

리졸버 - GraphQL 이 실제로 도는 방식
=====
-----
스키마는 "무엇이 있는지"만 적는다. **그 값을 실제로 채워 오는 함수가 리졸버(Resolver)** 다.

핵심은 이것이다: **리졸버는 필드 하나당 하나씩 있다.** GraphQL 서버는 쿼리를 위에서 아래로 따라가며 필드마다 리졸버를 호출한다.

```graphql
query {
  user(id: "1") {     # 1. Query.user 리졸버 호출 → User 한 명
    name              # 2. User.name 리졸버 (보통 객체 필드를 그냥 읽음)
    posts {           # 3. User.posts 리졸버 → Post 리스트
      title           # 4. 각 Post 마다 Post.title 리졸버
    }
  }
}
```

<div class="diagram" role="img" aria-label="쿼리 트리를 따라 필드마다 리졸버가 차례로 호출되고 부모의 결과가 자식 리졸버로 전달되는 구조">
{% include diagrams/graphql--resolver-tree.svg %}
</div>

- 위 리졸버의 결과가 아래 리졸버의 입력이 된다. `Query.user` 가 돌려준 User 가 `User.posts` 리졸버에 넘어간다
- 대부분의 필드는 부모 객체에서 값을 그대로 꺼내면 되므로 리졸버를 따로 안 짜도 된다. 프레임워크가 기본 동작을 제공한다
- **직접 짜야 하는 건 다른 곳에서 가져와야 하는 필드다.** `User.posts` 처럼 별도 조회가 필요한 경우

이 실행 모델을 이해하면 뒤에 나오는 N+1 문제가 왜 생기는지도 바로 보인다.

Spring for GraphQL 로 만들어보기
=====
-----
스프링에서는 `spring-boot-starter-graphql` 하나로 시작한다.

```gradle
dependencies {
    implementation 'org.springframework.boot:spring-boot-starter-graphql'
    implementation 'org.springframework.boot:spring-boot-starter-web'
}
```

## 1. 스키마 파일
`src/main/resources/graphql/schema.graphqls` 에 둔다. 이 경로는 규약이라 따로 설정하지 않아도 자동으로 읽는다.

```graphql
type Query {
    user(id: ID!): User
}

type Mutation {
    createPost(title: String!, content: String): Post!
}

type User {
    id: ID!
    name: String!
    posts: [Post!]!
}

type Post {
    id: ID!
    title: String!
    content: String
}
```

## 2. 리졸버
스프링에서는 컨트롤러에 애너테이션을 붙여 리졸버를 만든다.

```java
@Controller
public class UserController {

    private final UserService userService;
    private final PostService postService;

    public UserController(UserService userService, PostService postService) {
        this.userService = userService;
        this.postService = postService;
    }

    // Query 타입의 user 필드를 담당한다
    @QueryMapping
    public User user(@Argument String id) {
        return userService.findById(id);
    }

    // User 타입의 posts 필드를 담당한다.
    // 부모인 User 가 인자로 넘어온다.
    @SchemaMapping
    public List<Post> posts(User user) {
        return postService.findByUserId(user.getId());
    }

    @MutationMapping
    public Post createPost(@Argument String title, @Argument String content) {
        return postService.create(title, content);
    }
}
```

애너테이션 세 개만 알면 된다:

| 애너테이션 | 담당하는 것 |
|---|---|
| `@QueryMapping` | Query 타입의 필드 |
| `@MutationMapping` | Mutation 타입의 필드 |
| `@SchemaMapping` | 그 외 타입의 필드 (`User.posts` 등) |

- 메서드 이름이 스키마의 필드 이름과 같으면 자동으로 연결된다. 다르면 `@QueryMapping(name = "user")` 처럼 지정한다
- `@SchemaMapping` 은 첫 번째 파라미터 타입으로 어느 타입의 필드인지 판단한다. `User user` 를 받으므로 `User.posts` 가 된다
- `@Argument` 는 쿼리에 적힌 인자를 메서드 파라미터로 받는다
- `id`, `name`, `title` 처럼 객체에 이미 있는 필드는 리졸버를 안 짜도 된다. 게터로 자동 매핑된다

## 3. 확인하기
개발 중에는 브라우저에서 쿼리를 짜볼 수 있는 화면을 켜두면 편하다.

```yaml
spring:
  graphql:
    graphiql:
      enabled: true
```
- `http://localhost:8080/graphiql` 로 접속하면 GraphiQL 이 뜬다
- 스키마를 읽어 자동완성과 문서를 보여준다. 별도 API 문서를 만들지 않아도 되는 이유가 이것이다
- **운영 환경에서는 꺼둔다.** 스키마 전체가 노출된다

입문 다음에 만나는 것들
=====
-----
개념만 알고 실제로 붙이면 곧 만나는 문제들이다. 지금은 이름만 알아두면 된다.

## N+1 문제
앞의 리졸버 실행 모델 때문에 생긴다. 사용자 10명을 조회하고 각각의 `posts` 를 요청하면, `User.posts` 리졸버가 **10번 호출된다.** 리졸버는 사용자 한 명씩 받아 동작하므로 각자 쿼리를 날린다.

- 사용자 조회 1번 + 글 조회 10번 = 11번. 이게 N+1 이다
- 해결책은 **DataLoader**. 같은 요청 안에서 발생한 조회를 모아 한 번에 처리한다. 스프링에서는 `@BatchMapping` 으로 쓴다
- REST 에서 겪던 N+1 과 원인은 같지만, GraphQL 에서는 **클라이언트가 쿼리를 어떻게 짜느냐에 따라 발생 여부가 달라진다**는 점이 다르다. 서버 코드만 봐서는 언제 터질지 알기 어렵다

## HTTP 캐싱이 안 된다
GraphQL 은 대부분 POST 로 `/graphql` 한 곳을 호출한다.

- URL 이 같으니 브라우저·CDN 입장에서는 전부 같은 요청으로 보인다. **URL 기반 캐싱이 통하지 않는다**
- 그래서 캐싱을 애플리케이션 계층에서 직접 설계해야 한다. 클라이언트 라이브러리(Apollo Client, Relay 등)가 필드 단위 캐시를 제공하는 것도 이 때문이다

## 쿼리 복잡도 제한
클라이언트가 응답 모양을 정한다는 건, **악의적으로 무거운 쿼리도 보낼 수 있다**는 뜻이다.

```graphql
query {
  user(id: "1") { posts { author { posts { author { posts { ... } } } } } }
}
```
- 서로를 참조하는 타입은 이렇게 무한히 파고들 수 있다
- 그래서 **최대 깊이(depth)** 와 **복잡도(complexity)** 제한을 걸어둔다. 스프링에서는 `MaxQueryDepthInstrumentation` 등을 등록한다
- REST 에는 없던 종류의 보안 고려사항이다

## 에러 처리
HTTP 상태 코드로 구분하지 않는다.

- 쿼리 일부가 실패해도 **HTTP 200** 이 나가고, 응답 본문의 `errors` 배열에 내용이 담긴다
- `data` 와 `errors` 가 동시에 있을 수 있다. 일부 필드만 실패한 경우다
- 상태 코드만 보고 성공으로 판단하는 클라이언트 코드는 여기서 깨진다

언제 쓰고, 언제 쓰지 않나
=====
-----
앞 절까지가 GraphQL 이 무엇을 주고 무엇을 요구하는지였다. 그걸 알고 나면 판단은
"좋은 기술인가"가 아니라 **"내 상황에서 값을 하는가"** 가 된다.

기준은 하나로 정리된다. **응답 모양이 자주 달라지는가.**
달라지지 않는다면 GraphQL 이 푸는 문제 자체가 없다.

## GraphQL 이 값을 하는 경우
- **클라이언트가 여럿이고 화면마다 필요한 데이터가 다르다** — 웹은 목록만, 앱은 상세까지 필요한 식. REST 로는 화면별 엔드포인트를 따로 파거나, 가장 큰 응답에 맞춰 모두가 손해를 본다
- **화면 요구가 자주 바뀐다** — 기획이 바뀔 때마다 서버에 엔드포인트를 추가하고 있다면, 그 추가분이 바로 GraphQL 이 없애주는 작업이다
- **여러 리소스를 조합해야 한다** — 사용자 + 글 + 댓글처럼 한 화면에 여러 번 왕복이 쌓이는 구조
- **프론트와 백엔드가 나뉘어 있다** — 응답 모양을 협의하는 왕복이 스키마 하나로 대체된다

## REST 가 나은 경우
- **클라이언트가 하나고 응답 모양이 안정적이다** — 바뀌지 않는 것에 유연함을 사면 비용만 남는다
- **파일 업로드·다운로드가 주 기능이다** — GraphQL 이 가장 불편한 영역이다. 스펙에 파일 타입이 없어 별도 규약(multipart request spec)을 얹어야 한다
- **CDN·브라우저 캐싱에 기대고 있다** — 앞서 본 대로 URL 기반 캐싱이 통하지 않는다. 공개 API 나 트래픽이 큰 읽기 위주 서비스에서는 이게 큰 손해다
- **서버 간 통신이다** — 부르는 쪽이 이미 정해져 있으니 응답 모양을 고를 이유가 없다
- **팀에 GraphQL 경험이 없고 일정이 촉박하다** — N+1·복잡도 제한·에러 처리는 나중에 배우는 게 아니라 처음부터 필요하다. 배울 시간이 없으면 그 비용이 그대로 남는다

## 정리하면

| | REST | GraphQL |
|---|---|---|
| 클라이언트 | 하나 | 여럿, 요구가 제각각 |
| 응답 모양 | 안정적 | 화면마다 다르고 자주 바뀜 |
| 주 트래픽 | 파일·공개 읽기 | 화면 데이터 조회 |
| 캐싱 | HTTP 로 해결 | 직접 설계해야 함 |
| 팀 상황 | 경험 유무 무관 | 학습 시간이 필요 |

## 둘 중 하나만 골라야 하는 건 아니다
실무에서는 섞어 쓰는 경우가 많다.

- 파일 업로드·인증처럼 REST 가 잘하는 것은 REST 로 두고
- 화면 데이터 조회만 GraphQL 로 받는다

이미 REST 로 돌아가는 서비스라면 이 방식이 현실적이다. 전부 바꾸지 않고
가장 아픈 화면 하나부터 GraphQL 로 옮겨보면 값을 하는지 직접 확인할 수 있다.

정리
=====
-----
- GraphQL 은 **클라이언트가 응답 모양을 정하는** API 방식이다. 데이터베이스가 아니다
- 스키마(SDL)가 명세이자 검증 규칙이다. 별도 API 문서를 유지할 필요가 줄어든다
- 진입점은 Query(읽기)·Mutation(쓰기)·Subscription(실시간) 셋
- 실행은 **필드마다 리졸버를 호출**하는 방식이다. 이 모델을 알면 N+1 이 왜 생기는지가 보인다
- REST 가 공짜로 주던 HTTP 캐싱·상태 코드는 직접 설계해야 한다. **더 쉬워지는 게 아니라 문제의 종류가 바뀐다**

용어 정리
=====
-----

| 용어 | 한 줄 정의 |
|---|---|
| 스키마(Schema) | API 에 어떤 데이터가 어떤 모양으로 있는지 정의한 것 |
| SDL | 스키마를 적는 문법 (Schema Definition Language) |
| 스칼라 타입(Scalar) | 더 쪼갤 수 없는 값. Int, Float, String, Boolean, ID |
| 오브젝트 타입(Object) | 필드를 가지는 타입. User, Post 등 |
| non-null (`!`) | 이 필드는 널이 될 수 없다는 표시 |
| Query | 데이터를 읽는 진입점 |
| Mutation | 데이터를 바꾸는 진입점 |
| Subscription | 변경을 실시간으로 받는 진입점 |
| 리졸버(Resolver) | 필드 하나의 값을 실제로 채워 오는 함수 |
| 오버페칭(Over-fetching) | 쓰지 않는 필드까지 받아오는 것 |
| 언더페칭(Under-fetching) | 한 번으로 부족해 추가 호출이 필요한 것 |
| DataLoader | 같은 요청 안의 조회를 모아 N+1 을 막는 장치 |
| GraphiQL | 브라우저에서 쿼리를 짜보는 개발용 화면 |
