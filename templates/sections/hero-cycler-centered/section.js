/* kinetic-typography-cycler: 2800ms hold, 520ms ease-back entrance. The cycle is a repeating GSAP tween registered
   with BL.motion.ambient, so the page-wide Pause switch holds it. */
(function () {
  var BL = window.BL;
  document.querySelectorAll('[data-cycler]').forEach(function (box) {
    var words = box.querySelectorAll('.bl-cycler__word');
    if (words.length < 2 || !BL || BL.RM || !BL.gsap) return;
    var i = 0;
    function swap() {
      var cur = words[i];
      i = (i + 1) % words.length;
      var next = words[i];
      cur.classList.remove('is-active');
      cur.classList.add('is-leaving');
      cur.setAttribute('aria-hidden', 'true');
      next.style.transition = 'none';
      next.classList.remove('is-leaving');
      void next.offsetWidth;
      next.style.transition = '';
      next.classList.add('is-active');
      next.removeAttribute('aria-hidden');
    }
    BL.motion.ambient(BL.gsap.to({}, { duration: 2.8, repeat: -1, onRepeat: swap }));
  });
})();
