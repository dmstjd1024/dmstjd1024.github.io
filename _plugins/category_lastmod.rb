# 카테고리 목록(index.md)의 last_modified_at 을 그 아래 글 중 가장 최근 날짜로 둔다.
#
# 왜 필요한가:
#   목록 페이지는 front matter 에 date 가 없다. 컬렉션 문서는 date 가 없으면
#   빌드 시각을 쓰므로, 사이트맵 lastmod 가 빌드할 때마다 "오늘"로 나간다
#   (그 전에는 _config.yml 기본값 2025-05-27 로 고정돼 있었다). 목록이 실제로
#   바뀌는 때는 그 아래에 글이 생기거나 고쳐질 때다.
#
# date 도 같은 값으로 채우고 draft 로 표시한다. date 가 빌드 시각이면 jekyll-feed
# (posts.xml, 최근 50건)가 목록 32개를 맨 위에 빈 "Index" 항목으로 싣는다.
# 그 피드는 draft 가 true 인 문서를 거른다.
Jekyll::Hooks.register :site, :post_read do |site|
  docs = site.collections["pages"]&.docs || []
  posts = docs.reject { |d| File.basename(d.relative_path) == "index.md" }

  docs.each do |idx|
    next unless File.basename(idx.relative_path) == "index.md"
    dir = File.dirname(idx.relative_path) + "/"
    dir = "_pages/" if dir == "_pages/글/"   # '전체 글'은 디렉터리가 아니라 모든 글의 목록이다
    latest = posts.select { |p| p.relative_path.start_with?(dir) }
                  .map { |p| p.data["last_modified_at"] || p.data["date"] }
                  .compact
                  .map { |v| v.is_a?(String) ? Jekyll::Utils.parse_date(v) : v.to_time } # Date·Time 섞여 있으면 max 가 못 비교한다
                  .max
    idx.data["draft"] = true
    next unless latest
    idx.data["last_modified_at"] = latest
    idx.data["date"] = latest
  end
end
