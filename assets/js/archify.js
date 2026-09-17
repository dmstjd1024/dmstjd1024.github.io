// 탐색형 도식(Archify) 끼우기.
//
// 산출물 하나가 800KB 를 넘으므로 글을 열자마자 받지 않는다. giscus 와 같이
// IntersectionObserver 로 화면에 가까워질 때 iframe 을 만든다.
//
// 테마는 주소의 ?theme= 로 넘긴다. 이 블로그의 테마 버튼은 body.dark-theme
// 클래스로 동작하는데 iframe 안쪽에서는 그 클래스를 볼 수 없다. 넘겨주지
// 않으면 뷰어가 OS 설정을 따라가 본문과 어긋난다 — 인라인 SVG 로 옮길 때
// 겪었던 "어두운 페이지에 흰 도식" 과 같은 문제다.
(function () {
  var boxes = document.querySelectorAll('.archify[data-src]');
  if (!boxes.length) return;

  function theme() {
    return document.body.classList.contains('dark-theme') ? 'dark' : 'light';
  }

  function src(box) {
    return box.dataset.src + '?theme=' + theme() + '&present=1';
  }

  function mount(box) {
    if (box.dataset.loaded) return;
    box.dataset.loaded = '1';

    var frame = document.createElement('iframe');
    frame.src = src(box);
    frame.loading = 'lazy';
    frame.title = box.dataset.title || '도식';
    // 산출물은 자체완결이라 외부를 부르지 않는다. 그래도 최소 권한만 준다.
    frame.setAttribute('sandbox', 'allow-scripts allow-downloads');
    box.appendChild(frame);
  }

  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (!e.isIntersecting) return;
      io.unobserve(e.target);
      mount(e.target);
    });
  }, { rootMargin: '300px' });

  Array.prototype.forEach.call(boxes, function (box) { io.observe(box); });

  // 테마를 바꾸면 주소를 다시 준다. sandbox 에 allow-same-origin 을 주지
  // 않았으므로 postMessage 로 안쪽을 건드릴 수 없다 — src 교체가 유일한 길이다.
  var btn = document.getElementById('btn-theme');
  if (btn) {
    btn.addEventListener('click', function () {
      Array.prototype.forEach.call(boxes, function (box) {
        var frame = box.querySelector('iframe');
        if (frame) frame.src = src(box);
      });
    });
  }
})();
