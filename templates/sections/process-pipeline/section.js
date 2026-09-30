/* process-pipeline: builds the isometric stations and pipes as one static SVG from the steps in the list, then moves
   small HTML packets along the pipes with transform-only Web Animations (grey on the way in, brand colour once
   processed, a tick after the checking step). The lit station steps along the line every few seconds; hovering a
   step lights its station. Packets run only while the diagram is on screen and stop with the page-wide Pause switch;
   reduced motion shows one packet resting on each pipe. Iso axes: x goes down-right, y goes down-left, z goes up. */
(function () {
  var BL = window.BL;
  if (!BL) return;
  var NS = 'http://www.w3.org/2000/svg';
  var C30 = 0.8660254, S = 200, Y0 = 118, G = S / (2 * C30), HALF = 33, QA = ['shield-check', 'clipboard-check', 'check-circle', 'check', 'search', 'eye'];
  function iso(x, y, z) { return [C30 * (x - y), 0.5 * (x + y) - z]; }
  function el(name, attrs, parent) {
    var n = document.createElementNS(NS, name);
    Object.keys(attrs).forEach(function (k) { n.setAttribute(k, attrs[k]); });
    if (parent) parent.appendChild(n);
    return n;
  }
  function pts(list, ox) { return list.map(function (p) { return (p[0] + ox).toFixed(1) + ',' + (p[1] + Y0).toFixed(1); }).join(' '); }

  document.querySelectorAll('[data-ppl]').forEach(function (sec) {
    var st = BL.stage3d ? BL.stage3d(sec) : { rnd: Math.random, paused: false, onMotion: function () {} };
    var rnd = st.rnd;
    var steps = Array.prototype.slice.call(sec.querySelectorAll('[data-ppl-step]'));
    var n = steps.length;
    if (n < 2) return;
    var diagram = sec.querySelector('[data-ppl-diagram]'), svg = sec.querySelector('[data-ppl-svg]'), layer = sec.querySelector('[data-ppl-packets]');
    var kinds = {};
    sec.querySelectorAll('[data-ppl-kinds] [data-kind]').forEach(function (k) { kinds[k.getAttribute('data-kind')] = k.innerHTML; });
    var heights = steps.map(function () { return 46 + Math.round(rnd() * 22); });
    var pz = 14 + Math.round(rnd() * 6);
    var dur = 3000 + rnd() * 1200;
    var qa = -1;
    steps.forEach(function (s, i) { if (qa < 0 && QA.indexOf(s.getAttribute('data-icon')) >= 0) qa = i; });
    if (qa < 0) qa = n - 1;
    var W = S * n, vbH = 185;
    svg.setAttribute('viewBox', '0 0 ' + W + ' ' + vbH);

    /* pipes: intake into station 0, a V between each pair (out along +x, back along -y), exit from the last station */
    var routes = [];
    function cx(k) { return S / 2 + S * k; }
    var A = iso(HALF, 0, pz), B = iso(G, 0, pz), Cc = iso(G, -G + HALF, pz);
    routes.push([[cx(0) - S / 2, Y0 + B[1]], [cx(0) - A[0], Y0 + A[1]]]);
    for (var k = 0; k < n - 1; k++) routes.push([[cx(k) + A[0], Y0 + A[1]], [cx(k) + B[0], Y0 + B[1]], [cx(k) + Cc[0], Y0 + Cc[1]]]);
    routes.push([[cx(n - 1) + A[0], Y0 + A[1]], [cx(n - 1) + S / 2, Y0 + B[1]]]);

    var gShadow = el('g', {}, svg), gPipes = el('g', {}, svg), gSt = el('g', {}, svg);
    routes.forEach(function (r, i) {
      var d = r.map(function (p, j) { return (j ? 'L' : 'M') + p[0].toFixed(1) + ' ' + p[1].toFixed(1); }).join('');
      el('path', { d: d, 'class': 'bl-ppl__pipe-o' }, gPipes);
      el('path', { d: d, 'class': 'bl-ppl__pipe-i' }, gPipes);
      if (r.length === 3) el('ellipse', { cx: r[1][0].toFixed(1), cy: r[1][1].toFixed(1), rx: 8, ry: 4.6, 'class': 'bl-ppl__joint' }, gPipes);
    });
    var stations = steps.map(function (s, i) {
      var h = heights[i], x0 = cx(i);
      var sh = HALF + 9;
      el('polygon', { points: pts([iso(sh, sh + 8, 0), iso(sh, -sh, 0), iso(-sh, -sh, 0), iso(-sh, sh + 8, 0)], x0), 'class': 'bl-ppl__shadow' }, gShadow);
      var g = el('g', { 'class': 'bl-ppl__st' }, gSt);
      g.style.setProperty('--i', String(i));
      el('polygon', { points: pts([iso(-HALF, HALF, h), iso(HALF, HALF, h), iso(HALF, HALF, 0), iso(-HALF, HALF, 0)], x0), 'class': 'bl-ppl__f bl-ppl__f--l' }, g);
      el('polygon', { points: pts([iso(HALF, HALF, h), iso(HALF, -HALF, h), iso(HALF, -HALF, 0), iso(HALF, HALF, 0)], x0), 'class': 'bl-ppl__f bl-ppl__f--r' }, g);
      el('polygon', { points: pts([iso(-HALF, -HALF, h), iso(HALF, -HALF, h), iso(HALF, HALF, h), iso(-HALF, HALF, h)], x0), 'class': 'bl-ppl__f bl-ppl__f--top' }, g);
      var icon = s.querySelector('.bl-ppl__icon svg');
      if (icon) {
        var holder = el('g', { 'class': 'bl-ppl__glyph', transform: 'matrix(1.1 .635 -1.1 .635 ' + x0 + ' ' + (Y0 - h) + ')' }, g);
        var copy = icon.cloneNode(true);
        copy.setAttribute('x', '-12'); copy.setAttribute('y', '-12'); copy.setAttribute('width', '24'); copy.setAttribute('height', '24');
        holder.appendChild(copy);
      }
      return g;
    });

    /* lit station */
    var lit = -1, hold = -1, visible = false;
    function light(i) {
      lit = i;
      stations.forEach(function (g, k) { g.classList.toggle('is-lit', k === i); });
      steps.forEach(function (s, k) { s.classList.toggle('is-lit', k === i); });
    }
    steps.forEach(function (s, i) {
      s.addEventListener('pointerenter', function () { hold = i; light(i); });
      s.addEventListener('pointerleave', function () { hold = -1; });
    });
    if (BL.gsap) BL.motion.ambient(BL.gsap.to({}, { duration: 2.4, repeat: -1, onRepeat: function () {
      if (hold >= 0 || !visible || BL.RM) return;
      light((lit + 1) % n);
    } }));

    /* packets */
    var anims = [];
    function packet(kind, done, tick) {
      var p = document.createElement('span');
      p.className = 'bl-ppl__pk' + (done ? ' bl-ppl__pk--done' : '');
      p.innerHTML = kinds[kind] || kinds.doc || '';
      if (tick) { var i = document.createElement('i'); i.innerHTML = kinds.tick || ''; p.appendChild(i); }
      layer.appendChild(p);
      return p;
    }
    function build() {
      anims.forEach(function (a) { a.cancel(); });
      anims = [];
      layer.textContent = '';
      var scale = diagram.clientWidth / W;
      if (!scale) return;
      var pk = Math.max(9, Math.min(24, 26 * scale));
      diagram.style.setProperty('--pk', pk.toFixed(1) + 'px');
      var per = scale < 0.5 ? 1 : n > 4 ? 2 : 3;
      routes.forEach(function (r, i) {
        var kind = steps[Math.min(i, n - 1)].getAttribute('data-packet') || 'doc';
        var done = i > 0, tick = i > 0 && i - 1 >= qa;
        var lens = [0], total = 0;
        for (var j = 1; j < r.length; j++) { total += Math.hypot(r[j][0] - r[j - 1][0], r[j][1] - r[j - 1][1]); lens.push(total); }
        function at(p) { return 'translate3d(' + (p[0] * scale - pk / 2).toFixed(1) + 'px,' + (p[1] * scale - pk / 2).toFixed(1) + 'px,0)'; }
        if (BL.RM) {
          var still = packet(kind, done, tick), mid = r[Math.floor(r.length / 2)];
          if (r.length === 2) mid = [(r[0][0] + r[1][0]) / 2, (r[0][1] + r[1][1]) / 2];
          still.style.transform = at(mid); still.style.opacity = '1';
          return;
        }
        var frames = r.map(function (p, j) { return { transform: at(p), offset: lens[j] / total }; });
        frames[0].opacity = 0; frames[frames.length - 1].opacity = 0;
        frames.splice(1, 0, { opacity: 1, offset: 0.12 });
        frames.splice(frames.length - 1, 0, { opacity: 1, offset: 0.88 });
        frames.sort(function (a, b) { return a.offset - b.offset; });
        var d = dur * (r.length === 2 ? 0.62 : 1);
        for (var q = 0; q < per; q++) {
          var a = packet(kind, done, tick).animate(frames, { duration: d, iterations: Infinity, delay: -d * (q / per + i * 0.17), easing: 'linear' });
          if (!visible || BL.paused) a.pause();
          anims.push(a);
        }
      });
    }
    function run() { anims.forEach(function (a) { if (visible && !BL.paused) a.play(); else a.pause(); }); }
    st.onMotion(run);
    if ('IntersectionObserver' in window) {
      new IntersectionObserver(function (e) { visible = e[0].isIntersecting; run(); }, { threshold: 0 }).observe(diagram);
    } else visible = true;
    build();
    BL.onVisible(sec, function () { sec.classList.add('is-in'); if (lit < 0) light(0); }, 0.15);
    var rt = 0, lastW = diagram.clientWidth;
    window.addEventListener('resize', function () {
      clearTimeout(rt);
      rt = setTimeout(function () { if (diagram.clientWidth !== lastW) { lastW = diagram.clientWidth; build(); } }, 200);
    });
  });
})();
