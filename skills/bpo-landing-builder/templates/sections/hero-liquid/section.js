/* hero-liquid: liquid-merge-contours. Two main metaballs start apart and ease together until they merge; small
   droplets circle on slow, breathing orbits and join the shape now and then; on fine pointers one more droplet
   follows the pointer. The field (sum of r^2/d^2) is sampled on an 80 x 80 grid and traced with marching squares at
   three levels: a filled core, a lighter inner tone and two thin outline rings. One fill per level, one stroke per
   ring, 30 fps cap unless the pointer moves, backing store at most 1.5x. Reduced motion: one still, merged frame. */
(function () {
  var K = window.BL3D;
  var N = 80;
  /* marching squares: for each case, pairs of cell edges (0 top, 1 right, 2 bottom, 3 left) */
  var CASES = [[], [3, 2], [2, 1], [3, 1], [0, 1], null, [0, 2], [3, 0], [3, 0], [0, 2], null, [0, 1], [3, 1], [2, 1], [3, 2], []];

  function trace(f, T, cw, ch) {
    var W = N + 1, HOFF = (N + 1) * N, pts = {}, adj = {}, segs = [];
    function edgeId(i, j, e) {
      if (e === 0) return j * N + i;
      if (e === 2) return (j + 1) * N + i;
      if (e === 3) return HOFF + j * W + i;
      return HOFF + j * W + i + 1;
    }
    function point(id, i, j, e) {
      if (pts[id]) return;
      var a, b, ax, ay, bx, by;
      if (e === 0) { a = f[j * W + i]; b = f[j * W + i + 1]; ax = i; ay = j; bx = i + 1; by = j; }
      else if (e === 2) { a = f[(j + 1) * W + i]; b = f[(j + 1) * W + i + 1]; ax = i; ay = j + 1; bx = i + 1; by = j + 1; }
      else if (e === 3) { a = f[j * W + i]; b = f[(j + 1) * W + i]; ax = i; ay = j; bx = i; by = j + 1; }
      else { a = f[j * W + i + 1]; b = f[(j + 1) * W + i + 1]; ax = i + 1; ay = j; bx = i + 1; by = j + 1; }
      var t = (T - a) / ((b - a) || 1e-6);
      pts[id] = [(ax + (bx - ax) * t) * cw, (ay + (by - ay) * t) * ch];
    }
    function add(i, j, e1, e2) {
      var a = edgeId(i, j, e1), b = edgeId(i, j, e2);
      point(a, i, j, e1); point(b, i, j, e2);
      var k = segs.length;
      segs.push([a, b]);
      (adj[a] = adj[a] || []).push(k); (adj[b] = adj[b] || []).push(k);
    }
    for (var j = 0; j < N; j++) {
      for (var i = 0; i < N; i++) {
        var tl = f[j * W + i], tr = f[j * W + i + 1], br = f[(j + 1) * W + i + 1], bl = f[(j + 1) * W + i];
        var c = (tl >= T ? 8 : 0) | (tr >= T ? 4 : 0) | (br >= T ? 2 : 0) | (bl >= T ? 1 : 0);
        if (c === 0 || c === 15) continue;
        if (c === 5 || c === 10) {
          var mid = (tl + tr + br + bl) / 4 >= T;
          if ((c === 5) === mid) { add(i, j, 3, 0); add(i, j, 2, 1); } else { add(i, j, 0, 1); add(i, j, 3, 2); }
          continue;
        }
        add(i, j, CASES[c][0], CASES[c][1]);
      }
    }
    /* join segments into loops */
    var used = new Uint8Array(segs.length), loops = [];
    for (var s = 0; s < segs.length; s++) {
      if (used[s]) continue;
      used[s] = 1;
      var loop = [segs[s][0], segs[s][1]], cur = segs[s][1];
      for (var guard = 0; guard < segs.length; guard++) {
        var next = -1, list = adj[cur] || [];
        for (var q = 0; q < list.length; q++) if (!used[list[q]]) { next = list[q]; break; }
        if (next < 0) break;
        used[next] = 1;
        cur = segs[next][0] === cur ? segs[next][1] : segs[next][0];
        loop.push(cur);
      }
      if (loop.length > 3) loops.push(loop.map(function (id) { return pts[id]; }));
    }
    return loops;
  }

  function toPath(loops, dx, dy) {
    var p = new Path2D();
    loops.forEach(function (l) {
      var n = l.length, a = l[n - 1], b = l[0];
      p.moveTo((a[0] + b[0]) / 2 + dx, (a[1] + b[1]) / 2 + dy);
      for (var i = 0; i < n; i++) {
        var c = l[i], d = l[(i + 1) % n];
        p.quadraticCurveTo(c[0] + dx, c[1] + dy, (c[0] + d[0]) / 2 + dx, (c[1] + d[1]) / 2 + dy);
      }
      p.closePath();
    });
    return p;
  }

  document.querySelectorAll('[data-hliq]').forEach(function (sec) {
    if (!K) return;
    var stage = sec.querySelector('[data-hliq-stage]');
    var cv = sec.querySelector('[data-hliq-canvas]'), ctx = cv.getContext('2d');
    var chips = Array.prototype.slice.call(sec.querySelectorAll('[data-hliq-chip]'));
    var merged = sec.querySelector('[data-hliq-merged]');
    var rnd = K.seed(sec.getAttribute('data-seed') || 'brand');
    var css = getComputedStyle(sec);
    var cA = K.rgb(css.getPropertyValue('--c-accent')), cB = K.rgb(css.getPropertyValue('--c-accent-blend'));
    var cInk = K.rgb(css.getPropertyValue('--accent-ink'));
    var cLine = K.rgb(css.getPropertyValue('--c-on-accent'));
    var split = 0.35 + rnd() * 0.4;
    var axis = (rnd() - 0.5) * 0.7;
    var mains = [{ r: 0.15 + rnd() * 0.02, side: -1 }, { r: 0.14 + rnd() * 0.02, side: 1 }];
    var drops = [];
    var nDrops = 2 + Math.floor(rnd() * 2);
    for (var i = 0; i < nDrops; i++) {
      drops.push({ r: 0.035 + rnd() * 0.022, orbit: 0.36 + rnd() * 0.06, a: rnd() * 6.283, speed: (0.00004 + rnd() * 0.00005) * (rnd() < 0.5 ? -1 : 1),
        breathe: 5000 + rnd() * 6000, ph: rnd() * 6.283 });
    }
    var mergeMs = 4200 + rnd() * 1800;
    var ratio = Math.min(1.5, window.devicePixelRatio || 1);
    var size = null, grad = null, born = null;
    var f = new Float32Array((N + 1) * (N + 1));
    var thr = K.throttle();
    var mouse = { x: 0, y: 0, f: 0, tf: 0, moved: 0, on: false };

    function fit() {
      size = K.fit(cv, ratio);
      grad = K.rgba(K.mixRgb(cA, cB, split * 0.3), 1);
    }
    function ease(t) { return t < 0 ? 0 : t > 1 ? 1 : 1 - Math.pow(1 - t, 3); }

    function draw(ts) {
      if (!size) fit();
      if (born === null) born = ts;
      var busy = mouse.f > 0.01 && ts - mouse.moved < 600;
      if (!thr(ts, busy)) return;
      var w = size.w, h = size.h, m = Math.min(w, h), t = K.RM ? 1e9 : ts - born;
      mouse.f += (mouse.tf - mouse.f) * 0.1;
      /* separation of the two main shapes: apart, then merged, then a slow breath that never splits them again */
      var join = ease((t - 900) / mergeMs);
      var sep = (0.64 - 0.47 * join + 0.04 * join * Math.sin(t / 5200)) * m;
      var cx = w / 2, cy = h / 2, ca = Math.cos(axis), sa = Math.sin(axis);
      var balls = mains.map(function (b) {
        var d = sep / 2 * b.side;
        return [cx + ca * d, cy + sa * d + Math.sin(t / 6100 + b.side) * 0.015 * m, b.r * m];
      });
      drops.forEach(function (d) {
        var a = d.a + t * d.speed, rr = (d.orbit - 0.1 * Math.pow(0.5 + 0.5 * Math.sin(t / d.breathe + d.ph), 3)) * m;
        balls.push([cx + Math.cos(a) * rr, cy + Math.sin(a) * rr * 0.86, d.r * m]);
      });
      if (mouse.f > 0.02) balls.push([mouse.x, mouse.y, 0.06 * m * mouse.f]);
      var cw = w / N, ch = h / N, W = N + 1;
      for (var j = 0; j <= N; j++) {
        for (var i = 0; i <= N; i++) {
          var v = 0;
          if (i > 0 && j > 0 && i < N && j < N) {
            var x = i * cw, y = j * ch;
            for (var b = 0; b < balls.length; b++) {
              var dx = x - balls[b][0], dy = y - balls[b][1];
              var q = balls[b][2] * balls[b][2] / (dx * dx + dy * dy + 1);
              v += q * Math.sqrt(q);
            }
          }
          f[j * W + i] = v;
        }
      }
      ctx.setTransform(size.k, 0, 0, size.k, 0, 0);
      ctx.clearRect(0, 0, w, h);
      ctx.lineWidth = 1;
      ctx.strokeStyle = K.rgba(cInk, 0.18); ctx.stroke(toPath(trace(f, 0.24, cw, ch), 0, 0));
      ctx.strokeStyle = K.rgba(cInk, 0.34); ctx.stroke(toPath(trace(f, 0.52, cw, ch), 0, 0));
      ctx.fillStyle = grad; ctx.fill(toPath(trace(f, 1, cw, ch), 0, 0), 'evenodd');
      ctx.strokeStyle = K.rgba(cLine, 0.34); ctx.stroke(toPath(trace(f, 2.6, cw, ch), 0, 0));

      /* labels ride on the main shapes until they merge, then the merged label takes over */
      var together = join > 0.72;
      chips.forEach(function (el, k) {
        var bl = balls[k];
        el.style.transform = 'translate3d(' + (bl[0] - el.offsetWidth / 2).toFixed(1) + 'px,' + (bl[1] - el.offsetHeight / 2).toFixed(1) + 'px,0)';
        el.classList.toggle('is-on', !together);
      });
      if (merged) {
        merged.style.transform = 'translate3d(' + (cx - merged.offsetWidth / 2).toFixed(1) + 'px,' + (cy - merged.offsetHeight / 2).toFixed(1) + 'px,0)';
        merged.classList.toggle('is-on', together);
      }
    }

    var loop = K.loop(cv, draw);
    if (window.BL && window.BL.FINE && !K.RM) {
      stage.addEventListener('pointermove', function (e) {
        var r = cv.getBoundingClientRect();
        mouse.x = e.clientX - r.left; mouse.y = e.clientY - r.top; mouse.tf = 1; mouse.moved = performance.now();
      }, { passive: true });
      stage.addEventListener('pointerleave', function () { mouse.tf = 0; mouse.moved = performance.now(); });
    }
    window.addEventListener('resize', function () { fit(); if (K.RM || (window.BL && window.BL.paused)) loop.still(); });
  });
})();
