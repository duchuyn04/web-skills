/* Shared: flowing-line-ribbons renderer and a render loop that stops off screen, in hidden tabs, under reduced motion and when paused.
   Used by hero-ribbons (hero, echo sections, globe) and services-stack (brand card). */
(function () {
  if (window.BLRibbons) return;
  var RM = window.BL && window.BL.RM;
  var FINE = window.BL && window.BL.FINE;
  var DPR = Math.min(window.devicePixelRatio || 1, 2);
  var TAU = Math.PI * 2;
  var paused = false;
  var loops = [];

  function smooth(t) { return t * t * (3 - 2 * t); }

  function fit(canvas) {
    var r = canvas.getBoundingClientRect();
    var w = Math.max(1, Math.round(r.width)), h = Math.max(1, Math.round(r.height));
    if (canvas.width !== w * DPR || canvas.height !== h * DPR) { canvas.width = w * DPR; canvas.height = h * DPR; }
    return { w: w, h: h };
  }

  function loop(el, frame) {
    var l = { visible: false, raf: 0 };
    function tick(ts) {
      l.raf = 0;
      if (!l.visible || paused || document.hidden) return;
      frame(ts);
      l.raf = requestAnimationFrame(tick);
    }
    l.kick = function () { if (!l.raf && l.visible && !paused && !RM) l.raf = requestAnimationFrame(tick); };
    l.still = function () { frame(performance.now()); };
    if ('IntersectionObserver' in window) {
      new IntersectionObserver(function (entries) {
        l.visible = entries[0].isIntersecting;
        if (l.visible) { if (RM || paused) l.still(); else l.kick(); }
      }, { threshold: 0 }).observe(el);
    } else { l.visible = true; l.still(); }
    loops.push(l);
    return l;
  }

  /* Mix a #rrggbb colour toward white by t (0-1); canvas needs a plain colour string. */
  function lighten(hex, t) {
    var m = /^#?([0-9a-f]{6})$/i.exec((hex || '').trim());
    if (!m) return hex;
    var n = parseInt(m[1], 16), out = [(n >> 16) & 255, (n >> 8) & 255, n & 255].map(function (c) { return Math.round(c + (255 - c) * t); });
    return 'rgb(' + out.join(',') + ')';
  }

  /* Line ribbons. Cost is raster, not script: a full-width canvas stroked with ~50 long paths every frame.
     So: 1x backing store (thin soft lines look the same), smooth curves through ~60 points instead of ~160
     straight segments, one stroke per alpha bucket instead of one per line, and 30 fps once the draw-in ends. */
  function waves(canvas, host, opts) {
    var ctx = canvas.getContext('2d');
    var RD = 1, BUCKETS = 4;
    var size = fitRibbon();
    var mouse = { x: -9999, y: -9999, sx: -9999, sy: -9999, f: 0, tf: 0 };
    var born = null, lastDraw = 0;
    function fitRibbon() {
      var r = canvas.getBoundingClientRect();
      var w = Math.max(1, Math.round(r.width)), h = Math.max(1, Math.round(r.height));
      if (canvas.width !== w * RD || canvas.height !== h * RD) { canvas.width = w * RD; canvas.height = h * RD; }
      return { w: w, h: h };
    }
    function yAt(rb, ph, t, u, h) {
      var base = (rb.y0 + (rb.y1 - rb.y0) * smooth(Math.max(0, Math.min(1, u)))) * h + rb.amp * h * Math.sin(u * rb.freq * TAU + ph);
      var spread = rb.spread * h * Math.sin(u * rb.twist * Math.PI + ph * 0.7 + rb.shift);
      return base + (t - 0.5) * spread + 5 * Math.sin(u * 9 + t * 4 + ph * 1.3);
    }
    function draw(ts) {
      if (born === null) born = ts;
      var p = RM ? 1 : Math.min(1, (ts - born) / (opts.revealMs || 2000));
      if (p >= 1 && !RM && ts - lastDraw < 32) return;
      lastDraw = ts;
      var reveal = 1 - Math.pow(1 - p, 3);
      var T = RM ? 0 : ts;
      mouse.sx += (mouse.x - mouse.sx) * 0.22; mouse.sy += (mouse.y - mouse.sy) * 0.22;
      mouse.f += (mouse.tf - mouse.f) * 0.12;
      var w = size.w, h = size.h;
      ctx.setTransform(RD, 0, 0, RD, 0, 0);
      ctx.clearRect(0, 0, w, h);
      ctx.strokeStyle = opts.color;
      ctx.lineWidth = opts.width || 1;
      var segs = Math.max(24, Math.min(64, Math.round(w / 24)));
      var dx = (w + 40) / segs, maxX = w * reveal, rad2 = Math.pow(Math.min(w, 1200) * 0.14, 2);
      var push = mouse.f > 0.01;
      opts.ribbons.forEach(function (rb) {
        var ph = T * rb.speed;
        var paths = [];
        for (var b = 0; b < BUCKETS; b++) paths.push(new Path2D());
        for (var i = 0; i < rb.lines; i++) {
          var t = i / (rb.lines - 1);
          var a = Math.sin(Math.PI * t);
          var path = paths[Math.min(BUCKETS - 1, Math.floor(a * BUCKETS))];
          var px = -20, py = 0, first = true;
          for (var x = -20; x <= maxX + dx; x += dx) {
            var y = yAt(rb, ph, t, x / w, h);
            if (push) {
              var mx = x - mouse.sx, my = y - mouse.sy, d2 = mx * mx + my * my;
              if (d2 < rad2 * 4) y += (my >= 0 ? 1 : -1) * 46 * mouse.f * Math.exp(-d2 / rad2);
            }
            if (first) { path.moveTo(x, y); first = false; }
            else path.quadraticCurveTo(px, py, (px + x) / 2, (py + y) / 2);
            px = x; py = y;
          }
          path.lineTo(px, py);
        }
        for (var k = 0; k < BUCKETS; k++) {
          ctx.globalAlpha = rb.alpha * (0.35 + 0.65 * (k + 0.5) / BUCKETS);
          ctx.stroke(paths[k]);
        }
      });
      ctx.globalAlpha = 1;
    }

    var l = loop(canvas, draw);
    if (opts.mouse && FINE && !RM) {
      host.addEventListener('pointermove', function (e) {
        var r = canvas.getBoundingClientRect();
        mouse.x = e.clientX - r.left; mouse.y = e.clientY - r.top;
        if (mouse.sx < -999) { mouse.sx = mouse.x; mouse.sy = mouse.y; }
        mouse.tf = 1;
      }, { passive: true });
      host.addEventListener('pointerleave', function () { mouse.tf = 0; });
    }
    window.addEventListener('resize', function () { size = fitRibbon(); if (RM || paused) l.still(); });
    return l;
  }

  document.addEventListener('visibilitychange', function () { if (!document.hidden) loops.forEach(function (l) { l.kick(); }); });
  /* follow the page-wide motion switch in base.js */
  document.addEventListener('bl:motion', function (e) {
    paused = !!e.detail.paused;
    if (!paused) loops.forEach(function (l) { l.kick(); });
  });

  window.BLRibbons = {
    RM: RM, DPR: DPR, fit: fit, loop: loop, waves: waves, lighten: lighten,
    isPaused: function () { return paused; },
    setPaused: function (v) { if (window.BL && window.BL.setPaused) window.BL.setPaused(!!v); else paused = !!v; }
  };
})();
