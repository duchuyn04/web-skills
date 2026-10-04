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
    var active = 0;
    list.querySelectorAll('.bl-step').forEach(function (step, i) {
      var passed = step.getBoundingClientRect().top < mid;
      step.classList.toggle('is-passed', passed);
      if (passed) active = i;
    });
    /* step-photo-crossfade: the pinned frame shows the photo of the step being read (the last one with a photo) */
    var shots = list.__shots;
    if (shots && shots.length) {
      var pick = null;
      shots.forEach(function (s) { if (+s.getAttribute('data-step-shot') <= active) pick = s; });
      pick = pick || shots[0];
      shots.forEach(function (s) { s.classList.toggle('is-active', s === pick); });
    }
  }
  lists.forEach(function (list) {
    var box = list.closest('.bl-process');
    list.__shots = box ? [].slice.call(box.querySelectorAll('[data-step-shot]')) : [];
    var run = function () { sync(list); };
    if (window.ScrollTrigger) window.ScrollTrigger.create({ trigger: list, start: 'top bottom', end: 'bottom top', onUpdate: run, onRefresh: run });
    else { window.addEventListener('scroll', run, { passive: true }); window.addEventListener('resize', run); }
    run();
  });
})();
