/* locations-fan: photo-stack-fan-in. When a card comes into view its two back photos slide out from behind the front
   one (0.9s, the length measured on Cosmos; power2.out), 120ms later per card. GSAP moves them with
   xPercent, which sits on top of the resting CSS translate and is cleared afterwards, so the hover gather in
   section.css keeps working. Reduced motion: the cards rest in their final layout. */
(function () {
  var BL = window.BL;
  if (!BL || !BL.gsap) return;
  var gsap = BL.gsap;
  document.querySelectorAll('[data-locfan]').forEach(function (list) {
    var cards = [].slice.call(list.children);
    BL.motion.media(function (reduce) {
      if (reduce) return;
      cards.forEach(function (card, i) {
        var left = card.querySelector('.bl-locfan__ph--2');
        var right = card.querySelector('.bl-locfan__ph--3');
        var front = card.querySelector('.bl-locfan__ph--1');
        if (!left || !right) return;
        gsap.set(left, { xPercent: 54 });
        gsap.set(right, { xPercent: -54 });
        gsap.set(front, { scale: 0.94 });
        BL.onVisible(card, function () {
          var d = 0.15 + Math.min(i, 3) * 0.12;
          gsap.to([left, right], { xPercent: 0, duration: 0.9, delay: d, ease: 'power2.out', clearProps: 'transform' });
          gsap.to(front, { scale: 1, duration: 0.9, delay: d, ease: 'power2.out', clearProps: 'transform' });
        }, 0.3);
      });
      return function () { gsap.set(list.querySelectorAll('.bl-locfan__ph'), { clearProps: 'transform' }); };
    });
  });
})();
