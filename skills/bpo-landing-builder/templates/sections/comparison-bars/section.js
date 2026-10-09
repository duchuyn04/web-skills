/* comparison-bars: versus-bar-grow. Both bars of a row grow out from the centre divider (scaleX from 0, 0.9 s expo.out)
   as the row enters; rows that enter together start 120 ms apart. Reduced motion and no-JS keep the final widths. */
(function () {
  var gsap = window.gsap;
  if (!window.BL || !gsap) return;
  document.querySelectorAll('[data-cbars]').forEach(function (box) {
    var rows = [].slice.call(box.querySelectorAll('[data-cbar-row]'));
    window.BL.motion.media(function (reduce) {
      if (reduce) return;
      var next = 0;
      rows.forEach(function (row) {
        var bars = row.querySelectorAll('[data-cbar]');
        gsap.set(bars, { scaleX: 0 });
        window.BL.onVisible(row, function () {
          var now = performance.now() / 1000;
          var delay = Math.max(0, next - now);
          next = now + delay + 0.12;
          gsap.to(bars, { scaleX: 1, duration: 0.9, ease: 'expo.out', delay: delay, clearProps: 'transform' });
        }, 0.35);
      });
      return function () { rows.forEach(function (row) { gsap.set(row.querySelectorAll('[data-cbar]'), { clearProps: 'transform' }); }); };
    });
  });
})();
