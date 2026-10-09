/* process-drop: tilted-card-drop, step-counter-roll.
   Every card gets a tilt (2-7 deg, alternating sides) and a small offset seeded from the brand name, so the pile
   looks different for each client. Wide screens with motion: the block pins under the header for about 70% of a
   screen of scrolling per step; each next card falls from above the screen with extra spin, settles on the pile at its
   own tilt and nudges the card below; the counter rolls to the card on top (GSAP timeline, scrub). Phones, tablets
   and reduced motion: the list stays in place, each card slightly tilted. .bl-shot (QA element shots) undoes the pin. */
(function () {
  var BL = window.BL, gsap = window.gsap;
  var root = document.documentElement;
  function shot() { return root.classList.contains('bl-shot'); }
  function headerH() { return parseFloat(getComputedStyle(root).getPropertyValue('--header-h')) || 72; }
  function pad(v) { return (v < 10 ? '0' : '') + v; }
  function rng(str) {
    var h = 2166136261;
    for (var i = 0; i < str.length; i++) { h ^= str.charCodeAt(i); h = Math.imul(h, 16777619); }
    return function () {
      h += 0x6D2B79F5;
      var t = Math.imul(h ^ (h >>> 15), 1 | h);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  document.querySelectorAll('[data-pdrop]').forEach(function (sec) {
    var pin = sec.querySelector('[data-pd-pin]');
    var cards = [].slice.call(sec.querySelectorAll('[data-pd-card]'));
    var digits = sec.querySelector('[data-pd-digits]');
    var total = sec.querySelector('[data-pd-total]');
    var n = cards.length;
    if (!pin || n < 2) return;
    if (total) total.textContent = ' / ' + pad(n);

    var rnd = rng(sec.getAttribute('data-seed') || 'pile');
    var side = rnd() < 0.5 ? -1 : 1;
    var pose = cards.map(function (c, i) {
      var p = { tilt: side * (i % 2 ? -1 : 1) * (2 + rnd() * 5), x: (rnd() - 0.5) * 28, y: (rnd() - 0.5) * 20 };
      c.style.setProperty('--pd-tilt', p.tilt.toFixed(2) + 'deg');
      return p;
    });
    function setActive(i) { if (digits) digits.style.setProperty('--pd-active', String(i)); }

    if (!BL || !gsap || !window.ScrollTrigger) return;
    BL.motion.media(function (reduce) {
      if (reduce) return;
      var mm = gsap.matchMedia();
      mm.add('(min-width: 1024px)', function () {
        if (shot()) return;
        sec.classList.add('is-pinned');
        var fall = function () { return -(window.innerHeight * 0.95); };
        gsap.set(cards[0], { x: pose[0].x, y: pose[0].y, rotation: pose[0].tilt });
        /* the counter follows the timeline itself, so it keeps up while the scrub catches up with the scroll */
        var tl = gsap.timeline({
          defaults: { ease: 'none' },
          onUpdate: function () { setActive(Math.max(0, Math.min(n - 1, Math.floor(tl.time() + 0.7)))); },
          scrollTrigger: {
            trigger: pin, pin: pin, start: function () { return 'top top+=' + headerH(); },
            end: function () { return '+=' + Math.round(window.innerHeight * 0.7 * (n - 1) + window.innerHeight * 0.3); },
            scrub: 0.5, invalidateOnRefresh: true
          }
        });
        for (var i = 1; i < n; i++) {
          var p = pose[i], at = i - 1, spin = (p.tilt < 0 ? -1 : 1) * 16;
          tl.fromTo(cards[i], { x: p.x * 3, y: fall, rotation: p.tilt + spin, opacity: 0 },
            { x: p.x, y: p.y, rotation: p.tilt, duration: 1, ease: 'power3.out', immediateRender: true }, at);
          tl.to(cards[i], { opacity: 1, duration: 0.18 }, at);
          tl.to(cards[i - 1], { rotation: pose[i - 1].tilt - spin * 0.08, duration: 0.3, ease: 'power2.out' }, at + 0.7);
        }
        tl.to({}, { duration: 0.35 });
        setActive(0);
        return function () { sec.classList.remove('is-pinned'); setActive(0); };
      });
      var onShot = function () { if (shot()) mm.revert(); };
      window.addEventListener('resize', onShot);
      return function () { window.removeEventListener('resize', onShot); mm.revert(); };
    });
  });
})();
