/* Shared: helpers for CSS 3D sections (fx3d). BL.stage3d(section, {reveal}) returns {rnd, paused, onMotion}.
   - rnd: brand-seeded random numbers (FNV-1a + mulberry32, the same generator as scene3d.js and build.py site.seed)
   - paused: true under reduced motion or when the page-wide Pause animations switch is on
   - the switch also pauses Web Animations and CSS transitions inside the section (Element.getAnimations)
   - reveal(el): called on focusin so a face that holds keyboard focus can be turned to the front (WCAG 2.4.11) */
(function () {
  var BL = window.BL;
  if (!BL || BL.stage3d) return;
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
  BL.seed = BL.seed || seed;
  BL.stage3d = function (sec, opts) {
    opts = opts || {};
    var st = { rnd: seed(sec.getAttribute('data-seed') || 'brand'), paused: !!(BL.paused || BL.RM), listeners: [] };
    st.onMotion = function (fn) { st.listeners.push(fn); };
    document.addEventListener('bl:motion', function (e) {
      st.paused = !!e.detail.paused || !!BL.RM;
      /* leave the copy's one-off reveal transitions alone, or pausing early would freeze text half-faded */
      if (sec.getAnimations) sec.getAnimations({ subtree: true }).forEach(function (a) {
        var t = a.effect && a.effect.target;
        if (t && t.closest && t.closest('[data-reveal]')) return;
        if (st.paused) a.pause(); else a.play();
      });
      st.listeners.forEach(function (fn) { fn(st.paused); });
    });
    if (opts.reveal) sec.addEventListener('focusin', function (e) { opts.reveal(e.target); });
    return st;
  };
})();
