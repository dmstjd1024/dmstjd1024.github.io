---
title:  "MCP 12개, 도구 251개 — 무엇을 왜 붙였나"

categories:
  - AI
tags:
  - AI
  - Claude Code
  - MCP
  - 개발환경

date: 2026-08-27
thumbnail: "/assets/img/thumbnail/mcp_thumbnail.jpg"
card_thumbnail: "/assets/img/thumbnail/mcp_card.jpg"
---
## MCP 가 뭔가

Model Context Protocol. AI 가 외부 서비스를 도구로 쓰게 해주는 규약이다. 붙이면 Claude 가
Jira 티켓을 만들고, Slack 을 읽고, 브라우저를 조작할 수 있게 된다.

개념 설명은 [따로 쓴 글](/AI/MCP/MCP란.html)에 있고, 여기서는 **내가 실제로 무엇을 붙였고
왜 그랬는지**만 본다.

지금 12개가 붙어 있고, 그 12개가 제공하는 도구를 세면 **251개**다.

## 12개 목록

| MCP | 도구 수 | 대표 도구 |
|---|---:|---|
| oh-my-claudecode `t` | 51 | `lsp_goto_definition`, `wiki_query`, `python_repl` |
| atlassian | 43 | `searchJiraIssuesUsingJql`, `getConfluencePage` |
| chrome-devtools | 30 | `take_snapshot`, `list_console_messages` |
| Gmail | 29 | `search_threads`, `create_draft` |
| Notion | 28 | `notion-search`, `notion-create-pages` |
| github | 26 | `create_pull_request`, `search_code` |
| Cloudflare | 23 | `d1_database_query`, `workers_list` |
| slack | 19 | `slack_read_channel`, `slack_send_message` |
| outline | 18 | `search_documents`, `ask_documents` |
| Google Drive | 11 | `search_files`, `read_file_content` |
| brave-search | 2 | `brave_web_search` |
| **aside** | **1** | `repl` |

## 도구 1개짜리가 기본값이다

표에서 제일 이상한 줄은 마지막이다. `aside` 는 **도구가 하나뿐**인데, 전역 규칙에서
브라우저 자동화의 **1순위**로 지정해뒀다.

```
aside 를 우선 쓰고, chrome-devtools 는 후순위다.
```

도구 30개짜리를 두고 1개짜리를 먼저 쓰는 이유가 규칙에 적혀 있다.

```
aside 를 우선하는 이유는 로그인 세션이 살아 있어 사내 도구를 인증 단계 없이
바로 다루고, REPL 이라 여러 단계를 코드 한 덩어리로 묶어 왕복을 줄이기 때문이다.
```

`repl` 하나로 여러 단계를 코드 한 덩어리에 넣을 수 있다. `chrome-devtools` 는 클릭·입력·
확인을 도구 호출 여러 번으로 나눠야 한다. **도구 개수가 아니라 왕복 횟수가 비용이다.**

대신 콘솔·네트워크·성능 트레이스가 필요하면 `chrome-devtools` 로 간다. 그건 `repl` 로 안
되는 영역이다.

## 성격별로 묶으면

251개 도구를 대상 도메인으로 나누면 이렇게 갈린다.

| 묶음 | MCP |
|---|---|
| 브라우저 조작 | aside, chrome-devtools |
| 문서·지식 | outline, Notion, Google Drive |
| 협업·커뮤니케이션 | slack, Gmail, atlassian |
| 개발 인프라 | github, Cloudflare |
| 에이전트 확장 | oh-my-claudecode `t` |
| 웹 검색 | brave-search |

마지막에서 두 번째가 성격이 다르다. `oh-my-claudecode` 의 51개는 **외부 서비스가 없다.**
`lsp_goto_definition` 같은 코드 탐색, `notepad_write_working` 같은 세션 간 메모, `wiki_query`
같은 지식 축적 — 전부 에이전트 자신의 능력을 늘리는 것들이다.

## 등록 경로가 세 갈래다

이게 헷갈리는 대목인데, 12개가 서로 다른 방식으로 등록돼 있다.

| 경로 | 개수 | 어떤 것 |
|---|---:|---|
| `~/.claude.json` (로컬) | 6 | github, brave-search, outline, atlassian, aside, chrome-devtools |
| 플러그인이 자체 등록 | 2 | oh-my-claudecode, slack |
| claude.ai 계정 커넥터 | 4 | Gmail, Notion, Google Drive, Cloudflare |

세 번째가 특이하다. 이 4개는 **로컬 어느 파일에도 정의가 없다.** claude.ai 계정에 연결해두면
세션에 주입된다. 로컬에는 연결 이력만 캐시돼 있다.

## settings.json 에 쓰면 안 읽힌다

여기서 한 번 크게 헤맸다. MCP 를 `settings.json` 에 적어두면 심링크로 4대에 퍼질 테니
편할 것 같았다. 그런데 **Claude Code 가 그 자리를 읽지 않는다.**

증거가 지금도 남아 있다. `settings.json` 에 이런 블록이 있다.

```json
"mcpServers": {
  "youtube-transcript": {
    "command": "npx",
    "args": ["-y", "@kimtaeyoon83/mcp-server-youtube-transcript"]
  }
}
```

선언은 돼 있는데 **`claude mcp list` 에 안 나오고, 세션 도구 목록에도 없다.** 등록된 적이
없는 것이다.

그래서 `install.sh` 가 `claude mcp add` 를 직접 부른다. 주석에 이유가 있다.

```
MCP 설정은 ~/.claude.json 에만 있고 이 파일은 git 미추적이라 심링크로 못 퍼뜨린다
— settings.json 의 mcpServers 는 Claude Code 가 읽지 않으므로
반드시 `claude mcp add` 로 등록해야 한다.
```

저 `youtube-transcript` 블록은 일부러 안 지웠다. **지우면 이 주장의 증거가 사라진다.**

## 버전을 고정한 이유는 보안이다

`chrome-devtools` 만 버전이 박혀 있다.

```
npx -y chrome-devtools-mcp@1.7.0
```

`@latest` 를 안 쓰는 이유가 주석에 있다.

```
버전을 고정한다 — @latest 는 탈취된 새 버전이 확인 없이 실행되는 경로가 되고,
이 서버는 브라우저 조작 권한을 갖는다.
```

`npx -y ...@latest` 는 **확인 없이 최신 버전을 받아 실행한다.** 패키지가 탈취되면 브라우저를
조작할 수 있는 코드가 그대로 돈다. 공급망 공격 경로다.

핀을 실제로 강제하는 로직까지 있다. 등록 여부만 보면 낡은 핀이 남으므로, **버전 문자열까지
확인해서 다르면 지우고 다시 건다.**

```bash
# 등록돼 있어도 버전이 다르면 지우고 다시 건다 (존재 여부만 보면 낡은 핀이 남는다)
```

## 회사 머신에만 붙는 것

`aside` 는 프로파일 게이트 안에 있다.

```bash
if [[ "$CLAUDE_PROFILE" == company-* ]]; then
  # aside MCP 등록
```

사내 로그인 세션을 물고 사내 화면에 접근하는 도구라 개인 머신에는 안 넣는다. 반면
`chrome-devtools` 는 게이트 밖이다 — 범용 브라우저 디버깅은 어느 머신에서든 쓴다.

## 붙였다 갈아탄 것

조사하다 발견한 흔적이 하나 있다. 로컬 캐시에 "연결한 적 있는 커넥터" 목록이 남는데,
거기에 **Atlassian 이 들어 있다.** 그런데 지금 쓰는 `atlassian` 은 커넥터가 아니라
로컬 등록이다.

즉 **같은 서비스를 두 경로로 붙여보고 하나를 골랐다.** 왜 갈아탔는지는 주석에 안 남겨서
지금은 알 수 없다. 이런 건 그때 한 줄이라도 적어뒀어야 했다.

## 주의 — 자격증명이 평문으로 남는다

마지막으로 하나. `~/.claude.json` 에는 MCP 마다 환경변수가 들어가는데, **API 키가 평문으로
저장된다.** 이 파일은 git 미추적이라 저장소로 새지는 않지만, 파일 자체는 그냥 읽힌다.

이 글을 쓰면서 확인한 것이고, 스크린샷이나 발췌를 어디 올릴 일이 있으면 반드시 가려야 한다.

## 정리

- MCP 12개 · 도구 251개
- **도구 1개짜리(`aside`)가 30개짜리보다 우선**인 이유는 왕복 횟수
- 등록 경로가 셋 — 로컬 6 / 플러그인 2 / 계정 커넥터 4
- **`settings.json` 의 `mcpServers` 는 읽히지 않는다.** `claude mcp add` 를 써야 한다
- 브라우저 조작 권한을 가진 서버는 **버전을 핀**한다 (`@latest` 금지)
- `~/.claude.json` 에 API 키가 평문으로 남는다

같이 읽을 글:
[MCP 란](/AI/MCP/MCP란.html) ·
[Claude Code 설정을 맥 4대에 나눠 담기](/AI/Claude/claude-code-셋업-계층과-플러그인.html)
