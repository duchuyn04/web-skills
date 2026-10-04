/* team-coverflow: APG carousel without rotation. Each card gets its signed offset from the current person (the row
   wraps around), up to two cards per side are shown (one on phones). A card that wraps from one end to the other
   jumps without a transition so it never sweeps across the row. Buttons, arrow keys, Home and End, or a click on a
   side card change the person; the text below crossfades and hidden slides are inert. Moves on request only. */
(function () {
  var BL = window.BL;
  if (!BL) return;
  document.querySelectorAll('[data-tcov]').forEach(function (sec) {
    var wrap = sec.querySelector('[data-tcov-wrap]');
    var cards = Array.prototype.slice.call(sec.querySelectorAll('[data-card]'));
    var slides = Array.prototype.slice.call(sec.querySelectorAll('[data-slide]'));
    var info = sec.querySelector('[data-tcov-info]');
    var nowEl = sec.querySelector('[data-tcov-now]');
    var n = cards.length, cur = 0, last = [];
    var phone = window.matchMedia('(max-width: 640px)');
    var of = info.getAttribute('data-of-label') || 'of';
    function pad(i) { return (i < 9 ? '0' : '') + (i + 1); }
    if (BL.stage3d) BL.stage3d(sec);

    function offset(i) {
      var d = ((i - cur) % n + n) % n;
      if (d > n / 2) d -= n;
      /* with an even count the card straight opposite goes to the side with more room: the right */
      if (n % 2 === 0 && d === -n / 2) d = n / 2;
      return d;
    }
    function place(first) {
      var reach = phone.matches ? 1 : 2;
      cards.forEach(function (c, i) {
        var d = offset(i), ad = Math.abs(d);
        var jump = !first && last[i] !== undefined && Math.abs(d - last[i]) > 1;
        if (jump) c.classList.add('no-trans');
        c.style.setProperty('--d', String(d));
        c.style.setProperty('--ad', String(Math.min(ad, 3)));
        c.style.setProperty('--sg', String(d === 0 ? 0 : (d > 0 ? 1 : -1)));
        c.classList.toggle('is-center', d === 0);
        c.classList.toggle('is-far', ad > reach);
        if (jump) { void c.offsetWidth; c.classList.remove('no-trans'); }
        last[i] = d;
      });
      slides.forEach(function (s, i) {
        var on = i === cur;
        s.classList.toggle('is-current', on);
        s.inert = !on;
        s.setAttribute('aria-label', (i + 1) + ' ' + of + ' ' + n);
      });
      nowEl.textContent = pad(cur);
    }
    function go(i) { cur = (i + n) % n; place(false); }

    sec.querySelector('[data-tcov-total]').textContent = pad(n - 1);
    sec.querySelector('[data-tcov-prev]').addEventListener('click', function () { go(cur - 1); });
    sec.querySelector('[data-tcov-next]').addEventListener('click', function () { go(cur + 1); });
    cards.forEach(function (c, i) { c.addEventListener('click', function () { if (i !== cur) go(i); }); });
    wrap.addEventListener('keydown', function (e) {
      var k = { ArrowRight: 1, ArrowLeft: -1 }[e.key];
      if (e.key === 'Home') { e.preventDefault(); go(0); return; }
      if (e.key === 'End') { e.preventDefault(); go(n - 1); return; }
      if (!k) return;
      e.preventDefault();
      go(cur + k);
    });
    if (phone.addEventListener) phone.addEventListener('change', function () { place(true); });
    place(true);
  });
})();
