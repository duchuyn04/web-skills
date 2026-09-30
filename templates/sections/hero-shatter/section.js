/* hero-shatter: shatter-assemble-3d. When the photo is decoded and the hero is seen, 24 tiles (12 on narrow screens
   or with grid "4x3") fly in from seeded depths and angles: 900 ms each, staggered up to 500 ms, about 1.4 s in all.
   Then the tiles are hidden and the single photo shows. On fine pointers the tiles come back while the pointer is
   over the photo, and those within 120 px of it lift toward the viewer. Reduced motion: the photo only. */
(function () {
  var BL = window.BL;
  document.querySelectorAll('[data-hshat]').forEach(function (sec) {
    if (!BL || !BL.stage3d || BL.RM) return;
    var st = BL.stage3d(sec), rnd = st.rnd;
    var stage = sec.querySelector('[data-hshat-stage]'), img = sec.querySelector('[data-hshat-img]');
    var rig = sec.querySelector('[data-hshat-rig]');
    if (!img || !rig || !rig.animate) return;
    var small = window.innerWidth < 720 || sec.getAttribute('data-grid') === '4x3';
    var COLS = small ? 4 : 6, ROWS = small ? 3 : 4;
    var MODE = Math.floor(rnd() * 4);              /* 0 diagonal, 1 centre-out, 2 column wave, 3 scattered */
    var DEPTH = 0.7 + rnd() * 0.3, SPIN = 0.5 + rnd() * 0.5, AXIS = rnd(), DIR = rnd() < 0.5 ? -1 : 1;
    var LIFT = 10 + Math.round(rnd() * 6);
    var tiles = [];
    sec.style.setProperty('--cols', String(COLS));
    sec.style.setProperty('--rows', String(ROWS));

    for (var r = 0; r < ROWS; r++) for (var c = 0; c < COLS; c++) {
      var t = document.createElement('div');
      t.className = 'bl-hshat__tile';
      var im = document.createElement('img');
      im.src = img.currentSrc || img.src; im.alt = ''; im.decoding = 'async';
      t.appendChild(im);
      rig.appendChild(t);
      var cx = COLS > 1 ? c / (COLS - 1) : 0, cy = ROWS > 1 ? r / (ROWS - 1) : 0;
      var order = [
        DIR > 0 ? (cx + cy) / 2 : (1 - cx + cy) / 2,
        Math.min(1, Math.hypot(cx - 0.5, cy - 0.5) / 0.71),
        (DIR > 0 ? cx : 1 - cx) * 0.8 + cy * 0.2,
        rnd()
      ][MODE];
      tiles.push({ el: t, img: im, c: c, r: r, order: order, rz: rnd(), ra: rnd(), rb: rnd(), rx: rnd(), ry: rnd() });
    }

    var W = 0, H = 0, radius = '';
    function layout() {
      var b = stage.getBoundingClientRect();
      W = Math.round(b.width); H = Math.round(b.height);
      radius = getComputedStyle(img).borderTopLeftRadius;
      tiles.forEach(function (p) {
        var x0 = Math.round(p.c * W / COLS), x1 = Math.round((p.c + 1) * W / COLS);
        var y0 = Math.round(p.r * H / ROWS), y1 = Math.round((p.r + 1) * H / ROWS);
        var s = p.el.style;
        s.left = x0 + 'px'; s.top = y0 + 'px'; s.width = (x1 - x0) + 'px'; s.height = (y1 - y0) + 'px';
        var is = p.img.style;
        is.left = -x0 + 'px'; is.top = -y0 + 'px'; is.width = W + 'px'; is.height = H + 'px';
        p.x = (x0 + x1) / 2; p.y = (y0 + y1) / 2;
        s.borderTopLeftRadius = p.c === 0 && p.r === 0 ? radius : '';
        s.borderTopRightRadius = p.c === COLS - 1 && p.r === 0 ? radius : '';
        s.borderBottomLeftRadius = p.c === 0 && p.r === ROWS - 1 ? radius : '';
        s.borderBottomRightRadius = p.c === COLS - 1 && p.r === ROWS - 1 ? radius : '';
      });
    }

    function tiled(on) { rig.hidden = !on; sec.classList.toggle('is-tiled', on); }

    var assembled = false;
    function assemble() {
      layout();
      tiled(true);
      var runs = tiles.map(function (p) {
        var dz = Math.round((-400 + p.rz * 600) * DEPTH);
        var dx = Math.round((p.ra - 0.5) * 120), dy = Math.round((p.rb - 0.5) * 90);
        var ax = Math.round((p.rx - 0.5) * 90 * SPIN * AXIS), ay = Math.round((p.ry - 0.5) * 90 * SPIN * (1 - AXIS));
        var a = p.el.animate([
          { transform: 'translate3d(' + dx + 'px,' + dy + 'px,' + dz + 'px) rotateX(' + ax + 'deg) rotateY(' + ay + 'deg)', opacity: 0 },
          { transform: 'none', opacity: 1 }
        ], { duration: 950, delay: Math.round(p.order * 500), easing: 'cubic-bezier(.3, .6, .25, 1)', fill: 'backwards' });
        return a.finished;
      });
      Promise.all(runs).then(function () { assembled = true; if (!over) tiled(false); }, fail);
    }
    function fail() { assembled = true; tiled(false); }
    function go() {
      if (st.paused) { fail(); return; }
      var ready = img.decode ? img.decode() : Promise.resolve();
      ready.then(assemble, fail);
    }
    /* hide the photo until the tiles take over, so it does not flash first */
    sec.classList.add('is-tiled');
    BL.onVisible(stage, go, 0.25);
    window.addEventListener('resize', function () { if (!rig.hidden) layout(); });

    if (!BL.FINE) return;
    var over = false, raf = 0, px = 0, py = 0, leaveT = 0;
    function lift() {
      raf = 0;
      tiles.forEach(function (p) {
        var d = Math.hypot(p.x - px, p.y - py);
        var z = d < 120 ? Math.round((1 - d / 120) * LIFT * 10) / 10 : 0;
        p.el.style.transform = z ? 'translateZ(' + z + 'px)' : '';
        p.el.classList.toggle('is-up', z > LIFT * 0.4);
      });
    }
    stage.addEventListener('pointerenter', function () {
      over = true;
      if (!assembled || st.paused) return;
      clearTimeout(leaveT);
      layout();
      tiled(true);
    });
    stage.addEventListener('pointermove', function (e) {
      if (!assembled || st.paused || rig.hidden) return;
      var b = stage.getBoundingClientRect();
      px = e.clientX - b.left; py = e.clientY - b.top;
      if (!raf) raf = requestAnimationFrame(lift);
    }, { passive: true });
    stage.addEventListener('pointerleave', function () {
      over = false;
      if (!assembled) return;
      tiles.forEach(function (p) { p.el.style.transform = ''; p.el.classList.remove('is-up'); });
      leaveT = setTimeout(function () { if (!over) tiled(false); }, 500);
    });
  });
})();
