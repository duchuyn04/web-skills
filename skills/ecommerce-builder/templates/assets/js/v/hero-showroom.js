/* Hero 'showroom': keyboard reaches only the shown banner's links, pictures follow the pointer, the progress bar
   restarts whenever store.js restarts its timer, and the tab strip scrolls itself (not the page) to the chosen tab. */
(function () {
  var stage = document.querySelector('[data-hs-stage]'); if (!stage) return;
  var slides = stage.querySelectorAll('.hs-slide');
  var strip = document.querySelector('.hs-tabs');
  var reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  function each(list, fn) { Array.prototype.forEach.call(list, fn); }

  function syncLinks() {
    each(slides, function (s) {
      var on = s.classList.contains('is-active');
      each(s.querySelectorAll('a'), function (a) { if (on) a.removeAttribute('tabindex'); else a.setAttribute('tabindex', '-1'); });
    });
  }
  var mo = new MutationObserver(syncLinks);
  each(slides, function (s) { mo.observe(s, { attributes: true, attributeFilter: ['class'] }); });
  syncLinks();

  if (!reduce) {
    stage.addEventListener('pointermove', function (e) {
      if (e.pointerType !== 'mouse') return;
      var r = stage.getBoundingClientRect();
      stage.style.setProperty('--px', (((e.clientX - r.left) / r.width) * 2 - 1).toFixed(3));
      stage.style.setProperty('--py', (((e.clientY - r.top) / r.height) * 2 - 1).toFixed(3));
    });
    stage.addEventListener('pointerleave', function () { stage.style.setProperty('--px', 0); stage.style.setProperty('--py', 0); });
  }

  if (!strip) return;
  // store.js starts a full interval again when the pointer or focus leaves; the bar starts over with it.
  function restartBar() {
    var bar = strip.querySelector('[aria-selected="true"] .hs-bar'); if (!bar) return;
    bar.style.animation = 'none'; void bar.offsetWidth; bar.style.animation = '';
  }
  stage.addEventListener('mouseleave', restartBar);
  stage.addEventListener('focusout', function (e) { if (!stage.contains(e.relatedTarget)) restartBar(); });
  // scrollIntoView would also scroll the page and pull a reader further down back to the top
  var tabObserver = new MutationObserver(function () {
    var tab = strip.querySelector('[aria-selected="true"]'); if (!tab) return;
    var start = tab.offsetLeft, end = start + tab.offsetWidth;
    if (start < strip.scrollLeft) strip.scrollTo({ left: start, behavior: reduce ? 'auto' : 'smooth' });
    else if (end > strip.scrollLeft + strip.clientWidth) strip.scrollTo({ left: end - strip.clientWidth, behavior: reduce ? 'auto' : 'smooth' });
  });
  each(strip.querySelectorAll('[role="tab"]'), function (t) { tabObserver.observe(t, { attributes: true, attributeFilter: ['aria-selected'] }); });
})();
