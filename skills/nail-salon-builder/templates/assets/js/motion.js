/* Motion variants of the public site (references/patterns.md, Motion). No library: IntersectionObserver starts the
   one-off effects, one scroll handler (one requestAnimationFrame per scrolled frame) drives the pinned rows, the drop
   pile, the inked paragraph and the price list spy, and requestAnimationFrame runs otherwise only while a promo code
   resolves. Loops are CSS animations or timers that rest off screen, in a hidden tab and on the footer pause switch.
   Only transform and opacity move; prefers-reduced-motion is read live. */
(function () {
  'use strict';
  var doc = document, root = doc.documentElement;
  var RMQ = matchMedia('(prefers-reduced-motion: reduce)');
  var WIDE = matchMedia('(min-width: 1081px)');
  var BOARD = matchMedia('(min-width: 761px) and (hover: hover) and (pointer: fine)');
  function rm() { return RMQ.matches; }
  function $$(s, el) { return [].slice.call((el || doc).querySelectorAll(s)); }
  function clamp(v, a, b) { return v < a ? a : v > b ? b : v; }
  function ease(t) { return 1 - Math.pow(1 - t, 3); }
  /* small seeded random so tilts and board positions stay the same for one salon */
  function rand(seed) {
    var h = 2166136261;
    for (var i = 0; i < seed.length; i++) h = Math.imul(h ^ seed.charCodeAt(i), 16777619);
    return function () { h = Math.imul(h ^ (h >>> 15), 2246822507); h = Math.imul(h ^ (h >>> 13), 3266489909); return ((h ^= h >>> 16) >>> 0) / 4294967296; };
  }
  function once(el, cb, th) {
    if (!('IntersectionObserver' in window)) { cb(); return; }
    var io = new IntersectionObserver(function (es) { if (es[0].isIntersecting) { io.disconnect(); cb(); } }, { threshold: th == null ? 0.25 : th });
    io.observe(el);
  }
  function watch(el, cb) {
    if (!('IntersectionObserver' in window)) { cb(true); return; }
    new IntersectionObserver(function (es) { cb(es[0].isIntersecting); }).observe(el);
  }
  function headerH() { var h = doc.querySelector('.hdr'); return h ? h.offsetHeight : 0; }

  /* pause switch in the footer: freezes the CSS loops (html[data-motion=paused]) and the timers */
  var paused = false;
  var onPause = [];
  function setPaused(p) {
    paused = p;
    root.setAttribute('data-motion', p ? 'paused' : 'on');
    $$('[data-motion-toggle]').forEach(function (b) {
      b.setAttribute('aria-pressed', String(p));
      var l = b.querySelector('[data-motion-label]');
      if (l) l.textContent = b.getAttribute(p ? 'data-label-play' : 'data-label-pause');
    });
    onPause.forEach(function (f) { f(); });
  }
  $$('[data-motion-toggle]').forEach(function (b) { b.addEventListener('click', function () { setPaused(!paused); }); });
  doc.addEventListener('visibilitychange', function () { onPause.forEach(function (f) { f(); }); });
  function canLoop(on) { return on && !paused && !doc.hidden && !rm(); }

  /* one scroll handler for every scroll-linked piece */
  var scrollers = [], queued = false;
  function frame() { queued = false; scrollers.forEach(function (f) { f(); }); }
  function request() { if (!queued) { queued = true; requestAnimationFrame(frame); } }
  var relayouts = [];
  function relayout() { root.style.setProperty('--hdr-h', headerH() + 'px'); relayouts.forEach(function (f) { f(); }); request(); }
  addEventListener('scroll', request, { passive: true });
  var rt;
  addEventListener('resize', function () { clearTimeout(rt); rt = setTimeout(relayout, 120); });
  if (RMQ.addEventListener) { RMQ.addEventListener('change', relayout); WIDE.addEventListener('change', relayout); BOARD.addEventListener('change', relayout); }
  addEventListener('load', relayout);

  /* categories "scroll": wide screens pin the section and move the row sideways by its overflow; elsewhere the row
     scrolls natively with snap. A bar under the row follows either. */
  $$('[data-mx-row]').forEach(function (sec) {
    var pin = sec.querySelector('.mx-row-pin'), view = sec.querySelector('[data-mx-row-view]');
    var track = sec.querySelector('[data-mx-row-track]'), bar = sec.querySelector('[data-mx-row-bar]');
    var dist = 0, pinned = false;
    function layout() {
      sec.style.height = ''; track.style.transform = '';
      pinned = WIDE.matches && !rm();
      sec.classList.toggle('is-pinned', pinned);
      pin.style.top = headerH() + 'px';
      var cs = getComputedStyle(view);
      dist = Math.max(0, track.scrollWidth - (view.clientWidth - parseFloat(cs.paddingLeft) - parseFloat(cs.paddingRight)));
      if (pinned && dist > 0) sec.style.height = (pin.offsetHeight + dist) + 'px';
    }
    function update() {
      var p;
      if (pinned && dist > 0) {
        p = clamp((headerH() - sec.getBoundingClientRect().top) / dist, 0, 1);
        track.style.transform = 'translate3d(' + (-p * dist).toFixed(1) + 'px,0,0)';
      } else {
        var max = view.scrollWidth - view.clientWidth;
        p = max > 0 ? view.scrollLeft / max : 1;
      }
      bar.style.transform = 'scaleX(' + Math.max(0.04, p).toFixed(3) + ')';
    }
    view.addEventListener('scroll', request, { passive: true });
    relayouts.push(layout); scrollers.push(update);
    layout();
  });

  /* trust "drop": the pile pins on wide screens; each next card falls from above with extra spin and lands at its
     seeded tilt over the cards before it. The counter shows the card on top. */
  $$('[data-mx-drop]').forEach(function (sec) {
    var pin = sec.querySelector('.mx-drop-pin'), cards = $$('.mx-card', sec), count = sec.querySelector('[data-mx-count]');
    var r = rand(sec.getAttribute('data-seed') || 'salon');
    var tilt = cards.map(function (c, i) { var a = 2 + r() * 5; return (i % 2 ? 1 : -1) * a; });
    var off = cards.map(function () { return [(r() - 0.5) * 28, (r() - 0.5) * 18]; });
    var steps = cards.length - 1, per = 0, pinned = false, top = -1;
    cards.forEach(function (c, i) { c.style.setProperty('--tilt', tilt[i].toFixed(2) + 'deg'); });
    function layout() {
      sec.style.height = '';
      pinned = WIDE.matches && !rm() && steps > 0;
      sec.classList.toggle('is-pinned', pinned);
      pin.style.top = headerH() + 'px';
      per = innerHeight * 0.7;
      if (pinned) sec.style.height = (pin.offsetHeight + steps * per) + 'px';
      else cards.forEach(function (c) { c.style.transform = ''; c.style.opacity = ''; });
    }
    function update() {
      if (!pinned) return;
      var s = clamp((headerH() - sec.getBoundingClientRect().top) / per, 0, steps), lead = 0;
      cards.forEach(function (c, i) {
        var e = i === 0 ? 1 : ease(clamp(s - (i - 1), 0, 1));
        if (e > 0.55) lead = i;
        var nudge = clamp(s - i, 0, 1) * 6; /* the card below shifts a little as the next one lands */
        var y = (1 - e) * -innerHeight * 0.95 + off[i][1] + nudge;
        var rot = tilt[i] + (1 - e) * 16;
        c.style.transform = 'translate3d(' + off[i][0].toFixed(1) + 'px,' + y.toFixed(1) + 'px,0) rotate(' + rot.toFixed(2) + 'deg)';
        c.style.opacity = e > 0.001 ? '1' : '0';
      });
      if (lead !== top) { top = lead; count.textContent = (lead + 1 < 10 ? '0' : '') + (lead + 1); }
    }
    relayouts.push(layout); scrollers.push(update);
    layout();
  });

  /* story "ink": each word runs from pale to full ink in reading order while the paragraph moves from 85% to 40% of
     the screen height. Words stay plain text in the paragraph, so screen readers read it as written. */
  $$('[data-mx-ink]').forEach(function (p) {
    var text = p.textContent.normalize('NFC');
    p.textContent = '';
    var words = [];
    text.split(/(\s+)/).forEach(function (part) {
      if (!part) return;
      if (/^\s+$/.test(part)) { p.appendChild(doc.createTextNode(' ')); return; }
      var w = doc.createElement('span');
      w.className = 'ink-w';
      w.textContent = part;
      p.appendChild(w); words.push(w);
    });
    var last = [];
    function update() {
      var full = rm();
      var r = p.getBoundingClientRect(), vh = innerHeight;
      var prog = full ? 1 : clamp((vh * 0.85 - r.top) / (vh * 0.45 + r.height * 0.6), 0, 1);
      var n = words.length;
      words.forEach(function (w, k) {
        var o = full ? 1 : 0.2 + 0.8 * clamp((prog * (n + 4) - k) / 4, 0, 1);
        var v = o.toFixed(2);
        if (last[k] !== v) { last[k] = v; w.style.opacity = v; }
      });
    }
    scrollers.push(update);
  });

  /* price-list "spy": the row crossing 45% of the screen lights up, the dot slides to it and the sticky panel shows its
     look, price and time (two faces cross-fade) */
  $$('[data-mx-spy]').forEach(function (box) {
    var rows = $$('[data-spy-row]', box), dot = box.querySelector('[data-spy-dot]'), list = box.querySelector('.spy-list');
    var panel = box.querySelector('[data-spy-panel]'), faces = $$('.spy-face', panel), book = panel.querySelector('.spy-book');
    var active = -1, face = 0;
    function show(i) {
      if (i === active) return;
      if (active >= 0) rows[active].classList.remove('is-on');
      active = i;
      var row = rows[i];
      row.classList.add('is-on');
      dot.style.transform = 'translate3d(0,' + (row.offsetTop + row.offsetHeight / 2 - 5) + 'px,0)';
      var f = faces[face = 1 - face];
      var img = f.querySelector('img');
      if (img.getAttribute('src') !== row.getAttribute('data-img')) img.src = row.getAttribute('data-img');
      f.querySelector('b').textContent = row.getAttribute('data-name');
      f.querySelector('.spy-p').textContent = row.getAttribute('data-price');
      f.querySelector('small').textContent = row.getAttribute('data-min');
      faces[1 - face].classList.remove('is-on');
      f.classList.add('is-on');
      book.href = row.getAttribute('data-href');
    }
    function update() {
      var line = innerHeight * 0.45, pick = 0;
      for (var i = 0; i < rows.length; i++) { if (rows[i].getBoundingClientRect().top <= line) pick = i; else break; }
      show(pick);
      list.classList.toggle('is-live', box.getBoundingClientRect().top < line && box.getBoundingClientRect().bottom > line);
    }
    scrollers.push(update);
    show(0);
  });

  /* categories "fan": the two back looks slide out from behind the front one once, card by card; after that a hover or
     focus gathers them (front 1.08, backs 8px in, 0.5 s). Cosmos measured 0.9 s for both. */
  $$('[data-mx-fan]').forEach(function (grid) {
    once(grid, function () {
      grid.classList.add('is-in');
      setTimeout(function () { grid.classList.add('is-done'); }, 150 + 120 * grid.children.length + 950);
    }, 0.2);
  });

  /* popular "marquee": rows of names drift in opposite directions as CSS animations. Each row repeats its group until it
     is wider than the screen, then doubles it so the loop has no seam; copies are hidden from screen readers and
     keyboard. Hover or focus slows the row to a fifth. Rows rest off screen, in a hidden tab and on Pause. */
  $$('[data-mx-mq]').forEach(function (sec) {
    var rows = $$('[data-mq-row]', sec);
    var on = false;
    rows.forEach(function (row) {
      var group = row.querySelector('.mq-group'), track = doc.createElement('div');
      track.className = 'mq-track';
      row.insertBefore(track, group);
      track.appendChild(group);
      function copy() {
        var c = group.cloneNode(true);
        c.setAttribute('aria-hidden', 'true');
        $$('a', c).forEach(function (a) { a.tabIndex = -1; });
        track.appendChild(c);
      }
      var reps = Math.max(1, Math.ceil((innerWidth * 1.1) / Math.max(1, group.offsetWidth)));
      for (var i = 1; i < reps; i++) copy();
      var n = track.children.length;
      for (i = 0; i < n; i++) track.appendChild(track.children[i].cloneNode(true)).setAttribute('aria-hidden', 'true');
      $$('[aria-hidden=true] a', track).forEach(function (a) { a.tabIndex = -1; });
      track.style.setProperty('--mq-dur', (track.scrollWidth / 2 / 46).toFixed(1) + 's');
      function rate(v, ms) {
        var a = track.getAnimations ? track.getAnimations()[0] : null;
        if (a && a.updatePlaybackRate) a.updatePlaybackRate(v);
        else if (a) a.playbackRate = v;
      }
      function enter(e) {
        var item = e.target.closest('.mq-item'); if (!item) return;
        sec.classList.add('is-hover');
        $$('.mq-item.is-on', sec).forEach(function (x) { x.classList.remove('is-on'); });
        item.classList.add('is-on');
        rate(0.2);
      }
      function leave() {
        sec.classList.remove('is-hover');
        $$('.mq-item.is-on', row).forEach(function (x) { x.classList.remove('is-on'); });
        rate(1);
      }
      track.addEventListener('mouseover', enter);
      track.addEventListener('mouseleave', leave);
      track.addEventListener('focusin', enter);
      track.addEventListener('focusout', leave);
    });
    function apply() { sec.classList.toggle('is-on', canLoop(on)); }
    onPause.push(apply);
    watch(sec, function (v) { on = v; apply(); });
  });

  /* gallery "canvas": looks scattered on a board wider than the screen; drag it and it glides on from the release
     speed, arrow keys pan 160 px, Home centres it, a "Kéo" chip follows a fine pointer. Phones and touch screens get a
     swipe row from CSS. */
  $$('[data-mx-board]').forEach(function (view) {
    var board = view.querySelector('.board'), items = $$('.board-item', view), chip = view.querySelector('.board-chip');
    var r = rand(view.getAttribute('data-seed') || 'salon');
    var x = 0, y = 0, minX = 0, minY = 0, live = false;
    var order = items.map(function (it, i) { return [r(), i]; }).sort(function (a, b) { return a[0] - b[0]; }).map(function (a) { return a[1]; });
    var spots = items.map(function () { return { jx: r() - 0.5, jy: r() - 0.5, rot: (r() - 0.5) * 12 }; });
    var cells = [];
    var ROWS = Math.min(3, items.length), COLS = Math.ceil(items.length / ROWS) + 1;
    for (var ci = 0; ci < ROWS * COLS; ci++) cells.push([r(), ci]);
    cells = cells.sort(function (a, b) { return a[0] - b[0]; }).slice(0, items.length).map(function (a) { return a[1]; });
    function place(tx, ty, ms) {
      x = clamp(tx, minX, 0); y = clamp(ty, minY, 0);
      board.style.transition = ms ? 'transform ' + ms + 'ms cubic-bezier(.16,1,.3,1)' : 'none';
      board.style.transform = 'translate3d(' + x.toFixed(1) + 'px,' + y.toFixed(1) + 'px,0)';
    }
    function layout() {
      live = BOARD.matches;
      view.classList.toggle('is-board', live);
      board.style.transform = ''; board.style.width = ''; board.style.height = '';
      items.forEach(function (it) { it.style.left = it.style.top = ''; it.style.setProperty('--rot', '0deg'); });
      if (!live) return;
      var vw = view.clientWidth, vh = view.clientHeight;
      /* three rows and one spare column, so a few cells stay empty and the looks read as scattered, not gridded */
      var rows = ROWS, cols = COLS;
      var bw = Math.max(vw * 1.3, cols * 330), bh = Math.max(vh * 1.25, rows * 320 + 60);
      board.style.width = bw + 'px'; board.style.height = bh + 'px';
      items.forEach(function (it, i) {
        var cell = cells[i], c = cell % cols, rr = Math.floor(cell / cols), s = spots[i];
        var cx = (c + 0.5 + s.jx * 0.36) / cols, cy = (rr + 0.5 + s.jy * 0.36) / rows;
        it.style.left = (cx * 100).toFixed(2) + '%'; it.style.top = (cy * 100).toFixed(2) + '%';
        it.style.setProperty('--rot', s.rot.toFixed(1) + 'deg');
      });
      minX = vw - bw; minY = vh - bh;
      place(minX / 2, minY / 2, 0);
    }
    relayouts.push(layout);
    layout();
    order.forEach(function (i, k) { items[i].style.setProperty('--d', (k * 50) + 'ms'); });
    once(view, function () { view.classList.add('is-in'); }, 0.15);

    var drag = null, moved = false;
    view.addEventListener('pointerdown', function (e) {
      if (!live || e.button !== 0) return;
      drag = { sx: e.clientX, sy: e.clientY, x: x, y: y, t: performance.now(), vx: 0, vy: 0, lx: e.clientX, ly: e.clientY };
      moved = false;
      view.classList.add('is-drag');
    });
    addEventListener('pointermove', function (e) {
      if (live && chip) {
        var b = view.getBoundingClientRect();
        var inside = e.clientX >= b.left && e.clientX <= b.right && e.clientY >= b.top && e.clientY <= b.bottom;
        view.classList.toggle('is-over', inside);
        if (inside) chip.style.transform = 'translate3d(' + (e.clientX - b.left).toFixed(0) + 'px,' + (e.clientY - b.top).toFixed(0) + 'px,0)';
      }
      if (!drag) return;
      var now = performance.now(), dt = Math.max(1, now - drag.t);
      drag.vx = (e.clientX - drag.lx) / dt; drag.vy = (e.clientY - drag.ly) / dt;
      drag.t = now; drag.lx = e.clientX; drag.ly = e.clientY;
      var dx = e.clientX - drag.sx, dy = e.clientY - drag.sy;
      if (Math.abs(dx) + Math.abs(dy) > 6) { moved = true; try { view.setPointerCapture(e.pointerId); } catch (err) { /* already released */ } }
      if (moved) place(drag.x + dx, drag.y + dy, 0);
    }, { passive: true });
    function release() {
      if (!drag) return;
      view.classList.remove('is-drag');
      if (moved && !rm()) place(x + drag.vx * 300, y + drag.vy * 300, 900);
      drag = null;
    }
    addEventListener('pointerup', release);
    addEventListener('pointercancel', release);
    view.addEventListener('click', function (e) { if (moved) { e.preventDefault(); e.stopPropagation(); moved = false; } }, true);
    view.addEventListener('keydown', function (e) {
      if (!live || e.target !== view) return;
      var k = e.key, d = 160, ms = rm() ? 0 : 450;
      if (k === 'ArrowLeft') place(x + d, y, ms); else if (k === 'ArrowRight') place(x - d, y, ms);
      else if (k === 'ArrowUp') place(x, y + d, ms); else if (k === 'ArrowDown') place(x, y - d, ms);
      else if (k === 'Home') place(minX / 2, minY / 2, ms); else return;
      e.preventDefault();
    });
  });

  /* gallery "checker": tiles turn in as a diagonal wave, then every 3 s one look and a tinted tile next to it turn over
     so the look moves one square; extra looks from the pool rotate in. */
  $$('[data-mx-check]').forEach(function (grid) {
    var tiles = $$('.ck-tile', grid), pool = [], on = false, timer = 0, busy = false;
    var tpl = grid.querySelector('[data-ck-pool]');
    if (tpl && tpl.content) pool = [].slice.call(tpl.content.querySelectorAll('img'));
    var r = rand('checker' + tiles.length);
    once(grid, function () { grid.classList.add('is-in'); }, 0.2);
    function cols() { return getComputedStyle(grid).gridTemplateColumns.split(' ').length; }
    function swap() {
      if (busy) return;
      var photos = tiles.filter(function (t) { return t.classList.contains('ck-photo'); });
      var p = photos[Math.floor(r() * photos.length)], i = tiles.indexOf(p), c = cols();
      var near = [i - 1, i + 1, i - c, i + c].filter(function (j) {
        return j >= 0 && j < tiles.length && tiles[j].classList.contains('ck-tint') && (Math.abs(j - i) === c || Math.floor(j / c) === Math.floor(i / c));
      });
      if (!near.length) return;
      var t = tiles[near[Math.floor(r() * near.length)]];
      busy = true;
      p.classList.add('is-turn');
      setTimeout(function () { t.classList.add('is-turn'); }, 120);
      setTimeout(function () {
        var img = p.querySelector('img');
        if (pool.length && r() < 0.5) { var next = pool.shift(); pool.push(img); img = doc.importNode(next, true); p.querySelector('img').remove(); }
        t.querySelector('.ck-face').appendChild(img);
        p.classList.replace('ck-photo', 'ck-tint'); t.classList.replace('ck-tint', 'ck-photo');
        p.classList.remove('is-turn');
        setTimeout(function () { t.classList.remove('is-turn'); busy = false; }, 120);
      }, 400);
    }
    function apply() {
      clearInterval(timer); timer = 0;
      if (canLoop(on)) timer = setInterval(swap, 3000);
    }
    onPause.push(apply);
    watch(grid, function (v) { on = v; apply(); });
  });

  /* promo codes resolve from scrambled letters once when seen (0.6 s); the button keeps the real code as its name */
  $$('[data-scramble]').forEach(function (el) {
    var text = el.textContent.normalize('NFC'), chars = Array.from(text);
    var glyphs = chars.filter(function (ch) { return /\S/.test(ch); });
    if (rm() || !glyphs.length) return;
    el.style.display = 'inline-block';
    el.style.minWidth = el.getBoundingClientRect().width + 'px';
    once(el, function () {
      if (rm()) return;
      var t0 = performance.now(), dur = 600;
      (function tick(now) {
        var p = clamp((now - t0) / dur, 0, 1), settled = Math.floor(p * chars.length);
        el.textContent = chars.map(function (ch, i) {
          return i < settled || /\s/.test(ch) ? ch : glyphs[Math.floor(Math.random() * glyphs.length)];
        }).join('');
        if (p < 1) requestAnimationFrame(tick); else el.textContent = text;
      })(t0);
    }, 0.5);
  });

  /* footer "matrix" (after Robot.com): the panel is sized to whole dot cells and the initials are drawn once at one
     pixel per cell, shown pixelated under a mask of round dots, so only whole dots light up. The band sweep and the
     blink are CSS animations on a 6 s cycle; on a fine pointer a round patch of dots follows the pointer in whole
     cells. */
  $$('[data-mx-matrix]').forEach(function (box) {
    var mark = box.querySelector('[data-mx-mark]'), band = box.querySelector('[data-mx-band]'), spot = box.querySelector('[data-mx-spot]');
    var text = mark.textContent.trim(), dot = 12, cols = 0, rows = 0, SPOT = 7, on = false;
    function bitmap(w, h, draw) {
      var c = doc.createElement('canvas'); c.width = w; c.height = h;
      var g = c.getContext('2d'); draw(g);
      var img = g.getImageData(0, 0, w, h), d = img.data;
      for (var i = 3; i < d.length; i += 4) d[i] = d[i] >= 110 ? 255 : 0;
      g.putImageData(img, 0, 0);
      return c.toDataURL();
    }
    function layout() {
      box.style.width = ''; box.style.height = '';
      dot = parseFloat(getComputedStyle(box).getPropertyValue('--dot-px')) || 12;
      cols = Math.floor(box.clientWidth / dot); rows = Math.floor(box.clientHeight / dot);
      if (cols < 4 || rows < 4) return;
      box.style.width = cols * dot + 'px'; box.style.height = rows * dot + 'px';
      var cs = getComputedStyle(mark), color = cs.color, family = cs.fontFamily;
      mark.style.backgroundImage = 'url(' + bitmap(cols, rows, function (g) {
        g.fillStyle = color; g.textAlign = 'center'; g.textBaseline = 'alphabetic';
        var size = 100;
        g.font = '700 ' + size + 'px ' + family;
        var m = g.measureText(text), asc = m.actualBoundingBoxAscent || size * 0.72, desc = m.actualBoundingBoxDescent || 0;
        size = Math.max(4, size * Math.min(rows * 0.8 / (asc + desc), cols * 0.9 / (m.width || 1)));
        g.font = '700 ' + size + 'px ' + family;
        m = g.measureText(text); asc = m.actualBoundingBoxAscent || size * 0.72; desc = m.actualBoundingBoxDescent || 0;
        g.fillText(text, cols / 2, Math.round((rows + asc - desc) / 2));
      }) + ')';
      mark.classList.add('is-raster');
      var bw = Math.max(2, Math.round(cols * 0.12));
      band.style.width = bw * dot + 'px';
      band.style.setProperty('--from', (-bw * dot) + 'px');
      band.style.setProperty('--to', (cols * dot) + 'px');
      band.style.animationTimingFunction = 'steps(' + (cols + bw) + ')';
      spot.style.width = spot.style.height = SPOT * dot + 'px';
      spot.style.backgroundImage = 'url(' + bitmap(SPOT, SPOT, function (g) {
        g.fillStyle = color; g.beginPath(); g.arc(SPOT / 2, SPOT / 2, SPOT / 2, 0, Math.PI * 2); g.fill();
      }) + ')';
    }
    relayouts.push(layout);
    layout();
    if (doc.fonts && doc.fonts.ready) doc.fonts.ready.then(layout);
    function apply() { box.classList.toggle('is-on', canLoop(on)); }
    onPause.push(apply);
    watch(box, function (v) { on = v; apply(); });
    if (matchMedia('(hover: hover) and (pointer: fine)').matches) {
      box.addEventListener('pointermove', function (e) {
        if (rm()) return;
        var b = box.getBoundingClientRect(), h = Math.floor(SPOT / 2);
        var cx = Math.floor((e.clientX - b.left) / dot) - h, cy = Math.floor((e.clientY - b.top) / dot) - h;
        spot.style.transform = 'translate3d(' + cx * dot + 'px,' + cy * dot + 'px,0)';
        box.classList.add('is-pointer');
      });
      box.addEventListener('pointerleave', function () { box.classList.remove('is-pointer'); });
    }
  });

  setPaused(false);
  relayout();
})();
