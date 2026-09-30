/* Shared: gl-dots (magnetic-dot-plane). A grid of dots on a ground plane seen from 28-36 degrees above. The pointer
   presses the plane down with a Gaussian dip and pushes the dots aside; with no pointer, one ring-shaped ripple
   leaves a seeded origin every 7-11 s. About 9 000 dots drawn by the GPU in one call. Dots under data-gl-copy are
   dimmed. Mounts on data-gl="dots" (hero-magnetic and the "visual": "dots" backdrop of band sections). */
(function () {
  if (!window.BLGL) return;
  window.BLGL.register('dots', function (ctx) {
    var THREE = ctx.THREE, rnd = ctx.rnd, cam = ctx.camera, col = ctx.colors;
    var spacing = (ctx.small ? 0.34 : 0.25) * (0.94 + rnd() * 0.18);
    var elev = (28 + rnd() * 8) * Math.PI / 180;
    var period = 7 + rnd() * 4;
    var hot = ctx.mix(col.accent, col.blend, 0.2 + rnd() * 0.5);
    var target = [0.62 + rnd() * 0.24, 0.45 + rnd() * 0.3];
    /* narrow lens, far camera: weak perspective, so dots shrink to about 55 percent at the top edge */
    var L = 20;
    cam.fov = 22;
    cam.position.set(0, L * Math.sin(elev), L * Math.cos(elev));
    cam.lookAt(0, 0, 0);

    var pos = [];
    for (var z = -13; z <= 8; z += spacing) {
      for (var x = -14; x <= 14; x += spacing) pos.push(x, 0, z);
    }
    var geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.BufferAttribute(new Float32Array(pos), 3));

    var u = {
      uTime: { value: 0 }, uIntro: { value: 0 }, uPeriod: { value: period }, uRipR: { value: 15 }, uWave: { value: spacing * 3.2 },
      uOrigin: { value: [4, -2] }, uPtr: { value: [0, 0] }, uPtrF: { value: 0 }, uSig2: { value: 1.77 },
      uPx: { value: 3.0 }, uRip: { value: 1 }, uDot: { value: col.muted }, uHot: { value: hot }
    };
    Object.assign(u, ctx.guardUniforms);
    var mat = new THREE.ShaderMaterial({
      uniforms: u, transparent: true, depthTest: false, depthWrite: false,
      vertexShader: [
        ctx.GUARD,
        'uniform float uTime, uIntro, uPeriod, uRipR, uWave, uPtrF, uSig2, uPx, uRip;',
        'uniform vec2 uOrigin, uPtr;',
        'varying float vA, vHot;',
        'void main() {',
        '  vec3 p = position;',
        '  vec2 d = p.xz - uPtr;',
        '  float g = exp(-dot(d, d) / uSig2) * uPtrF;',
        '  float phase = mod(uTime, uPeriod) / uPeriod;',
        '  float dr = length(p.xz - uOrigin) - phase * uRipR * 1.1;',
        '  float rip = exp(-dr * dr / (2.0 * uWave * uWave)) * (1.0 - phase) * uRip;',
        '  p.y += rip * 0.34 - g * 0.72;',
        '  p.xz += normalize(d + vec2(1e-4)) * g * 0.12;',
        '  vec4 mv = modelViewMatrix * vec4(p, 1.0);',
        '  gl_Position = projectionMatrix * mv;',
        '  float sc = 20.0 / -mv.z;',
        '  gl_PointSize = max(1.0, uPx * sc * (1.0 + 0.5 * g));',
        '  float fade = guard(gl_Position.xy / gl_Position.w);',
        '  float far = smoothstep(-13.0, -9.0, position.z);',
        '  float e = max(g, rip * 0.8);',
        '  vHot = e * step(0.5, fade);',
        '  vA = (0.2 + 0.9 * min(1.0, sc * sc)) * fade * far * uIntro * (1.0 + e * 0.8);',
        '}'
      ].join('\n'),
      fragmentShader: [
        ctx.DISC,
        'uniform vec3 uDot, uHot;',
        'uniform float uIntro;',
        'varying float vA, vHot;',
        'void main() {',
        '  float h = smoothstep(0.22, 0.6, vHot);',
        '  float a = mix(min(vA, 0.82), 0.95 * uIntro, h) * disc();',
        '  if (a < 0.01) discard;',
        '  gl_FragColor = vec4(mix(uDot, uHot, h), a);',
        '}'
      ].join('\n')
    });
    ctx.scene.add(new THREE.Points(geo, mat));

    /* NDC point to the ground plane (y = 0) */
    var ray = new THREE.Vector3();
    function ground(nx, ny) {
      ray.set(nx, ny, 0.5).unproject(cam).sub(cam.position).normalize();
      if (ray.y > -1e-3) return null;
      var t = -cam.position.y / ray.y;
      return [cam.position.x + ray.x * t, cam.position.z + ray.z * t];
    }

    return {
      resize: function (w, h) {
        cam.updateMatrixWorld();
        var o = ground(target[0] * 2 - 1, 1 - target[1] * 2);
        if (o) u.uOrigin.value = o;
        u.uPx.value = 3.0 * Math.min(window.devicePixelRatio || 1, ctx.dprCap) * Math.min(1.2, Math.max(0.8, h / 800));
      },
      frame: function (time) {
        var ptr = ctx.pointer;
        u.uTime.value = time;
        u.uIntro.value = ctx.intro();
        u.uRip.value = window.BL && window.BL.RM ? 0 : 1;
        var hit = ptr.tf ? ground(ptr.tx, -ptr.ty) : null;
        if (hit) {
          u.uPtr.value = [u.uPtr.value[0] + (hit[0] - u.uPtr.value[0]) * 0.18, u.uPtr.value[1] + (hit[1] - u.uPtr.value[1]) * 0.18];
        }
        u.uPtrF.value = ptr.f;
      }
    };
  });
})();
