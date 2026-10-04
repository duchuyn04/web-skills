/* hero-deck: role-deck-fan-3d. The deck fans out once when the hero is seen. Then the front card goes to the back
   every 2.8 s until the first role is in front again (one full round, 4-7 steps), and the deck rests. The page-wide
   Pause switch, keyboard focus inside the deck and the Next role button stop the round for good (APG carousel);
   hovering the deck holds it. Card tints are seeded from the brand name. Reduced motion: static fan, Next still works. */
(function () {
  var BL = window.BL;
  function pad(v) { return (v < 10 ? '0' : '') + v; }
  document.querySelectorAll('[data-hdeck]').forEach(function (sec) {
    if (!BL || !BL.stage3d || !BL.gsap) return;
    var st = BL.stage3d(sec), rnd = st.rnd;
    var cards = [].slice.call(sec.querySelectorAll('[data-card]'));
    var n = cards.length;
    if (n < 2) return;
    var visual = sec.querySelector('.bl-hdeck__visual');
    var stage = sec.querySelector('.bl-hdeck__stage');
    var pos = sec.querySelector('[data-deck-pos]'), total = sec.querySelector('[data-deck-total]');
    var live = sec.querySelector('[data-deck-live]'), next = sec.querySelector('[data-deck-next]');
    var order = cards.slice();

    /* three tints: plain, a contrasting tone (dark on a light hero, brand colour on a dark one) and a light accent
       wash; the brand picks where the cycle starts */
    var dark = !sec.classList.contains('bl-tone-light') && !sec.classList.contains('bl-tone-muted');
    var off = Math.floor(rnd() * 3);
    cards.forEach(function (c, i) {
      var t = (i + off) % 3;
      c.classList.add('is-t' + t);
      if (t === 1) c.querySelector('.bl-hdeck__face').classList.add(dark ? 'bl-tone-accent' : 'bl-tone-dark');
    });
    if (total) total.textContent = ' / ' + pad(n);
    /* keep the whole fan within about 30 degrees, whatever the number of roles */
    sec.style.setProperty('--fan-fit', Math.min(1, 4 / (n - 1)).toFixed(3));

    function place() {
      order.forEach(function (c, s) { c.style.setProperty('--slot', String(s)); });
      if (pos) pos.textContent = pad(cards.indexOf(order[0]) + 1);
    }
    place();

    var busy = false;
    function step(announce) {
      if (busy) return;
      busy = true;
      var f = order.shift();
      order.push(f);
      if (pos) pos.textContent = pad(cards.indexOf(order[0]) + 1);
      if (announce && live) live.textContent = order[0].getAttribute('aria-label');
      if (BL.RM) { place(); busy = false; return; }
      f.classList.add('is-out');
      order.forEach(function (c, s) { if (c !== f) c.style.setProperty('--slot', String(s)); });
      BL.gsap.delayedCall(0.48, function () {
        f.classList.add('is-jump');
        f.classList.remove('is-out');
        f.style.setProperty('--slot', String(n - 1));
        void f.offsetWidth;
        f.classList.remove('is-jump');
        busy = false;
      });
    }

    /* the round is a repeating GSAP tween registered with BL.motion.ambient; stop() kills it for good */
    var timer = null, steps = 0, stopped = false, hover = false;
    function stop() { stopped = true; if (timer) timer.kill(); timer = null; }
    function start() {
      if (stopped || st.paused || BL.RM || timer) return;
      timer = BL.motion.ambient(BL.gsap.to({}, { duration: 2.8, repeat: -1, onRepeat: function () {
        if (hover || busy || document.documentElement.classList.contains('bl-shot')) return;
        if (st.paused) { stop(); return; }
        step(false);
        if (++steps >= n) stop();
      } }));
    }
    function fan() { sec.classList.add('is-fanned'); BL.gsap.delayedCall(0.9, start); }
    if (BL.RM) fan(); else BL.onVisible(sec, fan, 0.2);

    next.addEventListener('click', function () { stop(); step(true); });
    visual.addEventListener('focusin', stop);
    stage.addEventListener('pointerenter', function () { hover = true; });
    stage.addEventListener('pointerleave', function () { hover = false; });
    st.onMotion(function (paused) { if (paused) stop(); });
  });
})();
