---
title:  "리액트 시작하기"

categories:
  - frontend, react
tags:
  - Frontend
  - React

date: 2025-06-03
thumbnail: "/assets/img/thumbnail/react_thumbnail.webp"
---

리액트 설치 방법
=====
-----

- npm 설치
- node 설치
- 툴은 원하는대로

-----

JSX 문법
=====
-----
- 자바스크립트 확장 문법
- JavaScript + XML/HTML 
ex) 예시
```jsx
const element = <h1>Hello, world!</h1>;
```

## 원리
```javascript
React.createElement(
    type,
    [props], ## 속성
    [...children]  ## 자식 엘리먼트
)
```

## JSX 문법의 장점
- 가독성 향상: HTML과 유사한 문법으로 작성되어, 코드가 더 직관적이고 이해하기 쉬움
- Injection 방지: JSX는 자바스크립트 표현식을 안전하게 HTML에 삽입할 수 있도록 하여, XSS 공격을 방지하는 데 도움을 줌

{} 가 들어가면 무조건 자바스크립트 코드로 바뀜

Rendering Element
=====
-----

## Elements의 정의와 생김새
- 어떤 물체를 구성하는 성분
- 리액트 앱을 구성하는 가장 작은 블록들
- 화면에 보이는 것들을 기술
- 리액트(Elements)는 자바스크립트 객체 형태로 존재


## Elements의 특징 및 렌더링하기
- 불변성 (immutable)
- 변경된 부분을 계산하여 해당 부분만 다시 렌더링
- Root dom node
- ReactElement : React 의 Virtual DOM에 존재
- DOMElement : 실제 브라우저의 DOM에 존재
- ReactDOM.render()를 통해 ReactElement를 DOMElement로 변환

Components 와 Props
=====
-----
## 컴포넌트의 정의
- 컴포넌트는 UI를 구성하는 독립적인 재사용 가능한 코드 블록
- 컴포넌트는 함수나 클래스 형태로 정의되며, 입력값(Props)을 받아 UI를 렌더링
- 컴포넌트는 상태(State)를 가질 수 있으며, 상태가 변경되면 UI가 자동으로 업데이트됨
- 컴포넌트는 계층 구조로 구성되어, 상위 컴포넌트가 하위 컴포넌트를 포함할 수 있음
- 컴포넌트는 Props를 통해 데이터를 전달받아 렌더링
- 컴포넌트는 재사용 가능하고, 유지보수가 용이함

## Props의 정의
- Props는 컴포넌트에 전달되는 입력값 (React의 속성)
- ReadOnly 속성으로, 컴포넌트 내부에서 변경할 수 없음
- 모든 리액트 컴포넌트들은 그들의 Props에 관해서는 Pure(순수)함수 같은 역할을 해야한다.
- 모든 리액트 컴포넌트는 Props를 통해 데이터를 전달받아 렌더링해야한다.

```jsx
function App(pros){
    return (
        <Profile
            name="John Doe"
            age= {30}
            />
    );
}
```
```jsx
function App(pros){
    return (
        <Layout
            width={100}
            height={200}
            header={<Header title="제목"/>}
            footer={<Footer/>}
            />
    );
}
```

