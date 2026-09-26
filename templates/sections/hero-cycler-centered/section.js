/* kinetic-typography-cycler: 2800ms hold, 520ms ease-back entrance */
(function () {
  document.querySelectorAll('[data-cycler]').forEach(function (box) {
    var words = box.querySelectorAll('.bl-cycler__word');
    if (words.length < 2 || window.BL.RM) return;
    var i = 0;
    setInterval(function () {
      if (document.hidden) return;
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
    }, 2800);
  });
})();
