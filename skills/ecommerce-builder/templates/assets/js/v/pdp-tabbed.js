/* PDP 'tabbed': marks the tab of the section being read and shows the buy strip in the tab bar once the buy box has scrolled away. */
(function () {
  var bar = document.querySelector('[data-tabbar]'); if (!bar) return;
  var tabs = Array.prototype.slice.call(bar.querySelectorAll('[data-tab]'));
  var secs = tabs.map(function (t) { return document.getElementById(t.dataset.tab); });
  var mini = bar.querySelector('[data-buybar]');
  var buy = document.querySelector('.pdt-buy .buybox');
  var reduce = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
  function mark() {
    var line = bar.getBoundingClientRect().bottom + 24, cur = 0;
    secs.forEach(function (s, i) { if (s && s.getBoundingClientRect().top <= line) cur = i; });
    // at the very bottom the last section wins even when it is short
    if (window.innerHeight + window.scrollY >= document.documentElement.scrollHeight - 4) cur = tabs.length - 1;
    tabs.forEach(function (t, i) { if (i === cur && bar.getBoundingClientRect().top <= 80) t.setAttribute('aria-current', 'true'); else t.removeAttribute('aria-current'); });
  }
  tabs.forEach(function (t) {
    t.addEventListener('click', function (e) {
      var s = document.getElementById(t.dataset.tab); if (!s) return;
      e.preventDefault();
      s.scrollIntoView({ behavior: reduce ? 'auto' : 'smooth', block: 'start' });
      if (history.replaceState) history.replaceState(null, '', '#' + t.dataset.tab);
    });
  });
  if (mini && buy && 'IntersectionObserver' in window) {
    new IntersectionObserver(function (en) { mini.classList.toggle('is-on', !en[0].isIntersecting && en[0].boundingClientRect.top < 0); }, { threshold: 0 }).observe(buy);
  }
  var tick = false;
  window.addEventListener('scroll', function () { if (tick) return; tick = true; requestAnimationFrame(function () { tick = false; mark(); }); }, { passive: true });
  mark();
})();
