// ---------------------------------------------------------------------------
// 모든 페이지에서 도는 스크립트: 테마 전환, 모바일 메뉴.
//
// 테마의 첫 적용은 여기가 아니라 <body> 안의 인라인 스크립트가 한다.
// 이 파일은 defer 라 화면이 그려진 뒤에 도는데, 그때 테마를 켜면
// 흰 화면이 한 번 번쩍인 뒤 어두워진다(FOUC).
// ---------------------------------------------------------------------------
(function () {
  'use strict';

  // --- 테마 ---------------------------------------------------------------
  var themeBtn = document.getElementById('btn-theme');
  if (themeBtn) {
    themeBtn.addEventListener('click', function () {
      var dark = document.body.classList.toggle('dark-theme');
      try { localStorage.setItem('theme', dark ? 'dark' : 'light'); } catch (e) {}
    });
  }

  // --- 모바일 메뉴 --------------------------------------------------------
  var menuBtn = document.getElementById('btn-menu');
  var nav = document.querySelector('.nav');
  if (menuBtn && nav) {
    menuBtn.addEventListener('click', function (e) {
      e.stopPropagation();
      var open = nav.classList.toggle('is-open');
      menuBtn.setAttribute('aria-expanded', open ? 'true' : 'false');
    });

    // 바깥을 누르면 닫는다
    document.addEventListener('click', function (e) {
      if (!nav.classList.contains('is-open') || nav.contains(e.target)) return;
      nav.classList.remove('is-open');
      menuBtn.setAttribute('aria-expanded', 'false');
    });
  }
})();
