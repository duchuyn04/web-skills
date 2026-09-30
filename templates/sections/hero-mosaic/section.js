/* hero-mosaic: tinted-photo-mosaic (tiles fade in from the centre on load), mosaic-row-drift (alternate rows slide
   sideways in opposite directions while the hero scrolls away). One-shot and scroll-linked only, no time loop;
   under reduced motion the wall stays still. */
(function () {
  if (!window.BL || !window.BL.motion) return;
  document.querySelectorAll('[data-hero-mosaic]').forEach(function (sec) {
    var grid = sec.querySelector('[data-mosaic-grid]');
    if (!grid) return;
    var all = Array.prototype.slice.call(grid.children);
    /* the photo list is repeated to fill the wall; when the column count divides it, every column shows one photo,
       so take one column more */
    var photos = all.length / 6;
    var cols = parseInt(getComputedStyle(grid).getPropertyValue('--cols'), 10) || 7;
    if (photos % cols === 0) grid.style.setProperty('--cols', String(++cols));
    /* whole rows only, so the tilted wall has no ragged corner */
    var shown = all.filter(function (t) { return getComputedStyle(t).display !== 'none'; }).length;
    var keep = Math.floor(shown / cols) * cols;
    all.forEach(function (t, i) { if (i >= keep) t.classList.add('is-extra'); });
    var tiles = all.slice(0, keep);
    window.BL.motion.media(function (reduce) {
      var gsap = window.BL.gsap;
      if (reduce || !gsap) return;
      var intro = gsap.fromTo(tiles, { opacity: 0, scale: 0.94 }, {
        opacity: 1, scale: 1, duration: 0.5, ease: window.BL.motion.ease, stagger: { each: 0.02, from: 'center' }
      });
      var drift = null;
      if (window.ScrollTrigger) {
        var cols = getComputedStyle(grid).gridTemplateColumns.split(' ').length || 5;
        var even = tiles.filter(function (t, i) { return Math.floor(i / cols) % 2 === 0; });
        var odd = tiles.filter(function (t, i) { return Math.floor(i / cols) % 2 === 1; });
        drift = gsap.timeline({ scrollTrigger: { trigger: sec, start: 'top top', end: 'bottom top', scrub: 0.6 } });
        drift.to(even, { xPercent: -12, ease: 'none' }, 0).to(odd, { xPercent: 12, ease: 'none' }, 0);
      }
      return function () {
        intro.kill();
        if (drift) { if (drift.scrollTrigger) drift.scrollTrigger.kill(); drift.kill(); }
        gsap.set(tiles, { clearProps: 'opacity,transform' });
      };
    });
  });
})();
