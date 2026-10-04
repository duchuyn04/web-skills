/* Shared: gl-wave (dot-wave-field-3d). A wide field of dots seen from a low angle, lifted by three crossing swells;
   crests light up in the accent colour. The pointer raises a soft mound under it. Directions, lengths and speeds
   of the swells come from data-seed. About 20 000 dots in one draw call; dots under data-gl-copy are dimmed.
   Mounts on data-gl="wave" (hero-wavefield and the "visual": "wave" backdrop of band sections). */
(function () {
  if (!window.BLGL) return;
  window.BLGL.register('wave', function (ctx) {
    var THREE = ctx.THREE, rnd = ctx.rnd, cam = ctx.camera, col = ctx.colors;
    var spacing = ctx.small ? 0.3 : 0.2;
    var elev = (13 + rnd() * 5) * Math.PI / 180, L = 16;
    cam.fov = 30;
    cam.position.set(0, L * Math.sin(elev), L * Math.cos(elev));
    cam.lookAt(0, 0, -2);
    /* the horizon sits lower than the lens centre, so the space above the field stays empty for the copy */
    var drop = 0.1;

    var pos = [];
    for (var z = -22; z <= 7; z += spacing) {
      for (var x = -18; x <= 18; x += spacing) pos.push(x, 0, z);
    }
    var geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.BufferAttribute(new Float32Array(pos), 3));

    function swell() {
      var a = rnd() * Math.PI * 2;
      return [Math.cos(a), Math.sin(a), 0.35 + rnd() * 0.5, 0.25 + rnd() * 0.35];
    }
    var u = {
      uT: { value: 0 }, uIntro: { value: 0 }, uPx: { value: 2.4 }, uAmp: { value: 0.42 + rnd() * 0.16 },
      uW1: { value: swell() }, uW2: { value: swell() }, uW3: { value: swell() },
      uPtr: { value: [0, 0] }, uPtrF: { value: 0 },
      uDot: { value: col.muted }, uHot: { value: ctx.mix(col.accent, col.blend, 0.5) }
    };
    Object.assign(u, ctx.guardUniforms);
    ctx.scene.add(new THREE.Points(geo, new THREE.ShaderMaterial({
      uniforms: u, transparent: true, depthTest: false, depthWrite: false,
      vertexShader: [
        ctx.GUARD,
        'uniform float uT, uIntro, uPx, uAmp, uPtrF;',
        'uniform vec4 uW1, uW2, uW3;',
        'uniform vec2 uPtr;',
        'varying float vA, vCrest;',
        'float wave(vec4 w, vec2 p) { return sin(dot(w.xy, p) * w.z + uT * w.w * 2.0); }',
        'void main() {',
        '  vec3 p = position;',
        '  float h = (wave(uW1, p.xz) * 0.5 + wave(uW2, p.xz) * 0.3 + wave(uW3, p.xz * 1.7) * 0.2);',
        '  vec2 d = p.xz - uPtr;',
        '  float bump = exp(-dot(d, d) / 3.0) * uPtrF;',
        '  p.y = h * uAmp + bump * 0.9;',
        '  vec4 mv = modelViewMatrix * vec4(p, 1.0);',
        '  gl_Position = projectionMatrix * mv;',
        '  float sc = 16.0 / -mv.z;',
        '  gl_PointSize = max(1.0, uPx * sc);',
        '  vCrest = smoothstep(0.25, 0.85, h) * 0.8 + bump * 0.6;',
        '  float far = smoothstep(-14.0, -5.0, position.z) * smoothstep(18.0, 13.0, abs(position.x));',
        '  vA = (0.18 + 0.7 * min(1.0, sc * sc)) * far * guard(gl_Position.xy / gl_Position.w) * uIntro;',
        '}'
      ].join('\n'),
      fragmentShader: [
        ctx.DISC,
        'uniform vec3 uDot, uHot;',
        'varying float vA, vCrest;',
        'void main() {',
        '  float c = clamp(vCrest, 0.0, 1.0);',
        '  float a = min(0.9, vA * (1.0 + c * 0.7)) * disc();',
        '  if (a < 0.01) discard;',
        '  gl_FragColor = vec4(mix(uDot, uHot, c), a);',
        '}'
      ].join('\n')
    })));

    var ray = new THREE.Vector3();
    function ground(nx, ny) {
      ray.set(nx, ny, 0.5).unproject(cam).sub(cam.position).normalize();
      if (ray.y > -1e-3) return null;
      var t = -cam.position.y / ray.y;
      return [cam.position.x + ray.x * t, cam.position.z + ray.z * t];
    }

    return {
      resize: function (w, h) {
        cam.setViewOffset(w, h, 0, -drop * h, w, h);
        cam.updateMatrixWorld();
        u.uPx.value = 2.4 * Math.min(window.devicePixelRatio || 1, ctx.dprCap) * Math.min(1.2, Math.max(0.8, h / 800));
      },
      frame: function (time) {
        var ptr = ctx.pointer;
        u.uT.value = time;
        u.uIntro.value = ctx.intro();
        var hit = ptr.tf ? ground(ptr.tx, -ptr.ty) : null;
        if (hit) u.uPtr.value = [u.uPtr.value[0] + (hit[0] - u.uPtr.value[0]) * 0.15, u.uPtr.value[1] + (hit[1] - u.uPtr.value[1]) * 0.15];
        u.uPtrF.value = ptr.f;
      }
    };
  });
})();
