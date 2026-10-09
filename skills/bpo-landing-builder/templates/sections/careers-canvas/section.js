/* careers-canvas: photo-board-drift-in, photo-board-drag-glide, drag-chip-follow.
   Board mode (wide screen, mouse): the board is 1.6-1.8 times the view each way, photos placed one per cell with a
   seeded offset, size and tilt (seed: the brand name). Dragging moves the board with GSAP; on release it glides on
   from the release speed (0.9s power3.out) and stops at the edges. Arrow keys pan 160px, Home centres it.
   Reduced motion: dragging and keys still work, without the glide and the drift-in. */
(function () {
  var BL = window.BL;
  if (!BL || !BL.gsap) return;
  var gsap = BL.gsap;
  var boardMode = window.matchMedia('(min-width: 761px) and (hover: hover)');

  function rng(seed) {
    var h = 1779033703 ^ seed.length;
    for (var i = 0; i < seed.length; i++) { h = Math.imul(h ^ seed.charCodeAt(i), 3432918353); h = (h << 13) | (h >>> 19); }
    return function () {
      h = Math.imul(h ^ (h >>> 16), 2246822507); h = Math.imul(h ^ (h >>> 13), 3266489909);
      var t = (h ^= h >>> 16) >>> 0;
      return t / 4294967296;
    };
  }
  function clamp(v, lo, hi) { return Math.max(lo, Math.min(hi, v)); }

  document.querySelectorAll('[data-ccanvas]').forEach(function (root) {
    var view = root.querySelector('[data-ccanvas-view]');
    var board = root.querySelector('[data-ccanvas-board]');
    var chip = root.querySelector('[data-ccanvas-chip]');
    var photos = [].slice.call(board.children);
    var pos = { x: 0, y: 0 }, bounds = { minX: 0, minY: 0 }, glide = null, on = false;
    var chipX = gsap.quickTo(chip, 'x', { duration: 0.35, ease: 'power3.out' });
    var chipY = gsap.quickTo(chip, 'y', { duration: 0.35, ease: 'power3.out' });

    function place() {
      if (glide) glide.kill();
      on = boardMode.matches;
      view.classList.toggle('is-board', on);
      if (!on) {
        gsap.set(board, { clearProps: 'transform,width,height' });
        photos.forEach(function (p) { p.removeAttribute('style'); });
        return;
      }
      var r = rng(root.getAttribute('data-seed') || 'board');
      var W = view.clientWidth, H = view.clientHeight;
      var n = photos.length;
      var BW = Math.round(W * (1.35 + n * 0.03)), BH = Math.round(H * (1.3 + n * 0.025));
      /* a grid with more cells than photos; cells under the careers card (at the starting, centred view) stay
         empty and the photos take the cells nearest the centre, so the first view is full around the card */
      var card = root.querySelector('.bl-ccanvas__card');
      var cols = Math.max(4, Math.round(Math.sqrt(n * 1.7 * BW / BH))), rows = Math.max(3, Math.ceil(n * 1.7 / cols));
      var cw = BW / cols, ch = BH / rows;
      var hx = card.offsetWidth * 0.42, hy = card.offsetHeight * 0.42;
      var free = [];
      for (var k = 0; k < cols * rows; k++) {
        var cx = (k % cols + 0.5) * cw - BW / 2, cy = (Math.floor(k / cols) + 0.5) * ch - BH / 2;
        if (Math.abs(cx) < hx && Math.abs(cy) < hy) continue;
        free.push({ k: k, d: Math.abs(cx) / W + Math.abs(cy) / H + r() * 0.15 });
      }
      free.sort(function (a, b) { return a.d - b.d; });
      photos.forEach(function (p, i) {
        var cell = free[i % free.length].k;
        var c = cell % cols, row = Math.floor(cell / cols);
        var tall = r() < 0.35;
        var w = cw * (0.72 + r() * 0.16), h = w * (tall ? 1.25 : 0.75);
        if (h > ch * 0.9) { w *= ch * 0.9 / h; h = ch * 0.9; }
        var x = c * cw + r() * (cw - w), y = row * ch + r() * (ch - h);
        p.style.cssText = 'left:' + x.toFixed(1) + 'px;top:' + y.toFixed(1) + 'px;width:' + w.toFixed(1) + 'px;height:' + h.toFixed(1) + 'px;--r:' + ((r() * 2 - 1) * 6).toFixed(2) + 'deg';
      });
      board.style.width = BW + 'px';
      board.style.height = BH + 'px';
      bounds.minX = W - BW; bounds.minY = H - BH;
      pos.x = Math.round(bounds.minX / 2); pos.y = Math.round(bounds.minY / 2);
      gsap.set(board, { x: pos.x, y: pos.y });
    }

    function moveTo(x, y, dur) {
      pos.x = clamp(x, bounds.minX, 0); pos.y = clamp(y, bounds.minY, 0);
      if (glide) glide.kill();
      if (!dur || BL.RM) { gsap.set(board, { x: pos.x, y: pos.y }); return; }
      glide = gsap.to(board, { x: pos.x, y: pos.y, duration: dur, ease: 'power3.out' });
    }

    /* drag */
    var drag = null;
    view.addEventListener('pointerdown', function (e) {
      if (!on || e.button !== 0 || e.target.closest('.bl-ccanvas__card')) return;
      if (glide) glide.kill();
      var cur = { x: gsap.getProperty(board, 'x'), y: gsap.getProperty(board, 'y') };
      drag = { sx: e.clientX, sy: e.clientY, bx: cur.x, by: cur.y, t: performance.now(), lx: e.clientX, ly: e.clientY, vx: 0, vy: 0 };
      view.setPointerCapture(e.pointerId);
      view.classList.add('is-dragging');
      e.preventDefault();
    });
    view.addEventListener('pointermove', function (e) {
      if (on && BL.FINE) {
        var over = !e.target.closest('.bl-ccanvas__card') || drag;
        view.classList.toggle('is-chip', !!over);
        var vr = view.getBoundingClientRect();
        chipX(e.clientX - vr.left); chipY(e.clientY - vr.top);
      }
      if (!drag) return;
      var now = performance.now(), dt = Math.max(1, now - drag.t);
      drag.vx = drag.vx * 0.6 + (e.clientX - drag.lx) / dt * 0.4;
      drag.vy = drag.vy * 0.6 + (e.clientY - drag.ly) / dt * 0.4;
      drag.lx = e.clientX; drag.ly = e.clientY; drag.t = now;
      moveTo(drag.bx + e.clientX - drag.sx, drag.by + e.clientY - drag.sy, 0);
    });
    function release() {
      if (!drag) return;
      var d = drag; drag = null;
      view.classList.remove('is-dragging');
      if (!BL.RM && performance.now() - d.t < 90) moveTo(pos.x + d.vx * 320, pos.y + d.vy * 320, 0.9);
    }
    view.addEventListener('pointerup', release);
    view.addEventListener('pointercancel', release);
    view.addEventListener('pointerleave', function () { if (!drag) view.classList.remove('is-chip'); });

    /* keyboard */
    view.addEventListener('keydown', function (e) {
      if (!on) return;
      var step = 160, k = e.key;
      if (k === 'ArrowLeft') moveTo(pos.x + step, pos.y, 0.45);
      else if (k === 'ArrowRight') moveTo(pos.x - step, pos.y, 0.45);
      else if (k === 'ArrowUp') moveTo(pos.x, pos.y + step, 0.45);
      else if (k === 'ArrowDown') moveTo(pos.x, pos.y - step, 0.45);
      else if (k === 'Home') moveTo(bounds.minX / 2, bounds.minY / 2, 0.45);
      else return;
      e.preventDefault();
    });

    place();
    var lastW = view.clientWidth;
    if ('ResizeObserver' in window) {
      new ResizeObserver(function () { if (Math.abs(view.clientWidth - lastW) > 2) { lastW = view.clientWidth; place(); } }).observe(view);
    }
    if (boardMode.addEventListener) boardMode.addEventListener('change', place);

    /* photo-board-drift-in: once, when the board is first seen */
    BL.onVisible(view, function () {
      if (BL.RM || !on) return;
      gsap.from(photos, { y: -40, scale: 1.12, opacity: 0, duration: 0.9, ease: 'power3.out', stagger: { each: 0.05, from: 'random' }, clearProps: 'opacity,transform' });
    }, 0.25);
  });
})();
