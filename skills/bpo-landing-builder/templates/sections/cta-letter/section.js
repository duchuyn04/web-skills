/* cta-letter: letter-unfold-3d. The letter is folded by JS (so without JS or under reduced motion it is flat from
   the start) and unfolds once when a third of it is in view. Buttons stay focusable: if keyboard focus reaches the
   letter first, focusin opens it at once, so focus never sits on a folded panel. Fold order and seal side come
   from the brand name. The optional form checks the email, then posts to its action or shows the thank-you line. */
(function () {
  var BL = window.BL;
  if (!BL || !BL.stage3d) return;
  document.querySelectorAll('[data-fxletter]').forEach(function (sec) {
    var folded = false;
    function open(instant) {
      if (!folded) return;
      folded = false;
      if (instant) sec.classList.add('is-still');
      sec.classList.remove('is-folded');
      if (instant) { void sec.offsetWidth; sec.classList.remove('is-still'); }
    }
    var st = BL.stage3d(sec, { reveal: function () { open(true); } });
    var rnd = st.rnd;
    if (rnd() < 0.5) sec.classList.add('is-bottom-first');
    if (rnd() < 0.5) sec.classList.add('is-seal-right');
    st.onMotion(function (paused) { if (paused) open(true); });

    if (!BL.RM && !st.paused && !document.documentElement.classList.contains('bl-shot')) {
      folded = true;
      sec.classList.add('is-still', 'is-folded');
      void sec.offsetWidth;
      sec.classList.remove('is-still');
      var stage = sec.querySelector('[data-letter-stage]');
      if (!('IntersectionObserver' in window)) open(true);
      else {
        /* open when a third is in view, or at once if the visitor has already scrolled past it */
        var io = new IntersectionObserver(function (entries) {
          entries.forEach(function (e) {
            if (e.intersectionRatio >= 0.35) { io.disconnect(); setTimeout(function () { open(false); }, 150); }
            else if (e.boundingClientRect.top < 0) { io.disconnect(); open(true); }
          });
        }, { threshold: [0, 0.2, 0.35, 0.6] });
        io.observe(stage);
      }
    }

    /* flat for screenshots: qa_screenshot.py sets html.bl-shot and fires a resize */
    window.addEventListener('resize', function () { if (document.documentElement.classList.contains('bl-shot')) open(true); });

    var form = sec.querySelector('[data-letter-form]');
    if (form) form.addEventListener('submit', function (e) {
      var input = form.querySelector('input');
      if (!input.checkValidity()) { e.preventDefault(); input.reportValidity(); return; }
      if (form.getAttribute('action')) return;
      e.preventDefault();
      form.querySelector('.bl-fxletter__form-row').hidden = true;
      form.querySelector('.bl-fxletter__done').hidden = false;
    });
  });
})();
