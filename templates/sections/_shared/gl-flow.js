/* Shared: gl-flow (particle-flow-lanes-3d). Particles stream across the section in depth: scattered and wandering
   where they enter, sorted into calm parallel lanes by the time they leave, a picture of incoming work being put in
   order. Faster particles take the accent colour. The pointer parts the stream around it. Lane count, direction,
   speeds and wander come from data-seed; dots under data-gl-copy are dimmed.
   Mounts on data-gl="flow" (hero-flow and the "visual": "flow" backdrop of band sections).
   data-flow-dir="rtl" makes the stream run right to left; data-flow-density (default 1) scales the particle count and
   data-flow-lanes fixes the lane count. API for section scripts (host.__blgl.vis): setSort(p) with p from 0 to 1 takes
   over the sorting from the stream position: 0 is a cloud, 1 is calm lanes everywhere, so a scroll position can drive it. */
(function () {
  if (!window.BLGL) return;
  window.BLGL.register('flow', function (ctx) {
    var THREE = ctx.THREE, rnd = ctx.rnd, cam = ctx.camera, col = ctx.colors;
    var density = Math.max(0.3, Math.min(2.2, parseFloat(ctx.host.getAttribute('data-flow-density')) || 1));
    var N = Math.round((ctx.small ? 3600 : 9000) * density);
    var lanes = parseInt(ctx.host.getAttribute('data-flow-lanes'), 10) || 4 + Math.floor(rnd() * 4);
    var dir = ctx.host.getAttribute('data-flow-dir') === 'rtl' ? -1 : 1;
    cam.fov = 35;
    cam.position.set(0, 0, 10);
    cam.lookAt(0, 0, 0);

    var seed = new Float32Array(N * 4), pos = new Float32Array(N * 3);
    for (var i = 0; i < N; i++) {
      seed[i * 4] = rnd();                                  /* start along the stream */
      seed[i * 4 + 1] = rnd() * 2 - 1;                      /* entry height */
      seed[i * 4 + 2] = rnd() * 2 - 1;                      /* depth */
      seed[i * 4 + 3] = 0.035 + Math.pow(rnd(), 2) * 0.06;  /* speed: most slow, a few fast */
    }
    var geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
    geo.setAttribute('aSeed', new THREE.BufferAttribute(seed, 4));
    var u = {
      uT: { value: 0 }, uIntro: { value: 0 }, uPx: { value: 2 }, uHalf: { value: [8, 4] }, uDir: { value: dir },
      uLanes: { value: lanes }, uSpread: { value: 1 }, uSort: { value: 0 }, uWander: { value: 0.3 + rnd() * 0.25 }, uPtr: { value: [0, 0] }, uPtrF: { value: 0 },
      uDot: { value: ctx.mix(col.muted, col.text, 0.3) }, uHot: { value: col.blend }
    };
    Object.assign(u, ctx.guardUniforms);
    var pts = new THREE.Points(geo, new THREE.ShaderMaterial({
      uniforms: u, transparent: true, depthTest: false, depthWrite: false,
      vertexShader: [
        ctx.GUARD,
        'attribute vec4 aSeed;',
        'uniform float uT, uIntro, uPx, uDir, uLanes, uWander, uPtrF, uSpread, uSort;',
        'uniform vec2 uHalf, uPtr;',
        'varying float vA, vFast;',
        'void main() {',
        '  float s = fract(aSeed.x + uT * aSeed.w);',
        '  float x = (s * 2.3 - 1.15) * uHalf.x * uDir;',
        '  float lane = (floor((aSeed.y * 0.5 + 0.5) * uLanes) + 0.5) / uLanes * 2.0 - 1.0;',
        '  float order = clamp(smoothstep(0.25, 0.8, s) * uSpread + uSort, 0.0, 1.0);',
        '  float loose = aSeed.y * 0.9 + sin(x * 0.55 + aSeed.y * 1.6 + uT * 0.45) * uWander + sin(x * 1.3 - uT * 0.3 + aSeed.y * 2.4) * uWander * 0.35 + (aSeed.z * 0.08);',
        '  float y = mix(loose, lane * 0.82 + sin(x * 0.35 + lane * 2.0) * 0.05 + aSeed.z * 0.012, order) * uHalf.y * 0.85;',
        '  vec2 d = vec2(x, y) - uPtr;',
        '  float push = exp(-dot(d, d) / 1.6) * uPtrF;',
        '  y += sign(d.y + 1e-3) * push * 0.9;',
        '  vec3 p = vec3(x, y, aSeed.z * mix(2.2, 0.08, order));',
        '  vec4 mv = modelViewMatrix * vec4(p, 1.0);',
        '  gl_Position = projectionMatrix * mv;',
        '  float sc = 10.0 / -mv.z;',
        '  gl_PointSize = max(1.0, uPx * sc);',
        '  vFast = smoothstep(0.06, 0.09, aSeed.w);',
        '  float ends = smoothstep(0.0, 0.08, s) * smoothstep(1.0, 0.9, s);',
        '  vA = (0.25 + 0.55 * order) * ends * sc * guard(gl_Position.xy / gl_Position.w) * uIntro;',
        '}'
      ].join('\n'),
      fragmentShader: [
        ctx.DISC,
        'uniform vec3 uDot, uHot;',
        'varying float vA, vFast;',
        'void main() { float a = min(0.9, vA * (1.0 + vFast * 0.6)) * disc(); if (a < 0.01) discard; gl_FragColor = vec4(mix(uDot, uHot, vFast), a); }'
      ].join('\n')
    }));
    pts.frustumCulled = false;
    ctx.scene.add(pts);

    var sortWant = null, sortNow = 0;
    return {
      setSort: function (p) {
        sortWant = Math.max(0, Math.min(1, p));
        u.uSpread.value = 0;
        if (ctx.frozen()) { sortNow = sortWant; u.uSort.value = sortNow; ctx.redraw(); }
      },
      resize: function (w, h) {
        var halfH = 10 * Math.tan(cam.fov * Math.PI / 360);
        u.uHalf.value = [halfH * w / h, halfH];
        u.uPx.value = 2.5 * Math.min(window.devicePixelRatio || 1, ctx.dprCap);
      },
      frame: function (time, dt) {
        var ptr = ctx.pointer, half = u.uHalf.value;
        if (sortWant !== null) { sortNow += (sortWant - sortNow) * (1 - Math.exp(-dt * 6)); u.uSort.value = sortNow; }
        u.uT.value = time;
        u.uIntro.value = ctx.intro();
        if (ptr.tf) u.uPtr.value = [ptr.tx * half[0], -ptr.ty * half[1]];
        u.uPtrF.value = ptr.f;
      }
    };
  });
})();
