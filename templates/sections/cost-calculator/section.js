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
    var shown = 0, anim = 0, lastPct = null;
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
      var from = shown, t0 = null;
      cancelAnimationFrame(anim);
      if (window.BL.RM) { shown = save; saveEl.textContent = money(save); return; }
      (function step(ts) {
        if (t0 === null) t0 = ts;
        var p = Math.min((ts - t0) / 400, 1);
        shown = from + (save - from) * (1 - Math.pow(1 - p, 3));
        saveEl.textContent = money(shown);
        if (p < 1) anim = requestAnimationFrame(step);
      })(performance.now());
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
