---
title:  "RSI 과매수 필터란? — 임계값 50이 매수 신호를 막은 사례"

categories:
  - Develop
tags:
  - RSI
  - 자동매매
  - SignalFilter
  - Python
  - 퀀트

date: 2026-10-05
---
## 한 줄로

자동매매 봇에서 매수를 가장 많이 막은 사유는 `SIGNAL_FILTER`였다. 원인은 RSI 과매수 기준인 `rsi_threshold`가 `50.0`으로 잡혀 있기 때문으로 보인다. RSI 50은 중립 수준이어서, 전략이 BUY를 내는 RSI 50~70 모멘텀 구간이 통째로 막힌다. 다만 고쳐야 할 파일이 수정 허용 목록 밖이라 코드는 바꾸지 않았고 `[제안]`만 남겼다.

## RSI 과매수 필터란

RSI(상대강도지수)는 최근 가격이 얼마나 강하게 오르고 내렸는지를 0~100 사이 값으로 나타내는 지표다. 값이 높을수록 최근 상승세가 강했다는 뜻이고, 50 근처는 중립으로 본다.

과매수 필터는 RSI가 정해 둔 기준값(임계값)을 넘으면 '이미 많이 올랐다'고 보고 매수 신호를 거르는 장치다. 이 봇에서는 `SignalFilter`가 이 일을 하고, 기준값은 `rsi_threshold` 파라미터로 받는다. `SignalFilter`에 원래 들어 있던 기본값은 `70.0`이다.

같은 필터라도 기준값을 어디에 두느냐에 따라 하는 일이 크게 달라진다. 70이면 과열 구간만 거른다. 50이면 중립을 넘은 구간을 전부 '과매수'로 본다.

## 상황: 수익은 나는데 매수가 막힌다

분석할 때 입력으로 받은 운영 지표는 아래와 같다.

| 항목 | 값 |
|---|---|
| 최근 7일 매도 | 7건 |
| 최근 7일 순손익 / 승률 | +33,210원 / 71% |
| 매수 차단 | 17건 (가장 많은 사유 `SIGNAL_FILTER`) |
| 누적수익 / MDD / Sharpe | +1.26% / -0.00% / 1.55 |

전략 파라미터는 `ff_weight=0.1`, `ae_weight=0.9`, `geo_weight=0.0`, `buy_threshold=0.25`, `sell_threshold=-0.15`다.

## 이미 완화된 조건들

`SignalFilter`는 이미 `volume_multiplier=1.0`, `block_negative_macd=False`로 완화돼 있다. 음수 MACD를 막는 조건은 꺼져 있고, 거래량 배수도 1.0이다. 그런데도 매수를 가장 많이 막은 사유는 여전히 `SIGNAL_FILTER`였다.

## 원인: `rsi_threshold=50.0`

원인 위치는 `autotrading/realtime_engine.py` L247이다.

python
SignalFilter(rsi_threshold=50.0, ...)


중립값인 RSI 50이 과매수 기준으로 쓰이고 있다. HybridQuantAI가 BUY를 내는 구간은 RSI 50~70의 모멘텀 구간이다. 필터는 RSI가 50을 넘으면 막으므로, 전략이 사려는 구간과 필터가 막는 구간이 그대로 겹친다. 그래서 이 구간의 BUY가 통째로 막힌다고 판단했다.

## 함께 발견한 것: 거래량 필터가 두 번 걸린다

거래량 조건이 두 곳에서 따로 검사된다.

- `hybrid_quant_ai.py` 자체 필터: `_passes_volume_filter`, `volume_filter_mult=0.8`
- `SignalFilter`: `volume_multiplier=1.0`

이번 분석에서는 이 점을 기록만 해 두었다.

## 코드를 고치지 않은 이유

이 작업에는 수정 범위 제약이 걸려 있었다.

- 수정할 수 있는 파일은 `risk/trailing_stop.py`, `strategies/hybrid_quant_ai.py` 두 개뿐이다.
- `ai/llm_analyzer.py`는 수정할 수 없다.
- `buy_threshold`도 바꿀 수 없다. 8월 실거래에서 손실(-271,574원)이 난 뒤 사람이 0.15에서 올린 값이기 때문이다.

원인이 있는 `autotrading/realtime_engine.py`와 `strategies/signal_filter.py`는 둘 다 허용 목록 밖이다. 그래서 코드는 손대지 않고 `[제안]`만 남겼다.

## 남긴 `[제안]`

`rsi_threshold`를 `50.0`에서 `65.0`으로 올리자는 제안이다. 바꿀 코드는 다음과 같다.

python
SignalFilter(volume_multiplier=1.0, rsi_threshold=65.0, block_negative_macd=False)


이 제안을 실제로 적용하려면 수정 허용 목록에 `autotrading/realtime_engine.py`나 `strategies/signal_filter.py`를 넣어야 한다.
