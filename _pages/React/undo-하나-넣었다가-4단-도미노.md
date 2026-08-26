---
title:  "undo 하나 넣었다가 4단 도미노"

categories:
  - React
tags:
  - AI
  - Claude Code
  - React
  - ag-Grid
  - 성능최적화

date: 2026-08-22
thumbnail: "/assets/img/thumbnail/react_thumbnail.webp"
---
## 시작: undo 스냅샷이 과거를 바꿨다

그리드에 Ctrl+Z를 붙였다. 그런데 되돌리면 엉뚱한 값이 되살아났다.

재현이 딱 떨어졌다.

- 행1 월 셀에 **11** 입력
- 행2 월 셀에 **22** 입력
- Ctrl+Z **2회**
- 결과 — 행1은 0으로 복원되는데 **행2가 22로 되살아남** (기대 0)

원인은 얕은 복사였다.

```js
// 배열만 새로 만들고 행 객체 참조는 그대로 담았다
undoStack.push([...rows]);
```

그리고 ag-grid 셀 에디터의 `valueSetter`가 **`params.data`를 제자리 변형(in-place mutation)** 한다. `params.data`는 곧 `rows`의 그 행 객체다.

- 스냅샷을 찍는다 → 배열은 새것, **행 객체는 같은 것**
- 나중 행을 편집한다 → `valueSetter`가 그 객체를 직접 고친다
- **과거 스냅샷에 담긴 같은 객체도 함께 바뀐다**

<div class="diagram" role="img" aria-label="배열만 복사하고 행 객체는 참조를 공유해 나중 편집이 과거 스냅샷까지 바꾼다">
{% include diagrams/domino--shallow-snapshot.svg %}
</div>

수정은 행과 그 안의 사용량까지 얕은 복제하는 헬퍼를 만들고, 스택에 push하는 **4개 지점 전부**에 적용한 것이다. 한 곳만 고치면 나머지 경로로 같은 버그가 남는다.

테스트는 이렇게 확인했다.

> 수정 전 코드로 실행해 **실제로 실패함을 확인한 뒤**(행2가 22로 남음), 수정본에서 통과함을 확인했다.

여기까지는 깔끔하다. 문제는 이 수정이 **다음 세 개를 연쇄로 불렀다**는 것이다.

## 도미노 1: 포커스가 사라졌다

배출시설 직접입력 칸에 글자를 치면 **한 글자마다 포커스가 날아갔다.** 이미 고쳤던 티켓(0061)의 재발이었다.

원인 체인이 길다. 커밋에 적힌 그대로다.

1. undo 스냅샷을 찍으려고 `handleRowUpdate`의 `useCallback` deps를 `[]` → **`[rows]`** 로 바꿨다
2. `rows`가 바뀔 때(= **매 keystroke**)마다 `handleRowUpdate`의 identity가 바뀐다
3. 그 identity가 `emsColumn`(useMemo, deps에 포함) → `columnDefs`(useMemo)로 **전파**된다
4. ag-grid가 컬럼 정의가 바뀌었다고 판단해 **cellRenderer를 재생성**한다
5. 그 cellRenderer 안에 **항상 마운트돼 있던 순수 React `<input>`** 이 언마운트·재마운트된다
6. 포커스가 날아간다

<div class="diagram" role="img" aria-label="deps 한 줄 변경이 useCallback 에서 useMemo 를 거쳐 ag-grid cellRenderer 재생성과 input 재마운트로 전파된다">
{% include diagrams/domino--identity-chain.svg %}
</div>

**deps 배열 한 줄이 DOM 언마운트까지 도달했다.** 중간의 어느 단계도 잘못 짜인 게 없다. `useMemo`가 deps 변화에 반응한 것도, ag-grid가 컬럼 정의 변화에 반응한 것도 정상 동작이다. 정상 동작 다섯 개가 이어지니 사고가 됐다.

수정은 `rows`의 현재 값을 **동기적으로 미러링하는 `rowsRef`** 를 두고, deps를 다시 `[]`로 고정한 것이다.

여기서 `useEffect`로 ref를 동기화하지 않은 이유가 중요하다.

> `useEffect` 기반 동기화의 **커밋-이후 지연**(같은 틱 연속 호출 시 스테일 위험, GHG-0067 당시 rows 통째 스냅샷 방식이 이 이유로 기각된 전례와 동일한 함정)을 피했다.

`useEffect`는 렌더가 커밋된 **뒤에** 돈다. 같은 틱에서 핸들러가 연속 호출되면 ref가 아직 옛값이다. 그래서 `setRows`를 부르는 **같은 문장에서** ref도 함께 갱신하는 방식을 택했다.

## 도미노 2: 한글이 깨졌다

포커스는 유지됐다. 이번엔 한글이 낱자로 분리됐다.

```
"안녕" → "ㅇㅏㄴㄴㅕㅇ"
```

원인은 **controlled input의 값 왕복**이었다.

```jsx
<input value={row.manualEmsName ?? ""} ... />
```

이 값은 이렇게 한 바퀴 돈다.

```
onChange → handleManualEmsNameChange → handleRowUpdate
        → setRows → AG Grid rowData → params.data → value
```

**이 왕복이 한 렌더라도 늦으면**, React가 조합 중인 DOM input에 **이전(stale) 값을 다시 써 넣는다.** 그러면 브라우저의 IME 조합 상태가 파괴된다.

한글 입력은 여러 keystroke가 모여 한 글자가 되는 **조합(composition)** 과정이다. 그 도중에 DOM의 `value`를 밖에서 덮어쓰면 브라우저는 조합을 포기한다. 영문은 한 글자가 한 keystroke라 이 문제가 안 보인다. **영어로 테스트하면 절대 못 잡는 버그다.**

수정의 핵심은 **`value` prop을 input에 직접 물리지 않는 것**이다.

- 별도 컴포넌트를 만들어 **로컬 draft state로 DOM value를 관리**
- `composingRef` / `lastEmittedRef`로 **조합 중인지, 내가 emit한 값이 돌아온 건지** 판별
- 붙여넣기·Undo/Redo 같은 **진짜 외부 변경만** draft에 동기화
- `onChange`는 조합 중에도 **항상 상위에 알린다** — 저장·검증용 데이터는 최신 유지

즉 **DOM 표시값과 애플리케이션 데이터를 일부러 분리**했다. controlled input의 원칙을 국소적으로 깬 것인데, IME라는 브라우저 고유 상태를 보호하려면 이 방법밖에 없었다.

## 도미노 3: 그 수정에도 결함이 있었다

코드리뷰에서 두 가지가 더 나왔다.

**① `rowsRef` 갱신 위치가 틀렸다**

```js
// 잘못된 위치 — updater 콜백 "안"
setRows(prev => {
    const next = ...;
    rowsRef.current = next;   // 여기
    return next;
});
```

문제가 두 겹이다.

> updater는 **다음 렌더에서 실행**되므로 `handleRowUpdate` 주석이 세운 "setRows와 같은 문장에서 동기 갱신" 불변식이 이 경로엔 성립하지 않았고, 순수해야 할 updater 안의 ref 쓰기는 **렌더 단계 부수효과라 StrictMode 이중 실행 대상**이었다.

내가 도미노 1에서 세운 규칙("같은 문장에서 동기 갱신")을 **다른 4곳에서는 지키지 않고 있었다.** 그리고 `setState`의 updater는 순수 함수여야 하는데 거기서 ref를 쓰면 React 18 StrictMode에서 두 번 실행된다.

**② `composingRef`가 굳으면 셀이 영구 무반응**

- 조합 중 외부 값 변경(붙여넣기·Undo)이 오면 → 동기화 이펙트가 early-return하며 **그냥 버렸다**
- `compositionend`가 유실되면(조합 중 포커스 이동 등) → `composingRef`가 **`true`로 굳는다**
- 그 셀은 이후 **외부 값 변경에 영구히 무반응**

수정은 보류 큐(`pendingExternalRef`)를 두어 조합 중 온 외부 변경을 **버리지 않고 보관했다가 조합 종료 시 채택**하고, `onBlur`를 안전망으로 추가해 고착을 풀도록 한 것이다.

상태 플래그를 쓸 때 **"해제 이벤트가 안 올 수도 있다"** 를 항상 가정해야 한다는 교훈이다. `compositionend`, `transitionend`, `animationend` 같은 종료 이벤트는 생각보다 자주 유실된다.

## 도미노를 되짚으면

| 단계 | 고친 것 | 그 수정이 부른 것 |
|---|---|---|
| 0 | undo 스냅샷 참조 공유 | deps `[]` → `[rows]` |
| 1 | 포커스 유실 (deps 전파) | `rowsRef` 도입 |
| 2 | 한글 IME 붕괴 (controlled 왕복) | draft state + composingRef |
| 3 | ref 갱신 위치 · composingRef 고착 | — |

네 단계가 **전부 같은 주제**다. **참조 동일성(referential identity)과 상태 동기화 타이밍.**

- 0단계 — 객체 참조를 공유해서 과거가 바뀜
- 1단계 — 함수 참조가 매번 바뀌어서 컴포넌트가 재생성됨
- 2단계 — 값이 한 바퀴 도는 사이에 한 렌더가 밀림
- 3단계 — ref 갱신이 한 렌더 밀리고, 플래그가 안 풀림

React에서 "무엇이 언제 같은 것으로 취급되는가"가 어긋나면, 증상은 포커스·IME·undo처럼 전혀 달라 보여도 원인은 하나다.

## 배운 것

**① 참조 동일성 변경은 "전파 범위"를 먼저 그린다.**
deps에 값 하나 추가하는 건 한 줄이지만, 그 identity가 `useMemo` 사슬을 타고 어디까지 가는지는 한 줄이 아니다. 특히 ag-grid처럼 **참조 비교로 재생성을 판단하는 라이브러리**가 끝에 있으면 DOM까지 도달한다.

**② 한글 입력은 반드시 한글로 테스트한다.**
IME 조합은 영문 입력에 없는 상태 머신이다. controlled input, 값 왕복, 외부 동기화가 얽히면 **영문에서는 멀쩡하고 한글에서만 깨진다.** 자동화 테스트도 조합 이벤트를 흉내 내야 잡힌다.

**③ 회귀 테스트는 "되돌리면 실패하는가"까지 확인한다.**
이 네 커밋 전부 그렇게 했다. `deps`를 `[rows]`로 되돌려 테스트가 실제로 빨간불이 되는지 **수동으로 확인한 뒤** 복원했다. 수정 후에만 초록불인 테스트는 그 버그를 잡는다는 보장이 없다.

**④ 내가 세운 불변식을 내가 안 지키고 있는지 본다.**
도미노 3의 `rowsRef` 건이 정확히 그랬다. 주석으로 "같은 문장에서 동기 갱신"이라 적어두고, 다른 4곳에서는 updater 안에서 갱신하고 있었다. 규칙을 만들었으면 **그 규칙을 지키는지 검사하는 방법**까지 같이 만들어야 한다.
