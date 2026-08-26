---
title:  "RTK Query 워터폴을 평탄화하고, 캐시를 켜자 stale이 드러났다"

categories:
  - React
tags:
  - AI
  - Claude Code
  - React
  - RTK Query

date: 2026-06-12
thumbnail: "/assets/img/thumbnail/react_thumbnail.webp"
---
## 문제

대시보드 탭 하나를 여는 데 요청이 직렬로 연결.

```
summary 조회
  → 첫 제품 자동 선택
    → 해당 제품의 LCA 선택
      → 상세 데이터 호출
```

- 각 단계가 앞 단계의 응답을 기다린 뒤에야 시작 — 전형적인 워터폴
- 추가로 이 API 그룹은 `keepUnusedDataFor: 0`으로 캐싱 비활성 → 탭 재진입마다 체인을 처음부터 재실행

<div class="diagram" role="img" aria-label="요청이 직렬로 이어지는 워터폴 구조">
{% include diagrams/rtk--waterfall.svg %}
</div>

## 원인: lazy 훅 + useEffect 체인

```tsx
const { data: gwpData, isSuccess } = useGetGwpByProductsQuery({});
const [getGwpByProductIoByProductId] = useLazyGetGwpByProductIoByProductIdQuery();

const [selectedItem, setSelectedItem] = useState<any>(null);
const [instIOList, setInstIOList] = useState<any[]>([]);

useEffect(() => {
  if (isSuccess && gwpData?.data?.length > 0) {
    setSelectedItem(gwpData.data[0]);
  }
}, [gwpData?.data, isSuccess]);

useEffect(() => {
  if (selectedItem?.id) {
    (async () => {
      const res = await getGwpByProductIoByProductId({ productId: selectedItem.id });
      if (res.isSuccess) {
        setInstIOList(res.data?.data?.gwpIoTypeList ?? []);
      }
    })();
  }
}, [selectedItem]);
```

문제는 두 개다.

첫째, **effect가 상태를 거쳐 다음 effect를 깨우는 구조** — 렌더 사이클이 한 번씩 더 삽입:

- `gwpData` 도착 → 렌더 → effect 1 → `setSelectedItem` → 렌더 → effect 2 → 요청
- 요청 순서가 뒤인 건 불가피, 그 사이 불필요한 렌더 왕복이 문제

둘째, `selectedItem`과 `instIOList`가 **서버 상태의 복사본**:

- 원본 변경 시 복사본이 stale해질 창 발생

## 어떻게 고쳤나

- 방향: lazy 훅과 effect 체인을 일반 query + `skip` + 렌더 파생값으로 평탄화

```tsx
const { data: gwpData } = useGetGwpByProductsQuery({});
const [selectedId, setSelectedId] = useState<number | null>(null);

const products = useMemo(() => gwpData?.data ?? [], [gwpData?.data]);
const activeId = selectedId ?? products[0]?.id ?? null;
const selectedItem = useMemo(
  () => products.find((p: any) => p.id === activeId) ?? null,
  [products, activeId],
);

const { data: ioRes } = useGetGwpByProductIoByProductIdQuery(
  { productId: activeId as number },
  { skip: activeId == null },
);
const instIOList = useMemo<any[]>(() => ioRes?.data?.gwpIoTypeList ?? [], [ioRes]);
```

- 핵심 — `activeId = selectedId ?? products[0]?.id ?? null`
- "사용자가 고른 게 있으면 그것, 없으면 첫 번째"를 effect 동기화 대신 렌더 시점 계산으로 대체
- 효과 — `selectedItem`을 상태로 보유할 이유 소멸. 두 번째 요청은 `skip`이 풀리는 순간 RTK Query가 자동 발사

이관 중 걸린 함정:

- **lazy 훅과 일반 훅의 응답 언랩 깊이가 다름**
- lazy — `res.data.data`로 한 겹 더 진입
- 일반 훅 — `data.data`

- 그대로 옮길 시 — 조용히 `undefined` → 차트가 빈 채로 렌더

## 캐시를 켰더니 stale이 드러났다

- `keepUnusedDataFor` **0 → 120초** 상향
- 목적 — 탭 재진입 시 즉시 표시

그런데 이걸 켜자마자 새로운 문제가 생겼다. **저장 후 재진입하면 옛날 데이터가 보인다.**

- 원인 — 이 API 그룹은 `GHGEcoView` 태그를 정의만 해놓고, **이 태그를 invalidate하는 mutation이 하나도 없음**
- 배경 — 데이터를 바꾸는 저장 로직이 다른 API 슬라이스에 존재해 태그 미연결

- 캐싱 비활성 시 미발현 — 매번 재요청했기 때문
- 캐시 활성화 순간 "무효화 경로 부재"가 표면화

선택지:

1. 저장 mutation들이 `GHGEcoView` 태그를 invalidate하도록 배선
2. 마운트 시 재요청에 의존

- 1번이 정석. 다만 저장 경로가 여러 슬라이스에 분산돼 배선 누락 위험이 큼
- 캐시 이득의 본질은 "탭 전환 중 재요청 안 하기" → 2번으로도 획득 가능
- 조치 — 관련 훅 4개(`by-scope`, `by-month`, `by-branch`, `scope3`)에 `refetchOnMountOrArgChange: true`
- `refetchOnFocus`는 비활성 — 창 전환할 때마다 쏘는 건 과함

- 성격 — 절충안
- 잔존 부채: 태그 배선 부재 자체는 그대로
- 재검토 시점: 저장 경로가 늘어날 때

## 부수 작업: 차트 memo와 stale 막대차트

- 차트 3개에 `React.memo` 적용
- 전량 적용이 아니라 **부모가 넘기는 props가 안정적인 쪽만** 선별
- 이유 — props가 매 렌더 새로 생성되는 컴포넌트에 memo를 걸면 비교 비용만 증가

그러다 드러난 버그:

- 한 차트의 `options` `useMemo` 의존성에 `barData` 누락
- memo 적용 전 — 부모 리렌더 시 자식도 같이 리렌더되며 우연히 갱신
- memo 적용 후 — **막대차트가 옛날 데이터로 고정**
- 조치 — 의존성 보충

## 남는 교훈

하나는 **effect로 상태를 미러링하는 코드는 대부분 렌더 파생값으로 바꿀 수 있다는 것**이다.

- 사례: `selectedItem` 상태 + effect 동기화 → `activeId` 한 줄로 대체
- 동반 소멸: 요청 체인, desync 위험

다른 하나는 **최적화가 기존 버그를 드러낸다는 것**이다.

- 캐시 활성화 → invalidate 경로 부재 노출
- memo 적용 → 의존성 누락 노출
- 공통 — 원래부터 있던 결함을 비효율이 가려주던 상태
- 오독 주의: "최적화가 버그를 만들었다"로 읽으면 롤백으로 귀결. 실제는 반대
