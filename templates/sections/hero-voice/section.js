/* hero-voice: multilingual-greeting-card and voice-level-meter. Every 3.6 s the call card answers in the next language:
   the greeting fades up, its chip lights, and the level meter moves for about 2 s while it "speaks", then rests.
   One GSAP timeline, registered as ambient so Pause animations stops it; reduced motion shows the first greeting still. */
(function () {
  var BL = window.BL, gsap = window.gsap;
  document.querySelectorAll('[data-hvoice]').forEach(function (sec) {
    var card = sec.querySelector('[data-hvoice-call]');
    if (!card || !BL || !gsap) return;
    var list;
    try { list = JSON.parse(card.getAttribute('data-greetings')) || []; } catch (e) { list = []; }
    var text = card.querySelector('[data-hvoice-text]');
    var lang = card.querySelector('[data-hvoice-lang]');
    var bars = [].slice.call(card.querySelectorAll('[data-hvoice-meter] i'));
    var chips = [].slice.call(sec.querySelectorAll('[data-hvoice-chip]'));
    var i = 0;
    function light(k) { chips.forEach(function (c, n) { c.classList.toggle('is-on', n === k); }); }
    light(0);
    if (list.length < 2) return;

    /* speech-like levels: a slow envelope times a fast jitter, seeded per bar so it never looks like a uniform pulse */
    function speak(tl, at, dur) {
      var steps = Math.round(dur / 0.14);
      bars.forEach(function (b, n) {
        var sub = gsap.timeline();
        for (var s = 0; s < steps; s++) {
          var env = Math.sin(Math.PI * (s + 1) / (steps + 1));
          var jit = 0.35 + 0.65 * Math.abs(Math.sin(n * 1.7 + s * 2.3) * Math.cos(n * 0.6 - s * 1.1));
          sub.to(b, { scaleY: Math.max(0.12, env * jit), duration: 0.14, ease: 'sine.inOut' });
        }
        sub.to(b, { scaleY: 0.18, duration: 0.3, ease: 'power2.out' });
        tl.add(sub, at);
      });
    }

    BL.motion.media(function (reduce) {
      if (reduce) return;
      var tl = gsap.timeline({ repeat: -1, delay: 1.2 });
      list.forEach(function (g, k) {
        var at = k * 3.6;
        tl.to([text, lang], { opacity: 0, y: -6, duration: 0.25, ease: 'power2.in' }, at);
        tl.call(function () { text.textContent = g.text; lang.textContent = g.language; light(k); }, null, at + 0.25);
        tl.fromTo([text, lang], { opacity: 0, y: 8 }, { opacity: 1, y: 0, duration: 0.4, ease: 'expo.out' }, at + 0.26);
        speak(tl, at + 0.35, 2.1);
      });
      tl.to({}, { duration: 0.01 }, list.length * 3.6 - 0.01);
      BL.motion.ambient(tl);
      return function () { tl.kill(); text.textContent = list[0].text; lang.textContent = list[0].language; light(0); gsap.set([text, lang], { clearProps: 'opacity,transform' }); gsap.set(bars, { clearProps: 'transform' }); };
    });
  });
})();
