/* hero-sundial: live local time for each hub on a tilted 24-hour dial. Local hour and minute come from
   Intl.DateTimeFormat with the hub's IANA time zone (cities.json "tz"); a hub without a time zone is hidden, never
   guessed from longitude. Clocks update on the minute; the page-wide Pause switch freezes them and they jump to the
   current time on resume (WCAG 2.2.2, real-time content). Labels that would overlap are lifted apart. */
(function () {
  var BL = window.BL;
  if (!BL) return;
  function parseShift(text) {
    var m = /^(\d{2}):(\d{2})-(\d{2}):(\d{2})$/.exec((text || '').trim());
    if (!m) return [8 * 60, 17 * 60];
    return [(+m[1]) * 60 + (+m[2]), (+m[3]) * 60 + (+m[4])];
  }
  function inShift(min, s) {
    return s[0] <= s[1] ? (min >= s[0] && min < s[1]) : (min >= s[0] || min < s[1]);
  }
  function pad(n) { return (n < 10 ? '0' : '') + n; }

  document.querySelectorAll('[data-hsun]').forEach(function (sec) {
    var st = BL.stage3d ? BL.stage3d(sec) : { rnd: Math.random, paused: false, onMotion: function () {} };
    var rnd = st.rnd;
    rnd(); rnd();
    sec.setAttribute('data-ticks', rnd() < 0.5 ? 'dots' : 'bars');
    sec.setAttribute('data-glow', rnd() < 0.5 ? 'blend' : 'accent');
    var dir = rnd() < 0.5 ? 1 : -1;
    var rig = sec.querySelector('[data-hsun-rig]');
    var pulse = sec.querySelector('[data-hsun-pulse]');
    var count = sec.querySelector('[data-hsun-count]');
    var srItems = sec.querySelectorAll('[data-sr-hub]');
    var onText = 'On shift', offText = 'Off shift';
    var hubs = Array.prototype.map.call(sec.querySelectorAll('[data-hub]'), function (pin, i) {
      var tz = pin.getAttribute('data-tz'), fmt = null;
      try { if (tz) fmt = new Intl.DateTimeFormat('en-GB', { timeZone: tz, hour: '2-digit', minute: '2-digit', hourCycle: 'h23' }); } catch (e) { fmt = null; }
      if (!fmt) { pin.hidden = true; if (window.console) console.warn('hero-sundial: no valid time zone for hub ' + (i + 1)); }
      var state = pin.querySelector('[data-state]');
      return { pin: pin, fmt: fmt, shift: parseShift(pin.getAttribute('data-shift')), time: pin.querySelector('[data-time]'),
        state: state, chip: pin.querySelector('[data-chip]'), mark: pin.querySelector('[data-mark]'), sr: srItems[i], angle: 0 };
    });
    var legendOn = sec.querySelector('.bl-hsun__key--on');
    if (legendOn) onText = legendOn.parentNode.textContent.trim();
    var legendOff = sec.querySelector('.bl-hsun__key--off');
    if (legendOff) offText = legendOff.parentNode.textContent.trim();

    function update() {
      var now = new Date(), on = 0, live = 0;
      hubs.forEach(function (h) {
        if (!h.fmt) return;
        var hh = 0, mm = 0;
        h.fmt.formatToParts(now).forEach(function (p) { if (p.type === 'hour') hh = +p.value % 24; if (p.type === 'minute') mm = +p.value; });
        var min = hh * 60 + mm, isOn = inShift(min, h.shift), label = pad(hh) + ':' + pad(mm);
        live++; if (isOn) on++;
        h.angle = min / 1440 * 360;
        h.pin.style.setProperty('--a', h.angle.toFixed(2) + 'deg');
        h.pin.classList.toggle('is-on', isOn);
        h.time.textContent = label;
        h.state.textContent = isOn ? onText : offText;
        if (h.sr) {
          var t = h.sr.querySelector('[data-sr-time]');
          t.textContent = label; t.setAttribute('datetime', label);
          h.sr.querySelector('[data-sr-state]').textContent = isOn ? onText : offText;
        }
      });
      if (count) count.textContent = on + '/' + live;
    }

    /* lift labels that overlap on screen; measured in the final pose with transitions off */
    function declutter() {
      var wasSet = sec.classList.contains('is-set');
      sec.classList.add('is-measuring', 'is-set');
      var list = hubs.filter(function (h) { return h.fmt; });
      list.forEach(function (h) { h.chip.style.setProperty('--lift', '14px'); });
      var rects = list.map(function (h) { return { h: h, r: h.chip.getBoundingClientRect(), m: h.mark.getBoundingClientRect().bottom }; });
      /* nearest hub first, so labels further back rise behind it */
      rects.sort(function (a, b) { return b.m - a.m; });
      var placed = [];
      rects.forEach(function (it) {
        var r = { l: it.r.left, r: it.r.right, t: it.r.top, b: it.r.bottom }, up = 0, k = it.r.height / Math.max(1, it.h.chip.offsetHeight);
        for (var guard = 0; guard < 8; guard++) {
          var hit = null;
          placed.forEach(function (p) { if (r.l < p.r - 2 && r.r > p.l + 2 && r.t < p.b + 3 && r.b > p.t - 3) hit = p; });
          if (!hit) break;
          var d = r.b - hit.t + 5;
          r.t -= d; r.b -= d; up += d;
        }
        placed.push(r);
        it.h.chip.style.setProperty('--lift', (14 + Math.min(up / Math.max(0.3, k), it.h.chip.offsetHeight * 3)).toFixed(1) + 'px');
      });
      void sec.offsetWidth;
      if (!wasSet) sec.classList.remove('is-set');
      void sec.offsetWidth;
      sec.classList.remove('is-measuring');
    }

    function runPulse() {
      if (BL.RM || BL.paused || !pulse.animate) return;
      var ms = 3000;
      pulse.animate([
        { opacity: 0, transform: 'translateZ(2px) rotate(180deg)' },
        { opacity: 1, offset: 0.06 },
        { opacity: 1, offset: 0.92 },
        { opacity: 0, transform: 'translateZ(2px) rotate(' + (180 + dir * 360) + 'deg)' }
      ], { duration: ms, easing: 'linear' });
      hubs.forEach(function (h) {
        if (!h.fmt) return;
        var delta = ((dir * (h.angle - 180)) % 360 + 360) % 360;
        h.mark.animate([{ transform: 'scale(1)' }, { transform: 'scale(1.7)' }, { transform: 'scale(1)' }],
          { duration: 520, delay: delta / 360 * ms - 200, easing: 'ease-out' });
      });
    }

    var timer = 0;
    function schedule() {
      clearTimeout(timer);
      timer = setTimeout(function () { if (!BL.paused) { update(); declutter(); } schedule(); }, 60000 - Date.now() % 60000 + 40);
    }
    st.onMotion(function () { if (!BL.paused) { update(); declutter(); } });

    update();
    /* measure after the first paint and again once web fonts are in: synchronous reads during start-up can
       return flattened 3D geometry in some engines */
    function later() { requestAnimationFrame(function () { requestAnimationFrame(declutter); }); }
    later();
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(later);
    schedule();
    if (BL.RM) sec.classList.add('is-set');
    else BL.onVisible(sec, function () {
      requestAnimationFrame(function () { sec.classList.add('is-set'); if (BL.gsap) BL.gsap.delayedCall(1.1, runPulse); else runPulse(); });
    }, 0.2);
    var rt = 0;
    window.addEventListener('resize', function () { clearTimeout(rt); rt = setTimeout(declutter, 200); });
  });
})();
