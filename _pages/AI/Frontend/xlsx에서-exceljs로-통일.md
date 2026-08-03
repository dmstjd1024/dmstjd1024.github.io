---
title:  "엑셀 라이브러리가 두 개였다 — xlsx에서 exceljs로 통일하기"

categories:
  - AI
tags:
  - AI
  - Claude Code
  - 리팩터링
  - TypeScript

date: 2026-07-16
thumbnail: "/assets/img/thumbnail/sample.png"
---

## 문제

한 프로젝트 안에서 엑셀을 내보내는 경로가 두 개였고, 각각 다른 라이브러리를 쓰고 있었다.

| 경로 | 라이브러리 | 헤더 스타일 |
|---|---|---|
| AG Grid export | `xlsx` | 불가 |
| 리포트 export | `exceljs` | 적용됨 |

`xlsx`(SheetJS)의 커뮤니티 버전은 **셀 스타일을 지원하지 않는다.** 그래서 AG Grid에서 내보낸 파일만 헤더가 밋밋했다. 같은 제품에서 받은 두 엑셀 파일의 생김새가 달랐다.

## 경계를 정하는 게 먼저였다

`excelExport.ts`를 열어보니 코드가 두 종류로 나뉘어 있었다.

**순수 로직** — `resolveCellValue`(셀 값 해석), `buildSheetAoa`(AG Grid의 컬럼 정의와 노드에서 2차원 배열 만들기). 여기엔 "headerName이 있는 컬럼만 포함", "valueFormatter 반영", "isHeader 밴드행 제외" 같은 도메인 규칙이 들어 있다.

**렌더부** — 2차원 배열을 실제 워크북으로 만들고 파일로 떨구는 부분.

라이브러리에 묶인 건 렌더부뿐이었다. 그래서 **순수 로직은 그대로 두고 렌더부만 교체**하는 것으로 범위를 확정했다. 이 경계 덕에 도메인 규칙을 재검증할 필요가 없었고, 기존 테스트의 절반 이상이 그대로 유효했다.

## 교체

```ts
export async function exportGridsAsExcel(
  sheets: ExcelSheetSpec[],
  options: { fileName?: string } = {},
): Promise<void> {
  const { fileName = 'export.xlsx' } = options;
  const ExcelJS = (await import('exceljs')).default;
  const wb = new ExcelJS.Workbook();

  for (const { api, columnDefs, sheetName } of sheets) {
    const { headers, rows } = buildSheetAoa(api, columnDefs);
    await writeSheet(wb, sheetName, headers, rows);
  }
  // ...
}
```

`buildSheetAoa` 호출은 그대로다. 그 아래에서 워크북을 만드는 부분만 바뀌었다. 헤더 스타일은 리포트 export 쪽이 이미 쓰고 있던 `excelStyle.ts` 헬퍼(`addSheet`, `drawHeader`, `drawDataRow`, `freezeAt`)를 그대로 재사용했다. 두 경로가 같은 헬퍼를 쓰게 되니 생김새가 자동으로 통일된다.

컬럼 폭은 헤더 텍스트 길이 기반으로 계산하는 작은 함수를 뒀다.

```ts
function computeColumnWidths(headers: string[]): number[] {
  return headers.map((h) => Math.min(40, Math.max(10, h.length * 2 + 4)));
}
```

## 예상 못 한 파급: 함수가 async가 됐다

`exceljs`의 `writeBuffer()`는 Promise를 반환한다. `xlsx`의 `XLSX.write()`는 동기였다.

그래서 export 함수의 시그니처가 `void`에서 `Promise<void>`로 바뀌었다. 이게 호출부로 번진다. 이 함수들은 대부분 버튼 클릭 핸들러에서 fire-and-forget으로 불리고 있었다.

```tsx
onClick={() => void exportGridsAsExcel(...)}
```

TypeScript의 `no-floating-promises` 규칙에 걸리므로 호출부 **8곳에 `void` 표기**를 붙였다. `await`하지 않는 게 의도라는 걸 명시하는 것이다.

여기서 판단이 하나 있었다. 호출부를 전부 `async` 핸들러로 바꿔 `await`하고 로딩 상태를 노출하는 방법도 있었다. 하지만 그건 이 작업의 범위를 넘어선다 — 8개 화면의 UX를 동시에 바꾸는 일이 된다. 라이브러리 교체와 로딩 UX 개선은 별개의 변경이므로 섞지 않았다.

## 테스트

`excelExport.test.ts`를 140줄 갱신했다. 순수 로직 테스트(`resolveCellValue`, `buildSheetAoa`)는 대부분 손대지 않았고, 워크북 생성 결과를 검증하는 부분이 바뀌었다. 테스트도 async가 되면서 assertion 앞에 `await`가 붙는 기계적 변경이 상당수였다.

## 남는 교훈

라이브러리 교체 작업에서 가장 중요한 건 **어디까지가 라이브러리에 묶인 코드인지 선을 긋는 것**이었다. 선을 긋고 나니 실제로 다시 쓴 코드는 `excelExport.ts` 한 파일의 절반 정도였고, 나머지 9개 파일의 변경은 전부 `void` 한 글자였다.

만약 `buildSheetAoa` 같은 도메인 규칙이 라이브러리 호출과 뒤엉켜 있었다면 — 예를 들어 `XLSX.utils` 객체를 셀 단위로 조작하면서 필터링 규칙까지 그 안에서 처리했다면 — 교체 비용은 몇 배가 됐을 것이다. 이건 결과적으로 원래 코드가 잘 짜여 있었다는 얘기이기도 하다. 라이브러리를 바꿀 계획이 없더라도 순수 로직과 I/O를 분리해두면 이럴 때 값을 한다.

동기 함수가 async가 되면서 생기는 파급도 기억할 만하다. 라이브러리 API의 동기/비동기 성질은 함수 시그니처를 타고 호출부까지 번진다. 교체 전에 "이 라이브러리의 대응 API가 async인가"를 확인하면 작업량을 미리 가늠할 수 있다.
