/* news-cards-slide-in: the list card, then the feature card, slide in from the right once (0.45 s each).
   Reduced motion or no GSAP: the cards are shown in place. */
(function () {
  document.querySelectorAll('[data-hero-news]').forEach(function (sec) {
    var cards = [].slice.call(sec.querySelectorAll('[data-hnews-card]'));
    if (!cards.length) return;
    function show() { cards.forEach(function (c) { c.classList.add('is-in'); c.style.opacity = ''; }); }
    var gsap = window.BL && window.BL.gsap;
    if (!gsap || window.BL.RM) { show(); return; }
    window.BL.onVisible(sec, function () {
      cards.forEach(function (card, i) {
        card.classList.add('is-in');
        gsap.fromTo(card, { opacity: 0, x: 48 }, {
          opacity: 1, x: 0, duration: 0.45, ease: window.BL.motion.ease, delay: 0.25 + i * 0.15,
          clearProps: 'opacity,transform'
        });
      });
    }, 0.1);
  });
})();
