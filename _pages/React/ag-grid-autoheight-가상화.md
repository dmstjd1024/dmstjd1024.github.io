---
title:  "AG Grid의 autoHeight는 행 가상화를 끈다"

categories:
  - React
tags:
  - AI
  - Claude Code
  - React
  - 성능최적화

date: 2026-06-02
thumbnail: "/assets/img/thumbnail/sample.png"
---
## 문제

입출력 데이터를 입력하는 그리드에서 행이 수백 개로 늘어나자 **셀 하나를 편집할 때마다 눈에 띄게 버벅였다.** 타이핑 속도를 화면이 못 따라오는 정도였다.

## 원인 1: 편집할 때마다 columnDefs가 통째로 재생성됐다

- `columnDefs`는 `useMemo`로 감싸져 있었음
- 의존성 배열: `rows`, `visibleRows`, `updateMonth`, `onClickRowAction`

- 범인: `onClickRowAction`
- 내부 의존성에 `gridRows` 포함 → **셀 편집마다 identity 변경**
- 연쇄: `columnDefs` 재생성 → AG Grid가 컬럼 정의 변경으로 판단 → 전 컬럼 재적용
- 행이 수백 개면 이게 그대로 비용

<div class="diagram" role="img" aria-label="셀 편집이 identity 변경을 거쳐 전 컬럼 재적용으로 이어지는 연쇄">
{% include diagrams/ag-grid--identity-chain.svg %}
</div>

- 해결: 이 값들을 렌더 사이에 안정적인 ref로 읽기

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

- 셀 핸들러와 렌더러가 최신값을 ref로 읽음
- 결과: `columnDefs` 의존성에서 이 넷을 제거 가능 → 재생성 없음

## 원인 2: 체크박스 하나 누를 때마다 전체 배열을 remap했다

- 기존 방식: cellRenderer 자동 리렌더를 위해 row 데이터에 `_isChecked` 주입

```ts
const rowsWithSelection = useMemo(
  () => visibleRows.map((row: any) => ({
    ...row,
    _isChecked: (checkedItems as number[]).includes(row.id),
  })),
  [visibleRows, checkedItems],
);
```

- 토글 1회 → 전체 배열 재생성 → AG Grid가 전부 다시 diff
- 수백 행이면 토글 한 번의 비용이 큼

- 조치: remap을 걷어내고 `visibleRows`를 그대로 rowData로 사용

- cellRenderer는 `checkedItemsRef`를 읽음
- 선택 변경 시 **체크박스 컬럼만** 강제 새로고침

```ts
const api = agGridRef.current?.api;
api?.refreshHeader();
api?.refreshCells({ columns: ['__checkbox__'], force: true });
```

## 원인 3: autoHeight가 가상화를 끄고 있었다

- 가장 놓치기 쉬운 부분 — 그리드가 `domLayout='autoHeight'` 설정 상태
- `autoHeight`의 의미: 스크롤 없이 전체 높이만큼 늘어나 페이지에 흐르는 옵션
- 전제: **모든 행이 DOM에 존재**해야 전체 높이 확보 가능
- 귀결: AG Grid 네이티브 행 가상화 동작 불가
- 500행이면 500행이 다 DOM에 존재

- 대응: 행 수에 따라 전략 분기

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

- 임계값을 둔 이유: 작은·빈 섹션까지 고정 높이면 빈 공간과 중첩 스크롤 발생
- 12개 이하는 기존 동작 유지
- 12개 초과 시 DOM 행 수 일정 → 500행이든 5000행이든 렌더 비용 동일

- 예외: 접힌 섹션도 고정 높이 적용
- 이유: 부모가 `display: none`이면 `autoHeight`가 높이를 0으로 측정

## 부수 개선: 전체선택 판정

- 기존 계산 방식

```ts
visibleRows.every((r: any) => (checkedItems as number[]).includes(r.id));
```

- `includes`는 배열 선형 탐색
- 복잡도: 보이는 행 M개 × 선택 항목 N개 = O(M×N)
- 조치: `checkedItems`를 `Set`으로 변환해 조회
- 결과: O(M+N)

## 남는 교훈

세 원인 모두 "잘못 짠 코드"라기보다는 **의도한 대로 동작하는데 부작용이 있는 코드**였다.

- `useMemo` — 제대로 걸려 있었음. 의존성이 자주 바뀌었을 뿐
- `_isChecked` 주입 — 리렌더를 보장하는 정석적인 방법
- `autoHeight` — 레이아웃을 위해 합리적인 선택

특히 `autoHeight`가 가상화를 무력화한다는 건 옵션 이름만 봐서는 알 수 없다. 두 기능이 각각은 멀쩡한데 조합하면 한쪽이 다른 쪽을 끄는 경우가 있다.

이런 건 문서를 읽는 것보다 "왜 500행인데 DOM에 500행이 다 있지"를 실제로 확인해봐야 발견된다.
