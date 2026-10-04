/* Hero 'spotlight': links inside a slide are reachable by keyboard only while that slide is shown. */
(function () {
  var slides = document.querySelectorAll('.spot-slide'); if (!slides.length) return;
  function sync() {
    Array.prototype.forEach.call(slides, function (s) {
      var on = s.classList.contains('is-active');
      Array.prototype.forEach.call(s.querySelectorAll('a'), function (a) { if (on) a.removeAttribute('tabindex'); else a.setAttribute('tabindex', '-1'); });
    });
  }
  var mo = new MutationObserver(sync);
  Array.prototype.forEach.call(slides, function (s) { mo.observe(s, { attributes: true, attributeFilter: ['class'] }); });
  sync();
})();
