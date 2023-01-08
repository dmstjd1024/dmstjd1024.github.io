---
title: "엔티티 설정"

categories:
  - Spring
tags:
  - [spring, JPA, entity, TICKET-EXPEDITIONARY-FORCE]

toc: true
toc_sticky: true

date: 2023-01-06
last_modified_at: 2023-01-06
---

# 고민
---

과연 Account 객체를 생성할 때 필요한 column명을 찾아서 적어봤다.

---

## Account

~~~
@Getter
@Builder
@Entity
@NoArgsConstructor
@AllArgsConstructor
public class Account {

    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name="account_id")
    private Long id;

    @NotEmpty
    @Column(unique = true)
    private String publicIp;

    @Column(unique = true)
    private String loginId;

    @NotEmpty
    private String password;

    private String name;

    @Column(unique = true)
    private String nickname;

    @Column(unique = true)
    private String email;

    @Lob
    private String profileImage;

    private LocalDateTime createDate;

    private LocalDateTime modifyDate;

    @Enumerated(EnumType.STRING)
    private Role role;

}
~~~

##주요 어노테이션

일단 DB Diagram을 그려야 하는데 아직 모여서 정확하게 테이블 컬럼들을 정리하지 않아
 내가 블로그에서 봤던 기준으로 간단하게 Account를 정의해봤다.

@GeneratedValue(strategy = GenerationType.IDENTITY)
  
전적으로 db에게 기본키 생성을 위임한다. (아직 db쪽이 약해서 설명을 자세하게 쓰지 못했는데
좀더 알아보고 수정해서 적어봐야겠다.)

@Lob

Lob은 Large Obejct란 뜻으로 프로필사진같은 경우 데이터가 크기 때문에 지정하는 것도 있고
  데이터를 안정성 때문이다. -> 만약 이미지 경로로 지정해놨을 때 실수로 이미지 경로의 파일들이
  사라지는 경우 이미지파일을 찾을 수 없게되기 때문이다.

@Enumerated(EnumType.String)

Entity에선 enum을 db에 저장할 땐 default로 EnumType.ORIGINAL로 지정되있다. 이때 ORIGINAL로 저장하면
DB에 순서 enum의 순서를 정수로 저장하는데 이는 나중에 db를 볼때 1, 2, 3 등등으로 저장되기에
식별하기가 어려워 enum의 이름을 직접 저장하도록 string을 사용했다.

---

## 내 생각

일단 기본적으로 내가 아는 것들에 대해서 써놓았고 팀원들과 코드리뷰를 통해 Ticket이나 다른 테이블들의
컬럼과 연관관계를 짓는 작업을 진행해야겠다.
