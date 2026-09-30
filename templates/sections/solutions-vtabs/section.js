/* solutions-vtabs: vertical tabs with roving tabindex (arrow keys both ways, Home, End), vtabs-bar-slide and
   vtabs-cards-rise. On narrow screens the list becomes a horizontal pill row; the same keys work there. */
(function () {
  document.querySelectorAll('[data-vtabs]').forEach(function (root) {
    var bar = root.querySelector('.bl-solutions-vtabs__bar');
    var rail = root.querySelector('.bl-solutions-vtabs__rail');
    var tabs = Array.prototype.slice.call(root.querySelectorAll('[role="tab"]'));
    if (!tabs.length) return;

    function play(pane) {
      pane.classList.remove('is-entering');
      if (window.BL.RM) return;
      void pane.offsetWidth;
      pane.classList.add('is-entering');
    }
    function current() {
      return tabs.filter(function (t) { return t.getAttribute('aria-selected') === 'true'; })[0] || tabs[0];
    }
    function moveBar(tab) {
      if (!bar) return;
      bar.style.setProperty('--bar-y', (tab.offsetTop + tab.offsetHeight - 4) + 'px');
      bar.style.setProperty('--bar-o', '1');
    }
    function select(tab, focus) {
      tabs.forEach(function (t) {
        var on = t === tab;
        t.setAttribute('aria-selected', String(on));
        t.tabIndex = on ? 0 : -1;
        var pane = document.getElementById(t.getAttribute('aria-controls'));
        if (!pane) return;
        if (on && pane.hidden) { pane.hidden = false; play(pane); }
        else if (!on) pane.hidden = true;
      });
      moveBar(tab);
      if (focus) tab.focus();
      if (rail.scrollWidth > rail.clientWidth) {
        rail.scrollTo({ left: tab.offsetLeft - 24, behavior: window.BL.RM ? 'auto' : 'smooth' });
      }
    }
    tabs.forEach(function (tab, i) {
      tab.addEventListener('click', function () { select(tab, false); });
      tab.addEventListener('keydown', function (e) {
        var n = null;
        if (e.key === 'ArrowDown' || e.key === 'ArrowRight') n = tabs[(i + 1) % tabs.length];
        if (e.key === 'ArrowUp' || e.key === 'ArrowLeft') n = tabs[(i - 1 + tabs.length) % tabs.length];
        if (e.key === 'Home') n = tabs[0];
        if (e.key === 'End') n = tabs[tabs.length - 1];
        if (n) { e.preventDefault(); select(n, true); }
      });
    });
    /* hidden panes keep lazy photos unloaded; fetch them once the section is near, so a tab change never shows an
       empty frame */
    window.BL.onVisible(root, function () {
      root.querySelectorAll('.bl-solutions-vtabs__pane img[loading="lazy"]').forEach(function (img) { img.loading = 'eager'; });
    }, 0);
    if (bar) {
      bar.style.transition = 'none';
      moveBar(current());
      void bar.offsetWidth;
      bar.style.transition = '';
    }
    window.addEventListener('resize', function () { moveBar(current()); });
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(function () { moveBar(current()); });
  });
})();
