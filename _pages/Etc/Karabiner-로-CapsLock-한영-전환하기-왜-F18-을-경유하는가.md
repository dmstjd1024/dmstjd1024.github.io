---
title:  "Karabiner 로 CapsLock 한영 전환하기 — 왜 F18 을 경유하는가?"
subtitle: "CapsLock 신호를 없애던 device 매핑을 제거하고, F18과 입력 소스 단축키로 누르는 즉시 전환되게 했다"
description: "CapsLock 신호를 없애던 device 매핑을 제거하고, F18과 입력 소스 단축키로 누르는 즉시 전환되게 했다"

categories:
  - Etc
tags:
  - Karabiner
  - macOS
  - 키보드
  - 한영전환

date: 2026-09-09
---
## 한 줄로

CapsLock 을 한영 전환 키로 쓰려면 `caps_lock → f18` 로 매핑하고 macOS 의 「이전 입력 소스 선택」 단축키를 F18 로 재녹화하는 것이 맞다. macOS 네이티브 체크박스나 Karabiner 의 `to_if_alone` 은 키를 **뗄 때** 발화하기 때문에, 살짝 누르고 바로 타자를 치면 전환되지 않은 글자가 하나 먼저 들어간다. 그리고 규칙이 아무리 맞아도 device 매핑에 `caps_lock → vk_none` 이 남아 있으면 신호 자체가 먼저 죽는다.

## simple modification 과 complex modification

Karabiner-Elements 에는 키 변환 규칙이 두 층으로 있다.

- **simple modification**: "이 키를 저 키로" 라는 1:1 치환. `caps_lock → f18` 같은 것.
- **complex modification**: 조건·타이밍이 붙는 규칙. "짧게 누르면 A, 길게 누르면 B" 같은 `to_if_alone` 이 여기 속한다.

중요한 것은 **처리 순서**다. Karabiner 는 simple modification 을 complex 보다 먼저 처리한다. 그래서 simple 쪽에서 키가 이미 다른 것으로 바뀌었거나 죽었다면, complex 규칙은 볼 신호 자체가 없다.

`vk_none` 은 Karabiner 에서 "이 키를 아무것도 아닌 것으로 만든다" 는 뜻의 특수 대상이다. device 별 매핑에 `caps_lock → vk_none` 이 들어 있으면 CapsLock 은 눌러도 아무 이벤트를 내지 않는다.

## 진짜 원인은 규칙이 꺼져 있어서가 아니었다

처음에는 한영 전환 규칙이 비활성 상태라 안 되는 줄 알았다. 실제 원인은 device 매핑에 살아 있던 `caps_lock → vk_none` 이었다. 이게 있는 한 어떤 복합 규칙을 짜도 발동하지 않는다 — 신호가 먼저 죽으니 뒤에서 기다리는 규칙에는 도달하지 못한다.

1월에 규칙을 켰다가 2월에 되돌렸던 것도 같은 이유로 보인다. 규칙을 바꿔가며 시도했지만 원인은 다른 층에 있었다.

## 왜 F18 인가 — 발화 시점 때문이다

macOS 네이티브 체크박스 방식과 Karabiner 의 `to_if_alone` 방식은 키를 **뗄 때** 발화한다. CapsLock 하나에 기능이 둘 걸려 있으니 짧게 눌렀는지 길게 눌렀는지 판단을 뗄 때까지 미뤄야 하기 때문이다. Karabiner 공식 문서도 이렇게 적고 있다:

> The events are posted at the from key is released

(이벤트는 원래 키를 뗄 때 발생한다.)

결과적으로 살짝 누르고 바로 타자를 치면, 전환이 끝나기 전에 들어간 글자가 하나 먼저 찍힌다.

F18 은 다르다. 기능이 하나뿐이라 짧게/길게를 판별할 게 없고, 그래서 **누르는 즉시** 나간다.

대가도 있다:

- CapsLock 본래의 대문자 고정 기능 상실 (Shift 로 대체)
- 기존 Ctrl+Space 한영 전환 대체

## 재녹화는 GUI 로만 된다

단축키 값을 `defaults write` 로 직접 쓰는 것은 안 먹는다 — cfprefsd(설정값을 메모리에 캐싱하는 macOS 데몬) 때문이다. GUI 에서 직접 녹화해야 한다.


```text
시스템 설정 → 키보드 → 키보드 단축키… → 입력 소스
→ "이전 입력 소스 선택" 더블클릭 → CapsLock 짧게 톡
```

누른 채 유지하면 HUD 가 떠 버리므로 짧게 톡 쳐야 한다.

## 중간에 오진 한 번

재녹화 후 값이 `(65535, 79, 8388608)` 로 나왔다. Fn 플래그가 붙어버린 문제로 보고 F13 으로 우회했는데, 확인해 보니 **`8388608` 이 정상값**이었다. 다시 F18 로 되돌렸다.

## 검증

세 가지로 확인했다.

- Karabiner EventViewer 에서 `f18` 이벤트 확인 (출처: Karabiner VirtualHIDKeyboard)
- `defaults read` 로 60번 항목이 `(65535, 79, 8388608)` 인지 확인
- 실제 타이핑으로 전환 확인

정리 후 남은 설정은 `caps_lock → f18` 과 `F3 → Mission Control` 둘뿐이다.

## 다시 할 때를 위한 함정 4개

같은 작업을 다른 머신에서 반복할 것을 대비해 함정을 따로 적어 뒀다.

| 함정 | 내용 |
|---|---|
| `vk_none` 선삭제 | device 매핑에 남아 있으면 어떤 규칙도 발동하지 않는다 |
| `8388608` 정상값 | Fn 플래그 문제로 오해하고 우회하지 말 것 |
| `defaults write` 금지 | cfprefsd 캐시 때문에 안 먹는다. GUI 재녹화만 가능 |
| `select_input_source` 금지 | 사용 금지만 기록했고 이유는 노트에 남기지 않음 |

작업 중 Karabiner 가 16.1.0 → 16.3.0 으로 자동 업데이트됐으나 설정과 동작은 그대로였다.
