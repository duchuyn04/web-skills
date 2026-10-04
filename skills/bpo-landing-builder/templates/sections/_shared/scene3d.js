/* Shared: a small 3D toolkit for the canvas 2D heroes (orbits, particles, isometric and others; WebGL scenes use gl.js). Needs _shared/ribbons.js loaded first for its render loop,
   which stops off screen, in hidden tabs, under reduced motion and when the page-wide Pause animations switch is on.
   Everything a hero randomises comes from seed(), fed with the brand name, so two sites never get the same scene. */
(function () {
  if (window.BL3D || !window.BLRibbons) return;
  var R = window.BLRibbons;

  /* FNV-1a hash of a string, then mulberry32: the same brand always gives the same numbers */
  function seed(text) {
    var h = 2166136261 >>> 0;
    for (var i = 0; i < (text || '').length; i++) { h ^= text.charCodeAt(i); h = Math.imul(h, 16777619) >>> 0; }
    return function () {
      h = (h + 0x6D2B79F5) >>> 0;
      var t = h;
      t = Math.imul(t ^ (t >>> 15), t | 1);
      t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  function rotate(p, ax, ay) {
    var cy = Math.cos(ay), sy = Math.sin(ay), cx = Math.cos(ax), sx = Math.sin(ax);
    var x = p[0] * cy + p[2] * sy, z = -p[0] * sy + p[2] * cy;
    var y = p[1] * cx - z * sx;
    return [x, y, p[1] * sx + z * cx];
  }

  /* perspective projection: returns [screenX, screenY, scale, depth] with depth > 0 in front of the camera */
  function project(p, cx, cy, focal, dist) {
    var d = dist + p[2];
    var s = focal / Math.max(d, 1);
    return [cx + p[0] * s, cy + p[1] * s, s, dist - p[2]];
  }

  /* pointer position over an element, smoothed, in -1..1 on both axes (fine pointers only) */
  function pointer(el) {
    var st = { x: 0, y: 0, tx: 0, ty: 0 };
    if (window.BL && window.BL.FINE && !R.RM) {
      el.addEventListener('pointermove', function (e) {
        var r = el.getBoundingClientRect();
        st.tx = ((e.clientX - r.left) / r.width) * 2 - 1;
        st.ty = ((e.clientY - r.top) / r.height) * 2 - 1;
      }, { passive: true });
      el.addEventListener('pointerleave', function () { st.tx = 0; st.ty = 0; });
    }
    st.step = function (k) { st.x += (st.tx - st.x) * (k || 0.08); st.y += (st.ty - st.y) * (k || 0.08); return st; };
    return st;
  }

  function rgb(cssColor) {
    var m = /^#?([0-9a-f]{6})$/i.exec((cssColor || '').trim());
    if (!m) return [255, 255, 255];
    var n = parseInt(m[1], 16);
    return [(n >> 16) & 255, (n >> 8) & 255, n & 255];
  }
  function rgba(c, a) { return 'rgba(' + c[0] + ',' + c[1] + ',' + c[2] + ',' + a.toFixed(3) + ')'; }
  function mixRgb(a, b, t) { return [0, 1, 2].map(function (i) { return Math.round(a[i] + (b[i] - a[i]) * t); }); }

  /* canvas at a fixed backing ratio: 1 for soft, many-element scenes (see Motion and performance) */
  function fit(canvas, ratio) {
    var r = canvas.getBoundingClientRect();
    var w = Math.max(1, Math.round(r.width)), h = Math.max(1, Math.round(r.height));
    var k = ratio || 1;
    if (canvas.width !== Math.round(w * k) || canvas.height !== Math.round(h * k)) { canvas.width = Math.round(w * k); canvas.height = Math.round(h * k); }
    return { w: w, h: h, k: k };
  }

  /* throttle an ambient scene to about 30 fps; returns true when this frame should draw */
  function throttle() {
    var last = 0;
    return function (ts, busy) { if (busy || R.RM || ts - last >= 32) { last = ts; return true; } return false; };
  }

  /* sample the pixels of a short text into points in -1..1 (x) around the origin, for particle shapes */
  function textPoints(text, font, count, rnd) {
    var c = document.createElement('canvas');
    c.width = 240; c.height = 140;
    var x = c.getContext('2d', { willReadFrequently: true });
    x.fillStyle = '#fff';
    x.textAlign = 'center'; x.textBaseline = 'middle';
    var size = 120;
    x.font = '800 ' + size + 'px ' + font;
    while (x.measureText(text).width > 220 && size > 40) { size -= 6; x.font = '800 ' + size + 'px ' + font; }
    x.fillText(text, 120, 74);
    var d = x.getImageData(0, 0, 240, 140).data, hits = [];
    for (var yy = 0; yy < 140; yy += 2) for (var xx = 0; xx < 240; xx += 2) if (d[(yy * 240 + xx) * 4 + 3] > 128) hits.push([xx, yy]);
    var out = [];
    for (var i = 0; i < count; i++) {
      var hpt = hits.length ? hits[Math.floor(rnd() * hits.length)] : [120, 70];
      out.push([(hpt[0] - 120) / 110, (hpt[1] - 70) / 110, (rnd() - 0.5) * 0.22]);
    }
    return out;
  }

  window.BL3D = { R: R, RM: R.RM, loop: R.loop, seed: seed, rotate: rotate, project: project, pointer: pointer,
    rgb: rgb, rgba: rgba, mixRgb: mixRgb, fit: fit, throttle: throttle, textPoints: textPoints };
})();
