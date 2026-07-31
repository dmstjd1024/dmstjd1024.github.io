// ---------------------------------------------------------------------------
// 글 페이지 전용: 목차 생성, 읽는 위치 표시, 댓글 지연 로드.
// ---------------------------------------------------------------------------
(function () {
  'use strict';

  var body = document.getElementById('post-body');

  // --- 목차 ---------------------------------------------------------------
  // 본문의 h2/h3 를 훑어 옆쪽 목차를 만든다. 제목이 2개도 안 되면
  // 목차가 의미 없으므로 그냥 숨긴 채로 둔다.
  var toc = document.getElementById('toc');
  if (body && toc) {
    var heads = body.querySelectorAll('h2, h3');
    if (heads.length >= 2) {
      var list = toc.querySelector('.toc__list');
      var items = [];

      Array.prototype.forEach.call(heads, function (h, i) {
        // 마크다운이 id 를 안 붙였으면 여기서 붙인다 — 앵커 링크에 필요하다.
        if (!h.id) h.id = 'h-' + i;

        var li = document.createElement('li');
        if (h.tagName === 'H3') li.className = 'toc__sub';

        var a = document.createElement('a');
        a.href = '#' + h.id;
        a.textContent = h.textContent;
        li.appendChild(a);
        list.appendChild(li);

        items.push({ head: h, li: li });
      });

      toc.hidden = false;

      // 화면에 보이는 제목을 목차에서 강조한다.
      // 스크롤 이벤트마다 계산하면 버벅이므로 IntersectionObserver 를 쓴다.
      var visible = new Set();
      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (en) {
          if (en.isIntersecting) visible.add(en.target);
          else visible.delete(en.target);
        });

        var active = null;
        for (var i = 0; i < items.length; i++) {
          if (visible.has(items[i].head)) { active = items[i]; break; }
        }
        items.forEach(function (it) {
          it.li.classList.toggle('is-active', it === active);
        });
      }, { rootMargin: '-80px 0px -70% 0px' });

      items.forEach(function (it) { io.observe(it.head); });
    }
  }

  // --- 댓글 --------------------------------------------------------------
  // giscus 는 iframe 이라 무겁다. 처음부터 붙이면 글보다 먼저 네트워크를
  // 잡아먹으므로, 댓글 자리가 화면에 가까워질 때 붙인다.
  var box = document.getElementById('comments');
  if (box) {
    var meta = function (n) {
      var el = document.querySelector('meta[name="' + n + '"]');
      return el ? el.content : '';
    };

    var mount = function () {
      if (box.dataset.loaded) return;
      box.dataset.loaded = '1';

      var s = document.createElement('script');
      s.src = 'https://giscus.app/client.js';
      s.async = true;
      s.crossOrigin = 'anonymous';
      s.setAttribute('data-repo', meta('giscus_repo'));
      s.setAttribute('data-repo-id', meta('giscus_repoId'));
      s.setAttribute('data-category', meta('giscus_category'));
      s.setAttribute('data-category-id', meta('giscus_categoryId'));
      s.setAttribute('data-mapping', 'pathname');
      s.setAttribute('data-reactions-enabled', '1');
      s.setAttribute('data-emit-metadata', '0');
      s.setAttribute('data-input-position', 'bottom');
      s.setAttribute('data-lang', 'ko');
      s.setAttribute('data-loading', 'lazy');
      s.setAttribute('data-theme',
        document.body.classList.contains('dark-theme') ? 'dark' : 'light');
      box.appendChild(s);
    };

    var io2 = new IntersectionObserver(function (entries) {
      if (entries[0].isIntersecting) { io2.disconnect(); mount(); }
    }, { rootMargin: '300px' });
    io2.observe(box);

    // 테마를 바꾸면 iframe 안쪽도 따라 바꿔준다.
    var themeBtn = document.getElementById('btn-theme');
    if (themeBtn) {
      themeBtn.addEventListener('click', function () {
        var frame = box.querySelector('iframe.giscus-frame');
        if (!frame) return;
        var t = document.body.classList.contains('dark-theme') ? 'dark' : 'light';
        frame.contentWindow.postMessage(
          { giscus: { setConfig: { theme: t } } }, 'https://giscus.app');
      });
    }
  }
})();
