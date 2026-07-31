---
title:  "RTK Query 워터폴을 평탄화하고, 캐시를 켜자 stale이 드러났다"

categories:
  - AI
tags:
  - AI
  - Claude Code
  - React
  - RTK Query

date: 2026-06-12
thumbnail: "/assets/img/thumbnail/sample.png"
---

# 문제

대시보드 탭 하나를 여는 데 요청이 직렬로 줄줄이 이어졌다.

```
summary 조회
  → 첫 제품 자동 선택
    → 해당 제품의 LCA 선택
      → 상세 데이터 호출
```

각 단계가 앞 단계의 응답을 기다린 뒤에야 시작된다. 전형적인 워터폴이다. 게다가 이 API 그룹은 `keepUnusedDataFor: 0`으로 캐싱이 꺼져 있어서, 탭을 나갔다 들어올 때마다 이 체인을 처음부터 다시 탔다.

# 원인: lazy 훅 + useEffect 체인

구조가 이랬다.

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

첫째, **effect가 상태를 거쳐 다음 effect를 깨우는 구조**라 렌더 사이클이 한 번씩 더 끼어든다. `gwpData`가 도착 → 렌더 → effect 1 → `setSelectedItem` → 렌더 → effect 2 → 요청. 요청 자체가 순서상 뒤일 수밖에 없는 건 맞지만, 그 사이에 불필요한 렌더 왕복이 낀다.

둘째, `selectedItem`과 `instIOList`가 **서버 상태의 복사본**이라는 점이다. 원본이 바뀌면 복사본이 stale해질 창이 생긴다.

# 어떻게 고쳤나

lazy 훅과 effect 체인을 일반 query + `skip` + 렌더 파생값으로 평탄화했다.

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

핵심은 `activeId = selectedId ?? products[0]?.id ?? null`이다. "사용자가 고른 게 있으면 그것, 없으면 첫 번째"를 effect로 동기화하는 대신 렌더 시점에 계산한다. 그러면 `selectedItem`을 상태로 들고 있을 이유가 없어지고, 두 번째 요청은 `skip`이 풀리는 순간 RTK Query가 알아서 쏜다.

이관하면서 걸린 함정이 하나 있었다. **lazy 훅과 일반 훅의 응답 언랩 깊이가 다르다.** lazy는 `res.data.data`로 한 겹 더 들어가야 하는데, 일반 훅은 `data.data`다. 이걸 그대로 옮기면 조용히 `undefined`가 되고 차트가 빈 채로 뜬다.

# 캐시를 켰더니 stale이 드러났다

`keepUnusedDataFor`를 0에서 120초로 올렸다. 탭 재진입 시 즉시 표시되게 하려는 것이다.

그런데 이걸 켜자마자 새로운 문제가 생겼다. **저장 후 재진입하면 옛날 데이터가 보인다.** 조사해보니 이 API 그룹은 `GHGEcoView` 태그를 정의만 해놓고, **실제로 이 태그를 invalidate하는 mutation이 하나도 없었다.** 데이터를 바꾸는 저장 로직이 다른 API 슬라이스에 있어서 태그가 연결되지 않은 것이다.

캐싱이 꺼져 있을 때는 이 문제가 드러나지 않았다. 매번 다시 받아왔으니까. 캐시를 켜는 순간 "무효화 경로가 없다"는 사실이 표면으로 올라왔다.

선택지는 두 가지였다.

1. 저장 mutation들이 `GHGEcoView` 태그를 invalidate하도록 배선
2. 마운트 시 재요청에 의존

1번이 정석이지만 저장 경로가 여러 슬라이스에 흩어져 있어 배선 누락 위험이 컸다. 캐시 이득의 본질은 "탭 전환 중 재요청 안 하기"였고 그건 2번으로도 얻을 수 있어서, 관련 훅 4개(`by-scope`, `by-month`, `by-branch`, `scope3`)에 `refetchOnMountOrArgChange: true`를 붙였다. `refetchOnFocus`는 껐다 — 창 전환할 때마다 쏘는 건 과했다.

정확히는 이게 절충안이다. 태그 배선이 없다는 사실 자체가 남아 있으므로, 나중에 저장 경로가 늘어나면 다시 봐야 한다.

# 부수 작업: 차트 memo와 stale 막대차트

차트 3개에 `React.memo`를 적용했다. 전부 다 감싸지는 않고 **부모가 넘기는 props가 안정적인 쪽만** 골랐다. props가 매 렌더 새로 만들어지는 컴포넌트에 memo를 걸면 비교 비용만 늘고 이득이 없다.

그러다 버그가 하나 드러났다. 한 차트의 `options` `useMemo` 의존성에 `barData`가 빠져 있었다. memo를 걸기 전에는 부모가 리렌더될 때 자식도 같이 리렌더되면서 어찌어찌 갱신됐는데, memo를 걸자 **막대차트가 옛날 데이터로 굳어버렸다.** 의존성을 채워서 고쳤다.

# 남는 교훈

두 가지가 남는다.

하나는 **effect로 상태를 미러링하는 코드는 대부분 렌더 파생값으로 바꿀 수 있다는 것**이다. `selectedItem`을 상태로 들고 effect로 동기화하던 걸 `activeId` 한 줄로 대체하면서, 요청 체인과 desync 위험이 같이 사라졌다.

다른 하나는 **최적화가 기존 버그를 드러낸다는 것**이다. 캐시를 켜니 invalidate 경로가 없다는 게 드러났고, memo를 거니 의존성 누락이 드러났다. 둘 다 원래부터 있던 결함인데 비효율이 가려주고 있었다. 이런 걸 "최적화가 버그를 만들었다"고 읽으면 롤백하게 되는데, 실제로는 반대다.
