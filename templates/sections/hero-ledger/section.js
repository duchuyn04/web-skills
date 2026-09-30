/* hero-ledger: report-sheets-fan-in, ledger-rows-tick, trend-line-draw. One intro timeline when the hero is seen
   (sheets rise into their fan, rows fill left to right and are ticked in order, the trend line draws), then the sheets
   lean a few pixels with a fine pointer. Nothing loops. Reduced motion: the finished state, no pointer lean. */
(function () {
  var BL = window.BL, gsap = window.gsap;
  document.querySelectorAll('[data-hledger]').forEach(function (sec) {
    var visual = sec.querySelector('[data-hledger-visual]');
    var sheets = [].slice.call(sec.querySelectorAll('[data-hledger-sheet]'));
    if (!visual || !sheets.length || !BL || !gsap) return;
    var fills = sec.querySelectorAll('[data-hledger-fill]');
    var ticks = sec.querySelectorAll('[data-hledger-tick]');
    var line = sec.querySelector('[data-hledger-line]');

    BL.motion.media(function (reduce) {
      if (reduce) return;
      var len = line ? line.getTotalLength() : 0;
      gsap.set(sheets, { opacity: 0, y: 60 });
      gsap.set(fills, { scaleX: 0 });
      gsap.set(ticks, { scale: 0 });
      if (line) gsap.set(line, { strokeDasharray: len, strokeDashoffset: len });
      var tl = gsap.timeline({ paused: true, defaults: { ease: 'expo.out' } });
      tl.to(sheets.slice().reverse(), { opacity: 1, y: 0, duration: 0.9, stagger: 0.12 }, 0.2)
        .to(fills, { scaleX: 1, duration: 0.5, stagger: 0.05, ease: 'power2.out' }, 0.7)
        .to(ticks, { scale: 1, duration: 0.35, stagger: 0.07, ease: 'back.out(2)' }, 1.0);
      if (line) tl.to(line, { strokeDashoffset: 0, duration: 1.1, ease: 'power2.inOut' }, 0.9);
      BL.onVisible(visual, function () { tl.play(); }, 0.25);

      /* pointer lean: the sheets move up to 6 px, the front one most */
      var lean = null;
      if (BL.FINE) {
        var movers = sheets.map(function (s, k) {
          return { x: gsap.quickTo(s, 'x', { duration: 0.6, ease: 'power3.out' }), y: gsap.quickTo(s, 'y', { duration: 0.6, ease: 'power3.out' }), k: 1 - k * 0.3 };
        });
        lean = function (e) {
          if (tl.progress() < 1) return;
          var r = visual.getBoundingClientRect();
          var dx = (e.clientX - r.left) / r.width - 0.5, dy = (e.clientY - r.top) / r.height - 0.5;
          movers.forEach(function (m) { m.x(dx * 12 * m.k); m.y(dy * 10 * m.k); });
        };
        visual.addEventListener('pointermove', lean);
        visual.addEventListener('pointerleave', function () { movers.forEach(function (m) { m.x(0); m.y(0); }); });
      }
      return function () {
        tl.kill();
        if (lean) visual.removeEventListener('pointermove', lean);
        gsap.set(sheets, { clearProps: 'opacity,x,y' });
        gsap.set([fills, ticks], { clearProps: 'transform' });
        if (line) gsap.set(line, { clearProps: 'strokeDasharray,strokeDashoffset' });
      };
    });
  });
})();
