/* footer-wordmark-rise: fit the brand name to the footer width, then raise its letters once as it enters */
(function () {
  document.querySelectorAll('[data-wordmark]').forEach(function (el) {
    var text = el.textContent.trim();
    el.textContent = '';
    var inner = document.createElement('span');
    inner.className = 'bl-wm-inner';
    el.appendChild(inner);
    Array.prototype.forEach.call(text, function (ch, i) {
      var s = document.createElement('span');
      s.className = 'bl-wm-l';
      s.style.setProperty('--l', String(i));
      s.textContent = ch === ' ' ? ' ' : ch;
      inner.appendChild(s);
    });
    function fit() {
      el.style.fontSize = '100px';
      var pad = parseFloat(getComputedStyle(el).paddingLeft) * 2;
      var room = el.clientWidth - pad;
      var width = inner.offsetWidth;
      if (width > 0) el.style.fontSize = Math.max(32, Math.floor(100 * room / width * 0.98)) + 'px';
    }
    fit();
    window.addEventListener('resize', fit);
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(fit);
    if (window.BL && !window.BL.RM) {
      el.classList.add('is-ready');
      window.BL.onVisible(el, function () { el.classList.add('is-in'); }, 0.4);
    }
  });
})();
