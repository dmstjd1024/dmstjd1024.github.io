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

## State
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

## Hooks
함수 컨퍼넌트도 class 컴포넌트처럼 state를 가질 수 있게 해주는 기능
갈고리
함수명 앞에 use가 붙어서 훅이라는 것을 명시해준다.

## useState Hook
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

## useMemo, useCallback, useRef

### useMemo
- Memoized value를 리턴하는 Hook
- Memoization : 최적화를 사용하는 개념, 연산 값이 많은 값을 저장해놨다가 이전에 사용한 결과를 받아옴
- 사용법

```jsx
const memoizedValue = useMemo( () => {
    // 연산값이 높은 작업을 수행하여 결과를 반환
    return computeExpensiveValue(의존성 변수1, 의존성 변수2);
    },
    [의존성 변수1, 의존성 변수2]
);
```
- 랜더링에서 일어날 내용을 넣으면 안됨 ex) `useEffect`에서 실행되어야 할 side effect
- 의존성 배열을 넣지 않으면 컴포넌트가 랜더링 될 때마다 실행된다.

```jsx
const memoizedValue = useMemo(
        () => computeExpensiveValue(a,b)
);
```
- 의존성배열이 빈 배열인 경우, 컴포넌트 mount 시에만 호출된다. -> mount 이후에는 변경되지 않음

```jsx
const memoizedValue = useMemo(
        () => computeExpensiveValue(a,b),
        []
);
```
`useMemoHook`에 의존성 변수를 넣고, 해당 변수의 값이 변해야 할 경우에만 사용한다.
### useCallback()
- 값이 아닌 함수를 반환

```jsx
const memoizedCallback = useCallback(
    () => {
        doSomething(의존성 변수1, 의존성 변수2);
    },
    [의존성 변수1, 의존성 변수2]
);
```
따라서 `useCallback` 과 `useMemo` 의 함수 선언은 같은 말이다.
```jsx
  useCallback(함수, 의존성 배열); // 위아래 둘다 같은 내용
  useMemo(() => 함수, 의존성 배열); // 위아래 둘다 같은 내용
```
### useRef()
- reference를 사용하기 위한 Hook -> 특정 컴포넌트를 접근할 수 있는 객체
- `refObject.current` 속성 -> ref 하는 엘리먼트

```jsx
const refContainer = useRef(null);
```
컴포넌트가 mount 되기 전까지 계속 유지된다.
```jsx
function TextInputWithFocusButton() {
    const inputEl = useRef(null);
    
    function onButtonClick() {
        // `current`가 가리키는 DOM 노드에 포커스를 맞춘다.
        inputEl.current.focus();
    };
    
    return (
        <>
            <input ref={inputEl} type="text" />
            <button onClick={onButtonClick}>
                Focus the input
            </button>
        </>
    );
}
```
내부의 데이터가 변경되었을 때, 별도로 알려주지 않는다.
`useCallback`은 자식 엘리먼트가 변경되었을 때, 알림을 받을 수 있다.
### Callback Ref

```jsx
const mesureRef = useCallback(node => {
    if(node !== null) {
        // node가 변경되었을 때, 알림을 받는다.
        console.log('엘리먼트가 변경되었습니다.', node);
    }
}, []);
```

## Hook의 규칙과 Custom Hook 만들기
- Hook은 컴포넌트의 최상위 레벨에서만 호출해야 한다.
- Hook은 컴포넌트가 렌더링 될 때마다 매번 같은 순서로 호출되어야 한다.

잘못된 Hook 사용법
```jsx
function MyComponent(props) {
    const [name, setName] = useState('Inje');
    
    if(name !== ''){
       useEffect( () => {
          ... // 이 부분은 잘못된 사용 예시입니다.
       });
    }
}
```
- 리액트 함수 컴포넌트에서만 Hook을 호출해야 한다.
- 일반적인 javascript에서 호출 X
`eslint-plugin-react-hooks`를 사용하여 Hook의 규칙을 검사할 수 있다.

### Custom Hook
- Hook을 재사용할 수 있는 방법
- Custom Hook 추출하기
- 이름이 `use` 로 시작하고, 내부에서 다른 Hook을 호출하는 하나의 자바스크립트 함수

```jsx
// useUserStatus 를 사용하여 사용자 상태를 관리하는 Custom Hook
function UserStatus(props) {
    const isOnline = useUserStatus(props.user.id);
    
    if(isOnline === null){
        return '대기 중...';
    }
    return isOnline ? '온라인' : '오프라인';
}

function UserListItem(props) {
    const isOnline = useUserStatus(props.user.id);
    
    return (
        <li>
            {props.user.name} - {isOnline ? '온라인' : '오프라인'}
        </li>
    );
}
```
- 여러개의 컴포넌트에서 하나의 Custom Hook을 사용할 때, 컴포넌트 내부에 있는 모든 state와 effect는 전부 분리되어 있다.
- Custom Hook은 컴포넌트의 상태를 공유하지 않는다. (분리된 state와 effect를 가진다.)
- 분리된 데이터들을 공유하고싶을 때,

```jsx
function CheckUserStatus(props) {
    / ** Custom Hook을 사용하여 사용자 상태를 관리하는 예시
    const [userId, setUserId] = useState(1);
    const isUserOnline = useUserStatus(userId);
    / ** 으로 하면, 이전에 선택된 사용자를 취소하고, 새로운 사람의 상태를 다시 구독한다.
}
```