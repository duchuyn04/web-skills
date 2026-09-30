/* metrics-bars3d: when a pair is seen its columns grow once (CSS transition, 1.2 s, 150 ms apart) while the numbers
   on top count up in step. Each small stage gets a perspective origin that points at the middle of the row, so the
   pairs read as one scene seen from one camera. Reduced motion: final heights and numbers at once. */
(function () {
  var BL = window.BL;
  if (!BL || !BL.gsap) return;
  document.querySelectorAll('[data-mbars]').forEach(function (sec) {
    var grid = sec.querySelector('[data-mbars-grid]');
    var items = Array.prototype.slice.call(sec.querySelectorAll('[data-mbars-item]'));
    if (BL.stage3d) BL.stage3d(sec);

    function aim() {
      var g = grid.getBoundingClientRect(), mid = g.left + g.width / 2;
      items.forEach(function (it) {
        var r = it.getBoundingClientRect();
        it.querySelector('.bl-mbars__stage').style.setProperty('--po', Math.round((mid - (r.left + r.width / 2)) * 0.55) + 'px');
      });
    }
    aim();
    var t = null;
    window.addEventListener('resize', function () { clearTimeout(t); t = setTimeout(aim, 150); });

    function count(el, delay) {
      var target = parseFloat(el.getAttribute('data-num'));
      if (isNaN(target)) return;
      var dec = parseInt(el.getAttribute('data-dec') || '0', 10) || 0;
      var pre = el.getAttribute('data-pre') || '', suf = el.getAttribute('data-suf') || '';
      var final = el.textContent;
      el.textContent = pre + BL.formatNumber(0, dec) + suf;
      var n = { v: 0 };
      BL.gsap.to(n, {
        v: target, duration: 1.2, delay: delay / 1000, ease: 'power2.out',
        onUpdate: function () { el.textContent = pre + BL.formatNumber(n.v, dec) + suf; },
        onComplete: function () { el.textContent = final; }
      });
    }

    items.forEach(function (it, i) {
      if (BL.RM) { it.classList.add('is-grown'); return; }
      var nums = Array.prototype.slice.call(it.querySelectorAll('.bl-mbars__num'));
      BL.onVisible(it, function () {
        it.classList.add('is-grown');
        nums.forEach(function (el, k) { count(el, i * 160 + (nums.length > 1 ? k * 150 : 0)); });
      }, 0.35);
    });
  });
})();
