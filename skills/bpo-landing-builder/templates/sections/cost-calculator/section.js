/* reactive-cost-calculator */
(function () {
  document.querySelectorAll('[data-calc]').forEach(function (root) {
    var cur = root.getAttribute('data-currency') || '$';
    var roles = Array.prototype.slice.call(root.querySelectorAll('.bl-calc__role'));
    var range = root.querySelector('[data-calc-range]');
    var teamEl = root.querySelector('[data-calc-team]');
    var saveEl = root.querySelector('[data-calc-save]');
    var pctEl = root.querySelector('[data-calc-pct]');
    var onEl = root.querySelector('[data-calc-on]');
    var offEl = root.querySelector('[data-calc-off]');
    var offBar = root.querySelector('[data-calc-offbar]');
    var shown = 0, anim = null, lastPct = null;
    var money = function (n) { return cur + window.BL.formatNumber(Math.round(n), 0); };
    var active = function () { return roles.filter(function (r) { return r.getAttribute('aria-checked') === 'true'; })[0] || roles[0]; };

    function update() {
      var r = active();
      var n = Number(range.value);
      var on = n * Number(r.getAttribute('data-onshore'));
      var off = n * Number(r.getAttribute('data-offshore'));
      var save = Math.max(0, on - off);
      var pct = on ? Math.round((save / on) * 100) : 0;
      var min = Number(range.min), max = Number(range.max);
      range.style.setProperty('--fill', ((n - min) / (max - min)) * 100 + '%');
      teamEl.textContent = String(n);
      onEl.textContent = money(on);
      offEl.textContent = money(off);
      offBar.style.transform = 'scaleX(' + (on ? off / on : 0) + ')';
      pctEl.textContent = '-' + pct + '%';
      if (pct !== lastPct && lastPct !== null && !window.BL.RM) {
        pctEl.classList.remove('is-bump'); void pctEl.offsetWidth; pctEl.classList.add('is-bump');
      }
      lastPct = pct;
      if (anim) anim.kill();
      if (window.BL.RM || !window.BL.gsap) { shown = save; saveEl.textContent = money(save); return; }
      var box = { v: shown };
      anim = window.BL.gsap.to(box, {
        v: save, duration: 0.4, ease: 'power2.out',
        onUpdate: function () { shown = box.v; saveEl.textContent = money(shown); }
      });
    }
    roles.forEach(function (r) {
      r.addEventListener('click', function () {
        roles.forEach(function (x) { x.setAttribute('aria-checked', String(x === r)); });
        update();
      });
    });
    range.addEventListener('input', update);
    update();
  });
})();
