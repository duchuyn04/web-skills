/* industries-slats: slat-louvre-turn-3d. Slats left of the open one turn by +angle, slats right of it by -angle,
   so their outer edges come forward like a fan. Positions are solved with the same perspective the browser uses
   (x' = x * P / (P - z)) so projected slats keep an even gap, then the row is centred. Focus, hover or a first tap
   opens a slat; Enter or a second tap follows its link. */
(function () {
  var BL = window.BL;
  if (!BL || !BL.stage3d) return;
  document.querySelectorAll('[data-fxslat]').forEach(function (sec) {
    var stage = sec.querySelector('[data-fxslat-stage]');
    var slats = Array.prototype.slice.call(sec.querySelectorAll('[data-slat]'));
    var n = slats.length;
    if (!stage || n < 2) return;
    var act = -1, list = false, geo = null, hoverTimer = null;
    var st = BL.stage3d(sec, {
      reveal: function (el) {
        var s = el.closest && el.closest('[data-slat]');
        if (s) open(slats.indexOf(s), true);
      }
    });
    var rnd = st.rnd;
    var widthBias = 0.92 + rnd() * 0.14;
    var start = rnd() < 0.5 ? 0 : Math.floor((n - 1) / 2);
    var GAP = 10, LIFT = 36, MIN_W = 240;

    function persp() { return parseFloat(getComputedStyle(stage).perspective) || 1700; }
    function measure() {
      var inner = stage.clientWidth - 16;
      var base = (n <= 4 ? 400 : n === 5 ? 370 : n === 6 ? 340 : 305) * widthBias * Math.min(1, inner / 1176);
      var w = base;
      var cos = ((inner - w) / (n - 1) - GAP) / w;
      var lo = Math.cos(68 * Math.PI / 180), hi = Math.cos(48 * Math.PI / 180);
      if (cos < lo) { cos = lo; w = (inner - (n - 1) * GAP) / (1 + (n - 1) * lo); }
      if (cos > hi) cos = hi;
      return { inner: inner, w: w, a: Math.acos(cos), P: persp() };
    }
    function edges(ang, z0, hw) {
      var c = Math.cos(ang), s = Math.sin(ang);
      return { lx: -hw * c, lz: z0 + hw * s, rx: hw * c, rz: z0 - hw * s };
    }
    function solve(k, g) {
      var hw = g.w / 2, P = g.P, shift = 0, xs = [], i, e;
      var proj = function (x, z) { return x * P / (P - z); };
      var unproj = function (px, z) { return px * (P - z) / P; };
      for (var pass = 0; pass < 5; pass++) {
        xs = [];
        e = edges(0, LIFT, hw);
        xs[k] = shift;
        var right = proj(shift + e.rx, e.rz), left = proj(shift + e.lx, e.lz), minL = left, maxR = right;
        for (i = k + 1; i < n; i++) {
          e = edges(-g.a, 0, hw);
          xs[i] = unproj(right + GAP, e.lz) - e.lx;
          right = proj(xs[i] + e.rx, e.rz);
          maxR = Math.max(maxR, right);
        }
        for (i = k - 1; i >= 0; i--) {
          e = edges(g.a, 0, hw);
          xs[i] = unproj(left - GAP, e.rz) - e.rx;
          left = proj(xs[i] + e.lx, e.lz);
          minL = Math.min(minL, left);
        }
        shift -= (minL + maxR) / 2 * 0.9;
        if (pass === 4) return { xs: xs, span: maxR - minL };
      }
    }
    function place(k) {
      var s = solve(k, geo);
      if (s.span > geo.inner && geo.w > MIN_W) {
        geo.w = Math.max(MIN_W, geo.w * geo.inner / s.span);
        sec.style.setProperty('--sw', geo.w.toFixed(1) + 'px');
        s = solve(k, geo);
      }
      var deg = geo.a * 180 / Math.PI;
      slats.forEach(function (sl, i) {
        var ang = i === k ? 0 : i < k ? deg : -deg;
        sl.style.transform = 'translateX(' + s.xs[i].toFixed(1) + 'px) translateZ(' + (i === k ? LIFT : 0) + 'px) rotateY(' + ang.toFixed(2) + 'deg)';
      });
    }
    function mark(k) {
      slats.forEach(function (sl, i) {
        sl.classList.toggle('is-active', i === k);
        var b = sl.querySelector('button.bl-fxslat__ctl');
        if (b) b.setAttribute('aria-expanded', String(i === k || list));
      });
    }
    function open(k, instant) {
      if (k < 0 || list) return;
      if (k === act) return;
      act = k;
      mark(k);
      if (instant || BL.RM) sec.classList.add('is-still');
      place(k);
      if (instant || BL.RM) { void stage.offsetWidth; sec.classList.remove('is-still'); }
    }
    function layout() {
      geo = measure();
      list = window.innerWidth < 1000 || geo.w < MIN_W;
      sec.classList.toggle('is-list', list);
      if (list) {
        sec.style.removeProperty('--sw');
        slats.forEach(function (sl) { sl.style.transform = ''; });
        mark(-1);
        return;
      }
      sec.style.setProperty('--sw', geo.w.toFixed(1) + 'px');
      var k = act < 0 ? start : act;
      act = -1;
      sec.classList.add('is-still');
      open(k, true);
    }

    slats.forEach(function (sl, i) {
      sl.addEventListener('pointerenter', function (e) {
        if (e.pointerType !== 'mouse' || list) return;
        clearTimeout(hoverTimer);
        hoverTimer = setTimeout(function () { open(i, false); }, 70);
      });
      sl.addEventListener('pointerleave', function () { clearTimeout(hoverTimer); });
      sl.addEventListener('click', function (e) {
        if (list) return;
        var ctl = e.target.closest('a');
        if (i !== act) {
          /* touch: the first tap opens the slat, the second follows its link */
          if (ctl) e.preventDefault();
          clearTimeout(hoverTimer);
          open(i, false);
          return;
        }
        var href = sl.getAttribute('data-href');
        if (href && !ctl) window.location.href = href;
      });
    });

    layout();
    var rt = null;
    window.addEventListener('resize', function () { clearTimeout(rt); rt = setTimeout(layout, 150); });
  });
})();
