/* sticky-sidebar-process-scroll: fill the line to the viewport midpoint, light passed steps */
(function () {
  var lists = document.querySelectorAll('[data-process]');
  if (!lists.length) return;
  var ticking = false;
  function sync() {
    ticking = false;
    var mid = window.innerHeight * 0.55;
    lists.forEach(function (list) {
      var r = list.getBoundingClientRect();
      var p = Math.max(0, Math.min(1, (mid - r.top) / r.height));
      list.style.setProperty('--progress', p.toFixed(3));
      list.querySelectorAll('.bl-step').forEach(function (step) {
        step.classList.toggle('is-passed', step.getBoundingClientRect().top < mid);
      });
    });
  }
  window.addEventListener('scroll', function () { if (!ticking) { ticking = true; requestAnimationFrame(sync); } }, { passive: true });
  window.addEventListener('resize', sync);
  sync();
})();
