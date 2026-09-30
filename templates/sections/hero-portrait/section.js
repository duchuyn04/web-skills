/* hero-portrait: portrait-arc-draw (the accent arc draws once around the photo, 0.8 s), stat-sticker-pop (stickers pop
   in one after another) and chip-stagger (service chips rise in a short stagger). One-shot tweens only, no loops;
   reduced motion or no GSAP leaves everything in its final place. */
(function () {
  var BL = window.BL, gsap = window.gsap;
  if (!BL || !gsap) return;
  document.querySelectorAll('[data-hport]').forEach(function (sec) {
    var arc = sec.querySelector('[data-hport-arc]');
    var stickers = [].slice.call(sec.querySelectorAll('[data-hport-sticker]'));
    var chips = [].slice.call(sec.querySelectorAll('[data-hport-chips] li'));
    BL.motion.media(function (reduce) {
      if (reduce) return;
      var dash = arc ? parseFloat(getComputedStyle(arc).strokeDasharray) || 38 : 0;
      if (arc) gsap.set(arc, { strokeDashoffset: dash });
      gsap.set(stickers, { opacity: 0, scale: 0.86, y: 10 });
      gsap.set(chips, { opacity: 0, y: 8 });
      var tweens = [];
      BL.onVisible(sec, function () {
        if (arc) tweens.push(gsap.to(arc, { strokeDashoffset: 0, duration: 0.8, delay: 0.3, ease: 'power2.inOut' }));
        tweens.push(gsap.to(stickers, { opacity: 1, scale: 1, y: 0, duration: 0.45, delay: 0.7, stagger: 0.16, ease: 'back.out(1.6)' }));
        tweens.push(gsap.to(chips, { opacity: 1, y: 0, duration: 0.35, delay: 0.35, stagger: 0.05, ease: BL.motion.ease }));
      }, 0.05);
      return function () {
        tweens.forEach(function (t) { t.kill(); });
        gsap.set([arc].concat(stickers, chips).filter(Boolean), { clearProps: 'all' });
      };
    });
  });
})();
