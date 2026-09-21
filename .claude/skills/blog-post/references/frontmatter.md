# 프론트매터

## 형태

`title` 뒤에 **공백 두 칸**이 들어간다. 140편 중 108편이 그렇고,
**최근 글은 예외 없이 두 칸**이다 (한 칸짜리 32편은 `Text_Book_*` 같은 옛 글).
`categories` 와 `tags` 사이, `tags` 와 `date` 사이에 **빈 줄**이 있다.

```yaml
---
title:  "TOCTOU 한 건을 고치는 대신 버그 클래스를 없앴다"

categories:
  - Spring
tags:
  - AI
  - Claude Code
  - 동시성
  - Spring

date: 2026-05-10
thumbnail: "/assets/img/thumbnail/spring_thumbnail.webp"
card_thumbnail: "/assets/img/thumbnail/spring_card.webp"
---
```

- `categories` 는 **하나만** 쓴다. 디렉토리 이름과 일치해야 한다.
- `date` 는 작성일. 파일명에 날짜를 넣지 않는다 (옛 글 일부만 `2023-01-06-` 형식).
- 도식에 Mermaid 를 쓰면 `mermaid: true`, Archify 산출물을 넣으면 `archify: true` 를 추가한다.

## 카테고리

디렉토리가 곧 카테고리다. 파일은 `_pages/<카테고리>/<제목>.md` 에 놓는다.
파일명은 한글 제목을 하이픈으로 이은 형태를 쓴다 — `gin-trigram-인덱스가-안-먹던-이유.md`.

| 카테고리 | 글 수 | 쓰는 주제 |
|---|---|---|
| AI | 26 | Claude Code, 에이전트, AI 도구 |
| Spring | 16 | Spring Boot, JPA, 동시성 |
| React | 15 | 프론트엔드, 상태관리 |
| Java | 12 | 언어, 스터디 (하위 폴더 있음) |
| Database | 11 | PostgreSQL, 쿼리 튜닝, 마이그레이션 |
| Docker | 9 | 컨테이너, 이미지, 레지스트리 |
| Kubernetes | 8 | 클러스터, 오퍼레이터 |
| Etc | 8 | 어디에도 안 맞는 것 |
| BlockChain | 6 | Hyperledger Fabric, Besu |
| Infra | 5 | 배포, 서버, 자동화 |
| Develop | 5 | 도구, 워크플로우, 방법론 |
| Jira / Git | 4 | |
| AWS | 3 | |
| Sap / Linux / CI | 2 | |
| Messaging / GraphQL | 1 | |

총 140편 (2026-09 기준). 일부 카테고리는 하위 폴더를 쓴다
(`_pages/Java/Live-Study/`, `_pages/Sap/sapui5/`) — 새 글은 하위 폴더 없이
`_pages/<카테고리>/` 바로 아래 놓는 게 최근 관행이다.

`_pages/글/` 은 비어 있다.

## 태그

**`AI` 와 `Claude Code` 는 거의 모든 글에 붙는다** (140편 중 80편·78편 —
최근 글 기준 사실상 전부). Claude Code 로 작업한 내용이면 둘 다 붙인다.

여기에 **주제 태그 2~3개**를 더한다. 기존에 쓰던 것을 재사용한다 —
새 태그를 만들면 태그 페이지에 한 편짜리가 늘어난다.

실제 사용 중인 주제 태그 (괄호는 사용 글 수):

```
Spring(18)  Kubernetes(18)  개발환경(16)  React(15)  Java(13)  Docker(11)
성능최적화(8)  JPA(8)  자동화(7)  데이터베이스(6)  폐쇄망(6)  자동매매(6)
Next.js(6)  Git(6)  BlockChain(6)  PostgreSQL(5)  셸스크립트(5)
```

숫자는 2026-09 기준 사용 글 수(140편 중)다. 현재 목록은 이렇게 센다 —
**본문 불릿이 섞이지 않게 프론트매터만 파싱해야 한다:**

```bash
python3 - <<'EOF'
import pathlib, re, collections
c = collections.Counter()
for f in pathlib.Path("_pages").rglob("*.md"):
    if f.name == "index.md": continue
    m = re.match(r"^---\n(.*?)\n---", f.read_text(errors="replace"), re.S)
    if not m: continue
    tm = re.search(r"^tags:\s*\n((?:\s*-\s*.+\n?)+)", m.group(1), re.M)
    if tm:
        for line in tm.group(1).splitlines():
            t = line.strip().lstrip("-").strip()
            if t: c[t] += 1
for t, n in c.most_common(25): print(f"{n:4d}  {t}")
EOF
```

⚠️ `grep -rhF '  - '` 로 세지 않는다 — 본문의 들여쓴 불릿까지 잡혀 값이 부풀려진다.
실측(2026-09-18): `AI` 80편이 106으로, `Spring` 18편이 34로, `React` 15편이 30으로 나왔다.
`Claude Code` 처럼 본문에 안 나오는 문자열만 우연히 정확해서, 훑어봐서는 안 걸린다.

## 썸네일

`assets/img/thumbnail/` 에 있는 것만 쓴다. **없는 파일을 지어내지 않는다.**
대부분 `<이름>_thumbnail.<확장자>` + `<이름>_card.<확장자>` 쌍이다.
확장자가 제각각(`.png` / `.webp` / `.jpg` / `.jpeg`)이므로 반드시 실물을 확인한다.

```bash
ls assets/img/thumbnail/
```

주제별로 쓰던 것:

| 주제 | 파일 |
|---|---|
| PostgreSQL · DB | `postgresql_thumbnail.png` / `postgresql_card.png` |
| Spring · Java | `spring_thumbnail.webp` / `spring_card.webp` |
| Git · GitHub · 배포 | `github_thumbnail.png` / `github_card.png` |
| Claude Code · AI 도구 | `claude_thumbnail.png` / `claude_card.png` |
| Docker | `docker_thumbnail.png` / `docker_card.png` |
| Kubernetes | `kubernetes_thumbnail.png` / `kubernetes_card.png` |
| React | `react_thumbnail.webp` / `react_card.webp` |
| Jira | `jira_thumbnail.png` / `jira_card.png` |
| 맞는 게 없을 때 | `ect_thumbnail.jpg` |

⚠️ `card_thumbnail` 은 필수가 아니다 — 140편 중 상당수에 없다.
다만 **최근 글은 대체로 쌍으로 넣는다.** 쓰려는 이름의 `_card` 파일이
실제로 없으면 `thumbnail` 만 쓴다 (`로그-폭주가-지운-매매-기록` 이 그 예).
