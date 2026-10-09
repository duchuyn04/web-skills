/* about-checker: checker-wave-flip, checker-tile-swap.
   Builds a 4 x 3 board: photo tiles on the dark squares of a checkerboard, flat tinted tiles on the light ones.
   When the board is seen the tiles turn in as a diagonal wave (rotateY from -90deg, 0.6s, 80ms per diagonal).
   Then every 3s, while the board is on screen, one photo and a tinted tile next to it turn over (0.8s, the second
   120ms later) so the photo moves one square; extra photos (7-9) rotate in. The cycle is a GSAP tween registered with
   BL.motion.ambient, so Pause animations holds it. Reduced motion: a still board. */
(function () {
  var BL = window.BL;
  var COLS = 4, ROWS = 3, TINTS = ['a', 'b', 'c'];
  document.querySelectorAll('[data-checker]').forEach(function (grid) {
    var imgs = [].slice.call(grid.querySelectorAll('img'));
    if (imgs.length < 6) return;
    var pool = imgs.slice(6);
    var cells = [], next = 0;
    grid.textContent = '';
    grid.classList.add('is-built');

    function fill(face, kind, value) {
      face.className = 'bl-checker__face' + (face.__back ? ' bl-checker__face--back' : '') + (kind === 'tint' ? ' bl-checker__face--' + value : '');
      face.textContent = '';
      if (kind === 'photo') face.appendChild(value.cloneNode(false));
    }
    for (var r = 0; r < ROWS; r++) {
      for (var c = 0; c < COLS; c++) {
        var li = document.createElement('li');
        li.className = 'bl-checker__cell';
        var flip = document.createElement('div');
        flip.className = 'bl-checker__flip';
        var front = document.createElement('div'), back = document.createElement('div');
        back.__back = true;
        back.setAttribute('aria-hidden', 'true');
        flip.appendChild(front); flip.appendChild(back);
        li.appendChild(flip);
        grid.appendChild(li);
        var cell = { li: li, flip: flip, faces: [front, back], shown: 0, r: r, c: c, tint: TINTS[(r * COLS + c) % 3] };
        if ((r + c) % 2 === 1) { cell.kind = 'photo'; cell.img = imgs[next++]; fill(front, 'photo', cell.img); }
        else { cell.kind = 'tint'; fill(front, 'tint', cell.tint); }
        fill(back, 'none');
        cells.push(cell);
      }
    }
    if (!BL || !BL.gsap) return;
    var gsap = BL.gsap;
    var visible = false, flipping = false, moved = null;

    function at(r, c) { return r >= 0 && r < ROWS && c >= 0 && c < COLS ? cells[r * COLS + c] : null; }
    function turn(cell, delay) {
      var hidden = cell.faces[1 - cell.shown], shown = cell.faces[cell.shown];
      cell.shown = 1 - cell.shown;
      hidden.removeAttribute('aria-hidden');
      shown.setAttribute('aria-hidden', 'true');
      return gsap.to(cell.flip, { rotationY: '+=180', duration: 0.8, delay: delay, ease: 'power2.inOut' });
    }
    function swap() {
      if (flipping || !visible) return;
      var photos = cells.filter(function (x) { return x.kind === 'photo' && x !== moved; });
      var p = photos[Math.floor(Math.random() * photos.length)];
      var near = [at(p.r - 1, p.c), at(p.r + 1, p.c), at(p.r, p.c - 1), at(p.r, p.c + 1)].filter(function (x) { return x && x.kind === 'tint'; });
      if (!near.length) return;
      var t = near[Math.floor(Math.random() * near.length)];
      var img = p.img;
      if (pool.length) { pool.push(img); img = pool.shift(); }
      fill(p.faces[1 - p.shown], 'tint', t.tint);
      fill(t.faces[1 - t.shown], 'photo', img);
      var pt = p.tint; p.tint = t.tint; t.tint = pt;
      p.kind = 'tint'; p.img = null; t.kind = 'photo'; t.img = img;
      flipping = true;
      moved = t;
      turn(p, 0);
      turn(t, 0.12).eventCallback('onComplete', function () { flipping = false; });
    }

    BL.motion.media(function (reduce) {
      if (reduce) return;
      var flips = cells.map(function (x) { return x.flip; });
      gsap.set(flips, { rotationY: -90, opacity: 0 });
      var loop = null;
      BL.onVisible(grid, function () {
        gsap.to(flips, { rotationY: 0, opacity: 1, duration: 0.6, ease: 'power2.out', delay: function (i) { return 0.1 + (cells[i].r + cells[i].c) * 0.08; } });
        loop = BL.motion.ambient(gsap.to({}, { duration: 3, delay: 1.4, repeat: -1, onRepeat: swap }));
      }, 0.3);
      var io = 'IntersectionObserver' in window ? new IntersectionObserver(function (e) { visible = e[0].isIntersecting; }, { threshold: 0.2 }) : null;
      if (io) io.observe(grid); else visible = true;
      return function () {
        if (loop) loop.kill();
        if (io) io.disconnect();
        gsap.set(flips, { clearProps: 'transform,opacity' });
        flipping = false;
        cells.forEach(function (x) {
          fill(x.faces[0], x.kind, x.kind === 'photo' ? x.img : x.tint);
          fill(x.faces[1], 'none');
          x.faces[0].removeAttribute('aria-hidden'); x.faces[1].setAttribute('aria-hidden', 'true');
          x.shown = 0;
        });
      };
    });
  });
})();
