/* hero-particles: about 900 particles morph between a sphere, the brand monogram, a torus and a lattice cube.
   Shape order, spin direction, tilt and colour split come from the brand name. Reduced motion shows the monogram still. */
(function () {
  var K = window.BL3D;
  document.querySelectorAll('[data-hpart]').forEach(function (sec) {
    if (!K) return;
    var canvas = sec.querySelector('[data-hpart-canvas]');
    var ctx = canvas.getContext('2d');
    var rnd = K.seed(sec.getAttribute('data-seed') || 'brand');
    var css = getComputedStyle(sec);
    var cA = K.rgb(css.getPropertyValue('--c-accent-blend')), cB = K.rgb(css.getPropertyValue('--text-strong'));
    var small = window.innerWidth < 700;
    var N = small ? 520 : 900;
    var font = css.getPropertyValue('--font-heading').trim() || 'sans-serif';

    /* shapes in unit space */
    function sphere() {
      var out = [], g = Math.PI * (3 - Math.sqrt(5));
      for (var i = 0; i < N; i++) {
        var y = 1 - (i / (N - 1)) * 2, r = Math.sqrt(1 - y * y), t = g * i;
        out.push([Math.cos(t) * r, y, Math.sin(t) * r]);
      }
      return out;
    }
    function torus() {
      var out = [];
      for (var i = 0; i < N; i++) {
        var u = rnd() * Math.PI * 2, v = rnd() * Math.PI * 2, R = 0.78, r = 0.28;
        out.push([(R + r * Math.cos(v)) * Math.cos(u), r * Math.sin(v), (R + r * Math.cos(v)) * Math.sin(u)]);
      }
      return out;
    }
    function cube() {
      var out = [];
      for (var i = 0; i < N; i++) {
        var p = [rnd() * 2 - 1, rnd() * 2 - 1, rnd() * 2 - 1], axis = Math.floor(rnd() * 3);
        p[axis] = rnd() < 0.5 ? -1 : 1;
        for (var k = 0; k < 3; k++) if (k !== axis) p[k] = Math.round(p[k] * 5) / 5;
        out.push([p[0] * 0.72, p[1] * 0.72, p[2] * 0.72]);
      }
      return out;
    }
    var mark = K.textPoints(sec.getAttribute('data-mark') || 'B', font, N, rnd).map(function (p) { return [p[0] * 1.05, p[1] * 1.05, p[2]]; });
    var others = [sphere(), torus(), cube()];
    /* brand-seeded order; the monogram always comes second so it is seen early */
    for (var s = others.length - 1; s > 0; s--) { var j = Math.floor(rnd() * (s + 1)); var tmp = others[s]; others[s] = others[j]; others[j] = tmp; }
    var shapes = [others[0], mark, others[1], mark, others[2]];
    var spin = (rnd() < 0.5 ? -1 : 1) * (0.00012 + rnd() * 0.00008);
    var tiltBase = 0.25 + rnd() * 0.25;
    var tone = []; for (var i = 0; i < N; i++) tone.push(rnd());
    var delay = []; for (i = 0; i < N; i++) delay.push((i % 97) / 97 * 0.35);

    var HOLD = 3400, MORPH = 1700;
    var size = K.fit(canvas, 1), ptr = K.pointer(sec), gate = K.throttle();
    var born = null, ay = rnd() * Math.PI * 2, last = null;
    function ease(t) { return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2; }

    function draw(ts) {
      if (born === null) born = ts;
      var t = ts - born;
      var cycle = HOLD + MORPH, idx = Math.floor(t / cycle), inCycle = t - idx * cycle;
      var morphing = !K.RM && inCycle > HOLD;
      if (!gate(ts, morphing)) return;
      if (last !== null && !K.RM) ay += (ts - last) * spin;
      last = ts;
      var from = K.RM ? mark : shapes[idx % shapes.length], to = K.RM ? mark : shapes[(idx + 1) % shapes.length];
      var p = morphing ? (inCycle - HOLD) / MORPH : 0;
      ptr.step(0.06);
      var w = size.w, h = size.h, R = Math.min(w, h) * 0.36, focal = Math.min(w, h) * 1.15, dist = R * 3.2;
      var ax = tiltBase + ptr.y * 0.35, ry = ay + ptr.x * 0.7;
      ctx.setTransform(1, 0, 0, 1, 0, 0);
      ctx.clearRect(0, 0, w, h);
      var buckets = [[], [], [], []];
      /* the monogram always faces the viewer: undo the spin for its points and keep a gentle swing */
      var face = -ry + Math.sin(ts / 2600) * 0.35;
      var cf = Math.cos(face), sf = Math.sin(face);
      function facing(pt) { return [pt[0] * cf + pt[2] * sf, pt[1], -pt[0] * sf + pt[2] * cf]; }
      for (var i = 0; i < N; i++) {
        var k = morphing ? ease(Math.max(0, Math.min(1, (p - delay[i]) / (1 - 0.35)))) : 0;
        var a = from === mark ? facing(from[i]) : from[i], b = to === mark ? facing(to[i]) : to[i];
        var v = [(a[0] + (b[0] - a[0]) * k) * R, (a[1] + (b[1] - a[1]) * k) * R, (a[2] + (b[2] - a[2]) * k) * R];
        var q = K.project(K.rotate(v, ax, ry), w / 2, h / 2, focal, dist);
        var depth = Math.max(0, Math.min(1, (q[3] - (dist - R)) / (2 * R)));
        buckets[Math.min(3, Math.floor(depth * 4))].push(q[0], q[1], q[2], tone[i]);
      }
      for (var bk = 0; bk < 4; bk++) {
        var list = buckets[bk], alpha = 0.25 + bk * 0.22;
        for (var pass = 0; pass < 2; pass++) {
          ctx.fillStyle = K.rgba(pass ? cB : cA, alpha);
          for (var m = 0; m < list.length; m += 4) {
            if ((list[m + 3] < 0.62) === !!pass) continue;
            var r = Math.min(2.2, Math.max(0.9, list[m + 2] * (2.0 + bk * 0.6)));
            ctx.fillRect(list[m] - r, list[m + 1] - r, r * 2, r * 2);
          }
        }
      }
    }
    K.loop(canvas, draw);
    window.addEventListener('resize', function () { size = K.fit(canvas, 1); });
  });
})();
