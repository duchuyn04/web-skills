/* Product page 'gallery': choosing a colour brings its picture into view and marks it. */
(function () {
  var media = document.querySelector('[data-pg-media]'); if (!media) return;
  var shots = Array.prototype.slice.call(media.querySelectorAll('[data-pg-shot]'));
  function mark(name, scroll) {
    var hit = null;
    shots.forEach(function (s) { var on = s.getAttribute('data-pg-shot') === name; s.classList.toggle('is-on', on); if (on) hit = s; });
    if (hit && scroll) {
      var r = hit.getBoundingClientRect();
      if (window.innerWidth < 900) media.scrollTo({ left: hit.offsetLeft - media.offsetLeft, behavior: 'smooth' });
      else if (r.top < 80 || r.bottom > window.innerHeight) hit.scrollIntoView({ block: 'center', behavior: 'smooth' });
    }
  }
  document.addEventListener('click', function (e) {
    var b = e.target.closest('.pg-colors [data-opt-btn]');
    if (b) mark(b.getAttribute('data-opt-btn'), true);
  });
  var first = document.querySelector('.pg-colors [data-opt-btn]');
  if (first) mark(first.getAttribute('data-opt-btn'), false);
})();
