---
title:  "리액트 시작하기 (1 ~ 5장)"

categories:
  - React
tags:
  - Frontend
  - React

date: 2025-06-03
thumbnail: "/assets/img/thumbnail/react_thumbnail.webp"
---
## 리액트 설치 방법

- npm 설치
- node 설치
- 툴은 원하는대로

-----

## JSX 문법
- 자바스크립트 확장 문법
- JavaScript + XML/HTML 
ex) 예시
```jsx
const element = <h1>Hello, world!</h1>;
```

## 원리

```jsx
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

## Rendering Element

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

<div class="diagram" role="img" aria-label="Virtual DOM 이 바뀐 부분만 실제 DOM 에 반영하는 흐름">
{% include diagrams/react1--virtual-dom.svg %}
</div>

## Components 와 Props
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
  - Pure : 입력값이 동일하면 항상 동일한 출력을 반환하는 함수
- 모든 리액트 컴포넌트는 Props를 통해 데이터를 전달받아 렌더링해야한다.

<div class="diagram" role="img" aria-label="Props 가 상위에서 하위로 흐르는 구조">
{% include diagrams/react1--props-flow.svg %}
</div>

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
## Props의 특징 사용법
- Props는 컴포넌트에 전달되는 데이터로, 컴포넌트의 동작과 렌더링을 제어

```jsx
function App(props) {
    return (
        <Profile
            name="소플"
            introduction="안녕하세요, 소플입니다."
            viewCount={1000}
            />
    );
}
```

### Component 만들기 및 랜더링
- 클래스 컴포넌트, 함수 컴포넌트
- 주로 함수 컴포넌트를 사용한다함
- 그래도 클래스 컴포넌트를 알고있어야 한다.

#### 함수 컴포넌트
- react Component를 일종의 함수로 생각한다.

```jsx
function Welcome(props) {
    return <h1>안녕하세요, {props.name}님!</h1>;
}
```
#### 클래스 컴포넌트
- javascript es6 문법을 사용하여 만든 컴포넌트

```jsx
class Welcome extends React.Component {
    render() {
        return <h1>안녕하세요, {this.props.name}님!</h1>;
    }
}
```
- 컴포넌트의 이름
- 항상 대문자로 시작해야함 (소문자로 입력하면 DOM 엘리먼트로 인식됨)

```jsx
const element = <Welcome name="소플" />;
```
#### 컴포넌트 렌더링

```jsx
function Welcome(props) {
  return <h1>안녕하세요, {props.name}님!</h1>;
}
const element = <Welcome name="소플" />;
ReactDOM.render(
    element,
    document.getElementById('root')
);
```

### 컴포넌트 합성과 추출
#### 컴포넌트 합성
- 복잡한 화면을 여러개의 Components로 나눠서 구현

```jsx
function App() {
    return (
        <div>
            <Header />
            <MainContent />
            <Footer />
        </div>
    );
}
```
#### 컴포넌트 추출
- 큰 컴포넌트를 작은 컴포넌트로 나누어 재사용성을 높임

```jsx
function Component(props) {
    return (
        <div className="content">
          <div className="user-info">
            <img className="avatar"
                 src={props.author.avatarUrl}
                 alt={props.author.name} 
            />
            <div className="user-info-name">
              {props.author.name}
              </div>
          </div>
          <div className="comment-text">
                {props.text}
          </div>
          <div className="comment-date">
              {formatDate(props.date)}
          </div>
        </div>
    );
}
```
#### Avatar 추출

```jsx
function Avatar(props) {
    return (
        <img className="avatar"
             src={props.user.avatarUrl}
             alt={props.user.name} 
        />
    );
}
```
```jsx
function Component(props) {
    return (
        <div className="content">
          <div className="user-info">
            <Avatar user={props.author} />
            <div className="user-info-name">
              {props.author.name}
              </div>
          </div>
          <div className="comment-text">
                {props.text}
          </div>
          <div className="comment-date">
              {formatDate(props.date)}
          </div>
        </div>
    );
}
```
#### UserInfo 추출

```jsx
function UserInfo(props) {
    return (
        <div className="user-info">
            <Avatar user={props.user} />
            <div className="user-info-name">
                {props.user.name}
            </div>
        </div>
    );
}
```
```jsx
function Component(props) {
    return (
        <div className="content">
            <UserInfo user={props.author} />
          <div className="comment-text">
                {props.text}
          </div>
          <div className="comment-date">
              {formatDate(props.date)}
          </div>
        </div>
    );
}
```

### (실습) 댓글 컴포넌트 만들기
- Comment.jsx

```jsx
import React from "react";

function Comment(props) {
    return (
        <div>
            <div>
                <img
                src="https://upload.wikimedia.org/wikipedia/commons/8/89/Portrait_Placeholder.png"/>
            </div>
        <div>
            <span>{props.name}</span>
            <span>{props.comment}</span>
        </div>
        </div>

    );
}

export default Comment;
```

- CommentList.jsx

```jsx
import React from "react";
import Comment from "./Comment";

const comments = [
    { name: "test", comment: "안녕하세요 test." },
    { name: "test2", comment: "안녕하세요 test2." },
    { name: "test3", comment: "안녕하세요 test3." },
];

function CommentList(props) {
    return (
        <div>
            {comments.map((comment) => {
                return (
                    <Comment name={comment.name} comment={comment.comment}/>
                )
            })}
        </div>
    );
}

export default CommentList;
```

- App.jsx

```jsx
const root = createRoot(document.getElementById('root'));
root.render(
    <React.StrictMode>
        <CommentList />
    </React.StrictMode>,
    document.getElementById('root')
    );
```