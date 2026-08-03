---
title:  "AG Grid의 autoHeight는 행 가상화를 끈다"

categories:
  - AI
tags:
  - AI
  - Claude Code
  - React
  - 성능최적화

date: 2026-06-02
thumbnail: "/assets/img/thumbnail/sample.png"
---

## 문제

입출력 데이터를 입력하는 그리드 화면이 있었다. 행이 수백 개인 상황에서 **셀 하나를 편집할 때마다 눈에 띄게 버벅였다.** 값을 타이핑하는 속도를 화면이 못 따라오는 수준이었다.

## 원인 1: 편집할 때마다 columnDefs가 통째로 재생성됐다

`columnDefs`를 `useMemo`로 감싸긴 했는데, 의존성 배열에 `rows`, `visibleRows`, `updateMonth`, `onClickRowAction`이 들어 있었다.

문제는 `onClickRowAction`이다. 이 함수의 내부 의존성에 `gridRows`가 있어서 **셀을 하나 편집할 때마다 identity가 바뀐다.** 그러면 `columnDefs`가 재생성되고, AG Grid는 컬럼 정의가 바뀌었다고 판단해 전 컬럼을 다시 적용한다. 행이 수백 개면 이게 그대로 비용이다.

해결은 이 값들을 렌더 사이에 안정적인 ref로 읽는 것이었다.

```ts
const rowsRef = useRef<any[]>(rows);
rowsRef.current = rows;
const visibleRowsRef = useRef<any[]>(visibleRows);
visibleRowsRef.current = visibleRows;
const updateMonthRef = useRef<string>(updateMonth);
updateMonthRef.current = updateMonth;
const onClickRowActionRef = useRef(onClickRowAction);
onClickRowActionRef.current = onClickRowAction;
```

셀 핸들러와 렌더러가 최신값을 ref로 읽으니 `columnDefs`의 의존성에서 이 넷을 뺄 수 있다. 그러면 `columnDefs`는 재생성되지 않는다.

## 원인 2: 체크박스 하나 누를 때마다 전체 배열을 remap했다

기존 방식은 cellRenderer가 자동으로 리렌더되게 하려고 row 데이터에 `_isChecked`를 주입하고 있었다.

```ts
const rowsWithSelection = useMemo(
  () => visibleRows.map((row: any) => ({
    ...row,
    _isChecked: (checkedItems as number[]).includes(row.id),
  })),
  [visibleRows, checkedItems],
);
```

체크박스 토글 한 번에 전체 배열이 새로 만들어지고, AG Grid는 그걸 전부 다시 diff한다. 수백 행이면 토글 한 번의 비용이 크다.

이 remap을 없애고 `visibleRows`를 직접 rowData로 쓰되, cellRenderer는 `checkedItemsRef`를 읽게 했다. 선택이 바뀌면 **체크박스 컬럼만** 강제 새로고침한다.

```ts
const api = agGridRef.current?.api;
api?.refreshHeader();
api?.refreshCells({ columns: ['__checkbox__'], force: true });
```

## 원인 3: autoHeight가 가상화를 끄고 있었다

이게 가장 놓치기 쉬운 부분이었다. 그리드가 `domLayout='autoHeight'`로 돼 있었다.

`autoHeight`는 그리드가 스크롤 없이 전체 높이만큼 늘어나 페이지에 자연스럽게 흐르게 하는 옵션이다. 그런데 전체 높이를 차지한다는 건 **모든 행이 DOM에 존재해야 한다는 뜻**이고, 그러면 AG Grid의 네이티브 행 가상화가 동작할 수 없다. 500행이면 500행이 다 DOM에 있다.

행 수에 따라 전략을 나눴다.

```ts
const VISIBLE_ROWS = 12;
const ROW_HEIGHT = 32;
const HEADER_HEIGHT = 32;
const VIRTUALIZED_HEIGHT = HEADER_HEIGHT + VISIBLE_ROWS * ROW_HEIGHT;

const useFixedHeight = collapsed || rowData.length > VISIBLE_ROWS;
```

| 행 수 | domLayout | 결과 |
|---|---|---|
| 12개 이하 | `autoHeight` | 페이지에 자연스럽게 흐름, 중첩 스크롤 없음 |
| 12개 초과 | `normal` + 고정높이 | 네이티브 행 가상화 + 내부 스크롤 + sticky 헤더 |

작은 섹션이나 빈 섹션까지 고정 높이로 만들면 빈 공간이 남고 중첩 스크롤이 생겨서 오히려 불편하다. 그래서 임계값을 두고 12개 이하는 기존 동작을 유지했다. 12개를 넘어가면 DOM 행 수가 일정하게 유지되므로 500행이든 5000행이든 렌더 비용이 같아진다.

접힌 섹션도 고정 높이로 두는 예외가 하나 있는데, 부모가 `display: none`으로 숨기면 `autoHeight`가 높이를 0으로 측정해버리기 때문이다.

## 부수 개선: 전체선택 판정

전체선택 체크 여부를 이렇게 계산하고 있었다.

```ts
visibleRows.every((r: any) => (checkedItems as number[]).includes(r.id));
```

`includes`가 배열 선형 탐색이라 보이는 행 M개 × 선택 항목 N개, 즉 O(M×N)이다. `checkedItems`를 `Set`으로 만들어 조회하도록 바꿔 O(M+N)으로 줄였다(커밋 `9e508f52`).

## 남는 교훈

세 원인 모두 "잘못 짠 코드"라기보다는 **의도한 대로 동작하는데 부작용이 있는 코드**였다. `useMemo`는 제대로 걸려 있었고(의존성이 자주 바뀌었을 뿐), `_isChecked` 주입은 리렌더를 보장하는 정석적인 방법이고, `autoHeight`는 레이아웃을 위해 합리적인 선택이다.

특히 `autoHeight`가 가상화를 무력화한다는 건 옵션 이름만 봐서는 알 수 없다. 두 기능이 각각은 멀쩡한데 조합하면 한쪽이 다른 쪽을 끄는 경우가 있고, 이런 건 문서를 읽는 것보다 "왜 500행인데 DOM에 500행이 다 있지"를 실제로 확인해봐야 발견된다.
