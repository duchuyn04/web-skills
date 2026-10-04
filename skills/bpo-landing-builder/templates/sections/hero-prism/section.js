/* hero-prism: prism-headline-3d. The prism turns 120 degrees every dwell (2.4-3.2 s, seeded) plus a 0.9 s turn.
   With more than three phrases, the face that is about to come round gets the next phrase while it is still
   turned away. Two full passes, then it rests on the first phrase. The page-wide Pause switch holds it and Play
   resumes it; reduced motion shows the phrases as plain text. The prism line is scaled once to fit its column. */
(function () {
  var BL = window.BL;
  document.querySelectorAll('[data-hprism]').forEach(function (sec) {
    if (!BL || !BL.stage3d) return;
    var st = BL.stage3d(sec), rnd = st.rnd;
    var rig = sec.querySelector('[data-prism-rig]'), line = sec.querySelector('[data-prism-line]');
    var sizer = sec.querySelector('[data-prism-sizer]');
    var faces = [].slice.call(sec.querySelectorAll('[data-face]'));
    var items = [].slice.call(sec.querySelectorAll('[data-prism-item]'));
    var phrases = [].map.call(sizer.children, function (el) { return el.textContent; });
    var N = phrases.length, TURN = 900;
    var sign = parseFloat(sec.style.getPropertyValue('--sign')) < 0 ? -1 : 1;
    var dwell = Math.round(2400 + rnd() * 800);
    sec.style.setProperty('--dwell', (dwell + TURN) + 'ms');
    sec.style.setProperty('--shade', (0.32 + rnd() * 0.2).toFixed(2));
    if (rnd() < 0.35) sec.classList.add('bl-hprism--ink');

    function fit() {
      line.style.setProperty('--pscale', '1');
      var avail = line.parentNode.clientWidth, w = sizer.getBoundingClientRect().width;
      if (w > avail && w > 0) line.style.setProperty('--pscale', (avail / w * 0.99).toFixed(3));
    }
    fit();
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(fit);
    var rz = 0;
    window.addEventListener('resize', function () { clearTimeout(rz); rz = setTimeout(fit, 120); });

    if (BL.RM || N < 3 || !BL.gsap) return;
    var s = 0, total = 2 * N, timer = 0, done = false;
    function mark(k) { items.forEach(function (el, i) { el.classList.toggle('is-on', i === k); }); }
    function turn() {
      timer = 0;
      if (st.paused || done) return;
      if (document.documentElement.classList.contains('bl-shot')) { timer = BL.gsap.delayedCall(dwell / 1000, turn); return; }
      s++;
      var f = s % 3;
      faces[f].textContent = phrases[s % N];
      faces.forEach(function (el, i) { el.classList.toggle('is-front', i === f); });
      rig.style.setProperty('--turn', (-s * 120 * sign) + 'deg');
      mark(s % N);
      if (s >= total) { done = true; sec.classList.remove('is-running'); return; }
      timer = BL.gsap.delayedCall((dwell + TURN) / 1000, turn);
    }
    function run() {
      if (done || st.paused || timer) return;
      sec.classList.add('is-running');
      timer = BL.gsap.delayedCall((dwell + TURN) / 1000, turn);
    }
    BL.onVisible(sec, run, 0.3);
    st.onMotion(function (paused) {
      if (paused) { if (timer) timer.kill(); timer = 0; sec.classList.remove('is-running'); }
      else run();
    });
  });
})();
