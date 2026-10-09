/* industries-index: text-scramble-resolve. Each industry name is split into characters (NFC first, then Array.from,
   so a Vietnamese letter with its marks stays one character); every character box is fixed to the width of its real
   letter, so the row never jitters while random glyphs run through it. When the list comes into view each row
   resolves left to right (0.6 s, rows 80 ms apart); hover or keyboard focus scrambles it again for 0.35 s. The row
   keeps the real name as its accessible text. Reduced motion: no scramble. */
(function () {
  var gsap = window.gsap;
  document.querySelectorAll('[data-iindex]').forEach(function (sec) {
    if (!gsap || !window.BL || window.BL.RM) return;
    var rows = [].slice.call(sec.querySelectorAll('[data-iindex-row]'));
    var titles = rows.map(function (row) {
      var el = row.querySelector('[data-iindex-title]');
      var text = el.textContent.normalize('NFC');
      el.setAttribute('aria-hidden', 'true');
      var sr = document.createElement('span');
      sr.className = 'bl-sr-only';
      sr.textContent = text;
      el.parentNode.insertBefore(sr, el);
      el.textContent = '';
      var chars = [];
      text.split(/(\s+)/).forEach(function (part) {
        if (!part) return;
        if (/^\s+$/.test(part)) { el.appendChild(document.createTextNode(' ')); return; }
        var w = document.createElement('span'); /* one word per box, so a long name wraps between words only */
        w.className = 'bl-industries-index__w';
        Array.from(part).forEach(function (ch) {
          var s = document.createElement('span');
          s.className = 'bl-industries-index__ch';
          s.textContent = ch;
          w.appendChild(s);
          chars.push({ el: s, ch: ch, space: false });
        });
        el.appendChild(w);
      });
      /* glyphs come from the name's own letters, so they fit the boxes of the real ones */
      var pool = chars.map(function (c) { return c.ch.toUpperCase(); }).concat(['#', '%', '*', '+']);
      return { el: el, chars: chars, pool: pool, tween: null };
    });
    /* widths in em, so they follow the fluid font size at any screen width */
    function measure() {
      titles.forEach(function (t) {
        var fs = parseFloat(getComputedStyle(t.el).fontSize) || 16;
        t.chars.forEach(function (c) { c.el.style.width = ''; c.el.textContent = c.ch; });
        t.chars.forEach(function (c) { c.el.style.width = (c.el.getBoundingClientRect().width / fs).toFixed(4) + 'em'; });
      });
    }
    measure();
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(measure);

    function scramble(t, dur, delay) {
      if (t.tween) t.tween.kill();
      var st = { p: 0 }, n = t.chars.length, last = -1;
      t.tween = gsap.to(st, {
        p: 1, duration: dur, delay: delay || 0, ease: 'none',
        onStart: function () { t.el.classList.remove('is-wait'); },
        onUpdate: function () {
          var tick = Math.floor(st.p * dur * 22); /* new glyphs about 22 times a second */
          var fresh = tick !== last; last = tick;
          t.chars.forEach(function (c, i) {
            if (c.space) return;
            var done = st.p >= (i + 1) / n * 0.85 + 0.15 * (i / n);
            if (done) { if (c.el.textContent !== c.ch) { c.el.textContent = c.ch; c.el.classList.remove('is-x'); } return; }
            if (fresh) { c.el.textContent = t.pool[(Math.random() * t.pool.length) | 0]; c.el.classList.add('is-x'); }
          });
        },
        onComplete: function () { t.chars.forEach(function (c) { c.el.textContent = c.ch; c.el.classList.remove('is-x'); }); }
      });
    }

    titles.forEach(function (t) { t.el.classList.add('is-wait'); });
    window.BL.onVisible(sec.querySelector('.bl-industries-index__list'), function () {
      titles.forEach(function (t, i) { scramble(t, 0.6, 0.15 + i * 0.08); });
    }, 0.15);
    rows.forEach(function (row, i) {
      var again = function () { if (!titles[i].el.classList.contains('is-wait')) scramble(titles[i], 0.35, 0); };
      row.addEventListener('pointerenter', function (e) { if (e.pointerType === 'mouse') again(); });
      row.addEventListener('focus', function () { if (row.matches(':focus-visible')) again(); });
    });
  });
})();
