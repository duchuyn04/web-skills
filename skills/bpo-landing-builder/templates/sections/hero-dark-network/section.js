/* hero-3d-point-cloud-nodes: canvas 2D, at most 110 points, lerp 0.05 toward the pointer */
(function () {
  document.querySelectorAll('[data-network]').forEach(function (cv) {
    var ctx = cv.getContext('2d');
    if (!ctx) return;
    var host = cv.closest('section') || document.body;
    var dpr = Math.min(window.devicePixelRatio || 1, 2);
    var W = 0, H = 0, pts = [], raf = 0, visible = true;
    var mouse = { x: 0.5, y: 0.5 }, tilt = { x: 0.5, y: 0.5 };
    var css = getComputedStyle(cv);
    var c1 = css.getPropertyValue('--accent-ink').trim() || '#6f8cff';
    var c2 = css.getPropertyValue('--c-accent-2').trim() || '#5ef2c2';

    function seed() {
      var n = Math.round(Math.max(36, Math.min(110, (W * H) / 9000)));
      pts = [];
      for (var i = 0; i < n; i++) {
        pts.push({ x: Math.random() * W, y: Math.random() * H, z: Math.random(), vx: (Math.random() - 0.5) * 0.22, vy: (Math.random() - 0.5) * 0.22 });
      }
    }
    function resize() {
      var r = cv.getBoundingClientRect();
      W = r.width; H = r.height;
      cv.width = Math.round(W * dpr); cv.height = Math.round(H * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      seed();
      if (window.BL.RM) draw();
    }
    function draw() {
      tilt.x += (mouse.x - tilt.x) * 0.05;
      tilt.y += (mouse.y - tilt.y) * 0.05;
      var ox = (tilt.x - 0.5) * 36, oy = (tilt.y - 0.5) * 24;
      ctx.clearRect(0, 0, W, H);
      var P = [];
      for (var i = 0; i < pts.length; i++) {
        var p = pts[i];
        if (!window.BL.RM) {
          p.x += p.vx; p.y += p.vy;
          if (p.x < -20) p.x = W + 20;
          if (p.x > W + 20) p.x = -20;
          if (p.y < -20) p.y = H + 20;
          if (p.y > H + 20) p.y = -20;
        }
        P.push([p.x + ox * p.z, p.y + oy * p.z, p.z]);
      }
      ctx.lineWidth = 1;
      ctx.strokeStyle = c1;
      for (var a = 0; a < P.length; a++) {
        for (var b = a + 1; b < P.length; b++) {
          var dx = P[a][0] - P[b][0], dy = P[a][1] - P[b][1];
          var d = dx * dx + dy * dy;
          if (d < 16900) {
            ctx.globalAlpha = (1 - Math.sqrt(d) / 130) * 0.28;
            ctx.beginPath(); ctx.moveTo(P[a][0], P[a][1]); ctx.lineTo(P[b][0], P[b][1]); ctx.stroke();
          }
        }
      }
      var mx = mouse.x * W, my = mouse.y * H;
      for (var k = 0; k < P.length; k++) {
        var q = P[k];
        var near = Math.hypot(q[0] - mx, q[1] - my) < 140;
        ctx.globalAlpha = near ? 1 : 0.35 + q[2] * 0.5;
        ctx.fillStyle = k % 5 === 0 ? c2 : c1;
        ctx.beginPath(); ctx.arc(q[0], q[1], 1 + q[2] * 1.8 + (near ? 1 : 0), 0, Math.PI * 2); ctx.fill();
      }
      ctx.globalAlpha = 1;
    }
    function loop() { draw(); raf = requestAnimationFrame(loop); }
    function start() { if (!raf && visible && !document.hidden && !window.BL.RM) raf = requestAnimationFrame(loop); }
    function stop() { cancelAnimationFrame(raf); raf = 0; }

    resize();
    window.addEventListener('resize', function () { stop(); resize(); start(); });
    host.addEventListener('pointermove', function (e) {
      var r = cv.getBoundingClientRect();
      mouse.x = (e.clientX - r.left) / r.width;
      mouse.y = (e.clientY - r.top) / r.height;
    }, { passive: true });
    if ('IntersectionObserver' in window) {
      new IntersectionObserver(function (en) { visible = en[0].isIntersecting; if (visible) start(); else stop(); }).observe(cv);
    }
    document.addEventListener('visibilitychange', function () { if (document.hidden) stop(); else start(); });
    if (window.BL.RM) draw(); else start();
  });
})();
