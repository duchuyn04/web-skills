/* card-tilt-3d-perspective: pointer-driven, fine pointers only */
(function () {
  if (!window.BL.FINE || window.BL.RM) return;
  document.querySelectorAll('[data-tilt]').forEach(function (card) {
    var raf = 0, ev = null;
    card.addEventListener('pointermove', function (e) {
      ev = e;
      if (raf) return;
      raf = requestAnimationFrame(function () {
        raf = 0;
        var r = card.getBoundingClientRect();
        var px = (ev.clientX - r.left) / r.width, py = (ev.clientY - r.top) / r.height;
        card.classList.add('is-tilting');
        card.style.setProperty('--ry', ((px - 0.5) * 12).toFixed(2) + 'deg');
        card.style.setProperty('--rx', ((0.5 - py) * 12).toFixed(2) + 'deg');
      });
    });
    card.addEventListener('pointerleave', function () {
      card.classList.remove('is-tilting');
      card.style.setProperty('--rx', '0deg');
      card.style.setProperty('--ry', '0deg');
    });
  });
})();
