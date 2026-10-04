/* quote-spotlight: crossfade between quotes with buttons and arrow keys (no autoplay) */
(function () {
  document.querySelectorAll('[data-qspot]').forEach(function (root) {
    /* quote-mark-draw: every path of the mark gets the same length, so CSS can draw it with a dash offset */
    root.querySelectorAll('.bl-qspot__mark path').forEach(function (p) { p.setAttribute('pathLength', '100'); });
    var items = Array.prototype.slice.call(root.querySelectorAll('[data-qspot-item]'));
    var dots = Array.prototype.slice.call(root.querySelectorAll('.bl-qspot__dot'));
    if (items.length < 2) return;
    var i = 0;
    function show(n) {
      i = (n + items.length) % items.length;
      items.forEach(function (it, k) {
        it.classList.toggle('is-active', k === i);
        if (k === i) it.removeAttribute('aria-hidden'); else it.setAttribute('aria-hidden', 'true');
      });
      dots.forEach(function (d, k) { d.classList.toggle('is-active', k === i); });
    }
    var prev = root.querySelector('[data-qspot-prev]');
    var next = root.querySelector('[data-qspot-next]');
    if (prev) prev.addEventListener('click', function () { show(i - 1); });
    if (next) next.addEventListener('click', function () { show(i + 1); });
    root.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowRight') show(i + 1);
      if (e.key === 'ArrowLeft') show(i - 1);
    });
  });
})();
