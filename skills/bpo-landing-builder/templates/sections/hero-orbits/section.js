/* hero-orbits: three tilted rings around a brand core carry the service chips. Back halves of the rings are drawn
   under the core, front halves over it; chips are ordered by depth. Tilts, radii, speeds and directions come from
   the brand name. A chip under the pointer stops its ring. Reduced motion places everything once. */
(function () {
  var K = window.BL3D;
  document.querySelectorAll('[data-horb]').forEach(function (sec) {
    if (!K) return;
    var stage = sec.querySelector('[data-horb-stage]');
    var back = sec.querySelector('[data-horb-back]'), front = sec.querySelector('[data-horb-front]');
    var bctx = back.getContext('2d'), fctx = front.getContext('2d');
    var chips = Array.prototype.slice.call(sec.querySelectorAll('[data-chip]'));
    var rnd = K.seed(sec.getAttribute('data-seed') || 'brand');
    var css = getComputedStyle(sec);
    var cRing = K.rgb(css.getPropertyValue('--accent-ink')), cDot = K.rgb(css.getPropertyValue('--c-accent-blend'));
    /* atom layout: three steep ellipses 60 degrees apart, so chips on different rings rarely overlap;
       the brand seed turns the whole set and nudges each tilt, radius and speed */
    var turn = rnd() * Math.PI;
    var rings = [0, 1, 2].map(function (i) {
      return { r: 0.8 + i * 0.12, ax: 0.3 + (rnd() - 0.5) * 0.12, az: turn + i * Math.PI / 3 + (rnd() - 0.5) * 0.2,
        speed: (0.00007 + rnd() * 0.00006) * (i % 2 ? -1 : 1), phase: rnd() * 6.28, held: false };
    });
    var slots = chips.map(function (el, i) { return { el: el, ring: rings[i % 3], a: (i / chips.length) * Math.PI * 2 + rnd() * 0.4 }; });
    var size = K.fit(back, 1); K.fit(front, 1);
    var chipHalf = 0;
    function measure() {
      chipHalf = 0;
      slots.forEach(function (s) { s.w = s.el.offsetWidth; s.h = s.el.offsetHeight; chipHalf = Math.max(chipHalf, s.w / 2); });
    }
    measure();
    var ptr = K.pointer(sec), last = null;

    function tilt(p, ring) {
      var q = K.rotate(p, ring.ax, 0);
      var cz = Math.cos(ring.az), sz = Math.sin(ring.az);
      return [q[0] * cz - q[1] * sz, q[0] * sz + q[1] * cz, q[2]];
    }
    function draw(ts) {
      var dt = last === null || K.RM ? 0 : Math.min(64, ts - last);
      last = ts;
      rings.forEach(function (ring) { if (!ring.held) ring.phase += dt * ring.speed; });
      ptr.step(0.07);
      var w = size.w, h = size.h, focal = Math.min(w, h) * 1.4;
      /* keep the widest chip inside the stage: outer ring radius plus half a chip fits in half the width */
      var R = Math.max(40, Math.min(Math.min(w, h) * 0.42, (w / 2 - chipHalf - 6) / 1.12)), dist = R * 3.6;
      var gx = 0.12 + ptr.y * 0.3, gy = ptr.x * 0.5;
      [bctx, fctx].forEach(function (c) { c.setTransform(1, 0, 0, 1, 0, 0); c.clearRect(0, 0, w, h); c.lineWidth = 1.2; });
      rings.forEach(function (ring) {
        var pb = new Path2D(), pf = new Path2D(), lastFront = null;
        for (var k = 0; k <= 96; k++) {
          var t = k / 96 * Math.PI * 2;
          var p = K.rotate(tilt([Math.cos(t) * ring.r * R, 0, Math.sin(t) * ring.r * R], ring), gx, gy);
          var q = K.project(p, w / 2, h / 2, focal, dist);
          var isFront = p[2] < 0;
          var path = isFront ? pf : pb;
          if (lastFront !== isFront) path.moveTo(q[0], q[1]); else path.lineTo(q[0], q[1]);
          lastFront = isFront;
        }
        bctx.strokeStyle = K.rgba(cRing, 0.18); bctx.stroke(pb);
        fctx.strokeStyle = K.rgba(cRing, 0.45); fctx.stroke(pf);
        /* one travelling dot per ring */
        var dp = K.rotate(tilt([Math.cos(ring.phase * 2.3) * ring.r * R, 0, Math.sin(ring.phase * 2.3) * ring.r * R], ring), gx, gy);
        var dq = K.project(dp, w / 2, h / 2, focal, dist);
        var c = dp[2] < 0 ? fctx : bctx;
        c.fillStyle = K.rgba(cDot, dp[2] < 0 ? 1 : 0.5);
        c.beginPath(); c.arc(dq[0], dq[1], 3.5 * dq[2] * 2.6, 0, Math.PI * 2); c.fill();
      });
      slots.forEach(function (s) {
        var ring = s.ring, a = s.a + ring.phase;
        var p = K.rotate(tilt([Math.cos(a) * ring.r * R, 0, Math.sin(a) * ring.r * R], ring), gx, gy);
        var q = K.project(p, w / 2, h / 2, focal, dist);
        var front01 = Math.max(0, Math.min(1, 0.5 - p[2] / (2 * ring.r * R)));
        var scale = 0.72 + front01 * 0.38;
        s.el.style.transform = 'translate3d(' + (q[0] - s.w / 2).toFixed(1) + 'px,' + (q[1] - s.h / 2).toFixed(1) + 'px,0) scale(' + scale.toFixed(3) + ')';
        s.el.style.opacity = (0.35 + front01 * 0.65).toFixed(3);
        s.el.style.zIndex = p[2] < 0 ? String(55 + Math.round(front01 * 40)) : String(10 + Math.round(front01 * 30));
      });
    }
    slots.forEach(function (s) {
      s.el.addEventListener('pointerenter', function () { s.ring.held = true; s.el.classList.add('is-hot'); });
      s.el.addEventListener('pointerleave', function () { s.ring.held = false; s.el.classList.remove('is-hot'); });
    });
    K.loop(back, draw);
    window.addEventListener('resize', function () { size = K.fit(back, 1); K.fit(front, 1); measure(); });
  });
})();
