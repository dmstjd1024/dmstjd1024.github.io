---
title:  "AI 코드리뷰 봇 2종을 파이프라인에 넣고, 봇이 못 잡는 걸 배웠다"

categories:
  - AI
tags:
  - AI
  - Claude Code
  - 코드리뷰
  - 개발문화

date: 2026-07-13
thumbnail: "/assets/img/thumbnail/claude_thumbnail.png"
card_thumbnail: "/assets/img/thumbnail/claude_card.png"
redirect_from:
  - /AI/ai-코드리뷰-봇-2종.html
---
## 배경

- 대상: 프론트엔드 저장소 1곳
- 구성: AI 코드리뷰 두 겹
  - PR에 자동으로 달리는 Gemini 리뷰 봇
  - 작업 중간에 명시적으로 태우는 code-review 패스

- 목표: "지적을 받는 것"이 아니라 지적사항을 실제 커밋으로 환류시키기
- 기간: 약 두 달

- 두 달 운영 결과 — 봇이 잘 잡는 클래스와 전혀 못 잡는 클래스가 뚜렷하게 갈림

- 커밋 메시지에 `Co-Authored-By` 서명과 모델 세대를 남겨 두었다
  — Sonnet 4.6 → Opus 4.8 → Opus 4.8 1M → Opus 5

## 봇이 잡은 것

- 실제 커밋으로 이어진 지적을 유형별로 정리

| 유형 | 지적 내용 |
|---|---|
| 관용구 위반 | 차트 `option` 객체를 매 렌더 재생성 (useMemo 누락) |
| 누락된 cleanup | 메모리 누수 3건 추가 발견 |
| 레이스 컨디션 | 민감도 분석 로딩 순서 |
| 가드 비대칭 | heatmap의 x축은 가드가 있는데 y축만 있음 |
| 중복 방어 | `escapeHtml`이 이미 정규화하는데 바깥에 `String()` 래퍼 |
| 부작용 혼입 | `setGridRows` 업데이터 함수 안에서 다른 setState 호출 |
| 도달 불가능한 분기 | `crumbOf`의 구분선 처리 |

- 이 중 몇 개는 부연 필요

### 업데이터 안에 부작용이 섞여 있었다

- 형태: `setGridRows((prev) => { ... setDeleteIdList(...); return next; })`
- 원칙: React 업데이터 함수는 순수해야 함
- 위반: 안에서 다른 상태를 갱신
- 결과: Strict Mode·동시성 렌더에서 업데이터 2회 호출 → `deleteIdList`에 항목 중복

- 수정: 부작용을 이벤트 핸들러로 끌어올림
- 현재 스코프의 `gridRows`를 직접 참조해 계산
- 두 상태를 순차 갱신

- 상태: 버그 신고 이력 없음. 다만 조건이 맞으면 터질 자리

### 가드의 비대칭

- heatmap의 `yCats[y]` → 존재 확인 가드 있음
- `MODULES[x]` → 가드 없음
- 봇 지적: "왜 한쪽만 있냐"

- 특징: 사람이 diff로 볼 때는 잘 안 보이나, 패턴 매칭에는 잘 걸림

### 상태 미러링

- 기존: `useState` + `useEffect`로 `location.hash`를 `activeId`에 복사
- 문제: desync 창 발생 — hash는 바뀌었는데 state는 아직 안 바뀐 순간
- 조치: 렌더 시점에 hash에서 직접 파생 → 미러링과 effect 동시 제거

## 봇이 못 잡은 것

가장 큰 성능 문제는 봇이 하나도 못 잡았다.

- 사례: [PDF 다운로드가 7초 걸리던 문제](/AI/Frontend/한글-폰트-pdf-성능.html)
- 코드만 보면 이상한 구석 없음 — react-pdf로 PDF를 만드는 평범한 코드
- 실제 병목: 한글 폰트의 텍스트 layout
- 발견 경로: chrome-devtools로 직접 계측, 20여 종의 조합 실험

- 성격: 정적 분석으로 도달 불가능한 결론

## 봇이 잘 잡는 것과 못 잡는 것

- 두 달 운영 후 정리된 경계

| 잘 잡는 클래스 | 못 잡는 클래스 |
|---|---|
| 관용구 위반 (useMemo·useCallback 누락) | 성능 병목 (실측이 필요한 것) |
| 누락된 cleanup (dispose·revoke·clearTimeout) | 도메인 정합성 (이 계산식이 업무적으로 맞는가) |
| exhaustive check·가드 대칭성 | 아키텍처 수준의 중복 (V1/V2 이중 스택 같은 것) |
| 도달 불가능한 분기 | 사용자에게 실제로 어떻게 보이는가 |

- 공통점 — 잘 잡는 건 **파일 하나 안에서 판정 가능한 것**
- 못 잡는 건 **실행해봐야 알거나 도메인 지식이 필요한 것**

<div class="diagram" role="img" aria-label="정적 분석으로 판정 가능한 범위와 그 밖의 경계">
{% include diagrams/review-bot--boundary.svg %}
</div>

## 남는 교훈

- AI 리뷰 봇 도입 효과 — 지적사항 수 증가
- 왼쪽 열의 성격: 사람 리뷰어가 꾸준히 잡기 어려운 종류 (지루하고, 놓쳐도 당장 티가 안 남)
- 기계가 이를 대신 보는 것은 실질적 이득

다만 봇을 붙였다고 리뷰가 끝났다고 착각하면 위험하다.

- 오른쪽 열 — 여전히 사람 몫
- 그중 성능 문제 — 계측 없이는 판정 불가

봇의 통과 여부를 "문제 없음"의 근거로 쓰지 않는 것 — 그게 두 달 동안 얻은 가장 실용적인 결론이다.
