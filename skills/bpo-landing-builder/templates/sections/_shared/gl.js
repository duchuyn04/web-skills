/* Shared: BLGL, the WebGL toolkit on Three.js (_shared/three.js). Needs _shared/ribbons.js loaded first: every scene
   draws through BLRibbons.loop, the one render loop that stops off screen, in hidden tabs, under reduced motion and
   when the page-wide Pause animations switch is on (reduced motion and pause draw one still frame).
   A visual is a factory registered with BLGL.register(name, factory). It mounts on every element with
   data-gl="name" that holds a canvas with data-gl-canvas. Optional hooks on the host:
     data-seed     text that seeds every random choice (the brand name), so two sites never get the same scene
     data-gl-copy  on copy blocks; the GUARD shader chunk dims the scene under them so text keeps its contrast
   factory(ctx) returns { frame(time, dt), resize(w, h), ...its own API }; time stops while paused. The returned object is
   kept at host.__blgl.vis, so a section script can drive the scene (globe.focus, flow.setSort). host.__blgl is true, not
   an object, until the scene has mounted (and stays true when there is no WebGL). ctx carries renderer, scene, camera,
   rnd, colors (sRGB 0-1 from the CSS tokens), pointer, size, small, intro(), guardUniforms, project(). Without WebGL the
   host gets data-gl-off and the canvas is hidden; every visual is decoration, the section reads the same without it. */
(function () {
  if (window.BLGL || !window.THREE || !window.BLRibbons) return;
  var THREE = window.THREE, R = window.BLRibbons;
  var BL = window.BL || {};
  var MAX_GUARDS = 8;

  function reduced() { return !!BL.RM; }

  /* FNV-1a hash of a string, then mulberry32 (same numbers as BL3D.seed) */
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

  /* CSS colour to [r, g, b] in 0-1 sRGB. Shaders write these straight to the canvas, so no colour management. */
  function rgb(css, fallback) {
    var s = (css || '').trim(), m;
    if ((m = /^#([0-9a-f]{3})$/i.exec(s))) s = '#' + m[1].replace(/./g, '$&$&');
    if ((m = /^#([0-9a-f]{6})/i.exec(s))) {
      var n = parseInt(m[1], 16);
      return [((n >> 16) & 255) / 255, ((n >> 8) & 255) / 255, (n & 255) / 255];
    }
    if ((m = /^rgba?\(\s*([\d.]+)[\s,]+([\d.]+)[\s,]+([\d.]+)/i.exec(s))) return [m[1] / 255, m[2] / 255, m[3] / 255];
    return fallback || [1, 1, 1];
  }
  function mix(a, b, t) { return [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t]; }

  function colors(el) {
    var cs = getComputedStyle(el);
    var get = function (name, fb) { return rgb(cs.getPropertyValue(name), fb); };
    var text = get('--text-strong', [0.1, 0.1, 0.15]);
    return {
      text: text, muted: get('--text-muted', text), accent: get('--c-accent'), blend: get('--c-accent-blend', get('--c-accent')),
      accent2: get('--c-accent-2', get('--c-accent')), bg: get('--bg', [1, 1, 1])
    };
  }

  /* GLSL: guard(ndc) returns 0.1 under a copy block and 1 more than 90 px away from it */
  var GUARD = [
    'uniform vec4 uGuard[' + MAX_GUARDS + '];',
    'uniform float uGuardN;',
    'uniform vec2 uRes;',
    'float guard(vec2 ndc) {',
    '  vec2 px = vec2((ndc.x * 0.5 + 0.5) * uRes.x, (0.5 - ndc.y * 0.5) * uRes.y);',
    '  float f = 1.0;',
    '  for (int i = 0; i < ' + MAX_GUARDS + '; i++) {',
    '    if (float(i) >= uGuardN) break;',
    '    vec4 b = uGuard[i];',
    '    vec2 d = max(max(b.xy - px, px - b.zw), 0.0);',
    '    f = min(f, 0.1 + 0.9 * min(1.0, length(d) / 90.0));',
    '  }',
    '  return f;',
    '}'
  ].join('\n');

  /* GLSL: round, soft-edged point sprite; returns coverage 0-1 */
  var DISC = 'float disc() { float d = length(gl_PointCoord - 0.5); return smoothstep(0.5, 0.4, d); }';

  function pointer(el) {
    var st = { x: 0, y: 0, tx: 0, ty: 0, f: 0, tf: 0, moved: 0 };
    if (BL.FINE && !reduced()) {
      el.addEventListener('pointermove', function (e) {
        var r = el.getBoundingClientRect();
        st.tx = ((e.clientX - r.left) / r.width) * 2 - 1;
        st.ty = ((e.clientY - r.top) / r.height) * 2 - 1;
        st.tf = 1; st.moved = performance.now();
      }, { passive: true });
      el.addEventListener('pointerleave', function () { st.tx = 0; st.ty = 0; st.tf = 0; });
    }
    st.step = function (k) {
      k = k || 0.08;
      st.x += (st.tx - st.x) * k; st.y += (st.ty - st.y) * k; st.f += (st.tf - st.f) * k;
      return st;
    };
    return st;
  }

  function mount(host, factory) {
    if (host.__blgl) return;
    host.__blgl = true;
    var canvas = host.querySelector('[data-gl-canvas]');
    if (!canvas) return;
    /* Three.js needs WebGL2; asking first keeps the console quiet where there is none */
    var renderer, attrs = { alpha: true, antialias: false, premultipliedAlpha: true, powerPreference: 'low-power' };
    try {
      var context = canvas.getContext('webgl2', attrs);
      if (!context) throw new Error('no WebGL2');
      renderer = new THREE.WebGLRenderer({ canvas: canvas, context: context, alpha: true, antialias: false, powerPreference: 'low-power' });
    } catch (e) {
      host.setAttribute('data-gl-off', '');
      return;
    }
    renderer.setClearColor(0x000000, 0);
    canvas.addEventListener('webglcontextlost', function (e) { e.preventDefault(); host.setAttribute('data-gl-off', ''); });

    var guards = [].slice.call(host.querySelectorAll('[data-gl-copy]')).slice(0, MAX_GUARDS);
    var guardUniforms = {
      uGuard: { value: [] }, uGuardN: { value: 0 }, uRes: { value: [1, 1] }
    };
    for (var g = 0; g < MAX_GUARDS; g++) guardUniforms.uGuard.value.push(new THREE.Vector4(-1e4, -1e4, -1e4, -1e4));

    var ctx = {
      host: host, canvas: canvas, renderer: renderer, THREE: THREE,
      scene: new THREE.Scene(), camera: new THREE.PerspectiveCamera(40, 1, 0.1, 400),
      rnd: seed(host.getAttribute('data-seed') || 'brand'), colors: colors(host), mix: mix,
      pointer: pointer(host), size: { w: 1, h: 1 }, small: window.innerWidth < 760, dprCap: 1.5,
      guardUniforms: guardUniforms, GUARD: GUARD, DISC: DISC, time: 0,
      /* true while the scene draws only still frames (reduced motion or Pause animations) */
      frozen: function () { return reduced() || R.isPaused(); },
      /* draw one frame now; scroll-driven scenes call it after changing state while frozen */
      redraw: function () { if (loop) loop.still(); },
      intro: function () { if (reduced()) return 1; var p = Math.min(1, ctx.time / 1.4); return 1 - Math.pow(1 - p, 3); },
      /* world point to CSS pixels inside the canvas: [x, y, inFront] */
      project: function (v) {
        var p = v.clone().project(ctx.camera);
        return [(p.x * 0.5 + 0.5) * ctx.size.w, (0.5 - p.y * 0.5) * ctx.size.h, p.z < 1];
      }
    };
    var loop = null;
    var vis = factory(ctx) || {};

    function measureGuards() {
      var c = canvas.getBoundingClientRect();
      guards.forEach(function (el, i) {
        var r = el.getBoundingClientRect();
        guardUniforms.uGuard.value[i].set(r.left - c.left - 40, r.top - c.top - 30, r.right - c.left + 40, r.bottom - c.top + 30);
      });
      guardUniforms.uGuardN.value = guards.length;
    }

    function resize() {
      var r = canvas.getBoundingClientRect();
      var w = Math.max(1, Math.round(r.width)), h = Math.max(1, Math.round(r.height));
      renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, ctx.dprCap));
      renderer.setSize(w, h, false);
      ctx.size = { w: w, h: h };
      ctx.camera.aspect = w / h;
      ctx.camera.updateProjectionMatrix();
      guardUniforms.uRes.value = [w, h];
      measureGuards();
      if (vis.resize) vis.resize(w, h);
      if (loop && (reduced() || R.isPaused())) loop.still();
    }

    var last = 0, drawn = { frames: 0 };
    function frame(ts) {
      drawn.frames++;
      var dt = last ? Math.min(0.05, (ts - last) / 1000) : 0;
      last = ts;
      if (!reduced() && !R.isPaused()) ctx.time += dt;
      ctx.pointer.step(0.06);
      if (vis.frame) vis.frame(ctx.time, dt);
      renderer.render(ctx.scene, ctx.camera);
    }

    resize();
    loop = R.loop(canvas, frame);
    host.__blgl = { ctx: ctx, frame: frame, drawn: drawn, vis: vis };
    var pending = 0;
    if ('ResizeObserver' in window) {
      new ResizeObserver(function () {
        if (pending) return;
        pending = requestAnimationFrame(function () { pending = 0; resize(); });
      }).observe(canvas);
    }
    document.addEventListener('bl:motion', function () { last = 0; });
    /* copy reveals move the guard boxes a little after load; measure once more when they settle */
    setTimeout(measureGuards, 1400);
  }

  var factories = {};
  function register(name, factory) {
    factories[name] = factory;
    document.querySelectorAll('[data-gl="' + name + '"]').forEach(function (host) { mount(host, factory); });
  }

  /* QA hook: render the host's scene once and return the share of pixels drawn (0-1), or -1 when it has no scene */
  function coverage(host) {
    var m = host && host.__blgl;
    if (!m || !m.ctx) return -1;
    var r = m.ctx.renderer, gl = r.getContext();
    m.frame(performance.now());
    var w = gl.drawingBufferWidth, h = gl.drawingBufferHeight, buf = new Uint8Array(w * h * 4), n = 0;
    gl.readPixels(0, 0, w, h, gl.RGBA, gl.UNSIGNED_BYTE, buf);
    for (var i = 3; i < buf.length; i += 4) if (buf[i] > 8) n++;
    return n / (w * h);
  }

  window.BLGL = { THREE: THREE, register: register, seed: seed, rgb: rgb, mix: mix, GUARD: GUARD, DISC: DISC, coverage: coverage };
})();
