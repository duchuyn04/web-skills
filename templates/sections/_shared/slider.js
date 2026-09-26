/* Shared slider (case-slider, image-cards layout "slider"): native scroll-snap, mouse drag with momentum, prev/next buttons */
(function () {
  document.querySelectorAll('[data-slider]').forEach(function (root) {
    var track = root.querySelector('[data-slider-track]');
    var prev = root.querySelector('[data-slider-prev]');
    var next = root.querySelector('[data-slider-next]');
    if (!track) return;
    var cards = Array.prototype.slice.call(track.children);
    var smooth = window.BL.RM ? 'auto' : 'smooth';

    function step() { return cards.length > 1 ? cards[1].offsetLeft - cards[0].offsetLeft : track.clientWidth; }
    function sync() {
      var max = track.scrollWidth - track.clientWidth - 2;
      if (prev) prev.disabled = track.scrollLeft <= 2;
      if (next) next.disabled = track.scrollLeft >= max;
      var vw = track.getBoundingClientRect();
      cards.forEach(function (c) {
        var r = c.getBoundingClientRect();
        c.classList.toggle('is-dim', r.right > vw.right + 8 || r.left < vw.left - 8);
      });
    }
    if (prev) prev.addEventListener('click', function () { track.scrollBy({ left: -step(), behavior: smooth }); });
    if (next) next.addEventListener('click', function () { track.scrollBy({ left: step(), behavior: smooth }); });
    track.addEventListener('scroll', function () { requestAnimationFrame(sync); }, { passive: true });
    window.addEventListener('resize', sync);
    track.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowRight') { e.preventDefault(); track.scrollBy({ left: step(), behavior: smooth }); }
      if (e.key === 'ArrowLeft') { e.preventDefault(); track.scrollBy({ left: -step(), behavior: smooth }); }
    });

    var down = false, startX = 0, startLeft = 0, lastX = 0, lastT = 0, v = 0, moved = false;
    track.addEventListener('pointerdown', function (e) {
      if (e.pointerType !== 'mouse' || e.button !== 0) return;
      down = true; moved = false; startX = lastX = e.clientX; startLeft = track.scrollLeft; lastT = performance.now(); v = 0;
    });
    window.addEventListener('pointermove', function (e) {
      if (!down) return;
      var dx = e.clientX - startX;
      if (!moved && Math.abs(dx) > 4) { moved = true; track.classList.add('is-dragging'); }
      if (!moved) return;
      var now = performance.now();
      v = (e.clientX - lastX) / Math.max(1, now - lastT);
      lastX = e.clientX; lastT = now;
      track.scrollLeft = startLeft - dx;
    });
    window.addEventListener('pointerup', function () {
      if (!down) return;
      down = false;
      if (!moved) return;
      var target = track.scrollLeft - v * 280;
      track.classList.remove('is-dragging');
      var s = step();
      track.scrollTo({ left: Math.round(target / s) * s, behavior: smooth });
    });
    track.addEventListener('click', function (e) { if (moved) { e.preventDefault(); e.stopPropagation(); moved = false; } }, true);
    sync();
  });
})();
