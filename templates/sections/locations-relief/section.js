/* locations-relief: crops the dotted world map to the hubs (same lat/lon to map conversion as build.py: x and y in
   percent of the 1440 x 540 map), places a column and an upright label on each hub, and draws thin arcs to the head
   office. Column height follows headcount on a log scale only when every hub has a number; otherwise all columns
   are equal. Hovering or focusing a hub card lifts its column and draws its arc. The rise is one-shot, under 3 s. */
(function () {
  var BL = window.BL;
  if (!BL) return;
  var MW = 1440, MH = 540, NS = 'http://www.w3.org/2000/svg';
  function num(text) {
    var m = /(\d[\d,.]*)/.exec(text || '');
    if (!m) return NaN;
    return parseFloat(m[1].replace(/,/g, ''));
  }
  document.querySelectorAll('[data-lrel]').forEach(function (sec) {
    var st = BL.stage3d ? BL.stage3d(sec) : { rnd: Math.random };
    var rnd = st.rnd;
    rnd(); rnd();
    var rig = sec.querySelector('[data-lrel-rig]');
    var dots = sec.querySelector('[data-lrel-plate] .bl-map__dots');
    var arcs = sec.querySelector('[data-lrel-arcs]');
    var cols = Array.prototype.slice.call(sec.querySelectorAll('[data-col]'));
    var tags = Array.prototype.slice.call(sec.querySelectorAll('[data-tag]'));
    var cards = Array.prototype.slice.call(sec.querySelectorAll('[data-hub-card]'));
    sec.style.setProperty('--dot', (3.2 + rnd() * 1.2).toFixed(2));
    var soft = rnd() < 0.5 ? 1 : 0;
    var hq = cols.findIndex(function (c) { return c.getAttribute('data-hq') === 'true'; });
    cols.forEach(function (c, i) { if (i !== hq && (i + soft) % 2 === 0) c.setAttribute('data-tint', 'soft'); });
    var hubs = cols.map(function (c) {
      return { mx: parseFloat(c.getAttribute('data-x')) / 100 * MW, my: parseFloat(c.getAttribute('data-y')) / 100 * MH, n: num(c.getAttribute('data-headcount')) };
    });
    var scaled = hubs.every(function (h) { return h.n > 0; });
    var lo = Math.min.apply(null, hubs.map(function (h) { return h.n; })), hi = Math.max.apply(null, hubs.map(function (h) { return h.n; }));
    var hot = [];

    function layout() {
      var pw = rig.offsetWidth, ph = rig.offsetHeight;
      if (!pw || !ph) return;
      var A = pw / ph;
      var xs = hubs.map(function (h) { return h.mx; }), ys = hubs.map(function (h) { return h.my; });
      var bx0 = Math.min.apply(null, xs), bx1 = Math.max.apply(null, xs), by0 = Math.min.apply(null, ys), by1 = Math.max.apply(null, ys);
      var pad = 60 + 0.2 * Math.max(bx1 - bx0, (by1 - by0) * A);
      var vw = Math.max(bx1 - bx0 + 2 * pad, (by1 - by0 + 2 * pad) * A, 620), vh = vw / A;
      if (vw > MW) { vw = MW; vh = vw / A; }
      if (vh > MH) { vh = MH; vw = Math.max(vh * A, Math.min(MW, bx1 - bx0 + 2 * pad)); }
      var x0 = Math.min(Math.max((bx0 + bx1) / 2 - vw / 2, 0), Math.max(0, MW - vw));
      var y0 = Math.min(Math.max((by0 + by1) / 2 - vh / 2, 0), Math.max(0, MH - vh));
      if (vw >= MW) x0 = (MW - vw) / 2;
      var vb = x0.toFixed(1) + ' ' + y0.toFixed(1) + ' ' + vw.toFixed(1) + ' ' + vh.toFixed(1);
      dots.setAttribute('viewBox', vb);
      dots.setAttribute('preserveAspectRatio', 'none');
      arcs.setAttribute('viewBox', vb);
      var u = pw / 920;
      cols.forEach(function (c, i) {
        var h = hubs[i];
        var px = ((h.mx - x0) / vw * 100).toFixed(2) + '%', py = ((h.my - y0) / vh * 100).toFixed(2) + '%';
        var t = scaled && hi > lo ? (Math.log(h.n) - Math.log(lo)) / (Math.log(hi) - Math.log(lo)) : 0.55;
        var ch = Math.max(34, (46 + t * 104) * Math.max(0.6, u)).toFixed(0) + 'px';
        [c, tags[i]].forEach(function (e) { e.style.setProperty('--px', px); e.style.setProperty('--py', py); e.style.setProperty('--ch', ch); });
      });
      /* arcs: a faint dashed line from every hub to the head office, plus one that draws in on hover or focus */
      arcs.textContent = '';
      hot = [];
      if (hq >= 0) {
        var H = hubs[hq];
        hubs.forEach(function (h, i) {
          if (i === hq) { hot.push(null); return; }
          var mx = (h.mx + H.mx) / 2, my = (h.my + H.my) / 2, dx = H.mx - h.mx, dy = H.my - h.my, len = Math.hypot(dx, dy) || 1;
          var bend = 0.22 * len;
          var d = 'M' + h.mx.toFixed(1) + ' ' + h.my.toFixed(1) + 'Q' + (mx + dy / len * bend).toFixed(1) + ' ' + (my - Math.abs(dx) / len * bend).toFixed(1) + ' ' + H.mx.toFixed(1) + ' ' + H.my.toFixed(1);
          var sw = (vw / pw * 1.4).toFixed(2);
          var base = document.createElementNS(NS, 'path');
          base.setAttribute('d', d); base.setAttribute('class', 'bl-lrel__arc'); base.style.strokeWidth = sw;
          base.style.strokeDasharray = (vw / pw * 3).toFixed(2) + ' ' + (vw / pw * 6).toFixed(2);
          arcs.appendChild(base);
          var top = document.createElementNS(NS, 'path');
          top.setAttribute('d', d); top.setAttribute('pathLength', '1'); top.setAttribute('class', 'bl-lrel__arc bl-lrel__arc--hot'); top.style.strokeWidth = (vw / pw * 2.4).toFixed(2);
          arcs.appendChild(top);
          hot.push(top);
        });
      }
      /* measure labels after the first paint and again once web fonts are in */
      requestAnimationFrame(function () { requestAnimationFrame(declutter); });
    }

    /* move labels that overlap each other or a nearer column, measured in the final pose */
    function declutter() {
      var wasIn = sec.classList.contains('is-in');
      sec.classList.add('is-measuring', 'is-in');
      tags.forEach(function (t) { t.style.setProperty('--lift', '0px'); t.style.setProperty('--shift', '0px'); });
      var list = tags.map(function (t) { return { t: t, r: t.getBoundingClientRect() }; });
      /* the columns count as obstacles too, so a label never hides behind a neighbouring column */
      var placed = [], bars = cols.map(function (c) {
        var f = c.querySelector('.bl-lrel__f--front').getBoundingClientRect(), t = c.querySelector('.bl-lrel__f--top').getBoundingClientRect();
        return { l: Math.min(f.left, t.left), r: Math.max(f.right, t.right), t: Math.min(f.top, t.top), b: Math.max(f.bottom, t.bottom) };
      });
      /* nearest hub first: its label stays low and labels further back rise behind it, so their stems pass behind */
      list.sort(function (a, b) { return bars[tags.indexOf(b.t)].b - bars[tags.indexOf(a.t)].b; });
      var box = sec.querySelector('[data-lrel-stage]').getBoundingClientRect();
      list.forEach(function (it) {
        var own = tags.indexOf(it.t), w = it.r.width, h = it.r.height, k = h / Math.max(1, it.t.offsetHeight);
        var others = placed.concat(bars.filter(function (x, j) { return j !== own; }));
        /* try nearby spots (sideways first, then up) and keep the cheapest one that overlaps nothing */
        var cands = [];
        [0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4].forEach(function (u) {
          [0, 0.2, -0.2, 0.4, -0.4].forEach(function (sx) { cands.push({ dx: sx * w, dy: u * (h + 8), cost: Math.abs(sx) * w * 0.5 + u * (h + 8) }); });
        });
        cands.sort(function (a, b) { return a.cost - b.cost; });
        var pick = cands[cands.length - 1];
        for (var c = 0; c < cands.length; c++) {
          var q = cands[c], r = { l: it.r.left + q.dx, r: it.r.right + q.dx, t: it.r.top - q.dy, b: it.r.bottom - q.dy };
          if (r.l < box.left + 4 || r.r > box.right - 4) continue;
          var clash = others.some(function (p) { return r.l < p.r + 4 && r.r > p.l - 4 && r.t < p.b + 4 && r.b > p.t - 4; });
          if (!clash) { pick = q; break; }
        }
        placed.push({ l: it.r.left + pick.dx, r: it.r.right + pick.dx, t: it.r.top - pick.dy, b: it.r.bottom - pick.dy });
        it.t.style.setProperty('--lift', (pick.dy / Math.max(0.3, k)).toFixed(1) + 'px');
        it.t.style.setProperty('--shift', (pick.dx / Math.max(0.3, k)).toFixed(1) + 'px');
      });
      void sec.offsetWidth;
      if (!wasIn) sec.classList.remove('is-in');
      void sec.offsetWidth;
      sec.classList.remove('is-measuring');
    }

    function setHot(i, on) {
      cols[i].classList.toggle('is-hot', on);
      tags[i].classList.toggle('is-hot', on);
      tags[i].style.setProperty('--rise', on ? '1.18' : '1');
      cards[i].classList.toggle('is-hot', on);
      if (hot[i]) hot[i].classList.toggle('is-on', on);
    }
    cards.forEach(function (card, i) {
      card.addEventListener('pointerenter', function () { setHot(i, true); });
      card.addEventListener('pointerleave', function () { if (document.activeElement !== card) setHot(i, false); });
      card.addEventListener('focus', function () { setHot(i, true); });
      card.addEventListener('blur', function () { setHot(i, false); });
    });

    layout();
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(function () { requestAnimationFrame(declutter); });
    if (BL.RM) sec.classList.add('is-in');
    else BL.onVisible(sec.querySelector('[data-lrel-stage]'), function () { requestAnimationFrame(function () { sec.classList.add('is-in'); }); }, 0.2);
    var rt = 0, lastW = rig.offsetWidth;
    window.addEventListener('resize', function () {
      clearTimeout(rt);
      rt = setTimeout(function () { if (rig.offsetWidth !== lastW) { lastW = rig.offsetWidth; layout(); } }, 200);
    });
  });
})();
