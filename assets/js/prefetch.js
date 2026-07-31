// ---------------------------------------------------------------------------
// 링크 사전 로드
//
// 정적 사이트에서 페이지 이동이 느리게 느껴지는 이유는 클릭한 뒤에야 HTML 요청이
// 시작되기 때문이다. 사용자가 링크에 마우스를 올리고 실제로 누르기까지는 보통
// 수백 ms 가 비는데, 그 시간에 미리 받아두면 클릭 시점에 대부분 캐시에서 나온다.
//
// SPA 로 바꾸지 않고 <link rel="prefetch"> 만 쓴다. 라우터도, 히스토리 조작도,
// 스크롤 복원 문제도 없다. 추가되는 JS 는 1KB 남짓이다.
//
// 안전장치:
//   - 같은 출처의 문서 링크만 (외부 링크·앵커·다운로드 제외)
//   - 데이터 절약 모드나 느린 회선에서는 동작하지 않는다
//   - 한 페이지에서 최대 6개까지만
//   - 이미 방문한 URL 은 다시 받지 않는다
// ---------------------------------------------------------------------------
(function () {
  var conn = navigator.connection;
  if (conn && (conn.saveData || /2g/.test(conn.effectiveType || ''))) return;
  if (!document.createElement('link').relList.supports('prefetch')) return;

  var MAX = 6;
  var done = new Set([location.href.split('#')[0]]);
  var timer = null;

  function prefetch(url) {
    if (done.size > MAX || done.has(url)) return;
    done.add(url);

    var l = document.createElement('link');
    l.rel = 'prefetch';
    l.href = url;
    l.as = 'document';
    document.head.appendChild(l);
  }

  function candidate(a) {
    if (!a || !a.href) return null;
    if (a.origin !== location.origin) return null;      // 외부 링크
    if (a.hasAttribute('download')) return null;
    if (a.getAttribute('target') === '_blank') return null;

    var url = a.href.split('#')[0];
    if (url === location.href.split('#')[0]) return null; // 같은 페이지 앵커
    if (/\.(zip|pdf|png|jpe?g|webp|svg|gz)$/i.test(url)) return null;

    return url;
  }

  function onEnter(e) {
    var a = e.target.closest && e.target.closest('a[href]');
    var url = candidate(a);
    if (!url) return;

    // 스치듯 지나가는 마우스에는 반응하지 않는다
    clearTimeout(timer);
    timer = setTimeout(function () { prefetch(url); }, 65);
  }

  function onLeave() { clearTimeout(timer); }

  document.addEventListener('mouseover', onEnter, { passive: true });
  document.addEventListener('mouseout', onLeave, { passive: true });

  // 터치 기기에는 hover 가 없다 — 손가락이 닿는 순간 시작한다
  document.addEventListener('touchstart', function (e) {
    var a = e.target.closest && e.target.closest('a[href]');
    var url = candidate(a);
    if (url) prefetch(url);
  }, { passive: true });
})();
