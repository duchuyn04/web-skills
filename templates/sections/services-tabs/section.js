/* sliding-pill-tab-switcher with roving tabindex and arrow-key support */
(function () {
  document.querySelectorAll('[data-tabs]').forEach(function (root) {
    var list = root.querySelector('[role="tablist"]');
    var pill = root.querySelector('.bl-tabs__pill');
    var tabs = Array.prototype.slice.call(root.querySelectorAll('[role="tab"]'));
    if (!tabs.length) return;

    function movePill(tab) {
      if (!pill) return;
      pill.style.setProperty('--pill-x', tab.offsetLeft + 'px');
      pill.style.setProperty('--pill-w', tab.offsetWidth + 'px');
    }
    function select(tab, focus) {
      tabs.forEach(function (t) {
        var on = t === tab;
        t.setAttribute('aria-selected', String(on));
        t.tabIndex = on ? 0 : -1;
        var panel = document.getElementById(t.getAttribute('aria-controls'));
        if (!panel) return;
        if (on && panel.hidden) {
          panel.hidden = false;
          panel.classList.remove('is-entering');
          void panel.offsetWidth;
          panel.classList.add('is-entering');
        } else if (!on) {
          panel.hidden = true;
        }
      });
      movePill(tab);
      if (focus) tab.focus();
      var scroller = list.parentElement;
      if (scroller.scrollWidth > scroller.clientWidth) {
        scroller.scrollTo({ left: tab.offsetLeft - 24, behavior: window.BL.RM ? 'auto' : 'smooth' });
      }
    }
    tabs.forEach(function (tab, i) {
      tab.addEventListener('click', function () { select(tab, false); });
      tab.addEventListener('keydown', function (e) {
        var n = null;
        if (e.key === 'ArrowRight') n = tabs[(i + 1) % tabs.length];
        if (e.key === 'ArrowLeft') n = tabs[(i - 1 + tabs.length) % tabs.length];
        if (e.key === 'Home') n = tabs[0];
        if (e.key === 'End') n = tabs[tabs.length - 1];
        if (n) { e.preventDefault(); select(n, true); }
      });
    });
    var current = tabs.filter(function (t) { return t.getAttribute('aria-selected') === 'true'; })[0] || tabs[0];
    pill.style.transition = 'none';
    movePill(current);
    void pill.offsetWidth;
    pill.style.transition = '';
    window.addEventListener('resize', function () { movePill(tabs.filter(function (t) { return t.getAttribute('aria-selected') === 'true'; })[0]); });
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(function () { movePill(current); });
  });
})();
