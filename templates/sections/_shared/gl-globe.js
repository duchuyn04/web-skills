/* Shared: gl-globe (dotted-globe-arcs-3d). A globe of evenly spread dots (Fibonacci sphere): land dots from the
   world-dots land mask, faint ocean dots for the outline, the far side dimmed. Pins come from [data-globe-pin]
   elements (data-lat, data-lon, data-kind="hub" or "market"); each market arcs to its nearest hub, or hubs chain to
   each other, and a light pulse runs along every arc. Pin labels are the pin elements themselves, moved over their
   dot and hidden on the far side. With pins the globe sways around the hubs; without pins it turns slowly.
   Mounts on data-gl="globe". data-globe-layout picks the framing:
     fit   a whole globe centred in its box (hero stage)
     side  a large globe cropped at the right of a band (default)
     rise  a huge globe rising from the bottom edge of a full-screen hero, right of centre
     tour  a large whole globe right of centre, for a scroll-driven tour
   "rise" and "tour" are solid: a body sphere with soft light, an atmosphere rim in the accent colour, dots lit from the
   upper left and no far side showing through.
   Overrides on the host: data-globe-scale (multiplies the radius), data-globe-x and data-globe-y (centre as a share of the
   box width and height) and data-globe-tilt (degrees the pins sit above the disc centre; default 30 for rise, else 0).
   API for section scripts (host.__blgl.vis): focus(lat, lon) turns the globe to face a point and marks the pin there
   with .is-focus; focus(null) goes back to the sway. Mask: scripts/make_globe_mask.py. */
(function () {
  if (!window.BLGL) return;
  var MASK = 'AAAAyPzz//8A4AAAAAADAAAAAACAlAnw//8AAAAAB4AfAAAAAADAAywA/P8AAABgAP4fAAEAAQKAPvYH+H8AAABguP//7x8A4P//K9wc+B8AgH+g1///////z////z98+AMC4L/8////////AP///684+AAB8P7///////9/wP///wMGcAAAfP7//////38fgAf+/wdeAAAAfP7//////wEBAAH4/x9+AABAKP//////f8ABAADw/3//AQCw+P///////8AAAADg////AwDA/////////wAAAADA//8vBwDA/////////wAAAADA//8/AACA/6//////fwAAAADA//8PAACA1wf/////PwIAAADA//8HAADwYW//////DwEAAACA//8DAADwQPn///9/BAEAAACA//8DAAAAD+D/////yAAAAAAA/v8BAADgD8D/////IAAAAAAA+n8AAADwf9f/////AQAAAAAA/IMAAADw///3////AQAAAAAA8IEAAAD8/7/P////AAAAAAAA4AEAAAD8/79/+P9/AQAAAAAAwBEAAAD+/3//8OcHAAAAAAAAwBsYAAD8/39/4MMLAAAAAAAAAB4AAAD+//8e4IEHAQAAAAAAAHAAAAD+//8HwIAPAwAAAAAAAAAUAAD8//8JwIAGAAAAAAAAAID+AAD4//8PAIAABAAAAAAAAAD+AQDw/f8PAAEBAAAAAAAAAAD+DwAA8P8HAIBhAAAAAAAAAAD/DwAA8P8DAABzAAAAAAAAAAD/PwAA8P8BAABzMQAAAAAAAAD//wEA8P8AAAACwQMAAAAAAAD//wMA4P8AAAAEgAcAAAAAAAD//wMA4P8AAACABQEAAAAAAAD+/wEA4P8AAAAAAAAAAAAAAAD+/wAA4P8IAAAAMAAAAAAAAAD4/wAA4P8MAAAAfgIAAAAAAADw/wAA4D8MAAAA/gcAAAAAAADw/wAA4D8GAADA/w8AAAAAAADwPwAAwD8GAADg/w8AAAAAAADwHwAAwB8AAADg/x8AAAAAAAD4DwAAgB8AAADA/x8AAAAAAAD4DwAAgA8AAADA/x8AAAAAAAD4BwAAgAMAAADAwx8AAAAAAAD4AQAAAAAAAAAAAA8AAAAAAAD4AAAAAAAAAAAAAARAAAAAAAA8AAAAAAAAAAAAAAQgAAAAAAA4AAAAAAAAAAAAAAAQAAAAAAAcAAAAAAAAAAAAAAAIAAAAAAAcAAAAAAAAAAAAAAAAAAAAAAAMAQAAAAAAAAAAAAAAAAAAAAAYAAAAAAAAAAAAAAAA';
  var MW = 144, MH = 54, LAT_TOP = 80, STEP = 2.5;
  var bytes = null;
  function land(lat, lon) {
    if (!bytes) { var s = atob(MASK); bytes = new Uint8Array(s.length); for (var i = 0; i < s.length; i++) bytes[i] = s.charCodeAt(i); }
    /* bilinear over the 2.5 degree cells so coasts are not stair steps */
    var fx = (lon + 180) / STEP - 0.5, fy = (LAT_TOP - lat) / STEP - 0.5;
    var x0 = Math.floor(fx), y0 = Math.floor(fy), tx = fx - x0, ty = fy - y0;
    function cell(x, y) {
      if (y < 0 || y >= MH) return 0;
      x = ((x % MW) + MW) % MW;
      var k = y * MW + x;
      return (bytes[k >> 3] >> (k & 7)) & 1;
    }
    var top = cell(x0, y0) * (1 - tx) + cell(x0 + 1, y0) * tx;
    var bot = cell(x0, y0 + 1) * (1 - tx) + cell(x0 + 1, y0 + 1) * tx;
    return top * (1 - ty) + bot * ty > 0.5;
  }
  function vec(THREE, lat, lon, r) {
    var a = lat * Math.PI / 180, b = lon * Math.PI / 180;
    return new THREE.Vector3(Math.cos(a) * Math.sin(b), Math.sin(a), Math.cos(a) * Math.cos(b)).multiplyScalar(r || 1);
  }

  window.BLGL.register('globe', function (ctx) {
    var THREE = ctx.THREE, rnd = ctx.rnd, cam = ctx.camera, col = ctx.colors;
    var layout = ctx.host.getAttribute('data-globe-layout') || 'side';
    var solid = layout === 'rise' || layout === 'tour';
    var D = Math.PI / 180;
    var group = new THREE.Group();
    ctx.scene.add(group);
    cam.fov = 30;

    /* dots */
    var N = solid ? (ctx.small ? 30000 : 90000) : (ctx.small ? 7000 : 14000), pos = [], kind = [];
    var golden = Math.PI * (3 - Math.sqrt(5));
    for (var i = 0; i < N; i++) {
      var y = 1 - (i + 0.5) / N * 2, r = Math.sqrt(1 - y * y), th = golden * i;
      var x = Math.cos(th) * r, z = Math.sin(th) * r;
      var lat = Math.asin(y) * 180 / Math.PI, lon = Math.atan2(x, z) * 180 / Math.PI;
      var isLand = land(lat, lon);
      if (!isLand && i % 3) continue;
      pos.push(x, y, z);
      kind.push(isLand ? 1 : 0);
    }
    var geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.BufferAttribute(new Float32Array(pos), 3));
    geo.setAttribute('aLand', new THREE.BufferAttribute(new Float32Array(kind), 1));
    var u = {
      uIntro: { value: 0 }, uPx: { value: 2 }, uT: { value: 0 },
      uFar: { value: solid ? 0 : 0.12 }, uLit: { value: solid ? 1 : 0 },
      uLand: { value: ctx.mix(col.muted, col.text, 0.45) }, uSea: { value: col.muted }, uHot: { value: col.blend }
    };
    Object.assign(u, ctx.guardUniforms);
    var FACING = [
      'float facing(vec3 p) {',
      '  vec3 w = (modelMatrix * vec4(p, 1.0)).xyz;',
      '  vec3 n = normalize(mat3(modelMatrix) * p);',
      '  return dot(n, normalize(cameraPosition - w));',
      '}'
    ].join('\n');
    /* fixed light from the upper left, in view space */
    var LIGHT = 'const vec3 LIGHT = vec3(-0.5, 0.55, 0.67);';

    /* body and atmosphere (solid layouts): drawn first, with depth, so they hide the far side and the glow stays outside */
    if (solid) {
      var bodyColor = ctx.mix(col.bg, col.accent, 0.1);
      var bodyMat = new THREE.ShaderMaterial({
        uniforms: { uBody: { value: bodyColor }, uHot: u.uHot, uIntro: u.uIntro },
        transparent: true, depthTest: true, depthWrite: true,
        vertexShader: 'varying vec3 vN; void main() { vN = normalize(normalMatrix * normal); gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }',
        fragmentShader: [
          LIGHT, 'uniform vec3 uBody, uHot; uniform float uIntro; varying vec3 vN;',
          'void main() {',
          '  vec3 n = normalize(vN);',
          '  float l = 0.5 + 0.5 * dot(n, normalize(LIGHT));',
          '  float rim = pow(1.0 - clamp(n.z, 0.0, 1.0), 3.0);',
          '  vec3 c = mix(uBody * 0.7, uBody * 1.7, l) + uHot * rim * 0.22;',
          '  gl_FragColor = vec4(c, uIntro);',
          '}'
        ].join('\n')
      });
      var body = new THREE.Mesh(new THREE.SphereGeometry(0.985, 64, 40), bodyMat);
      body.renderOrder = -2;
      ctx.scene.add(body);
      var glowMat = new THREE.ShaderMaterial({
        uniforms: { uHot: u.uHot, uIntro: u.uIntro },
        transparent: true, depthTest: true, depthWrite: false, side: THREE.BackSide, blending: THREE.AdditiveBlending,
        vertexShader: 'varying vec3 vN; void main() { vN = normalize(normalMatrix * normal); gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }',
        fragmentShader: [
          'uniform vec3 uHot; uniform float uIntro; varying vec3 vN;',
          'void main() {',
          '  float i = pow(clamp(0.5 + dot(normalize(vN), vec3(0.0, 0.0, 1.0)) * 0.9, 0.0, 1.0), 3.4);',
          '  gl_FragColor = vec4(uHot * i, i * 0.6 * uIntro);',
          '}'
        ].join('\n')
      });
      var glow = new THREE.Mesh(new THREE.SphereGeometry(1.12, 64, 40), glowMat);
      glow.renderOrder = -1;
      ctx.scene.add(glow);
    }

    var dots = new THREE.Points(geo, new THREE.ShaderMaterial({
      uniforms: u, transparent: true, depthTest: false, depthWrite: false,
      vertexShader: [
        ctx.GUARD, FACING, LIGHT,
        'attribute float aLand;',
        'uniform float uIntro, uPx, uFar, uLit;',
        'varying float vA, vLand;',
        'void main() {',
        '  vec4 mv = modelViewMatrix * vec4(position, 1.0);',
        '  gl_Position = projectionMatrix * mv;',
        '  float f = facing(position);',
        '  float side = mix(uFar, 1.0, smoothstep(-0.05, 0.3, f));',
        '  float lit = mix(1.0, 0.45 + 0.75 * clamp(dot(normalize(mat3(modelViewMatrix) * position), normalize(LIGHT)) * 0.5 + 0.5, 0.0, 1.0), uLit);',
        '  gl_PointSize = uPx * mix(0.8, 1.15, aLand) * (0.7 + 0.3 * smoothstep(-0.2, 0.6, f));',
        '  vLand = aLand;',
        '  vA = mix(0.16, 0.9, aLand) * side * lit * guard(gl_Position.xy / gl_Position.w) * uIntro;',
        '}'
      ].join('\n'),
      fragmentShader: [
        ctx.DISC,
        'uniform vec3 uLand, uSea;',
        'varying float vA, vLand;',
        'void main() { float a = vA * disc(); if (a < 0.01) discard; gl_FragColor = vec4(mix(uSea, uLand, vLand), a); }'
      ].join('\n')
    }));
    dots.frustumCulled = false;
    group.add(dots);

    /* pins, arcs */
    var pinEls = [].slice.call(ctx.host.querySelectorAll('[data-globe-pin]'));
    var pins = pinEls.map(function (el) {
      var la = parseFloat(el.getAttribute('data-lat')), lo = parseFloat(el.getAttribute('data-lon'));
      return { el: el, lat: la, lon: lo, hub: el.getAttribute('data-kind') !== 'market', v: vec(THREE, la, lo, 1.005), w: 0, h: 0 };
    }).filter(function (p) { return !isNaN(p.lat) && !isNaN(p.lon); });
    var hubs = pins.filter(function (p) { return p.hub; });
    var pairs = [];
    pins.forEach(function (p) {
      if (p.hub || !hubs.length) return;
      var best = hubs[0];
      hubs.forEach(function (h) { if (h.v.distanceTo(p.v) < best.v.distanceTo(p.v)) best = h; });
      pairs.push([best, p]);
    });
    if (!pairs.length) for (var h = 1; h < hubs.length; h++) pairs.push([hubs[h - 1], hubs[h]]);

    if (pairs.length) {
      var SEG = 48, apos = [], at = [], ak = [], aidx = [];
      pairs.forEach(function (pr, n) {
        var a = pr[0].v.clone().normalize(), b = pr[1].v.clone().normalize();
        var om = Math.acos(Math.max(-1, Math.min(1, a.dot(b)))) || 1e-3, lift = Math.min(0.2, om * 0.14);
        for (var s = 0; s <= SEG; s++) {
          var t = s / SEG;
          var p = a.clone().multiplyScalar(Math.sin((1 - t) * om)).add(b.clone().multiplyScalar(Math.sin(t * om))).divideScalar(Math.sin(om));
          p.multiplyScalar(1 + Math.sin(Math.PI * t) * lift);
          var base = apos.length / 3;
          apos.push(p.x, p.y, p.z); at.push(t); ak.push(n * 0.37 % 1);
          if (s) aidx.push(base - 1, base);
        }
      });
      var ageo = new THREE.BufferGeometry();
      ageo.setAttribute('position', new THREE.BufferAttribute(new Float32Array(apos), 3));
      ageo.setAttribute('aT', new THREE.BufferAttribute(new Float32Array(at), 1));
      ageo.setAttribute('aK', new THREE.BufferAttribute(new Float32Array(ak), 1));
      ageo.setIndex(aidx);
      var arcs = new THREE.LineSegments(ageo, new THREE.ShaderMaterial({
        uniforms: u, transparent: true, depthTest: false, depthWrite: false,
        vertexShader: [
          FACING,
          'attribute float aT, aK;',
          'uniform float uT;',
          'varying float vA;',
          'void main() {',
          '  gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);',
          '  float head = fract(uT * 0.22 + aK);',
          '  float d = head * 1.3 - aT;',
          '  float pulse = step(0.0, d) * smoothstep(0.35, 0.0, d);',
          '  vA = (0.22 + 0.78 * pulse) * mix(0.15, 1.0, smoothstep(-0.2, 0.2, facing(position)));',
          '}'
        ].join('\n'),
        fragmentShader: 'uniform vec3 uHot; uniform float uIntro; varying float vA; void main() { gl_FragColor = vec4(uHot, vA * uIntro); }'
      }));
      arcs.frustumCulled = false;
      group.add(arcs);

      var pgeo = new THREE.BufferGeometry();
      var pp = [];
      pins.forEach(function (p) { pp.push(p.v.x, p.v.y, p.v.z); });
      pgeo.setAttribute('position', new THREE.BufferAttribute(new Float32Array(pp), 3));
      var marks = new THREE.Points(pgeo, new THREE.ShaderMaterial({
        uniforms: u, transparent: true, depthTest: false, depthWrite: false,
        vertexShader: [
          FACING,
          'uniform float uPx, uT;',
          'varying float vA, vRing;',
          'void main() {',
          '  gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);',
          '  vRing = fract(uT * 0.5 + position.x);',
          '  gl_PointSize = uPx * 9.0;',
          '  vA = smoothstep(-0.05, 0.25, facing(position));',
          '}'
        ].join('\n'),
        fragmentShader: [
          'uniform vec3 uHot; uniform float uIntro; varying float vA, vRing;',
          'void main() {',
          '  float d = length(gl_PointCoord - 0.5) * 2.0;',
          '  float core = smoothstep(0.34, 0.24, d);',
          '  float ring = smoothstep(0.1, 0.0, abs(d - vRing)) * (1.0 - vRing);',
          '  float a = max(core, ring * 0.8) * vA * uIntro;',
          '  if (a < 0.01) discard;',
          '  gl_FragColor = vec4(uHot, a);',
          '}'
        ].join('\n')
      }));
      marks.frustumCulled = false;
      group.add(marks);
    }

    /* where the globe faces: the middle of the hubs, or a seeded longitude */
    var baseLon = rnd() * 360 - 180, baseLat = 18 + rnd() * 10;
    if (hubs.length) {
      var c = new THREE.Vector3();
      hubs.forEach(function (p) { c.add(p.v); });
      c.normalize();
      baseLon = Math.atan2(c.x, c.z) * 180 / Math.PI;
      baseLat = Math.max(-30, Math.min(35, Math.asin(c.y) * 180 / Math.PI));
    }
    var swing = pins.length ? 0.35 : 0;
    var spin = pins.length ? 0 : 0.07 + rnd() * 0.03;

    var cx = 0.5, cy = 0.5, rpx = 1;
    var num = function (name) { var v = parseFloat(ctx.host.getAttribute(name)); return isNaN(v) ? null : v; };
    var tilt = num('data-globe-tilt') != null ? num('data-globe-tilt') : (layout === 'rise' ? 30 : 0);
    function place(w, h) {
      if (layout === 'fit') { rpx = 0.4 * Math.min(w, h); cx = 0.5; cy = 0.5; }
      else if (layout === 'rise') {
        if (w < 760) { rpx = 0.95 * w; cx = 0.5; cy = 1.1; }
        else { rpx = Math.min(0.78 * h, 0.52 * w); cx = 0.68; cy = 1.16; }
      } else if (layout === 'tour') {
        if (w < 760) { rpx = 0.42 * w; cx = 0.5; cy = 0.5; }
        else { rpx = Math.min(0.4 * h, 0.3 * w); cx = 0.7; cy = 0.5; }
      } else if (w < 760) { rpx = 0.62 * w; cx = 0.5; cy = 0.98; }
      else { rpx = Math.min(0.62 * h, 0.3 * w); cx = 0.8; cy = 0.62; }
      rpx *= num('data-globe-scale') || 1;
      if (num('data-globe-x') != null) cx = num('data-globe-x');
      if (num('data-globe-y') != null) cy = num('data-globe-y');
      var tanHalf = Math.tan(cam.fov * Math.PI / 360);
      var dist = (h / 2) / (rpx * tanHalf);
      cam.position.set(0, 0, dist);
      cam.lookAt(0, 0, 0);
      cam.setViewOffset(w, h, (0.5 - cx) * w, (0.5 - cy) * h, w, h);
      cam.near = Math.max(0.1, dist - 2); cam.far = dist + 2;
      cam.updateProjectionMatrix();
      cam.updateMatrixWorld();
    }

    /* rotation state, eased toward the sway or toward a focused point */
    var focusAt = null, yaw = null, pitch = null;
    function target(time) {
      if (focusAt) return [-focusAt[1] * D, (focusAt[0] - tilt) * D];
      return [-(baseLon * D) + Math.sin(time * 0.12) * swing - time * spin, (baseLat - tilt) * D];
    }
    function markFocus() {
      pins.forEach(function (p) {
        var on = !!focusAt && Math.abs(p.lat - focusAt[0]) < 0.6 && Math.abs(p.lon - focusAt[1]) < 0.6;
        p.el.classList.toggle('is-focus', on);
      });
    }

    var tmp = new THREE.Vector3(), nrm = new THREE.Vector3();
    function placePins() {
      pins.forEach(function (p) {
        tmp.copy(p.v); group.localToWorld(tmp);
        nrm.copy(tmp).normalize();
        var front = nrm.dot(tmp.clone().sub(cam.position).negate().normalize()) > 0.15;
        var s = ctx.project(tmp);
        p.el.style.transform = 'translate3d(' + (s[0] - p.w / 2).toFixed(1) + 'px,' + (s[1] - p.h - 12).toFixed(1) + 'px,0)';
        p.el.classList.toggle('is-on', front && u.uIntro.value > 0.6);
      });
    }

    return {
      resize: function (w, h) {
        var dpr = Math.min(window.devicePixelRatio || 1, ctx.dprCap);
        place(w, h);
        u.uPx.value = dpr * (solid ? Math.max(1.3, Math.min(2.4, rpx / 300)) : Math.max(1.6, Math.min(3.2, rpx / 110)));
        pins.forEach(function (p) { p.w = p.el.offsetWidth; p.h = p.el.offsetHeight; });
      },
      /* turn the globe to face lat/lon (degrees); focus(null) returns to the sway */
      focus: function (la, lo) {
        focusAt = (la == null || lo == null) ? null : [la, lo];
        markFocus();
        if (ctx.frozen()) {
          var t = target(ctx.time);
          yaw = t[0]; pitch = t[1];
          ctx.redraw();
        }
      },
      frame: function (time, dt) {
        var ptr = ctx.pointer, t = target(time);
        u.uT.value = time;
        u.uIntro.value = ctx.intro();
        if (yaw === null) { yaw = t[0]; pitch = t[1]; }
        else {
          var k = focusAt ? 1 - Math.exp(-dt * 3.4) : 1 - Math.exp(-dt * 2.2);
          var d = t[0] - yaw;
          d = ((d + Math.PI) % (2 * Math.PI) + 2 * Math.PI) % (2 * Math.PI) - Math.PI; /* the short way round */
          yaw += d * k; pitch += (t[1] - pitch) * k;
        }
        group.rotation.y = yaw + ptr.x * 0.25;
        group.rotation.x = pitch + ptr.y * 0.12;
        group.updateMatrixWorld();
        placePins();
      }
    };
  });
})();
