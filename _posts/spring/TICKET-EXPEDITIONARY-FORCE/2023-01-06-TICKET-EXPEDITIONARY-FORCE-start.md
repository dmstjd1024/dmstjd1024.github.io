---
title: "티켓 원정대 출발!"

categories:
  - spring
tags:
  - [spring, JPA, entity, TICKET-EXPEDITIONARY-FORCE]

toc: true
toc_sticky: true

date: 2023-01-06
last_modified_at: 2023-01-06
---

# 프로젝트 시작
---
 TDD 책을 정독하고 읽었던 내용들을 사용해보는 프로젝트를 진행해보려고 한다.  
 나는 2,3번 프로젝트를 진행해봤는데 결과는 좋지 않았고 이번에는 결과물을 완성하고 싶은 마음이 크다.
  
---
  
## 설명  
 
  100명에게 Ticket을 배포하는 프로그램을 RESTful방식 개발합니다 *신청시 확률에 따라 티켓을 획득 하거나 꽝이 됩니다  
- 티켓:100매  
- 로그인도 추가하기 (카카오, 네이버)  
- 공인 IP당 1회 신청가능  
- 30%확률로티켓획득가능  
- WAS는 2대 이상 이용한다고 가정  
  
---
  
## 사용 기술  
  
| 기술명 | 내용 |
|:---------:|:---------------:|
| `spring boot` | Spring framework의 다양한 설정을 최소화 |  
| `thymeleaf` | 스프링에서 미는 Java XML / XHTML / HTML5 템플릿 엔진|  
| `lombok` | getter, setter, 등의 기본 메서드 코드 간략화|  
| `spring boot test` | spring 통합테스트 진행으로 api 테스트 사용|    
| `h2 database` | RDBMS, 메모리에 데이터 저장 용도(추후 database 추가) |    
| `spring boot security` | spring 기반 Application 보안, 인증 담당 framework |    
| `swagger` | api 문서화 활용 |    
| `bootstrap` | 웹사이트 꾸며주는 HTML, CSS, JS 프레임워크 |    
| `git` | 버전관리 툴로 github를 통해 개발 진행 |  

  
---  
  
## 파트
  
 - 템플릿 설정
 - 티켓
 - 회원 관리(내 파트)
 - 로그인

 개발 방법  
 애자일 방법론으로 서로 스터디를 통한 프로젝트이기에 짧은 반복을 진행할 것이며  
 배달의 민족에서 사용하는 git flow를 사용해 기능마다 merge시키는 방식을 진행할 것입니다.
  
---
  
## 처음 내가 해야 할 일  
  Account Entity에서 내가 생각하는 column명을 Template 설정 파트 담당에게 넘길 것이다.

 