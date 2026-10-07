/* Public site behaviour: menu drawer, price tabs, look filter, copy promo code. */
(function () {
  var N = window.NS, $ = N.$, $$ = N.$$;

  var drawer = $('[data-drawer]');
  $$('[data-drawer-open]').forEach(function (b) { b.addEventListener('click', function () { if (drawer.showModal) drawer.showModal(); else drawer.setAttribute('open', ''); }); });
  $$('[data-drawer-close]').forEach(function (b) { b.addEventListener('click', function () { drawer.close(); }); });
  if (drawer) drawer.addEventListener('click', function (e) { if (e.target === drawer) drawer.close(); });

  /* tabs: arrow keys move between tabs */
  $$('[data-tabs]').forEach(function (box) {
    var tabs = $$('[role=tab]', box);
    function pick(t, focus) {
      tabs.forEach(function (x) {
        var on = x === t;
        x.setAttribute('aria-selected', on ? 'true' : 'false');
        x.tabIndex = on ? 0 : -1;
        document.getElementById(x.getAttribute('aria-controls')).hidden = !on;
      });
      if (focus) t.focus();
    }
    tabs.forEach(function (t, i) {
      t.addEventListener('click', function () { pick(t); });
      t.addEventListener('keydown', function (e) {
        if (e.key === 'ArrowRight') pick(tabs[(i + 1) % tabs.length], true);
        if (e.key === 'ArrowLeft') pick(tabs[(i - 1 + tabs.length) % tabs.length], true);
      });
    });
  });

  /* gallery filter */
  var filter = $('[data-look-filter]');
  if (filter) {
    filter.addEventListener('click', function (e) {
      var b = e.target.closest('[data-tag]'); if (!b) return;
      $$('[data-tag]', filter).forEach(function (x) { x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); });
      var tag = b.getAttribute('data-tag'), shown = 0;
      $$('[data-look]').forEach(function (f) {
        var on = !tag || f.getAttribute('data-tags').split('|').indexOf(tag) >= 0;
        f.hidden = !on; if (on) shown++;
      });
      var empty = $('[data-look-empty]'); if (empty) empty.hidden = shown > 0;
    });
  }

  /* copy a promo code */
  $$('[data-copy]').forEach(function (b) {
    b.addEventListener('click', function () {
      var v = b.getAttribute('data-copy');
      var done = function () { N.toast('Đã sao chép mã ' + v); };
      if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(v).then(done, done); else done();
    });
  });

  /* phone bar sheets: branch list for Gọi and Chỉ đường */
  var openSheet = null;
  function closeSheet() {
    if (!openSheet) return;
    openSheet.hidden = true;
    $$('[data-sheet-open]').forEach(function (b) { b.setAttribute('aria-expanded', 'false'); });
    openSheet = null;
  }
  $$('[data-sheet-open]').forEach(function (b) {
    b.addEventListener('click', function (e) {
      e.stopPropagation();
      var sh = $('[data-sheet="' + b.getAttribute('data-sheet-open') + '"]');
      var was = openSheet === sh;
      closeSheet();
      if (!was) { sh.hidden = false; b.setAttribute('aria-expanded', 'true'); openSheet = sh; var a = $('a', sh); if (a) a.focus(); }
    });
  });
  document.addEventListener('click', function (e) { if (openSheet && !openSheet.contains(e.target)) closeSheet(); });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') closeSheet(); });

  /* header shadow once the page scrolls */
  var hdr = $('.hdr');
  if (hdr) {
    var onScroll = function () { hdr.classList.toggle('scrolled', window.scrollY > 8); };
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  }
})();
