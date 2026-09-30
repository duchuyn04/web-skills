/* sticky-sidebar-process-scroll: fill the line to the viewport midpoint, light passed steps. The fill reports where
   the reader is, so it follows the scroll under reduced motion too (a ScrollTrigger per list, no tween). */
(function () {
  var lists = document.querySelectorAll('[data-process]');
  if (!lists.length) return;
  function sync(list) {
    var mid = window.innerHeight * 0.55;
    var r = list.getBoundingClientRect();
    var p = Math.max(0, Math.min(1, (mid - r.top) / r.height));
    list.style.setProperty('--progress', p.toFixed(3));
    list.querySelectorAll('.bl-step').forEach(function (step) {
      step.classList.toggle('is-passed', step.getBoundingClientRect().top < mid);
    });
  }
  lists.forEach(function (list) {
    var run = function () { sync(list); };
    if (window.ScrollTrigger) window.ScrollTrigger.create({ trigger: list, start: 'top bottom', end: 'bottom top', onUpdate: run, onRefresh: run });
    else { window.addEventListener('scroll', run, { passive: true }); window.addEventListener('resize', run); }
    run();
  });
})();
