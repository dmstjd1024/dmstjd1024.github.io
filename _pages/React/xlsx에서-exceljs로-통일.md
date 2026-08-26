---
title:  "엑셀 라이브러리가 두 개였다 — xlsx에서 exceljs로 통일하기"

categories:
  - React
tags:
  - AI
  - Claude Code
  - 리팩터링
  - TypeScript

date: 2026-07-16
thumbnail: "/assets/img/thumbnail/sample.png"
---
## 문제

한 프로젝트 안에서 엑셀을 내보내는 경로가 두 개였고, 각각 다른 라이브러리를 사용 중.

| 경로 | 라이브러리 | 헤더 스타일 |
|---|---|---|
| AG Grid export | `xlsx` | 불가 |
| 리포트 export | `exceljs` | 적용됨 |

- `xlsx`(SheetJS) 커뮤니티 버전의 제약 — **셀 스타일 미지원**
- 결과 — AG Grid에서 내보낸 파일만 헤더가 밋밋

사용자 입장에서는 같은 제품에서 받은 두 엑셀 파일의 생김새가 다른 셈이다.

## 경계를 정하는 게 먼저였다

- `excelExport.ts` 확인 결과: 코드가 두 종류로 분리 가능

**순수 로직**

- `resolveCellValue` — 셀 값 해석
- `buildSheetAoa` — AG Grid의 컬럼 정의와 노드에서 2차원 배열 생성
- 담긴 도메인 규칙 — "headerName이 있는 컬럼만 포함", "valueFormatter 반영", "isHeader 밴드행 제외"

**렌더부**

- 하는 일 — 2차원 배열을 실제 워크북으로 만들고 파일로 출력

- 라이브러리에 묶인 범위: 렌더부뿐

그래서 **순수 로직은 그대로 두고 렌더부만 교체**하기로 범위를 확정했다.

- 이 경계의 효과: 도메인 규칙 재검증 불필요, 기존 테스트 절반 이상 그대로 유효

<div class="diagram" role="img" aria-label="순수 로직과 렌더부의 경계를 그어 교체 범위를 정한 구조">
{% include diagrams/xlsx--boundary.svg %}
</div>

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

- `buildSheetAoa` 호출 — 그대로 유지
- 변경 범위 — 그 아래 워크북 생성 부분
- 헤더 스타일 — 리포트 export 쪽이 이미 쓰던 `excelStyle.ts` 헬퍼(`addSheet`, `drawHeader`, `drawDataRow`, `freezeAt`) 재사용

- 두 경로가 같은 헬퍼 사용 → 생김새 자동 통일
- 컬럼 폭 — 헤더 텍스트 길이 기반 계산 함수 추가

```ts
function computeColumnWidths(headers: string[]): number[] {
  return headers.map((h) => Math.min(40, Math.max(10, h.length * 2 + 4)));
}
```

## 예상 못 한 파급: 함수가 async가 됐다

- `exceljs`의 `writeBuffer()` — Promise 반환
- `xlsx`의 `XLSX.write()` — 동기
- 결과 — export 함수 시그니처가 `void`에서 `Promise<void>`로 변경
- 파급 지점 — 호출부. 이 함수들은 대부분 버튼 클릭 핸들러에서 fire-and-forget으로 호출 중

```tsx
onClick={() => void exportGridsAsExcel(...)}
```

- 걸리는 규칙 — TypeScript `no-floating-promises`
- 조치 — 호출부 **8곳에 `void` 표기** 추가
- 의미 — `await`하지 않는 게 의도임을 명시

- 여기서 판단 하나 발생
- 대안: 호출부를 전부 `async` 핸들러로 전환해 `await` + 로딩 상태 노출
- 기각 사유: 작업 범위 초과 — 8개 화면의 UX를 동시 변경하는 일
- 판단: 라이브러리 교체와 로딩 UX 개선은 별개의 변경이므로 미혼합

## 테스트

- `excelExport.test.ts` — 140줄 갱신
- 순수 로직 테스트(`resolveCellValue`, `buildSheetAoa`) — 대부분 무변경
- 바뀐 부분 — 워크북 생성 결과 검증
- 변경 성격 — 테스트도 async가 되면서 assertion 앞에 `await`가 붙는 기계적 변경이 상당수

## 남는 교훈

라이브러리 교체 작업에서 가장 중요한 건 **어디까지가 라이브러리에 묶인 코드인지 선을 긋는 것**이었다.

- 선을 그은 뒤 실제 재작성 범위: `excelExport.ts` 한 파일의 절반 정도
- 나머지 9개 파일의 변경: 전부 `void` 한 글자

- 가정: `buildSheetAoa` 같은 도메인 규칙이 라이브러리 호출과 뒤엉킨 경우 — 예컨대 `XLSX.utils` 객체를 셀 단위로 조작하며 필터링 규칙까지 그 안에서 처리 — 교체 비용 몇 배
이건 결과적으로 원래 코드가 잘 짜여 있었다는 얘기이기도 하다. 라이브러리를 바꿀 계획이 없더라도 순수 로직과 I/O를 분리해두면 이럴 때 값을 한다.

- 기억할 점: 동기 함수가 async가 되며 생기는 파급
- 라이브러리 API의 동기·비동기 성질은 함수 시그니처를 타고 호출부까지 전파
- 사전 점검 항목: "이 라이브러리의 대응 API가 async인가" → 작업량 사전 가늠 가능
