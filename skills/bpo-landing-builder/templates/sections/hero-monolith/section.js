/* hero-monolith: monolith-extrude-3d. The monogram is rendered once into small sprites: a face and five side
   shades. Each frame (30 fps cap) draws 16-24 side layers back to front, each shifted and scaled by its depth for
   the current turn, then the face with a sheen that follows the turn. The side shade of every layer depends on its
   depth and on how far the block has turned toward the light. The turn loops on BLRibbons.loop, so it stops off
   screen, in hidden tabs and with the page-wide Pause switch; reduced motion draws one three-quarter frame. */
(function () {
  var K = window.BL3D;
  document.querySelectorAll('[data-hmono]').forEach(function (sec) {
    if (!K) return;
    var canvas = sec.querySelector('[data-hmono-canvas]');
    var ctx = canvas.getContext('2d');
    var rnd = K.seed(sec.getAttribute('data-seed') || 'brand');
    var mark = (sec.getAttribute('data-mark') || 'B').slice(0, 3);
    var css = getComputedStyle(sec);
    var cAccent = K.rgb(css.getPropertyValue('--c-accent')), cBlend = K.rgb(css.getPropertyValue('--c-accent-blend'));
    var cPrimary = K.rgb(css.getPropertyValue('--c-primary'));
    var WHITE = [255, 255, 255], BLACK = [0, 0, 0];
    var font = css.getPropertyValue('--font-heading').trim() || 'serif';

    /* brand-seeded look */
    var LAYERS = 16 + Math.floor(rnd() * 9);
    var AMP = (20 + rnd() * 8) * Math.PI / 180;
    var LIGHT = rnd() < 0.5 ? -1 : 1;
    var INK = rnd() < 0.4;
    var PERIOD = 12000 + rnd() * 4000;
    var PITCH = (8 + rnd() * 4) * Math.PI / 180;
    var DEPTH = 0.3 + rnd() * 0.08;
    var PHASE = rnd() * Math.PI * 2;

    var faceTop = INK ? K.mixRgb(cPrimary, WHITE, 0.12) : K.mixRgb(cAccent, WHITE, 0.06);
    var faceBottom = INK ? cPrimary : K.mixRgb(cAccent, BLACK, 0.14);
    var rim = INK ? K.mixRgb(cBlend, WHITE, 0.2) : K.mixRgb(cAccent, WHITE, 0.45);
    var sideBase = INK ? K.mixRgb(cPrimary, cAccent, 0.18) : K.mixRgb(cAccent, cPrimary, 0.55);
    var shades = [0.55, 0.38, 0.22, 0.08, -0.08].map(function (t) { return t >= 0 ? K.mixRgb(sideBase, BLACK, t) : K.mixRgb(sideBase, WHITE, -t); });

    var R = Math.min(window.devicePixelRatio || 1, 2);
    var size = null, sp = null, gate = K.throttle(), ptr = K.pointer(sec), born = null;

    function css3(c) { return 'rgb(' + c[0] + ',' + c[1] + ',' + c[2] + ')'; }
    function sprite(w, h) { var c = document.createElement('canvas'); c.width = Math.ceil(w * R); c.height = Math.ceil(h * R); return c; }

    function build() {
      size = K.fit(canvas, R);
      var w = size.w, h = size.h;
      var fs = Math.round(h * 0.5), probe = document.createElement('canvas').getContext('2d');
      probe.font = '700 ' + fs + 'px ' + font;
      while (probe.measureText(mark).width > w * 0.64 && fs > 24) { fs -= 4; probe.font = '700 ' + fs + 'px ' + font; }
      var m = probe.measureText(mark);
      var asc = m.actualBoundingBoxAscent || fs * 0.72, desc = m.actualBoundingBoxDescent || 0;
      var pad = Math.ceil(fs * 0.04) + 2;
      var gw = Math.ceil(m.width + pad * 2), gh = Math.ceil(asc + desc + pad * 2);
      function glyph(c, fill, stroke) {
        var x = c.getContext('2d');
        x.setTransform(R, 0, 0, R, 0, 0);
        x.font = probe.font; x.textBaseline = 'alphabetic'; x.textAlign = 'center';
        /* the rim is stroked first and filled over, so only its outer half shows and inner contours stay hidden */
        if (stroke) { x.lineWidth = 2.4; x.lineJoin = 'round'; x.strokeStyle = stroke; x.strokeText(mark, gw / 2, pad + asc); }
        x.fillStyle = fill;
        x.fillText(mark, gw / 2, pad + asc);
        return c;
      }
      var face = sprite(gw, gh), fx = face.getContext('2d');
      var grad = fx.createLinearGradient(0, pad * R, 0, (pad + asc + desc) * R);
      grad.addColorStop(0, css3(faceTop)); grad.addColorStop(1, css3(faceBottom));
      glyph(face, grad, K.rgba(rim, 0.9));
      var sides = shades.map(function (c) { return glyph(sprite(gw, gh), css3(c)); });
      var shadow = sprite(gw * 1.3, gh * 0.22), sx = shadow.getContext('2d');
      var rg = sx.createRadialGradient(shadow.width / 2, shadow.height / 2, 0, shadow.width / 2, shadow.height / 2, shadow.width / 2);
      rg.addColorStop(0, K.rgba(cPrimary, 0.28)); rg.addColorStop(1, K.rgba(cPrimary, 0));
      sx.setTransform(1, 0, 0, shadow.height / shadow.width, 0, 0);
      sx.fillStyle = rg; sx.fillRect(0, 0, shadow.width, shadow.width);
      sp = { face: face, sheen: sprite(gw, gh), sides: sides, shadow: shadow, gw: gw, gh: gh, depth: gh * DEPTH };
    }

    function draw(ts) {
      if (!sp || !gate(ts)) return;
      if (born === null) born = ts;
      ptr.step(0.06);
      var t = K.RM ? 0 : ts - born;
      var yaw = K.RM ? AMP * 0.8 : AMP * Math.sin(t / PERIOD * Math.PI * 2 + PHASE) + ptr.x * 0.14;
      var pitch = PITCH + ptr.y * 0.08;
      var w = size.w, h = size.h, cx = w / 2, cy = h * 0.44, focal = w * 2.4;
      var sy = Math.sin(yaw), cyaw = Math.cos(yaw), sp2 = Math.sin(pitch), cp = Math.cos(pitch);
      ctx.setTransform(1, 0, 0, 1, 0, 0);
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      /* floor shadow */
      var shw = sp.gw * (1.05 + 0.2 * Math.abs(sy)), shh = sp.gh * 0.2;
      ctx.setTransform(R, 0, 0, R, 0, 0);
      ctx.drawImage(sp.shadow, Math.round(cx - shw / 2 + sy * sp.depth * 0.5), Math.round(cy + sp.gh * 0.44), Math.round(shw), Math.round(shh));
      /* side layers, back to front: light term from how far the block turns toward the light */
      var light = sy / Math.sin(AMP) * LIGHT;
      for (var i = LAYERS; i >= 1; i--) {
        var z = sp.depth * i / LAYERS;
        var s = focal / (focal + z * cyaw * cp);
        var x = cx + z * sy * s, y = cy - z * sp2 * s;
        var b = Math.round((1 - i / LAYERS) * 2 + 1 + light * 1.2);
        b = Math.max(0, Math.min(4, b));
        ctx.setTransform(R * s * cyaw, 0, 0, R * s * cp, Math.round(x * R), Math.round(y * R));
        ctx.drawImage(sp.sides[b], -sp.gw / 2, -sp.gh / 2, sp.gw, sp.gh);
      }
      /* face with a sheen band that crosses it as the block turns */
      var sh = sp.sheen, sx = sh.getContext('2d');
      sx.globalCompositeOperation = 'copy';
      sx.drawImage(sp.face, 0, 0);
      sx.globalCompositeOperation = 'source-atop';
      var bx = sh.width * (0.5 - sy * 1.6), band = sh.width * 0.34;
      var g = sx.createLinearGradient(bx - band, 0, bx + band, sh.height * 0.3);
      g.addColorStop(0, 'rgba(255,255,255,0)'); g.addColorStop(0.5, 'rgba(255,255,255,0.14)'); g.addColorStop(1, 'rgba(255,255,255,0)');
      sx.fillStyle = g; sx.fillRect(0, 0, sh.width, sh.height);
      sx.globalCompositeOperation = 'source-over';
      ctx.setTransform(R * cyaw, 0, 0, R * cp, Math.round(cx * R), Math.round(cy * R));
      ctx.drawImage(sh, -sp.gw / 2, -sp.gh / 2, sp.gw, sp.gh);
    }

    var loop = K.loop(canvas, draw);
    function ready() { build(); if (loop.still) loop.still(); if (loop.kick) loop.kick(); }
    var fontSpec = '700 100px ' + font;
    if (document.fonts && document.fonts.load) document.fonts.load(fontSpec, mark).then(ready, ready); else ready();
    var rz = 0;
    window.addEventListener('resize', function () { clearTimeout(rz); rz = setTimeout(function () { build(); if (loop.still) loop.still(); }, 150); });
  });
})();
