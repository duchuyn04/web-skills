/* hero-scatter: scatter-grow-in (the photos grow from 82% and fade in one after another, 0.9 s, 90 ms apart),
   scatter-depth-drift (wide screens: while the hero scrolls away each photo rises by its own depth, so near photos move
   more than far ones; fine pointers: the photos lean up to 10 px toward the pointer, again by depth).
   Reduced motion: none of it runs. No loops. */
(function () {
  var BL = window.BL, gsap = window.gsap;
  if (!BL || !gsap) return;
  var DEPTH = [0.6, 1, 1.2, 0.35, 0.45, 0.5];
  document.querySelectorAll('[data-hscat]').forEach(function (sec) {
    var phs = [].slice.call(sec.querySelectorAll('[data-hscat-ph]'));
    if (!phs.length) return;
    var wide = window.matchMedia('(min-width: 901px)');
    BL.motion.media(function (reduce) {
      if (reduce) return;
      gsap.fromTo(phs, { scale: 0.82, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.9, ease: BL.motion.ease, stagger: 0.09, delay: 0.2 });
      if (!wide.matches) return;
      if (window.ScrollTrigger) {
        phs.forEach(function (ph, i) {
          gsap.to(ph, { yPercent: -18 * DEPTH[i], ease: 'none', scrollTrigger: { trigger: sec, start: 'top top', end: 'bottom top', scrub: true } });
        });
      }
      if (!BL.FINE) return;
      var movers = phs.map(function (ph, i) {
        return { x: gsap.quickTo(ph, 'x', { duration: 0.8, ease: 'power3.out' }), y: gsap.quickTo(ph, 'y', { duration: 0.8, ease: 'power3.out' }), d: DEPTH[i] };
      });
      var onMove = function (e) {
        var r = sec.getBoundingClientRect();
        var nx = (e.clientX - r.left) / r.width * 2 - 1, ny = (e.clientY - r.top) / r.height * 2 - 1;
        movers.forEach(function (m) { m.x(nx * 10 * m.d); m.y(ny * 10 * m.d); });
      };
      var onLeave = function () { movers.forEach(function (m) { m.x(0); m.y(0); }); };
      sec.addEventListener('pointermove', onMove);
      sec.addEventListener('pointerleave', onLeave);
      return function () { sec.removeEventListener('pointermove', onMove); sec.removeEventListener('pointerleave', onLeave); };
    });
  });
})();
