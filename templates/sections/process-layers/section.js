/* process-layers: an IntersectionObserver on a thin band across the middle of the screen marks the step in view.
   Steps and plates up to it get is-open, the one in view gets is-active (lit plate, icon, leader line).
   Where scroll-driven animations are supported (desktop, motion allowed) the plates follow the scroll through CSS
   view timelines instead (class is-sd) and the observer only marks the text. Motion follows scroll; nothing loops. */
(function () {
  var BL = window.BL;
  if (!BL) return;
  var SD = !!(window.CSS && CSS.supports && CSS.supports('animation-timeline: view()'));
  document.querySelectorAll('[data-play]').forEach(function (sec) {
    var steps = Array.prototype.slice.call(sec.querySelectorAll('[data-step]'));
    var plates = Array.prototype.slice.call(sec.querySelectorAll('[data-plate]'));
    if (BL.stage3d) BL.stage3d(sec);
    var wide = window.matchMedia('(min-width: 900px)');
    function mode() { sec.classList.toggle('is-sd', SD && wide.matches && !BL.RM); }
    mode();
    if (wide.addEventListener) wide.addEventListener('change', mode);

    var active = -2;
    function set(a) {
      if (a === active) return;
      active = a;
      plates.forEach(function (p, i) { p.classList.toggle('is-open', i <= a); p.classList.toggle('is-active', i === a); });
      steps.forEach(function (s, i) { s.classList.toggle('is-active', i === a); });
    }
    if (!('IntersectionObserver' in window)) { set(0); return; }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        var i = steps.indexOf(e.target);
        if (e.isIntersecting) set(i);
        else if (i === 0 && e.boundingClientRect.top > e.rootBounds.bottom) set(-1);
      });
    }, { rootMargin: '-45% 0px -45% 0px', threshold: 0 });
    steps.forEach(function (s) { io.observe(s); });
    set(-1);
  });
})();
