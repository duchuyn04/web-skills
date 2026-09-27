/* case-filter: build one pill per industry, filter with a View Transition where supported, announce the count */
(function () {
  document.querySelectorAll('[data-cfilter]').forEach(function (sec) {
    var cards = Array.prototype.slice.call(sec.querySelectorAll('[data-industry]'));
    var pills = sec.querySelector('[data-cfilter-pills]');
    var status = sec.querySelector('[data-cfilter-status]');
    /* each card needs a unique view-transition-name, or the browser skips the transition */
    cards.forEach(function (c, i) { c.style.viewTransitionName = (sec.id || 'cases') + '-case-' + i; });
    var names = [];
    cards.forEach(function (c) { var k = c.getAttribute('data-industry'); if (names.indexOf(k) < 0) names.push(k); });
    if (names.length < 2) return;

    function pill(label, key, n) {
      var b = document.createElement('button');
      b.type = 'button';
      b.className = 'bl-cfilter__pill';
      b.setAttribute('aria-pressed', key === '' ? 'true' : 'false');
      b.setAttribute('data-key', key);
      b.textContent = label;
      var s = document.createElement('small');
      s.textContent = String(n);
      s.setAttribute('aria-hidden', 'true');
      b.appendChild(s);
      pills.appendChild(b);
    }
    pill(sec.getAttribute('data-all'), '', cards.length);
    names.forEach(function (k) { pill(k, k, cards.filter(function (c) { return c.getAttribute('data-industry') === k; }).length); });
    pills.hidden = false;

    function apply(key) {
      var shown = 0;
      cards.forEach(function (c) {
        var on = !key || c.getAttribute('data-industry') === key;
        c.hidden = !on;
        if (on) { shown++; c.classList.add('is-in'); }
      });
      Array.prototype.forEach.call(pills.children, function (b) { b.setAttribute('aria-pressed', String(b.getAttribute('data-key') === key)); });
      status.textContent = shown + ' ' + sec.getAttribute('data-count-label');
    }
    pills.addEventListener('click', function (e) {
      var b = e.target.closest('.bl-cfilter__pill');
      if (!b || b.getAttribute('aria-pressed') === 'true') return;
      var key = b.getAttribute('data-key');
      if (document.startViewTransition) document.startViewTransition(function () { apply(key); });
      else apply(key);
    });
  });
})();
