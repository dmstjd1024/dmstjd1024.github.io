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

  // --- 모바일 메뉴(왼쪽 서랍) ---------------------------------------------
  //
  // 좁은 화면에서 왼쪽에서 밀려 들어오는 세로 메뉴. 열려 있는 동안에는
  // 뒤쪽 본문이 같이 스크롤되지 않도록 <body> 를 잠근다.
  var menuBtn = document.getElementById('btn-menu');
  var nav = document.querySelector('.nav');
  var scrim = document.querySelector('.nav__scrim');

  if (menuBtn && nav) {
    var setMenu = function (open) {
      nav.classList.toggle('is-open', open);
      menuBtn.setAttribute('aria-expanded', open ? 'true' : 'false');
      document.body.classList.toggle('nav-locked', open);

      // 막은 닫힐 때 서서히 사라져야 하므로 전환이 끝난 뒤에 감춘다.
      if (!scrim) return;
      if (open) {
        scrim.hidden = false;
      } else {
        window.setTimeout(function () {
          if (!nav.classList.contains('is-open')) scrim.hidden = true;
        }, 250);
      }
    };

    menuBtn.addEventListener('click', function (e) {
      e.stopPropagation();
      setMenu(!nav.classList.contains('is-open'));
    });

    if (scrim) scrim.addEventListener('click', function () { setMenu(false); });

    // 링크를 고르면 이동하면서 닫는다
    nav.addEventListener('click', function (e) {
      if (e.target.closest('.nav__menu a')) setMenu(false);
    });

    // --- 지금 보고 있는 카테고리를 펼쳐 둔다 ----------------------------
    //
    // 서버에서 미리 펼치지 않는 이유: 페이지마다 메뉴 높이가 달라지면
    // 페이지 전환 때 옛/새 화면을 겹쳐 맞추는 과정에서 아래 항목이 밀렸다
    // 돌아온다(메뉴가 흔들려 보인다). 마크업은 모든 페이지에서 동일하게
    // 두고, 열림 상태만 여기서 얹는다.
    //
    // no-anim 을 잠깐 걸어 첫 펼침이 스르륵 열리지 않게 한다. 페이지를
    // 옮길 때마다 메뉴가 열리는 연출이 반복되면 그것대로 산만하다.
    (function () {
      var current = nav.querySelector('.nav__menu a[aria-current="page"]');
      if (!current) return;

      var li = current.closest('.has-sub');
      if (!li) return;

      li.classList.add('no-anim', 'is-open');
      var t = li.querySelector('.nav__toggle');
      if (t) t.setAttribute('aria-expanded', 'true');

      // 다음 프레임에 애니메이션을 되돌려 준다 — 이후 사용자가 직접
      // 접었다 펴는 것은 정상적으로 부드럽게 동작한다.
      window.requestAnimationFrame(function () {
        window.requestAnimationFrame(function () {
          li.classList.remove('no-anim');
        });
      });
    })();

    // --- 하위 카테고리 접기/펴기 ---------------------------------------
    //
    // 화살표만 토글이다. 카테고리 이름은 링크로 남겨 둔다 — 이름까지
    // 토글로 만들면 그 카테고리 페이지에 갈 방법이 없어진다.
    nav.addEventListener('click', function (e) {
      var btn = e.target.closest('.nav__toggle');
      if (!btn) return;

      e.preventDefault();
      e.stopPropagation();          // 위의 "링크 누르면 닫기" 로 새지 않게

      var li = btn.closest('.has-sub');
      if (!li) return;

      var open = li.classList.toggle('is-open');
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
    });

    document.addEventListener('keydown', function (e) {
      if (!nav.classList.contains('is-open')) return;

      if (e.key === 'Escape') {
        setMenu(false);
        menuBtn.focus();               // 닫은 뒤 돌아갈 자리를 잃지 않게
        return;
      }

      // 열려 있는 동안 Tab 이 뒤쪽 본문으로 새어나가지 않도록 서랍 안에 가둔다.
      // 서랍은 막으로 본문을 덮고 있어서, 안 보이는 곳에 포커스가 가면
      // 키보드 사용자는 자기가 어디 있는지 알 수 없다.
      if (e.key !== 'Tab') return;

      var menu = nav.querySelector('.nav__menu');
      if (!menu) return;

      // 접기 버튼도 탭 순서에 포함한다. 링크만 세면 화살표를 건너뛴다.
      var items = [menuBtn].concat(
        Array.prototype.slice.call(
          menu.querySelectorAll('a[href], button:not([disabled])')
        )
      );
      if (!items.length) return;

      var first = items[0];
      var last = items[items.length - 1];

      if (e.shiftKey && document.activeElement === first) {
        e.preventDefault();
        last.focus();
      } else if (!e.shiftKey && document.activeElement === last) {
        e.preventDefault();
        first.focus();
      }
    });

    // 넓은 화면으로 돌아가면 서랍 상태를 털어낸다.
    // 열어둔 채 창을 넓히면 body 잠금만 남아 스크롤이 안 되는 일이 생긴다.
    var wide = window.matchMedia('(min-width:901px)');
    var onWide = function (e) { if (e.matches) setMenu(false); };

    // addEventListener 는 Safari 14 부터다. 그 이전은 addListener 로 받는다.
    if (wide.addEventListener) wide.addEventListener('change', onWide);
    else if (wide.addListener) wide.addListener(onWide);
  }
})();
