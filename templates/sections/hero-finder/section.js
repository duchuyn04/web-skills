/* hero-finder: the finder bar opens the section of the most specific choice (the last dropdown with a value), and
   finder-panel-rise (the brand panel grows up from its base), finder-card-pop (the white cards pop in one after
   another) and finder-mark-draw (bars grow, the tick draws, list lines extend). One-shot tweens only, no loops;
   reduced motion or no GSAP leaves everything in its final place. */
(function () {
  var BL = window.BL, gsap = window.gsap;
  document.querySelectorAll('[data-hfind]').forEach(function (sec) {
    var form = sec.querySelector('[data-hfind-form]');
    if (form) {
      var hint = form.querySelector('[data-hfind-hint]');
      var selects = [].slice.call(form.querySelectorAll('select'));
      selects.forEach(function (s) { s.addEventListener('change', function () { if (hint) hint.textContent = ''; }); });
      form.addEventListener('submit', function (e) {
        e.preventDefault();
        var pick = selects.filter(function (s) { return s.value; }).pop();
        if (!pick) {
          if (hint) hint.textContent = hint.getAttribute('data-text') || '';
          if (selects[0]) selects[0].focus();
          return;
        }
        var href = pick.value;
        if (href.charAt(0) !== '#') { window.location.href = href; return; }
        var target = document.getElementById(href.slice(1));
        if (!target) { window.location.hash = href; return; }
        if (history.pushState) history.pushState(null, '', href);
        target.scrollIntoView({ behavior: BL && BL.RM ? 'auto' : 'smooth', block: 'start' });
        if (!target.hasAttribute('tabindex')) target.setAttribute('tabindex', '-1');
        target.focus({ preventScroll: true });
      });
    }

    if (!BL || !gsap) return;
    var panel = sec.querySelector('[data-hfind-panel]');
    var photo = sec.querySelector('[data-hfind-photo]');
    var cards = [].slice.call(sec.querySelectorAll('[data-hfind-card]'));
    var bars = [].slice.call(sec.querySelectorAll('.bl-hfind__card--bars .bl-hfind__bars i'));
    var ticks = [].slice.call(sec.querySelectorAll('.bl-hfind__card--tick .bl-hfind__tick polyline'));
    var lines = [].slice.call(sec.querySelectorAll('.bl-hfind__card--list .bl-hfind__lines i'));
    var bar = form;
    BL.motion.media(function (reduce) {
      if (reduce) return;
      if (panel) gsap.set(panel, { scaleY: 0.2, opacity: 0 });
      if (photo) gsap.set(photo, { opacity: 0, y: 24 });
      gsap.set(cards, { opacity: 0, scale: 0.9, y: 12 });
      gsap.set(bars, { scaleY: 0 });
      gsap.set(ticks, { strokeDashoffset: 1 });
      gsap.set(lines, { scaleX: 0 });
      if (bar) gsap.set(bar, { y: 18 });
      var tweens = [];
      BL.onVisible(sec, function () {
        if (panel) tweens.push(gsap.to(panel, { scaleY: 1, opacity: 1, duration: 0.8, delay: 0.1, ease: 'power3.out' }));
        if (photo) tweens.push(gsap.to(photo, { opacity: 1, y: 0, duration: 0.8, delay: 0.3, ease: BL.motion.ease }));
        tweens.push(gsap.to(cards, { opacity: 1, scale: 1, y: 0, duration: 0.5, delay: 0.75, stagger: 0.16, ease: 'back.out(1.5)' }));
        tweens.push(gsap.to(bars, { scaleY: 1, duration: 0.5, delay: 1, stagger: 0.07, ease: 'power2.out' }));
        tweens.push(gsap.to(ticks, { strokeDashoffset: 0, duration: 0.45, delay: 1.2, ease: 'power2.inOut' }));
        tweens.push(gsap.to(lines, { scaleX: 1, duration: 0.5, delay: 1.3, stagger: 0.08, ease: 'power2.out' }));
        if (bar) tweens.push(gsap.to(bar, { y: 0, duration: 0.8, delay: 0.4, ease: 'power3.out' }));
      }, 0.05);
      return function () {
        tweens.forEach(function (t) { t.kill(); });
        gsap.set([panel, photo, bar].concat(cards, bars, ticks, lines).filter(Boolean), { clearProps: 'all' });
      };
    });
  });
})();
