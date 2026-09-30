/* hero-isometric: a 7 x 7 operations floor in isometric view. Blocks rise in a wave, brand roofs mark busy desks,
   packets move along the aisles, the block nearest the pointer lifts. Heights, roofs and routes come from the brand name.
   Drawn back to front (painter's order), three shaded faces per block, one canvas at 1x. */
(function () {
  var K = window.BL3D;
  document.querySelectorAll('[data-hiso]').forEach(function (sec) {
    if (!K) return;
    var canvas = sec.querySelector('[data-hiso-canvas]');
    var ctx = canvas.getContext('2d');
    var rnd = K.seed(sec.getAttribute('data-seed') || 'brand');
    var css = getComputedStyle(sec);
    var bg = K.rgb(css.getPropertyValue('--bg')), ink = K.rgb(css.getPropertyValue('--c-primary'));
    var acc = K.rgb(css.getPropertyValue('--c-accent')), acc2 = K.rgb(css.getPropertyValue('--c-accent-blend'));
    var dark = (bg[0] + bg[1] + bg[2]) / 3 < 110;
    var base = dark ? K.mixRgb(bg, [255, 255, 255], 0.14) : K.mixRgb(bg, ink, 0.05);
    var faces = { top: base, left: K.mixRgb(base, ink, dark ? 0.35 : 0.12), right: K.mixRgb(base, ink, dark ? 0.5 : 0.22) };
    var afaces = { top: acc2, left: acc, right: K.mixRgb(acc, [0, 0, 0], 0.25) };
    var G = window.innerWidth < 560 ? 5 : 7;
    var cells = [];
    for (var y = 0; y < G; y++) for (var x = 0; x < G; x++) {
      var aisle = (x === 3 || y === 3) && G === 7 || (x === 2 || y === 2) && G === 5;
      cells.push({ x: x, y: y, h: aisle ? 0 : 0.35 + rnd() * (rnd() < 0.18 ? 1.9 : 0.9), brand: !aisle && rnd() < 0.2, aisle: aisle, delay: (x + y) * 70 + rnd() * 120, lift: 0 });
    }
    var packets = [];
    for (var i = 0; i < 5; i++) packets.push({ axis: rnd() < 0.5 ? 'x' : 'y', lane: G === 7 ? 3 : 2, off: rnd(), speed: (0.00008 + rnd() * 0.00008) * (rnd() < 0.5 ? -1 : 1) });
    var size = K.fit(canvas, 1), ptr = K.pointer(sec), gate = K.throttle(), born = null, mouse = null;
    if (window.BL && window.BL.FINE && !K.RM) {
      canvas.parentNode.addEventListener('pointermove', function (e) { var r = canvas.getBoundingClientRect(); mouse = [e.clientX - r.left, e.clientY - r.top]; }, { passive: true });
      canvas.parentNode.addEventListener('pointerleave', function () { mouse = null; });
    }

    function iso(gx, gy, gz, s, ox, oy) { return [ox + (gx - gy) * s * 0.866, oy + (gx + gy) * s * 0.5 - gz * s]; }
    function poly(pts, color) {
      ctx.fillStyle = 'rgb(' + color[0] + ',' + color[1] + ',' + color[2] + ')';
      ctx.beginPath(); ctx.moveTo(pts[0][0], pts[0][1]);
      for (var k = 1; k < pts.length; k++) ctx.lineTo(pts[k][0], pts[k][1]);
      ctx.closePath(); ctx.fill();
    }
    function draw(ts) {
      if (born === null) born = ts;
      var t = K.RM ? 1e9 : ts - born;
      var rising = t < 2400;
      if (!gate(ts, rising || !!mouse)) return;
      ptr.step(0.06);
      var w = size.w, h = size.h, s = Math.min(w / (G * 1.9), h / (G * 1.45)), ox = w / 2 + ptr.x * 6, oy = h * 0.22 + ptr.y * 6;
      var gap = 0.12;
      ctx.setTransform(1, 0, 0, 1, 0, 0);
      ctx.clearRect(0, 0, w, h);
      /* floor */
      poly([iso(0, 0, 0, s, ox, oy), iso(G, 0, 0, s, ox, oy), iso(G, G, 0, s, ox, oy), iso(0, G, 0, s, ox, oy)], K.mixRgb(bg, ink, dark ? 0.2 : 0.04));
      var hot = null, best = 1e9;
      cells.forEach(function (c) {
        var rise = Math.max(0, Math.min(1, (t - c.delay) / 700));
        rise = 1 - Math.pow(1 - rise, 3);
        var breathe = K.RM ? 0 : Math.sin(ts / 1400 + c.x * 0.7 + c.y * 0.4) * 0.04;
        c.cur = c.aisle ? 0 : (c.h + breathe) * rise + c.lift;
        if (mouse && !c.aisle) {
          var ctr = iso(c.x + 0.5, c.y + 0.5, c.cur, s, ox, oy);
          var d = Math.hypot(ctr[0] - mouse[0], ctr[1] - mouse[1]);
          if (d < best) { best = d; hot = c; }
        }
      });
      cells.forEach(function (c) { c.lift += ((c === hot && best < s * 1.2 ? 0.6 : 0) - c.lift) * 0.18; });
      /* packets travel the aisles, drawn with the cells in painter's order */
      var items = cells.map(function (c) { return { key: c.x + c.y, cell: c }; });
      packets.forEach(function (p) {
        var f = ((t * p.speed + p.off) % 1 + 1) % 1 * G;
        var gx = p.axis === 'x' ? f : p.lane + 0.5, gy = p.axis === 'x' ? p.lane + 0.5 : f;
        items.push({ key: gx + gy - 0.5, packet: [gx, gy] });
      });
      items.sort(function (a, b) { return a.key - b.key; });
      items.forEach(function (it) {
        if (it.packet) {
          var q = iso(it.packet[0], it.packet[1], 0.08, s, ox, oy);
          ctx.fillStyle = 'rgb(' + acc[0] + ',' + acc[1] + ',' + acc[2] + ')';
          ctx.beginPath(); ctx.arc(q[0], q[1], Math.max(2.5, s * 0.09), 0, Math.PI * 2); ctx.fill();
          return;
        }
        var c = it.cell;
        if (c.aisle || c.cur <= 0.01) return;
        var f = c.brand ? afaces : faces;
        var x0 = c.x + gap, y0 = c.y + gap, x1 = c.x + 1 - gap, y1 = c.y + 1 - gap, z = c.cur;
        poly([iso(x0, y1, 0, s, ox, oy), iso(x1, y1, 0, s, ox, oy), iso(x1, y1, z, s, ox, oy), iso(x0, y1, z, s, ox, oy)], f.left);
        poly([iso(x1, y0, 0, s, ox, oy), iso(x1, y1, 0, s, ox, oy), iso(x1, y1, z, s, ox, oy), iso(x1, y0, z, s, ox, oy)], f.right);
        poly([iso(x0, y0, z, s, ox, oy), iso(x1, y0, z, s, ox, oy), iso(x1, y1, z, s, ox, oy), iso(x0, y1, z, s, ox, oy)], f.top);
      });
    }
    K.loop(canvas, draw);
    window.addEventListener('resize', function () { size = K.fit(canvas, 1); });
  });
})();
