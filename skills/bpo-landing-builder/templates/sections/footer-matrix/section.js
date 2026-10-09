/* footer-matrix: dot-matrix-sweep, dot-matrix-blink, dot-matrix-pointer.
   Robot.com lights whole dots only: its picture is drawn at one pixel per dot under a dot mask. Here the panel is
   sized to whole cells, the monogram is drawn once on a small canvas at one pixel per cell (no loop) and shown
   pixelated, and the band and the pointer spot move in whole cells. One GSAP timeline sweeps the band across (2.4 s)
   and blinks the monogram (scaleY squash, 150 ms) on a 6 s cycle; it is registered with BL.motion.ambient so Pause
   animations stops it, and it rests while the panel is off screen. On a fine pointer the dots under the pointer light up. */
(function () {
  var gsap = window.gsap;
  var SPOT = 7; /* pointer spot diameter in cells */

  function bitmap(cols, rows, draw) {
    var c = document.createElement('canvas');
    c.width = cols; c.height = rows;
    var g = c.getContext('2d');
    draw(g);
    /* hard threshold so every cell is either lit or dark */
    var img = g.getImageData(0, 0, cols, rows), d = img.data;
    for (var i = 3; i < d.length; i += 4) d[i] = d[i] >= 110 ? 255 : 0;
    g.putImageData(img, 0, 0);
    return c.toDataURL();
  }

  document.querySelectorAll('[data-fmatrix]').forEach(function (box) {
    var mark = box.querySelector('[data-fmatrix-mark]');
    var band = box.querySelector('[data-fmatrix-band]');
    var spot = box.querySelector('[data-fmatrix-spot]');
    var text = mark.textContent.trim();
    var grid = { dot: 12, cols: 0, rows: 0 };

    function layout() {
      box.style.width = ''; box.style.height = '';
      var probe = document.createElement('span');
      probe.style.cssText = 'position:absolute;width:var(--dot);height:0';
      box.appendChild(probe);
      var dot = probe.getBoundingClientRect().width || 12;
      box.removeChild(probe);
      var cols = Math.floor(box.clientWidth / dot), rows = Math.floor(box.clientHeight / dot);
      if (cols < 4 || rows < 4) return;
      grid = { dot: dot, cols: cols, rows: rows };
      box.style.width = cols * dot + 'px';
      box.style.height = rows * dot + 'px';
      var cs = getComputedStyle(mark);
      var color = cs.color, family = cs.fontFamily;
      mark.style.backgroundImage = 'url(' + bitmap(cols, rows, function (g) {
        g.fillStyle = color;
        g.textAlign = 'center';
        g.textBaseline = 'alphabetic';
        var size = 100;
        g.font = '800 ' + size + 'px ' + family;
        var m = g.measureText(text);
        var asc = m.actualBoundingBoxAscent || size * 0.72, desc = m.actualBoundingBoxDescent || 0;
        /* fill 80% of the rows, never wider than 90% of the columns */
        var k = Math.min(rows * 0.8 / (asc + desc), cols * 0.9 / (m.width || 1));
        size = Math.max(4, size * k);
        g.font = '800 ' + size + 'px ' + family;
        m = g.measureText(text);
        asc = m.actualBoundingBoxAscent || size * 0.72; desc = m.actualBoundingBoxDescent || 0;
        g.fillText(text, cols / 2, Math.round((rows + asc - desc) / 2));
      }) + ')';
      mark.classList.add('is-raster');
      var bw = Math.max(2, Math.round(cols * 0.12));
      band.style.width = bw * dot + 'px';
      spot.style.width = spot.style.height = SPOT * dot + 'px';
      spot.style.backgroundImage = 'url(' + bitmap(SPOT, SPOT, function (g) {
        g.fillStyle = color;
        g.beginPath(); g.arc(SPOT / 2, SPOT / 2, SPOT / 2, 0, Math.PI * 2); g.fill();
      }) + ')';
    }
    layout();
    var resizeTimer;
    window.addEventListener('resize', function () { clearTimeout(resizeTimer); resizeTimer = setTimeout(function () { layout(); if (box.__fmBuild) box.__fmBuild(); }, 150); });
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(function () { layout(); if (box.__fmBuild) box.__fmBuild(); });

    if (!window.BL || !gsap) return;
    var snap = function (v) { return Math.round(v / grid.dot) * grid.dot; };
    window.BL.motion.media(function (reduce) {
      if (reduce) return;
      var seen = false;
      /* band start and end are functions, so a relayout only invalidates the timeline */
      var tl = gsap.timeline({ repeat: -1, paused: true });
      tl.fromTo(band, { x: function () { return -band.offsetWidth; } }, {
        x: function () { return grid.cols * grid.dot; }, duration: 2.4, ease: 'power1.inOut',
        modifiers: { x: function (v) { return snap(parseFloat(v)) + 'px'; } }
      }, 0.4)
        .to(mark, { scaleY: 0.08, duration: 0.075, ease: 'power2.in' }, 3.4)
        .to(mark, { scaleY: 1, duration: 0.075, ease: 'power2.out' }, 3.475)
        .to({}, { duration: 2.45 }, 3.55);
      window.BL.motion.ambient(tl);
      box.__fmBuild = function () { tl.invalidate(); };
      var io = 'IntersectionObserver' in window ? new IntersectionObserver(function (es) {
        seen = es[0].isIntersecting;
        if (seen && !window.BL.paused) tl.resume(); else tl.pause();
      }) : null;
      if (io) io.observe(box); else tl.resume();

      var off = function () {};
      if (window.BL.FINE) {
        var p = { x: 0, y: 0 };
        var r0 = Math.floor(SPOT / 2);
        var apply = function () {
          spot.style.transform = 'translate(' + (snap(p.x) - r0 * grid.dot) + 'px,' + (snap(p.y) - r0 * grid.dot) + 'px)';
        };
        var qx = gsap.quickTo(p, 'x', { duration: 0.35, ease: 'power3.out', onUpdate: apply });
        var qy = gsap.quickTo(p, 'y', { duration: 0.35, ease: 'power3.out', onUpdate: apply });
        var at = function (e) { var r = box.getBoundingClientRect(); return [e.clientX - r.left - grid.dot / 2, e.clientY - r.top - grid.dot / 2]; };
        var move = function (e) { var a = at(e); qx(a[0]); qy(a[1]); };
        var enter = function (e) { var a = at(e); p.x = a[0]; p.y = a[1]; qx(a[0], a[0]); qy(a[1], a[1]); apply(); box.classList.add('is-pointer'); };
        var leave = function () { box.classList.remove('is-pointer'); };
        box.addEventListener('pointerenter', enter);
        box.addEventListener('pointermove', move);
        box.addEventListener('pointerleave', leave);
        off = function () {
          box.removeEventListener('pointerenter', enter);
          box.removeEventListener('pointermove', move);
          box.removeEventListener('pointerleave', leave);
          box.classList.remove('is-pointer');
        };
      }
      return function () { tl.kill(); box.__fmBuild = null; if (io) io.disconnect(); off(); gsap.set([band, mark], { clearProps: 'transform' }); spot.style.transform = ''; };
    });
  });
})();
