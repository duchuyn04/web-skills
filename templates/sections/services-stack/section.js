/* services-stack: sticky-card-stack, flowing-line-ribbons on the brand card */
(function () {
  document.querySelectorAll('[data-sstack]').forEach(function (sec) {
    var cards = Array.prototype.slice.call(sec.querySelectorAll('[data-scard]'));
    var items = cards.map(function (c) { return c.parentNode; });
    var shades = cards.map(function (c) { return c.querySelector('.bl-services-stack__shade'); });

    cards.forEach(function (card, i) {
      if (window.BL) window.BL.onVisible(card, function () { card.classList.add('is-seen'); }, 0.25);
      if (i % 3 === 2 && window.BLRibbons) {
        var c = document.createElement('canvas');
        c.className = 'bl-services-stack__waves';
        c.setAttribute('aria-hidden', 'true');
        card.insertBefore(c, card.firstChild);
        window.BLRibbons.waves(c, card, {
          color: getComputedStyle(card).getPropertyValue('--card-strong').trim() || '#fff', revealMs: 2000, mouse: true,
          ribbons: [{ y0: 0.95, y1: 0.15, amp: 0.06, freq: 0.8, spread: 0.3, twist: 1.3, shift: 0.8, speed: 0.00016, lines: 26, alpha: 0.3 }]
        });
      }
    });

    /* scroll-linked shrink and shade: one ScrollTrigger per stack, skipped under reduced motion */
    function update() {
      if (!wide.matches) {
        cards.forEach(function (c, i) { c.style.transform = ''; shades[i].style.opacity = '0'; });
        return;
      }
      var tops = items.map(function (it) { return parseFloat(getComputedStyle(it).top) || 0; });
      cards.forEach(function (card, i) {
        var h = card.offsetHeight || 1;
        var depth = 0;
        for (var j = i + 1; j < cards.length; j++) {
          var r = items[j].getBoundingClientRect();
          depth += Math.max(0, Math.min(1, (tops[j] + h - r.top) / h));
        }
        card.style.transform = depth ? 'scale(' + (1 - depth * 0.045).toFixed(4) + ')' : '';
        shades[i].style.opacity = Math.min(0.45, depth * 0.22).toFixed(3);
      });
    }
    var wide = window.matchMedia('(min-width: 861px)');
    if (!window.ScrollTrigger || !window.BL) return;
    window.BL.motion.media(function (reduce) {
      if (reduce) return;
      var trig = window.ScrollTrigger.create({ trigger: sec, start: 'top bottom', end: 'bottom top', onUpdate: update, onRefresh: update });
      update();
      return function () {
        trig.kill();
        cards.forEach(function (c, i) { c.style.transform = ''; shades[i].style.opacity = '0'; });
      };
    });
  });
})();
