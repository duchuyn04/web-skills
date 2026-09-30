/* services-cylinder: cylinder-turn-3d. n cards on a drum of radius r = (w / 2) / tan(180 / n) + gap. The rig is
   moved back by r (and up by the tilt) so the front card sits at z = 0 at its natural size, then turned by
   rotateY(-k * 360 / n). Cards more than 100 degrees from the front are hidden; every card except the front one is
   inert, so Tab never reaches a link turned away. Tilt, direction, gap and the intro offset come from the brand. */
(function () {
  var BL = window.BL;
  if (!BL || !BL.stage3d) return;
  document.querySelectorAll('[data-fxcyl]').forEach(function (sec) {
    var rig = sec.querySelector('[data-fxcyl-rig]');
    var cards = Array.prototype.slice.call(sec.querySelectorAll('[data-fxcyl-card]'));
    var tabs = Array.prototype.slice.call(sec.querySelectorAll('[role="tab"]'));
    var now = sec.querySelector('[data-fxcyl-now]'), live = sec.querySelector('[data-fxcyl-live]');
    var n = cards.length;
    if (!rig || n < 2) return;
    var mq = window.matchMedia('(max-width: 719px)');
    var cur = 0, pos = 0, r = 0, list = false, pending = false, timer = null;

    var st = BL.stage3d(sec, {
      reveal: function (el) {
        var card = el.closest && el.closest('[data-fxcyl-card]');
        if (pending) intro();
        if (card && !list && cards.indexOf(card) !== cur) select(cards.indexOf(card), false);
      }
    });
    var rnd = st.rnd;
    var dir = rnd() < 0.5 ? 1 : -1;
    var tilt = (4 + rnd() * 5) * Math.PI / 180;
    var gap = 26 + rnd() * 34;
    var offset = 1 + Math.floor(rnd() * 2);
    var step = 360 / n;
    var total = sec.querySelector('[data-fxcyl-total]');
    if (total) total.textContent = (n < 10 ? '0' : '') + n;

    function rel(i) {
      var a = ((dir * i * step - dir * pos * step) % 360 + 540) % 360 - 180;
      return Math.abs(a);
    }
    function shade(final) {
      cards.forEach(function (c, i) {
        var a = rel(i);
        c.style.setProperty('--dim', a < 1 ? '0' : Math.min(0.72, 0.28 + a / 160).toFixed(2));
        if (final) c.classList.toggle('is-away', a > 100);
        else if (a <= 100) c.classList.remove('is-away');
      });
    }
    function pose(animate) {
      if (list) return;
      var turn = -dir * pos * step;
      clearTimeout(timer);
      if (!animate || BL.RM) sec.classList.add('is-still');
      else rig.style.willChange = 'transform';
      shade(false);
      rig.style.transform = 'translate3d(0,' + (r * Math.sin(tilt)).toFixed(1) + 'px,' + (-r * Math.cos(tilt)).toFixed(1) + 'px) rotateX(' +
        (tilt * 180 / Math.PI).toFixed(2) + 'deg) rotateY(' + turn.toFixed(2) + 'deg)';
      if (!animate || BL.RM) {
        void rig.offsetWidth;
        sec.classList.remove('is-still');
        shade(true);
        return;
      }
      timer = setTimeout(function () { rig.style.willChange = ''; shade(true); }, 1050);
    }
    function mark() {
      tabs.forEach(function (t, k) {
        var on = k === cur;
        t.setAttribute('aria-selected', String(on));
        t.tabIndex = on ? 0 : -1;
      });
      cards.forEach(function (c, k) {
        var on = k === cur;
        c.classList.toggle('is-front', on && !list);
        c.inert = !on && !list;
      });
      if (now) now.textContent = (cur < 9 ? '0' : '') + (cur + 1);
    }
    function select(k, announce) {
      if (pending) { pending = false; pos = 0; }
      var delta = ((k - cur) % n + n) % n;
      if (delta > n / 2) delta -= n;
      pos += delta;
      cur = k;
      mark();
      pose(true);
      if (announce && live) live.textContent = (cur + 1) + ' / ' + n + ': ' + cards[cur].querySelector('h3').textContent;
    }
    function layout() {
      list = mq.matches;
      sec.classList.toggle('is-list', list);
      if (list) {
        rig.style.transform = '';
        cards.forEach(function (c) { c.style.transform = ''; c.classList.remove('is-away'); });
        mark();
        return;
      }
      var w = rig.offsetWidth;
      r = (w / 2) / Math.tan(Math.PI / n) + gap;
      cards.forEach(function (c, i) { c.style.transform = 'rotateY(' + (dir * i * step).toFixed(2) + 'deg) translateZ(' + r.toFixed(1) + 'px)'; });
      mark();
      pose(false);
    }
    function intro() {
      pending = false;
      pos = 0;
      pose(!st.paused);
    }

    tabs.forEach(function (t, i) {
      t.addEventListener('click', function () { if (i !== cur) select(i, false); });
      t.addEventListener('keydown', function (e) {
        var k = { ArrowRight: 1, ArrowDown: 1, ArrowLeft: -1, ArrowUp: -1 }[e.key];
        if (e.key === 'Home') k = -i; else if (e.key === 'End') k = n - 1 - i;
        if (k === undefined) return;
        e.preventDefault();
        var to = (i + k + n) % n;
        select(to, false);
        tabs[to].focus();
      });
    });
    var prev = sec.querySelector('[data-fxcyl-prev]'), next = sec.querySelector('[data-fxcyl-next]');
    if (prev) prev.addEventListener('click', function () { select((cur - 1 + n) % n, true); });
    if (next) next.addEventListener('click', function () { select((cur + 1) % n, true); });

    /* first view: the drum stands a seeded step or two away and turns to the first card */
    if (!BL.RM && !st.paused && !mq.matches) { pos = -offset; pending = true; }
    layout();
    if (pending) BL.onVisible(sec.querySelector('[data-fxcyl-stage]'), function () { if (pending) intro(); }, 0.35);

    var rt = null;
    window.addEventListener('resize', function () {
      clearTimeout(rt);
      rt = setTimeout(function () {
        if (pending && mq.matches) { pending = false; pos = 0; }
        layout();
      }, 150);
    });
  });
})();
