/* hero-overlap: photo-settle-zoom (1.06 to 1 once), heading-word-rise (words rise once), photo-scroll-drift (the photo
   moves a little slower than the page while the hero scrolls away). The card rises with the page reveal.
   Reduced motion: none of it runs, the hero shows at rest. No loops. */
(function () {
  var BL = window.BL, gsap = window.gsap;
  if (!BL || !gsap) return;
  document.querySelectorAll('[data-hovl]').forEach(function (sec) {
    var img = sec.querySelector('[data-hovl-img]');
    var pan = sec.querySelector('[data-hovl-pan]');
    var title = sec.querySelector('[data-hovl-title]');
    var stage = sec.querySelector('.bl-hovl__stage');
    BL.motion.media(function (reduce) {
      if (reduce) return;
      var parts = title ? BL.motion.split(title, 'words') : null;
      if (img) gsap.fromTo(img, { scale: 1.06 }, { scale: 1, duration: 1.6, ease: BL.motion.ease, clearProps: 'transform' });
      if (parts && parts.targets.length) {
        gsap.fromTo(parts.targets, { yPercent: 110 }, { yPercent: 0, duration: 0.6, ease: BL.motion.ease, stagger: 0.05, delay: 0.1, clearProps: 'transform' });
      }
      if (pan && stage && window.ScrollTrigger) {
        gsap.fromTo(pan, { yPercent: 0 }, {
          yPercent: 9, ease: 'none',
          scrollTrigger: { trigger: stage, start: 'top top', end: 'bottom top', scrub: true }
        });
      }
    });
  });
})();
