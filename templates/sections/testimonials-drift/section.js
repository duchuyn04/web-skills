/* testimonials-drift: deal the cards into three columns, each column holds its list twice and drifts up at its own speed.
   The copy is aria-hidden and inert. The section button and the page-wide motion switch pause it; it also stops off screen. */
(function () {
  document.querySelectorAll('[data-drift]').forEach(function (sec) {
    var BL = window.BL || {};
    var list = sec.querySelector('[data-drift-list]');
    var toggle = sec.querySelector('[data-drift-toggle]');
    if (BL.RM || !list) { if (toggle) toggle.hidden = true; return; }
    var cards = Array.prototype.slice.call(list.children);
    var wall = document.createElement('div');
    wall.className = 'bl-drift__wall';
    var speeds = [52, 64, 58];
    var mq2 = window.matchMedia('(max-width: 960px)'), mq1 = window.matchMedia('(max-width: 600px)');
    function build() {
      var n = mq1.matches ? 1 : (mq2.matches ? 2 : 3);
      wall.textContent = '';
      wall.style.gridTemplateColumns = 'repeat(' + n + ', minmax(0, 1fr))';
      for (var c = 0; c < n; c++) {
        var col = document.createElement('div');
        col.className = 'bl-drift__col';
        var track = document.createElement('div');
        track.className = 'bl-drift__track';
        track.style.setProperty('--dur', (speeds[c] * (n === 1 ? 1.8 : 1)) + 's');
        var real = document.createElement('ul');
        cards.forEach(function (card, i) { if (i % n === c) real.appendChild(card); });
        var copy = real.cloneNode(true);
        copy.setAttribute('aria-hidden', 'true');
        copy.setAttribute('inert', '');
        track.appendChild(real);
        track.appendChild(copy);
        col.appendChild(track);
        wall.appendChild(col);
      }
    }
    build();
    list.replaceWith(wall);
    /* never taller than the shortest column, so a card and its copy are not on screen together */
    function size() {
      var h = Infinity;
      wall.querySelectorAll('.bl-drift__track > ul:first-child').forEach(function (u) { h = Math.min(h, u.offsetHeight); });
      wall.style.height = isFinite(h) ? Math.min(mq1.matches ? 560 : 640, h) + 'px' : '';
    }
    size();
    window.addEventListener('resize', size);
    [mq1, mq2].forEach(function (mq) { if (mq.addEventListener) mq.addEventListener('change', function () { build(); size(); }); });

    var userPaused = false;
    function show() {
      var p = userPaused || !!BL.paused;
      sec.classList.toggle('is-paused', p);
      toggle.setAttribute('aria-pressed', String(p));
      toggle.querySelector('[data-drift-label]').textContent = toggle.getAttribute(p ? 'data-label-play' : 'data-label-pause');
    }
    toggle.addEventListener('click', function () { userPaused = !(userPaused || BL.paused); if (!userPaused && BL.paused && BL.setPaused) BL.setPaused(false); show(); });
    document.addEventListener('bl:motion', show);
    if ('IntersectionObserver' in window) {
      new IntersectionObserver(function (entries) { sec.classList.toggle('is-offscreen', !entries[0].isIntersecting); }).observe(wall);
    }
  });
})();
