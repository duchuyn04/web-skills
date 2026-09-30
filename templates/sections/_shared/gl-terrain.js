/* Shared: gl-terrain (wireframe-terrain-3d). A wireframe terrain seen from above, rolling slowly toward the viewer.
   Rows and columns form a real mesh drawn by the GPU (84 x 52 vertices, 40 x 26 on small screens); heights are
   computed in the vertex shader, vertices are dots, high ground is lit in the accent colour and up to three
   data-beacon children ride the peaks. The camera leans with the pointer. Ridge frequencies, phases, height and
   beacon anchors come from data-seed. Mounts on data-gl="terrain" (hero-terrain and the "visual": "terrain" backdrop). */
(function () {
  if (!window.BLGL) return;
  window.BLGL.register('terrain', function (ctx) {
    var THREE = ctx.THREE, rnd = ctx.rnd, cam = ctx.camera, col = ctx.colors;
    ctx.dprCap = 1; /* 1 px lines read like the canvas version; at 2x they turn into hairlines */
    var COLS = ctx.small ? 40 : 84, ROWS = ctx.small ? 26 : 52;
    var P = {
      f1: 1.1 + rnd() * 1.2, f2: 0.8 + rnd() * 1.0, f3: 2.4 + rnd() * 2.0,
      p1: rnd() * 6.28, p2: rnd() * 6.28, p3: rnd() * 6.28,
      flow: 0.18 + rnd() * 0.1, amp: 1.1 + rnd() * 0.5
    };
    var beacons = [].slice.call(ctx.host.querySelectorAll('[data-beacon]')).slice(0, 3);
    var anchors = beacons.map(function (_, i) { return [0.52 + i * 0.14 + rnd() * 0.04, 0.34 + i * 0.12 + rnd() * 0.05]; });
    var bsize = [];

    /* same height field as the shader, for the beacons */
    function height(u, v, t) {
      var x = (u - 0.5) * 4, z = v * 4 + t * P.flow;
      var ridge = 1 - Math.abs(Math.sin(x * P.f1 * 0.7 + z * 0.35 + P.p1));
      return P.amp * (0.55 * ridge * ridge + 0.3 * Math.sin(z * P.f2 + P.p2) * Math.cos(x * 0.9) + 0.15 * Math.sin((x - z) * P.f3 * 0.4 + P.p3));
    }
    function world(u, v, y) { return new THREE.Vector3((u - 0.5) * 14, y, -(2.2 + v * 11)); }

    var uv = new Float32Array(COLS * ROWS * 3), idx = [];
    for (var r = 0; r < ROWS; r++) {
      for (var c = 0; c < COLS; c++) {
        var k = r * COLS + c;
        uv[k * 3] = c / (COLS - 1); uv[k * 3 + 1] = r / (ROWS - 1);
        if (c > 0) idx.push(k - 1, k);
        if (r > 0) idx.push(k - COLS, k);
      }
    }
    var attr = new THREE.BufferAttribute(uv, 3);
    var lineGeo = new THREE.BufferGeometry();
    lineGeo.setAttribute('position', attr);
    lineGeo.setIndex(idx);
    var dotGeo = new THREE.BufferGeometry();
    dotGeo.setAttribute('position', attr);

    var u = {
      uT: { value: 0 }, uIntro: { value: 0 }, uPx: { value: 1 },
      uF: { value: [P.f1, P.f2, P.f3] }, uPh: { value: [P.p1, P.p2, P.p3] }, uFlow: { value: P.flow }, uAmp: { value: P.amp },
      uLine: { value: col.text }, uPeak: { value: col.blend }
    };
    var HEAD = [
      'uniform float uT, uIntro, uPx, uFlow, uAmp;',
      'uniform vec3 uF, uPh;',
      'float height(vec2 q) {',
      '  float x = (q.x - 0.5) * 4.0, z = q.y * 4.0 + uT * uFlow;',
      '  float ridge = 1.0 - abs(sin(x * uF.x * 0.7 + z * 0.35 + uPh.x));',
      '  return uAmp * (0.55 * ridge * ridge + 0.3 * sin(z * uF.y + uPh.y) * cos(x * 0.9) + 0.15 * sin((x - z) * uF.z * 0.4 + uPh.z));',
      '}',
      'varying float vNear, vHi;',
      'void place() {',
      '  float y = height(position.xy);',
      '  vec3 w = vec3((position.x - 0.5) * 14.0, y, -(2.2 + position.y * 11.0));',
      '  gl_Position = projectionMatrix * viewMatrix * vec4(w, 1.0);',
      '  vNear = 1.0 - position.y;',
      '  vHi = y / uAmp;',
      '}'
    ].join('\n');

    var lines = new THREE.LineSegments(lineGeo, new THREE.ShaderMaterial({
      uniforms: u, transparent: true, depthTest: false, depthWrite: false,
      vertexShader: HEAD + '\nvoid main() { place(); }',
      fragmentShader: [
        'uniform vec3 uLine;', 'uniform float uIntro;', 'varying float vNear, vHi;',
        'void main() { gl_FragColor = vec4(uLine, (0.05 + vNear * 0.16) * uIntro); }'
      ].join('\n')
    }));
    var dots = new THREE.Points(dotGeo, new THREE.ShaderMaterial({
      uniforms: u, transparent: true, depthTest: false, depthWrite: false,
      vertexShader: HEAD + '\nvoid main() { place(); float hi = step(0.62, vHi); gl_PointSize = uPx * mix(1.2 + vNear * 0.9, 1.8 + vNear * 1.8, hi); }',
      fragmentShader: [
        ctx.DISC,
        'uniform vec3 uLine, uPeak;', 'uniform float uIntro;', 'varying float vNear, vHi;',
        'void main() {',
        '  float hi = step(0.62, vHi);',
        '  float a = mix(0.1 + vNear * 0.25, 0.35 + vNear * 0.6, hi) * uIntro * disc();',
        '  if (a < 0.01) discard;',
        '  gl_FragColor = vec4(mix(uLine, uPeak, hi), a);',
        '}'
      ].join('\n')
    }));
    lines.frustumCulled = dots.frustumCulled = false;
    ctx.scene.add(lines, dots);

    /* The old canvas projection: focal length 0.9 h, horizon 0.3 h from the top, vanishing point 0.6 w from the left */
    cam.fov = 2 * Math.atan(0.5 / 0.9) * 180 / Math.PI;
    function aim(w, h) {
      var ptr = ctx.pointer;
      var horizon = h * (0.3 - ptr.y * 0.03);
      cam.position.set(ptr.x * 0.8, 3.4 + ptr.y * 0.3, 0);
      cam.setViewOffset(w, h, -0.1 * w, 0.5 * h - horizon, w, h);
      cam.updateMatrixWorld();
    }

    return {
      resize: function (w, h) {
        u.uPx.value = Math.min(window.devicePixelRatio || 1, ctx.dprCap);
        bsize = beacons.map(function (el) { return [el.offsetWidth, el.offsetHeight]; });
        aim(w, h);
      },
      frame: function (time) {
        var w = ctx.size.w, h = ctx.size.h;
        u.uT.value = time;
        u.uIntro.value = ctx.intro();
        aim(w, h);
        beacons.forEach(function (el, i) {
          var a = anchors[i];
          var pt = ctx.project(world(a[0], a[1], height(a[0], a[1], time)));
          var bx = Math.max(16, Math.min(w - bsize[i][0] - 16, pt[0] - bsize[i][0] / 2));
          el.style.transform = 'translate3d(' + bx.toFixed(1) + 'px,' + (pt[1] - bsize[i][1] - 44).toFixed(1) + 'px,0)';
          el.classList.add('is-on');
        });
      }
    };
  });
})();
