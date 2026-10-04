/* PDP 'compact': the gallery is a swipe strip, so a colour choice (store.js marks the matching dot) scrolls to its picture,
   swiping updates the dots, and links to #reviews, #specs, #qa open the collapsible section they point to. */
(function () {
  var g = document.querySelector('.pdc-swipe'); if (!g) return;
  var imgs = Array.prototype.slice.call(g.querySelectorAll('[data-gallery-img]'));
  var dots = Array.prototype.slice.call(document.querySelectorAll('.pdc-dots [data-gallery-thumb]'));
  var reduce = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
  var lock = false;
  function to(i) {
    if (!imgs[i]) return;
    lock = true;
    g.scrollTo({ left: imgs[i].offsetLeft - g.offsetLeft, behavior: reduce ? 'auto' : 'smooth' });
    setTimeout(function () { lock = false; }, 450);
  }
  // store.js writes aria-selected on the dots when a colour is chosen or a dot is pressed
  var mo = new MutationObserver(function () {
    var i = dots.findIndex(function (d) { return d.getAttribute('aria-selected') === 'true'; });
    var cur = Math.round(g.scrollLeft / Math.max(1, g.clientWidth));
    if (i >= 0 && i !== cur && !lock) to(i);
  });
  dots.forEach(function (d) { mo.observe(d, { attributes: true, attributeFilter: ['aria-selected'] }); });
  var settle;
  g.addEventListener('scroll', function () {
    if (lock) return;
    clearTimeout(settle);
    // once the swipe stops, press the dot so store.js keeps its own index (prev and next buttons) in step
    settle = setTimeout(function () {
      var i = Math.round(g.scrollLeft / Math.max(1, g.clientWidth));
      if (dots[i] && dots[i].getAttribute('aria-selected') !== 'true') dots[i].click();
    }, 120);
  }, { passive: true });
  function openFor(id) {
    var el = id && document.getElementById(id);
    if (el && el.tagName === 'DETAILS') { el.open = true; setTimeout(function () { el.scrollIntoView({ behavior: reduce ? 'auto' : 'smooth', block: 'start' }); }, 30); }
  }
  document.addEventListener('click', function (e) {
    var a = e.target.closest('a[href^="#"]'); if (!a) return;
    var id = a.getAttribute('href').slice(1);
    if (document.getElementById(id) && document.getElementById(id).tagName === 'DETAILS') { e.preventDefault(); openFor(id); }
  });
  if (location.hash) openFor(location.hash.slice(1));
})();
