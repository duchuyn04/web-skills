/* hero-dashboard: dashboard-explode-3d. When the hero is seen, the unit swings to a three-quarter pose and the panels
   lift to seeded depths (one-shot, 1.6 s with an 80 ms stagger). Afterwards a fine pointer orbits the camera a few
   degrees; the loop runs only while the pose is still catching up with the pointer. Reduced motion shows the final
   pose at once and no orbit. */
(function () {
  var BL = window.BL;
  document.querySelectorAll('[data-hdash]').forEach(function (sec) {
    if (!BL || !BL.stage3d) return;
    var st = BL.stage3d(sec), rnd = st.rnd;
    var rig = sec.querySelector('[data-hdash-rig]');
    var stage = rig.parentNode;
    var lifted = [].slice.call(sec.querySelectorAll('[data-slot="queue"], [data-slot="kpi"]'));

    /* seeded layer order: shuffle the depth ranks, then put the service panel on top or at the bottom */
    var ranks = lifted.map(function (s, i) { return i; });
    for (var i = ranks.length - 1; i > 0; i--) { var j = Math.floor(rnd() * (i + 1)), t = ranks[i]; ranks[i] = ranks[j]; ranks[j] = t; }
    var qTop = rnd() < 0.5, qi = ranks.indexOf(qTop ? ranks.length - 1 : 0);
    var t0 = ranks[0]; ranks[0] = ranks[qi]; ranks[qi] = t0;
    lifted.forEach(function (s, k) {
      s.style.setProperty('--z', 'calc(var(--gap) * ' + (1 + ranks[k] * 0.75).toFixed(2) + ')');
      s.style.setProperty('--i', String(k + 1));
    });
    /* decorative bars: a seeded rising pattern, no figures */
    sec.querySelectorAll('.bl-hdash__bars').forEach(function (b) {
      [].forEach.call(b.children, function (bar, n) { bar.style.setProperty('--h', Math.round(26 + n * 5.5 + rnd() * 18) + '%'); });
    });

    var ready = false;
    function open() {
      sec.classList.add('is-open');
      setTimeout(function () { ready = true; }, BL.RM ? 0 : 1900);
    }
    if (BL.RM) open(); else BL.onVisible(sec, open, 0.2);

    if (!BL.FINE || BL.RM) return;
    var num = function (name, d) { var v = parseFloat(sec.style.getPropertyValue(name)); return isNaN(v) ? d : v; };
    var pitch = 14 + num('--sa', 0.5) * 8, yaw = (20 + num('--sb', 0.5) * 8) * (num('--sign', 1) < 0 ? -1 : 1);
    var x = 0, y = 0, tx = 0, ty = 0, raf = 0;
    function step() {
      raf = 0;
      x += (tx - x) * 0.08; y += (ty - y) * 0.08;
      rig.style.transform = 'rotateX(' + (pitch - y * 6).toFixed(2) + 'deg) rotateY(' + (yaw + x * 8).toFixed(2) + 'deg)';
      if (Math.abs(tx - x) + Math.abs(ty - y) > 0.002) raf = requestAnimationFrame(step);
      else rig.style.willChange = '';
    }
    function kick() {
      if (raf || !ready) return;
      rig.classList.add('is-live');
      rig.style.willChange = 'transform';
      raf = requestAnimationFrame(step);
    }
    sec.addEventListener('pointermove', function (e) {
      if (st.paused) return;
      var r = stage.getBoundingClientRect();
      tx = Math.max(-1, Math.min(1, ((e.clientX - r.left) / r.width) * 2 - 1));
      ty = Math.max(-1, Math.min(1, ((e.clientY - r.top) / r.height) * 2 - 1));
      kick();
    }, { passive: true });
    sec.addEventListener('pointerleave', function () { tx = 0; ty = 0; kick(); });
    st.onMotion(function (paused) { if (paused) { tx = 0; ty = 0; kick(); } });
  });
})();
