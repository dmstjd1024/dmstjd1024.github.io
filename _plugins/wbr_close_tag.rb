# jekyll-loading-lazy 는 <img> 가 있는 페이지를 Nokogiri.HTML(HTML4 파서)로 다시 쓰는데,
# 그 파서는 <wbr> 을 빈 요소로 몰라 "Live-<wbr>Study</wbr>" 처럼 닫는 태그를 붙인다.
# 브라우저는 버리지만 HTML 검사기에는 오류라, 그 플러그인 뒤(:low)에 지운다.
Jekyll::Hooks.register [:pages, :documents], :post_render, priority: :low do |doc|
  doc.output = doc.output.gsub("</wbr>", "") if doc.output&.include?("</wbr>")
end
