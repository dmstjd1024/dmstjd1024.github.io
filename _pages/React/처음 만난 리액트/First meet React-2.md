---
title:  "리액트 시작하기 (6 ~ 장)"

categories:
  - frontend, react
tags:
  - Frontend
  - React

date: 2025-07-12
thumbnail: "/assets/img/thumbnail/react_thumbnail.webp"
---

State
=====
-----
- 리액트 Component의 상태를 관리하는 객체
- state는 개발자가 정의한다.
- 랜더링이나 데이터의 흐름에 사용되는 값들만 state에 포함시켜야한다.
  - state가 변경될 경우, 컴포넌트가 재 랜더링 되기 때문에 랜더링과 데이터의 흐름에 관계없는 데이터를 저장하면, 컴포넌트가 재 랜더링되어 성능에 영향을 줄 수 있다.
  - 컴포넌트의 인스턴스 필드로 정의
- Javascript 객체라 생각

```jsx
class LikeButton extends React.Component {
    constructor(props) {
        super(props);
        this.state = {liked: false}; // state 정의
    }
}
```
- state는 직접 수정할 수 없다.
```jsx
  (X)
  this.state = {name : 'Inje'}
  
  this.setState({
    name: 'Inje'
    });
```

컴포넌트가 계속 존재하는게 아니라 시간에 따라 생성, 업데이트되다가 사라진다.
Hook
=====
-----
함수 컨퍼넌트도 class 컴포넌트처럼 state를 가질 수 있게 해주는 기능
갈고리
함수명 앞에 use가 붙어서 훅이라는 것을 명시해준다.

useState Hook
state 를 사용하기 위한 Hook

```jsx
const [변수명, set함수명] = useState(초기값);
// return 값은 배열 -> 1. state 변수, 2. state를 업데이트하는(set) 함수
```

```jsx
import React, {useState} from "react";

function Counter(props) {
    const [count, setCount] = useState(0); // count라는 state 변수와 setCount라는 업데이트 함수 생성
// setCount -> 변수 각가에 대해 set함수가 따로 존재!  
  return (
      <div>
        <p>총 {count}번 클릭했습니다.</p>
        <button onClick={() => setCount(count + 1)}>
          클릭
        </button>
      </div>
  );
}
```
### useEffect()
- side effect를 수행하기 위한 Hook
- side effect = 효과, 영향
- 다른 컴포넌트에 영향을 미칠 수 있으며, 렌더링 중에는 작업이 완료될 수 없기 때문이다.
- 함수 컴포넌트에서 Side effect를 실행할 수 있게 해주는 Hook

```jsx
useEffect(이펙트 함수, 의존성 배열);
```
첫번째 컴포넌트가 랜더링 된 이후, 재 랜더링 된 이후에 실행됨

```jsx
useEffect(이펙트 함수);
```
의존성 배열 생략 시, 컴포넌트가 업데이트 될 때마다 호출됨

useEffect와 useState를 함께 사용하여 컴포넌트의 상태를 관리할 수 있다.

```jsx
import React, {useState, useEffect} from "react";

function Counter(props) {
  const [count, setCount] = useState(0);

  // componentDidMount, componentDidUpdate와 비슷하게 작동한다
  useEffect(() => {
      // 브라우저 API를 사용해서 document의 title을 업데이트
    document.title = `You clicked ${count} times`;
  });
  
  return (
      <div>
        <p>총 {count}번 클릭했습니다.</p>
        <button onClick={() => setCount(count + 1)}>
          클릭
        </button>
        </div>
  );
}
```

```jsx
import React, {useState, useEffect} from "react";

function UserStatus(pros) {
    const [isOnline, setIsOnline] = useState(null);
    
    function handleStatusChange(status) {
        seInOnline(status.isOnline);
    }
    
    useEffect( () => {
        ServerAPI.subscribeUserStatus(props.userId, handleStatusChange);
        return () => {
            ServerAPI.unsubscribeUserStatus(props.user.id, handleStatusChange);
        };
    });
    
    if(isOnline === null) {
        return '대기 중...';
    }
    return isOnline ? '온라인' : '오프라인';
}
```

```jsx
function UserStatusWithCounter(props) {
    const [count, setCount] = useState(0);
    useEffect(() => {
        document.title = `총 ${count}번 클릭했습니다.`;
    }); 
    
    const [isOnline, setIsOnline] = useState(null);
    useEffect(() => {
    ServerAPI.subscribeUserStatus(props.userId, handleStatusChange);)
        return () => {
            ServerAPI.unsubscribeUserStatus(props.userId, handleStatusChange);
        };
    });
    
    function handleStatusChange(status) {
        setIsOnline(status.isOnline);
    }
}
```