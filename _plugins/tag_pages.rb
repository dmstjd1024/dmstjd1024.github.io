# 태그별 페이지를 빌드 때 만들어 준다.
#
# 왜 플러그인인가:
#   태그는 108 개이고 계속 는다. 그때마다 _pages 아래에 빈 파일을 손으로
#   만들면 글을 쓸 때마다 잊어버린다. 카테고리는 디렉터리가 곧 메뉴라
#   빈 index.md 로 충분했지만, 태그는 글에서 파생되므로 생성이 맞다.
#
# 배포 안전성:
#   .github/workflows 가 저장소 Gemfile 그대로 빌드하므로(build_type: legacy
#   가 아니다) 이 플러그인이 운영에서도 실행된다. GitHub 기본 빌드였다면
#   _plugins 는 무시된다.
#
# 주소 규칙:
#   /tags/            태그 전체 목록
#   /tags/<slug>/     그 태그의 글 목록
#   slug 는 tag-list.html 의 링크 생성과 반드시 같은 규칙이어야 한다
#   (slugify 'raw' + url_encode). 한글 태그가 많아 raw 를 쓴다 — 기본
#   slugify 는 한글을 통째로 지워 서로 다른 태그가 같은 주소가 된다.
module TagPages
  class TagPage < Jekyll::Page
    def initialize(site, base, dir, tag)
      @site, @base, @dir, @name = site, base, dir, "index.html"
      process(@name)
      self.data = {
        "layout"   => "page",
        "tag"      => tag,
        "title"    => "##{tag}",
        # 목록 페이지는 사이트맵에 넣지 않는다. 글이 아니라 색인이고,
        # 태그마다 한 장씩 늘어 사이트맵이 본문보다 커진다.
        "sitemap"  => false,
      }
    end
  end

  class Generator < Jekyll::Generator
    safe true
    priority :low

    def generate(site)
      # 글은 site.pages 가 아니라 "pages" 컬렉션에 있다.
      # _config.yml 이 collections.pages 를 정의해서 그렇다 — 이름이 같아
      # 헷갈리지만 site.pages 에는 404·index 등 28개뿐이다.
      docs = site.collections["pages"] ? site.collections["pages"].docs : []
      tags = {}
      docs.each do |p|
        next if p.url.end_with?("index.html")
        Array(p.data["tags"]).each do |t|
          t = t.to_s.strip
          next if t.empty?
          (tags[t] ||= 0)
          tags[t] += 1
        end
      end

      # 태그 전체 목록
      site.pages << ListPage.new(site, site.source)

      tags.each_key do |tag|
        site.pages << TagPage.new(site, site.source, File.join("tags", slug_for(tag)), tag)
      end

      Jekyll.logger.info "TagPages:", "#{tags.size} 개 태그 페이지 생성"
    end

    # Liquid 의 `slugify: 'raw'` 와 같은 동작. 공백을 하이픈으로 바꾸는 정도만
    # 하고 한글은 남긴다. URL 인코딩은 브라우저·서버가 처리한다.
    def slug_for(tag)
      tag.to_s.downcase.strip.gsub(/\s+/, "-")
    end
  end

  class ListPage < Jekyll::Page
    def initialize(site, base)
      @site, @base, @dir, @name = site, base, "tags", "index.html"
      process(@name)
      self.data = {
        "layout"  => "page",
        "tag"     => "",
        "title"   => "태그",
        "sitemap" => false,
      }
    end
  end
end
