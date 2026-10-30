#!/usr/bin/env bash
# 글 한 편의 요약 카드 초안을 codex 로 만든다.
#
#   script/gen-summary.sh _pages/Database/어떤글.md          # 초안만 출력
#   script/gen-summary.sh _pages/Database/어떤글.md --write  # 프론트매터에 삽입
#
# --write 는 summary: 가 이미 있으면 거부한다. 덮어쓰면 사람이 고친 내용이
# 사라진다. 다시 만들려면 기존 블록을 지우고 돌린다.
set -euo pipefail
cd "$(dirname "$0")/.."

POST="${1:?글 경로를 넘겨라}"
WRITE="${2:-}"
[ -f "$POST" ] || { echo "없는 파일: $POST" >&2; exit 1; }

if grep -q '^summary:' "$POST"; then
  echo "이미 summary 가 있다: $POST" >&2
  # 여러 편을 도는 루프가 "거부" 를 성공으로 보지 않도록 1 로 끝낸다.
  if [ "$WRITE" = "--write" ]; then exit 1; fi
fi

OUT=$(codex exec --skip-git-repo-check \
  "$(cat script/summary-prompt.md)

$(cat "$POST")" 2>/dev/null)

# codex 출력에서 YAML 블록만 꺼낸다
YAML=$(printf '%s' "$OUT" | sed -n '/^```yaml$/,/^```$/p' | sed '1d;$d')
[ -n "$YAML" ] || { echo "YAML 을 못 찾았다. 원문:" >&2; printf '%s\n' "$OUT" >&2; exit 1; }

# 파싱되는지 먼저 본다 — 깨진 YAML 을 글에 넣으면 빌드가 죽는다.
# PyYAML 대신 ruby 를 쓴다. Jekyll 이 쓰는 파서라 설치가 보장되고,
# 빌드 때와 같은 파서로 검사하는 편이 맞다.
printf '%s\n' "$YAML" | ruby -ryaml -e '
  d = YAML.safe_load($stdin.read)
  s = d && d["summary"]
  abort "summary 키가 없다" unless s.is_a?(Hash)
  ok = ["context","환경","문제","선택","포기","결과"]
  bad = s.keys - ok
  abort "모르는 칸: #{bad}" unless bad.empty?
  r = s["결과"] || []
  abort "결과는 목록이어야 한다" unless r.is_a?(Array)
  filled = s.values.reject { |v| v.to_s.empty? }.size
  warn "  칸 #{filled}개 / 결과 #{r.size}개"
' || { echo "YAML 검사 실패" >&2; printf '%s\n' "$YAML" >&2; exit 1; }

if [ "$WRITE" = "--write" ]; then
  # YAML 을 파이썬 소스에 끼워 넣지 않는다. codex 가 쓴 문자열이라
  # 따옴표 세 개가 하나만 들어와도 문자열이 거기서 닫히고 그 뒤가
  # 코드로 실행된다. 환경변수로 넘기고 heredoc 구분자를 따옴표로 묶어
  # 셸이 본문을 치환하지 않게 한다.
  SUMMARY_YAML="$YAML" python3 -I - "$POST" <<'PY'
import os, sys, pathlib
post = pathlib.Path(sys.argv[1])
t = post.read_text(encoding="utf-8")
yaml_block = os.environ["SUMMARY_YAML"]
# 프론트매터는 첫 --- 와 두 번째 --- 사이다. 그 끝에 붙인다.
a = t.index("---", 0) + 3
b = t.index("\n---", a)
post.write_text(t[:b] + "\n" + yaml_block.rstrip() + t[b:], encoding="utf-8")
print("넣었다:", post)
PY
else
  printf '%s\n' "$YAML"
fi
