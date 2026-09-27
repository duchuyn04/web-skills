/* metrics-rings: draw each ring once when it is seen (the number counts up through base.js data-count) */
(function () {
  document.querySelectorAll('[data-ring]').forEach(function (ring) {
    var BL = window.BL || {};
    if (BL.RM || !BL.onVisible) { ring.classList.add('is-drawn'); return; }
    BL.onVisible(ring, function () { requestAnimationFrame(function () { ring.classList.add('is-drawn'); }); }, 0.4);
  });
})();
