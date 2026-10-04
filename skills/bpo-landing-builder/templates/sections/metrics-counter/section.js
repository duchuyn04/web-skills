/* photo-band-parallax: the optional band photo moves a little slower than the page (scroll-linked, no time loop).
   Under reduced motion it stays still. */
(function () {
  if (!window.BL || !window.BL.motion) return;
  document.querySelectorAll('[data-metrics-photo]').forEach(function (media) {
    var img = media.querySelector('img');
    var sec = media.closest('section');
    if (!img || !sec) return;
    window.BL.motion.media(function (reduce) {
      var gsap = window.BL.gsap;
      if (reduce || !gsap || !window.ScrollTrigger) return;
      var tw = gsap.fromTo(img, { yPercent: -6 }, {
        yPercent: 6, ease: 'none',
        scrollTrigger: { trigger: sec, start: 'top bottom', end: 'bottom top', scrub: 0.5 }
      });
      return function () {
        if (tw.scrollTrigger) tw.scrollTrigger.kill();
        tw.kill();
        gsap.set(img, { clearProps: 'transform' });
      };
    });
  });
})();
