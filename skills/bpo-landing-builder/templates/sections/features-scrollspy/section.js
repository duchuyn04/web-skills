/* features-scrollspy: the row crossing the reading line (45% of the screen height) lights up, the dot slides to it and
   the sticky panel cross-fades to its photo. The state reports where the reader is, so it follows the scroll under
   reduced motion too (one ScrollTrigger per list, no tween; CSS drops the transitions). Clicking a row scrolls it to
   the reading line. */
(function () {
  document.querySelectorAll('[data-sspy]').forEach(function (sec) {
    var items = [].slice.call(sec.querySelectorAll('[data-sspy-item]'));
    var panes = [].slice.call(sec.querySelectorAll('[data-sspy-pane]'));
    var dot = sec.querySelector('[data-sspy-dot]');
    var wide = window.matchMedia('(min-width: 861px)');
    var LINE = 0.45, cur = -1;

    function set(i) {
      if (i === cur) return;
      cur = i;
      items.forEach(function (it, k) {
        it.classList.toggle('is-on', k === i);
        it.querySelector('[data-sspy-row]').setAttribute('aria-current', k === i ? 'true' : 'false');
      });
      panes.forEach(function (p, k) { p.classList.toggle('is-on', k === i); });
      var row = items[i].querySelector('[data-sspy-row]');
      dot.style.setProperty('--dot-y', (items[i].offsetTop + row.offsetHeight / 2 - 5) + 'px');
      dot.style.setProperty('--dot-o', '1');
    }
    function sync() {
      if (!wide.matches) return;
      var line = window.innerHeight * LINE, pick = 0;
      items.forEach(function (it, k) { if (it.getBoundingClientRect().top <= line) pick = k; });
      set(pick);
    }
    items.forEach(function (it, k) {
      it.querySelector('[data-sspy-row]').addEventListener('click', function () {
        if (!wide.matches) return;
        var r = it.getBoundingClientRect();
        var y = window.scrollY + r.top - window.innerHeight * LINE + 2;
        window.scrollTo({ top: y, behavior: window.BL && window.BL.RM ? 'auto' : 'smooth' });
        set(k);
      });
    });
    /* photos load as the section nears, so a cross-fade never lands on an empty frame */
    if (window.BL) window.BL.onVisible(sec, function () { sec.querySelectorAll('img').forEach(function (im) { im.loading = 'eager'; }); }, 0);
    if (window.ScrollTrigger) window.ScrollTrigger.create({ trigger: sec, start: 'top bottom', end: 'bottom top', onUpdate: sync, onRefresh: sync });
    else { window.addEventListener('scroll', sync, { passive: true }); window.addEventListener('resize', sync); }
    set(0);
    cur = -1;
    sync();
  });
})();
