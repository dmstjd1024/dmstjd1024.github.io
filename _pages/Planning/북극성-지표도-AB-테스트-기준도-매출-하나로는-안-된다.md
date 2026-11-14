---
title:  "북극성 지표도 A/B 테스트 기준도 매출 하나로는 안 된다"
subtitle: "방향은 북극성 지표, 새는 곳은 AARRR, 인과는 A/B 테스트가 묻는다"
description: "방향은 북극성 지표, 새는 곳은 AARRR, 인과는 A/B 테스트가 묻는다"

categories:
  - Planning
tags:
  - 서비스기획
  - 지표
  - A/B테스트

date: 2026-11-03 09:07
thumbnail: "/assets/img/thumbnail/ect_thumbnail.jpg"
---
## 결론부터

검증 단계의 세 개념은 **서로 다른 질문에 답한다.** 셋을 한 줄에 놓고 "어느 게 더 좋은 지표인가"를 물으면 헷갈린다.

- 북극성 지표 — 제품이 맞는 방향으로 가고 있나
- AARRR — 사용자가 어느 단계에서 빠져나가나
- A/B 테스트 — 이 변화가 그 지표를 움직였나

그리고 두 출처가 같은 경고를 한다. Amplitude 는 매출을 북극성 지표로 삼지 말라고 쓰고, Kohavi 등은 매출만으로는 실험의 평가 기준이 부족하다고 쓴다. **결론은 같은데 근거가 다르다.** 앞쪽은 시점의 문제이고, 뒤쪽은 방향의 문제다. 이렇게 가른 것은 내 해석이다.

이 글은 [1편 용어 지도](/Planning/서비스-기획-용어-17개는-쓰이는-단계로-나누면-안-헷갈린다.html)의 마지막 단계인 검증을 깊게 판다. 정의는 원저자 글과 책의 공개 발췌에서 가져왔다. 배달앱 예시는 전부 설명을 위해 지어낸 것이고, 세 개념을 잇는 해석은 내 해석이다.

## 북극성 지표는 고객이 얻는 가치를 세는 지표 하나다

[Amplitude 의 2024년 글](https://amplitude.com/blog/product-north-star-metric)은 North Star Framework 를 이렇게 정의한다.

> a product management model based on a single metric—your North Star Metric—that best captures the value customers derive from your product

핵심은 두 군데다. 지표가 **하나**이고, 그 하나가 **고객이 얻는 가치**를 담아야 한다. 회사가 얻는 것이 아니다.

같은 글은 좋은 북극성 지표가 두 부분으로 이뤄진다고 쓴다.

- 제품 비전을 적은 문장
- 현재 제품 전략을 재는 핵심 지표

그리고 세 가지 조건을 단다.

- 고객 가치와 맞닿아 있다 (aligns to customer value)
- 제품 전략을 대표한다 (represents your product strategy)
- 성공의 선행 지표다 (is a leading indicator of success)

선행 지표(leading indicator)는 결과가 나오기 전에 먼저 움직이는 지표다. 반대인 후행 지표(lagging indicator)는 이미 일어난 일을 기록한다.

### DAU 는 왜 북극성 지표가 못 되나

같은 글은 "Daily Active Users" 나 "Registered Users" 가 좋은 북극성 지표가 아니라고 못 박는다. 이유는 하나다. 고객이 제품의 무엇에 가치를 느끼는지 **아무것도 말해주지 않는다.**

Amplitude 의 [다른 글](https://www.amplitude.com/blog/good-bad-north-star-metric)은 셀프서브 SaaS 를 예로 든다. 무료 체험 계정 전체가 아니라 "첫 주에 3명 넘게 활동한 체험 계정(trial accounts with >3 users active in week 1)"을 세라는 것이다. 숫자 3 은 Amplitude 가 든 예시의 일부이고 측정값이 아니다. 요점은 범위를 좁혀서 **가치를 실제로 얻은 계정만** 센다는 데 있다.

### 누가 만든 말인가

원전을 확인하지 못했다. 위의 Amplitude 글은 이 용어를 Sean Ellis 와 그로스해킹 커뮤니티가 만들었다고 쓰고 GrowthHackers 블로그 글로 링크한다. 그 링크는 내가 열었을 때 응답하지 않았다(HTTP 522). 그래서 이 글에서 Sean Ellis 는 "Amplitude 가 지목한 사람"으로만 둔다.

## 입력 지표는 팀이 손댈 수 있는 3~5개다

북극성 지표 하나만으로는 팀이 내일 무엇을 할지 정할 수 없다. 그래서 Amplitude 는 입력 지표(input)를 같이 둔다.

> Inputs are a set of three to five influential, complementary factors that you believe most directly affect your North Star Metric and that your team can directly influence through your product.

세 가지 조건이 들어 있다.

- 북극성 지표에 가장 직접 영향을 준다고 **믿는** 것 — 증명된 것이 아니라 가설이다
- 서로 보완한다 — 같은 것을 다른 이름으로 두 번 세지 않는다
- 팀이 **제품으로** 직접 움직일 수 있다

입력 지표를 찾는 실마리로 같은 글은 폭(breadth), 깊이(depth), 빈도(frequency), 효율(efficiency) 넷을 든다. 각 항목의 정의는 그 글에 없다. 아래는 배달앱으로 지어낸 예이고, 네 축에 무엇을 대입할지는 내 해석이다.

```text
북극성 지표   주간 정상 배달 완료 주문 수
              (고객이 "제때 밥을 받았다"는 가치를 얻은 횟수)

입력 지표
  폭    이번 주에 한 번이라도 주문한 사용자 수
  깊이  두 곳 이상의 가게에서 주문해 본 사용자 수
  빈도  사용자당 주간 주문 횟수
  효율  앱을 연 뒤 결제까지 이탈 없이 간 비율
```

북극성 지표가 "주문 수"가 아니라 "정상 배달 완료 주문 수"인 이유가 있다. 주문만 받고 취소되거나 늦게 도착한 건은 고객이 가치를 얻지 못한 주문이다. DAU 를 피한 것과 같은 논리다.

**입력 지표는 목표가 아니라 가설이다.** "빈도가 오르면 북극성 지표가 오른다"는 믿음을 적어둔 것이다. 그 믿음이 맞는지는 뒤의 A/B 테스트가 확인한다.

## KPI 는 북극성 지표 아래에 여러 개 있다

1편에서 "KPI 는 이 셋과 같은 층의 말이 아니다"라고 썼다. 층위를 Amplitude 는 이렇게 설명한다.

> Think of it as the single, value-based outcome that sits above the many operational KPIs your team already tracks.

같은 문단은 MRR(월간 반복 매출)이나 ARPU(사용자당 평균 매출) 같은 값이 사업이 **어떻게 됐는지**를 알려준다고 쓴다. 북극성 지표는 그 숫자들이 **어디로 갈지**를 가리킨다.

정리하면 이렇다. 이 구분은 내 해석이다.

| 구분 | 북극성 지표 | KPI |
|---|---|---|
| 개수 | 하나 | 여럿 |
| 재는 것 | 고객이 얻는 가치 | 부서·목표별 운영 성과 |
| 시점 | 선행 | 선행도 후행도 있다 |
| 매출이 들어가나 | 넣지 않는다 | 들어간다 |

KPI 자체의 표준 정의는 1차 출처로 확인하지 못했다. 위 표의 KPI 열은 쓰임새 기준이다.

## AARRR 은 사용자가 어디서 새는지를 다섯 칸으로 나눈다

Dave McClure 의 발표 자료 [「Startup Metrics for Pirates: AARRR!」](https://www.slideshare.net/slideshow/startup-metrics-for-pirates-presentation/629833)를 직접 열었다. SlideShare 페이지 제목에는 "Startonomics SF 2008" 이 붙어 있지만 발표 자료 본문에는 연도가 없다. 처음 발표한 해는 자료마다 엇갈려서 적지 않는다. 제목의 "AARRR!" 은 다섯 단계의 머리글자다.

자료 안에서 McClure 는 이를 "5-Step Startup Metrics Model" 이라고 부른다. 단계별 설명은 아래와 같다. 오른쪽 열은 배달앱으로 지어낸 대입이다.

| 단계 | McClure 의 한 줄 | 배달앱에 대입하면 |
|---|---|---|
| Acquisition(획득) | users come to site from various channels | 광고·검색·지인 링크로 앱을 설치한다 |
| Activation(활성화) | users enjoy 1st visit: "happy" experience | 첫 주문이 제때 도착한다 |
| Retention(유지) | users come back, visit site multiple times | 다음 주에 다시 주문한다 |
| Referral(추천) | users like product enough to refer others | 친구에게 초대 링크를 보낸다 |
| Revenue(수익) | users conduct some monetization behavior | 결제한다, 유료 멤버십에 가입한다 |

이 예시에서는 Revenue 인 결제가 Activation 인 첫 주문의 정시 도착보다 먼저 일어난다. 다섯 칸이 항상 머리글자 순서대로 일어나지는 않는다.

### 머리글자 순서가 일의 순서는 아니다

같은 자료는 다섯 단계를 셋으로 묶는다.

- Get Users — Acquisition, Referral
- Drive Usage — Activation, Retention
- Make Money — Revenue

그리고 "One Step at a Time" 이라며 좋은 제품 만들기(Activation & Retention)를 먼저 둔다. 머리글자는 A 로 시작하지만 McClure 가 먼저 하라고 한 것은 획득이 아니다.

**AARRR 은 깔때기의 칸을 나눌 뿐, 어디부터 고치라고 정해주지 않는다.** 그 판단은 칸마다 얼마나 새는지를 보고 사람이 한다.

### 지표를 많이 두라는 말이 아니다

자료에는 "Focus on Critical Few Actionable Metrics" 라는 문장이 있고, 괄호로 기준을 단다. 그 지표로 결정을 내리지 않는다면 실행 가능한 지표가 아니라는 것이다(if you don't use the metric to make a decision, it's not actionable). 전환 이벤트는 "~3-5" 개를 목표로 하라고도 쓴다.

예시 전환율을 보여주는 장에는 McClure 자신이 "*not* actuals" 라고 달아 두었다. 실제 값이 아니라는 뜻이다. 그래서 이 글도 그 숫자를 옮기지 않는다.

## A/B 테스트는 사용자를 무작위로, 계속 같은 쪽에 나눈다

Kohavi, Tang, Xu 의 『Trustworthy Online Controlled Experiments』(Cambridge, 2020) [1장 공개 발췌](https://web.archive.org/web/20220503101107/https://assets.cambridge.org/97811087/24265/excerpt/9781108724265_excerpt.pdf)를 읽었다. 책은 통제 실험(controlled experiment)과 A/B 테스트를 같은 뜻으로 쓴다. 가장 흔한 형태는 이렇다.

> users are randomly split between variants in a persistent manner (a user receives the same variant in multiple visits)

두 단어가 핵심이다. **무작위로** 나누고, **지속적으로** 나눈다. 같은 사람은 몇 번을 다시 와도 같은 화면을 본다.

설계할 때 정해야 하는 용어를 발췌에서 골랐다.

- Control / Treatment — 가장 단순한 실험의 두 변형이다. Control(A)은 기존 버전, Treatment(B)는 바꾼 버전이다
- Variant(변형) — 시험하는 사용자 경험 하나다. 책은 Control 도 비교의 기준이 되는 "특별한 변형"으로 본다. 실험에 버그가 나면 실험을 멈추고 모든 사용자를 Control 에 배정한다
- Parameter(파라미터) — OEC 에 영향을 준다고 생각하는, 통제 가능한 실험 변수다. 단순한 A/B 테스트는 흔히 파라미터 하나에 값 두 개다
- Randomization Unit(무작위 배정 단위) — 해싱 같은 의사 무작위 과정으로 변형에 배정하는 단위다. 사용자일 수도 페이지일 수도 있다. 책은 사용자를 단위로 쓰기를 강하게 권한다

배정 단위에는 조건이 둘 붙는다. **지속적이어야 하고, 독립적이어야 한다.** 독립적이라는 것은 한 사용자의 배정이 다른 사용자의 배정에 대해 아무것도 알려주지 않아야 한다는 뜻이다.

### OEC 는 실험이 이겼는지 판정하는 기준이다

OEC(Overall Evaluation Criterion, 종합 평가 기준)를 책은 "실험의 목적을 재는 정량 척도(A quantitative measure of the experiment's objective)"로 정의한다. 예로 든 것은 사용자당 활동 일수(active days per user)다.

조건이 하나 더 있다. OEC 는 **실험 기간 안에 잴 수 있어야 하고, 동시에 장기 전략 목표를 인과적으로 끌어올린다고 믿을 수 있어야 한다.** 여러 목표를 함께 볼 수도 있지만, 가중 조합으로라도 지표 하나를 고르기를 강하게 권한다.

여기서 북극성 지표와 겹치는 지점이 보인다. 둘 다 "하나"를 고르라고 하고, 둘 다 지금 잴 수 있으면서 장기 성과를 미리 가리키는 지표를 원한다. 이 연결은 내 해석이다. 내가 읽은 범위에서 Amplitude 글과 Kohavi 책은 서로를 언급하지 않는다.

### 왜 실험이어야 하나

책은 구독 서비스를 예로 든다. 새 기능을 쓴 사용자의 해지율이 쓰지 않은 사용자의 절반이라고 하자. 그 기능이 해지를 줄였다고 말하고 싶어진다. 책의 답은 이 데이터로는 **어떤 결론도 낼 수 없다**는 것이다. 줄였을 수도, 늘렸을 수도 있다.

실제 사례도 든다. Microsoft Office 365 에서 오류 메시지를 보고 충돌을 겪은 사용자가 오히려 해지율이 낮았다. 오류를 더 띄우라는 뜻이 아니다. 셋 다 **사용량**이라는 한 요인에서 나왔다. 많이 쓰는 사람이 오류도 더 보고, 충돌도 더 겪고, 덜 해지한다.

책은 무작위 통제 실험을 인과를 세우는 표준(gold standard)이라고 부른다.

## 쿠폰 기능을 A/B 테스트로 설계하면 이렇다

1편의 쿠폰 소재를 이어서, 앞의 용어를 하나씩 채운 예다. 전부 지어낸 예이고, 기간과 금액 같은 값은 칸을 보이려고 넣은 예시이며 측정값이 아니다.

```text
가설        첫 주문 뒤 7일 안에 쓰는 재주문 쿠폰을 주면
            입력 지표 '빈도'가 오르고, 북극성 지표도 오른다

배정 단위   사용자 (주문·세션 단위로 나누지 않는다)
Control     쿠폰 없음
Treatment   첫 주문 뒤 재주문 쿠폰 지급
Parameter   쿠폰 지급 여부 (값 둘)

OEC         실험 기간 중 사용자당 정상 배달 완료 주문 일수
같이 볼 것  주문당 순매출, 주문 취소율
```

각 칸을 그렇게 정한 이유는 이렇다.

- 배정 단위를 사용자로 둔 이유 — 주문 단위로 나누면 같은 사람이 어떤 주문에서는 쿠폰을 받고 어떤 주문에서는 못 받는다. 책이 말한 "같은 사용자는 같은 경험"이 깨진다
- OEC 를 주문 수가 아니라 정상 배달 완료 일수로 둔 이유 — 앞의 북극성 지표와 같은 논리다. 활동 일수를 OEC 예로 든 책의 방식을 배달에 옮겼다
- 주문당 순매출을 같이 보는 이유 — 쿠폰은 할인이다. 주문은 늘고 주문당 매출은 줄 수 있다. 그 맞바꿈을 보지 않으면 할인으로 주문을 산 것을 기능 효과로 착각한다

하나 더 걸리는 것이 있다. 쿠폰을 친구에게 넘길 수 있게 만들면 Treatment 사용자의 쿠폰이 Control 사용자에게 간다. 책은 실험 단위끼리 간섭이 없거나 적어야 한다는 것을 유용한 실험의 첫 번째 조건으로 꼽는다. **양도 가능한 쿠폰은 실험 설계를 깨는 기능이다.** 실험 기간에는 양도를 막거나, 막을 수 없다면 이 설계를 그대로 쓰면 안 된다.

## 북극성 지표를 매출로 잡으면 두 출처가 다른 이유로 말린다

가장 흔한 오해는 "결국 회사가 원하는 건 매출이니 매출을 북극성 지표로 두자"는 것이다. 두 출처가 모두 반대하는데, 이유가 다르다.

Amplitude 의 이유는 **시점**이다. [좋은/나쁜 북극성 지표 글](https://www.amplitude.com/blog/good-bad-north-star-metric)은 매출이 후행 지표라서 이미 끝난 일이라고 쓴다.

> So "don't" make revenue your North Star Metric, but "do" relate your North Star Metric to revenue.

매출을 버리라는 말이 아니다. 북극성 지표가 매출을 앞서 가리키도록 **연결**하라는 말이다.

Kohavi 등의 이유는 **방향**이다. 책을 여는 Bing 사례가 그렇다. 광고 제목을 길게 바꾼 실험이 Bing 역사상 가장 큰 매출을 낸 아이디어가 됐다. 그런데 바로 그 사례에서 책은 이렇게 쓴다.

> revenue alone is insufficient as an OEC. It could lead to plastering the web site with ads, which is known to hurt the user experience.

매출만 보면 사이트를 광고로 덮는 변형이 이긴다. 그래서 Bing 은 매출과 사용자 경험 지표(사용자당 세션 수 등)를 함께 저울질하는 OEC 를 쓴다. 이 사례에서 중요한 것은 매출이 크게 늘었는데도 **사용자 경험 지표가 유의하게 나빠지지 않았다**는 점이라고 책은 강조한다.

배달앱으로 옮기면 이렇다. 지어낸 예다.

- 배달비를 올려도 매출은 오른다
- 가게 목록 상단을 광고로 채워도 매출은 오른다
- 둘 다 고객이 "제때 원하는 밥을 받았다"는 가치는 늘리지 않는다

매출이 북극성 지표라면 위 두 변화가 모두 성공으로 기록된다. 정상 배달 완료 주문 수가 북극성 지표라면 적어도 그 가치가 줄었는지는 보인다.

## 출시 전후 비교로는 쿠폰 효과를 주장할 수 없다

두 번째 흔한 오해다. 쿠폰을 출시하고, 출시 전 주와 후 주의 주문 수를 비교해서 "쿠폰이 주문을 늘렸다"고 쓰는 것이다.

책의 해지율 예시와 같은 구조다. 아래 두 문장은 내가 배달앱에 대입한 것이다.

- 출시 주에 연휴가 끼었거나 날씨가 나빴다면 쿠폰이 없어도 주문은 늘었다
- "쿠폰을 쓴 사용자가 재주문을 더 한다"는 관찰도 마찬가지다. 원래 자주 주문하는 사람이 쿠폰도 더 챙겨 쓸 수 있다. Office 365 의 사용량처럼 숨은 요인 하나가 둘을 같이 움직일 수 있다

전후 비교에서는 **바꾼 것과 그 주에 바뀐 다른 모든 것이 섞인다.** 무작위로 나눈 두 집단을 같은 기간에 비교하면 그 주의 날씨와 연휴는 양쪽에 똑같이 걸린다. 남는 차이가 쿠폰의 몫이 된다.

책도 통제 실험의 장점으로 이 점을 든다. 시간에 따른 변화를 보는 것 같은 다른 기법으로는 잡기 어려운 작은 변화를 잡아낸다는 것이다(changes that are harder to detect with other techniques, such as changes over time).

## 그럼 A/B 테스트를 못 돌리면 지표는 의미가 없나

그렇지 않다. 세 가지를 짚는다.

첫째, 책 스스로 모든 결정을 통제 실험으로 내릴 수는 없다고 쓴다. 인수합병은 합병한 세계와 안 한 세계를 동시에 만들 수 없으니 실험이 안 된다. 통제 실험이 불가능할 때는 관찰 연구처럼 덜 신뢰할 만한 방법이라도 쓰라고 권한다.

둘째, 실험에는 단위가 충분해야 한다. 책은 실험 단위를 수천 개 이상 두기를 권하고, 많을수록 작은 효과를 잡을 수 있다고 쓴다. 작은 스타트업도 사용자가 금방 모이니 처음에는 큰 효과를 찾는 실험부터 시작할 수 있다고 덧붙인다.

셋째, AARRR 과 A/B 테스트는 처음부터 경쟁 관계가 아니었다. McClure 의 같은 발표 자료에 "Measure, A/B Test, Iterate FAST (daily/weekly)" 라는 문장이 있다. 깔때기로 새는 칸을 찾고, 그 칸을 고친 변화가 효과가 있었는지는 실험으로 확인하는 흐름이 한 자료 안에 이미 들어 있다.

**실험을 못 돌리는 상황에서도 북극성 지표와 AARRR 은 어디를 볼지 알려준다.** 다만 그때는 "이 기능 덕분에 올랐다"가 아니라 "이 기능을 낸 뒤에 올랐다"까지만 말할 수 있다.

## 원전을 확인한 것과 못 한 것

- 북극성 지표 설명은 전부 Amplitude 블로그 두 편에서 왔다. Amplitude 는 제품 분석 도구를 파는 회사다. 두 글 모두 2024년에 처음 게시됐고, 이후 갱신 날짜가 붙어 있다
- 북극성 지표라는 용어를 만든 사람은 확인하지 못했다. Amplitude 는 Sean Ellis 를 지목하지만 링크된 원문은 열리지 않았다
- 폭·깊이·빈도·효율 네 축은 Amplitude 글에 이름만 있고 정의가 없다. 배달앱 대입은 내 해석이다
- McClure 자료는 행사 주최 측 계정으로 SlideShare 에 올라온 판을 봤다. 연도는 페이지 제목에만 있다. 검색하면 같은 제목의 다른 해 판이 여럿 보이지만 열어보지 않았고, 그중 무엇이 처음인지 확인하지 못했다
- Kohavi 등의 책은 1장 공개 발췌만 읽었다. OEC 를 깊게 다루는 7장, 간섭을 다루는 22장은 읽지 못했다
- KPI 의 표준 정의는 1차 출처로 확인하지 못했다
- 이 글의 배달앱 예시에는 측정값이 하나도 없다. 실제 서비스에서 이 설계가 어떤 결과를 낼지는 알 수 없다

## 정리

세 개념은 서로를 대체하지 않는다. 각자 답하는 질문과 답하지 못하는 질문이 있다.

| 개념 | 답하는 질문 | 답하지 못하는 질문 |
|---|---|---|
| 북극성 지표 | 고객이 얻는 가치가 늘고 있나 | 무엇 때문에 늘었나 |
| 입력 지표 | 팀이 지금 무엇을 움직여야 하나 | 그걸 움직이면 정말 북극성 지표가 오르나 |
| AARRR | 사용자가 어느 단계에서 빠지나 | 어느 칸부터 고쳐야 하나 |
| A/B 테스트 | 이 변화가 이 지표를 움직였나 | 애초에 어떤 지표를 봐야 하나 |

매출은 이 표 어디에도 주인공으로 들어가지 않는다. 북극성 지표에서는 선행 지표가 가리켜야 할 결과로, OEC 에서는 사용자 경험 지표와 함께 저울질할 항목 하나로 들어간다.
