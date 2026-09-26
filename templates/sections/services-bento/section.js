/* bento-spotlight-hover: one pointermove listener per grid, rAF throttled */
(function () {
  if (!window.BL.FINE) return;
  document.querySelectorAll('[data-spotlight]').forEach(function (grid) {
    var raf = 0, last = null;
    grid.addEventListener('pointermove', function (e) {
      last = e;
      if (raf) return;
      raf = requestAnimationFrame(function () {
        raf = 0;
        var card = last.target.closest('.bl-bento__card, [data-spot]');
        if (!card) return;
        var r = card.getBoundingClientRect();
        card.style.setProperty('--mx', (last.clientX - r.left) + 'px');
        card.style.setProperty('--my', (last.clientY - r.top) + 'px');
      });
    }, { passive: true });
  });
})();
