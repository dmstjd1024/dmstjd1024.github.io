# jekyll-loading-lazy 는 <img> 가 있는 페이지를 Nokogiri.HTML(HTML4 파서)로 다시 쓰는데,
# 그 파서는 <wbr> 을 빈 요소로 몰라 "Live-<wbr>Study</wbr>" 처럼 닫는 태그를 붙인다.
# 브라우저는 버리지만 HTML 검사기에는 오류라, 그 플러그인 뒤(:low)에 지운다.
# h1 안에서는 </wbr> 뒤에 줄바꿈도 붙여, Firefox 가 제목을 복사할 때 끝에 공백이 생겼다.
# </wbr> 는 늘 부모가 닫히기 직전에 오므로 바로 뒤 줄바꿈은 파서가 넣은 것뿐이다.
Jekyll::Hooks.register [:pages, :documents], :post_render, priority: :low do |doc|
  doc.output = doc.output.gsub(%r{</wbr>\n?}, "") if doc.output&.include?("</wbr>")
end
