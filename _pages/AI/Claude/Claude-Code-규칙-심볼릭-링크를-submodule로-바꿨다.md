---
title:  "Claude Code 규칙 심볼릭 링크를 submodule로 바꿨다"
subtitle: "`@` import는 안쪽 폴더에서 `NONE`이었고, `.claude/rules`는 바깥·안쪽 모두 읽혔다"
description: "`@` import는 안쪽 폴더에서 `NONE`이었고, `.claude/rules`는 바깥·안쪽 모두 읽혔다"

categories:
  - AI
tags:
  - Claude Code
  - git submodule
  - CLAUDE.md
  - .claude/rules

date: 2026-11-06
---
## 한 줄로

서비스 레포 2개가 같은 Claude Code 규칙을 쓰도록 공통 규칙 레포를 따로 만들고, 양쪽 `.claude/rules/` 아래에 submodule로 넣었다. 심볼릭 링크와 달리 두 레포를 나란히 둘 필요가 없고, 실험에서도 `.claude/rules`는 바깥·안쪽 폴더 모두에서 읽혔다. 대신 규칙을 고칠 때마다 바깥 레포마다 submodule을 갱신해 커밋해야 한다.

회사 프로젝트라 레포 이름과 프로젝트 이름은 일반명사로 바꿔 적었다.

## 용어

- **git submodule**: 저장소 안의 폴더가 다른 저장소의 특정 커밋을 가리키게 하는 Git 기능이다.
- **`.claude/rules`**: Claude Code가 규칙 파일을 읽는 폴더다.
- **`@` import**: `CLAUDE.md` 안에서 다른 파일을 불러오는 문법이다.
- **바깥 레포·안쪽 레포**: 이 글에서는 서비스별 최상위 레포를 바깥 레포, 그 안에 따로 clone하는 백엔드·프런트엔드 레포를 안쪽 레포라고 부른다.

## 심볼릭 링크를 버린 이유

11-05 노트로는 「CLAUDE.md 공유용 PR 6개를 닫고 심볼릭 링크로 바꿨다」는 글이 자동 생성됐다. 그런데 11-06에 심볼릭 링크를 없애면서 그 글의 결론은 이미 지난 내용이 됐다.

submodule로 바꾸면서 달라진 점은 두 가지다.

- 두 레포를 나란히 둘 필요가 사라졌다.
- 각 `CLAUDE.md`에는 서비스별 구조만 남는다.

다른 방법 두 가지는 이런 이유로 뺐다.

- **커밋한 PC 절대경로**: 다른 사람 PC에서 깨진다.
- **PC 전체를 검색하는 방식**: 엉뚱한 사본에 연결될 수 있다.

`CLAUDE.md`에 적혀 있던 작업 폴더 경로도 `<작업 폴더>/`로 바꿨다.

## 규칙 위치 실험

어디에 두어야 안쪽 레포에서 작업할 때도 읽히는지 먼저 시험했다.

| 방식 | 결과 |
|---|---|
| `.claude/rules` | 바깥·안쪽 폴더 모두 `MARKER_RULES_DIR`이 읽힘 |
| `@` import | 안쪽에서 `NONE` |

결정적인 차이는 안쪽 폴더다. 그래서 `.claude/rules`를 골랐다. 실제 백엔드 레포 안에서도 규칙에 적힌 Slack 채널 ID와 에픽 번호를 읽는 것까지 확인했다.

## 최종 구조

서비스마다 같은 모양이다.

```text
<작업 폴더>/
└── <서비스>/                     [바깥 레포]
    ├── README.md / CLAUDE.md
    ├── .claude/rules/<프로젝트>/  [submodule → 공통 규칙 레포]
    ├── <서비스>-backend/          common/ user/ admin/
    └── <서비스>-frontend/         common/ user/ admin/
```

submodule은 바깥 레포에만 두기를 권했다. 안쪽 레포만 단독으로 clone하면 규칙이 없는데, 이 점은 감수하기로 하고 README에도 그렇게 적었다.

## 대가: 규칙을 고칠 때마다 갱신해야 한다

공통 규칙 레포를 고친 뒤 바깥 레포마다 아래를 실행한다.

```bash
git submodule update --remote .claude/rules/<프로젝트>
git add .claude/rules/<프로젝트>
git commit -m "ITS-xxx 공통 규칙 갱신"
```

이 절차를 빠뜨리면 그 레포만 옛 규칙을 본다.

바깥 README에는 `git config submodule.recurse true`도 추가했다. 이미 clone한 팀원은 직접 한 번 실행해야 한다.

## 팀원 셋업은 어디까지 자동인가

"진행하자"만으로 clone까지 되지는 않는다. 역할은 이렇게 나뉜다.

- **사람**: 바깥 레포 받기, 인증
- **Claude**: 이후 구조 확인과 안내

이를 위해 README에 Claude용 설치 프롬프트를 넣고, `claude -p`와 sonnet으로 시험했다.

| 실험 | 결과 |
|---|---|
| 서비스 B clone 후 README 프롬프트 | backend·frontend clone, submodule `c213144`, 바깥 `git status` 깨끗함 |
| 서비스 A에서 안쪽 레포 없이 엔티티 생성 요청 | 코드 작성을 멈추고 clone을 안내 |
| 서비스 B 프런트엔드 레포 안에서 세션 | Slack 채널·에픽을 규칙에서 읽음 |

세 번째 줄은 위 실험과 같은 내용을 프런트엔드 레포에서 다시 확인한 것이다. 두 번째 줄은 안쪽 레포가 없는 상태에서 코드를 쓰지 않고 clone부터 안내한 사례다.

## 아직 비어 있는 것

공통 규약을 모을 `rule.md`는 만들어 push했다(공통 규칙 레포 `c10c1be`, 바깥 레포 `c9647cf`, `d694e74`). 내용은 아직 없다. 한쪽 서비스의 백엔드 설계를 마친 뒤 다른 서비스 쪽과 협의해 채운다.

팀원 안내도 아직 직접 해야 할 일로 남아 있다.
