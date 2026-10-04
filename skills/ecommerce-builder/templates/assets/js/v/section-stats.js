/* Section 'stats' (counters): count the leading number of each figure up once when it scrolls into view.
   The final text is already in the page; with reduced motion, or without IntersectionObserver, nothing changes.
   Only plain integers and integers with a dot as thousands separator animate ("12 cua hang", "1.200 don"). */
(function () {
  var els = Array.prototype.slice.call(document.querySelectorAll('[data-stats] [data-stat]'));
  if (!els.length || !('IntersectionObserver' in window)) return;
  if (window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  function fmt(n, grouped) { return grouped ? String(n).replace(/\B(?=(\d{3})+(?!\d))/g, '.') : String(n); }
  function run(el) {
    var full = el.textContent, m = full.match(/^(\d{1,3}(?:\.\d{3})+|\d+)([^\d,.][\s\S]*)?$/);
    if (!m) return;
    var grouped = m[1].indexOf('.') >= 0, target = parseInt(m[1].replace(/\./g, ''), 10), rest = m[2] || '';
    if (!isFinite(target) || target < 2) return;
    var start = null, dur = 900;
    el.setAttribute('aria-label', full);
    function step(t) {
      if (start === null) start = t;
      var p = Math.min(1, (t - start) / dur), eased = 1 - Math.pow(1 - p, 3);
      el.textContent = fmt(Math.round(target * eased), grouped) + rest;
      if (p < 1) requestAnimationFrame(step); else { el.textContent = full; el.removeAttribute('aria-label'); }
    }
    el.textContent = fmt(0, grouped) + rest;
    requestAnimationFrame(step);
  }
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) { if (e.isIntersecting) { io.unobserve(e.target); run(e.target); } });
  }, { threshold: 0.4 });
  els.forEach(function (el) { io.observe(el); });
})();
