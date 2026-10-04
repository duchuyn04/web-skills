/* about-helix: at 900px and up, with motion allowed, the section pins and one invisible marker per milestone crosses
   the middle of the screen as the visitor scrolls. The marker in the middle sets --act on the rig, which turns and
   lifts the helix (0.85 s transition) so that milestone faces the reader; cards two or more steps away fade.
   Moves with scroll only. Phones and reduced motion keep the plain timeline. */
(function () {
  var BL = window.BL;
  if (!BL) return;
  document.querySelectorAll('[data-helix]').forEach(function (sec) {
    var rig = sec.querySelector('[data-helix-rig]');
    var cards = Array.prototype.slice.call(sec.querySelectorAll('[data-card]'));
    var rail = Array.prototype.slice.call(sec.querySelectorAll('[data-rail]'));
    var marks = Array.prototype.slice.call(sec.querySelectorAll('[data-mark]'));
    var n = cards.length, act = -1, io = null;
    var wide = window.matchMedia('(min-width: 900px)');
    if (BL.stage3d) BL.stage3d(sec);
    sec.style.setProperty('--n', String(n));

    function set(a) {
      a = Math.max(0, Math.min(n - 1, a));
      if (a === act) return;
      act = a;
      rig.style.setProperty('--act', String(a));
      cards.forEach(function (c, i) { c.setAttribute('data-dist', String(Math.min(Math.abs(i - a), 3))); });
      rail.forEach(function (r, i) { r.classList.toggle('is-active', i === a); });
    }
    function mode() {
      var on = wide.matches && !BL.RM && 'IntersectionObserver' in window;
      sec.classList.toggle('is-3d', on);
      if (on && !io) {
        io = new IntersectionObserver(function (entries) {
          entries.forEach(function (e) { if (e.isIntersecting) set(marks.indexOf(e.target)); });
        }, { rootMargin: '-49.5% 0px -49.5% 0px', threshold: 0 });
        marks.forEach(function (m) { io.observe(m); });
      } else if (!on && io) {
        io.disconnect(); io = null;
      }
    }
    set(0);
    mode();
    if (wide.addEventListener) wide.addEventListener('change', mode);
  });
})();
