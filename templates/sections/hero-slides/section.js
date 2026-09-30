/* hero-slides: slides-crossfade, slides-dot-timer, slides-height-follow. Carousel pattern (APG): a region with
   aria-roledescription "carousel", slides labelled "n of m", inactive slides inert. While nobody has picked a slide,
   one GSAP tween fills the active dot over 6 s and moves on when it completes. It is registered as ambient, so Pause
   animations stops it; it also holds on hover, on focus and while most of the hero is off screen, stops for good when a
   dot is picked (the stop button can start it again), and is never built with reduced motion. Up to 1024px the hero
   follows the height of the active slide. Over a full-bleed photo the header and the dots switch to light text. */
(function () {
  var BL = window.BL, gsap = window.gsap;
  document.querySelectorAll('[data-hslides]').forEach(function (sec) {
    var vp = sec.querySelector('[data-hslides-viewport]');
    var slides = [].slice.call(vp.children);
    var dots = [].slice.call(sec.querySelectorAll('[data-hslides-dots] button'));
    var bars = dots.map(function (d) { return d.querySelector('[data-hslides-bar]'); });
    var toggle = sec.querySelector('[data-hslides-toggle]');
    var header = document.querySelector('[data-bl-header]');
    var m = slides.length, cur = 0, stopped = false, tl = null;
    var holds = { hover: false, focus: false, off: false };
    var narrow = window.matchMedia('(max-width: 1024px)');
    var reduce = window.matchMedia('(prefers-reduced-motion: reduce)');
    if (m < 2) return;

    slides.forEach(function (s, n) {
      s.setAttribute('aria-label', (n + 1) + ' of ' + m + ': ' + s.getAttribute('aria-label'));
      [].slice.call(s.querySelectorAll('.bl-hslides__rise')).forEach(function (el, i) { el.style.setProperty('--i', String(Math.min(i, 6))); });
    });
    dots.forEach(function (d, n) { d.setAttribute('aria-label', 'Slide ' + (n + 1) + ' of ' + m + ': ' + d.getAttribute('aria-label')); });

    /* the header reads over the hero: a full-bleed slide is always dark, whatever tone the hero has */
    var headerTone = header && [].slice.call(header.classList).filter(function (c) { return c.indexOf('bl-tone-') === 0; })[0];
    function paintHeader() {
      if (!header || !headerTone) return;
      var dark = slides[cur].getAttribute('data-layout') === 'fullbleed' && !header.classList.contains('is-scrolled') && headerTone !== 'bl-tone-dark';
      header.classList.toggle(headerTone, !dark);
      header.classList.toggle('bl-tone-dark', dark || headerTone === 'bl-tone-dark');
    }
    function paint() {
      var layout = slides[cur].getAttribute('data-layout');
      sec.classList.toggle('is-over-photo', layout === 'fullbleed');
      paintHeader();
    }

    function show(k, focusDot) {
      if (k === cur && slides[k].classList.contains('is-active')) return;
      var follow = narrow.matches && !reduce.matches;
      if (follow) vp.style.height = vp.offsetHeight + 'px';
      slides.forEach(function (s, n) {
        var on = n === k;
        s.classList.toggle('is-active', on);
        if (on) { s.removeAttribute('aria-hidden'); s.removeAttribute('inert'); }
        else { s.setAttribute('aria-hidden', 'true'); s.setAttribute('inert', ''); }
        dots[n].classList.toggle('is-active', on);
        if (on) dots[n].setAttribute('aria-current', 'true'); else dots[n].removeAttribute('aria-current');
        dots[n].tabIndex = on ? 0 : -1;
        if (bars[n]) bars[n].style.transform = '';
      });
      cur = k;
      paint();
      if (focusDot) dots[k].focus();
      if (follow) {
        var h = slides[k].offsetHeight;
        requestAnimationFrame(function () { vp.style.height = h + 'px'; });
        var done = function (e) { if (e.target === vp) { vp.style.height = ''; vp.removeEventListener('transitionend', done); } };
        vp.addEventListener('transitionend', done);
        setTimeout(function () { vp.style.height = ''; }, 700);
      }
    }
    function sync() {
      if (!tl) return;
      if (stopped || BL.paused || holds.hover || holds.focus || holds.off) tl.pause(); else tl.resume();
      vp.setAttribute('aria-live', stopped || holds.focus ? 'polite' : 'off');
    }
    function stop(state) {
      stopped = state;
      sec.classList.toggle('is-stopped', stopped);
      if (toggle) toggle.setAttribute('aria-label', toggle.getAttribute(stopped ? 'data-label-play' : 'data-label-pause'));
      if (!stopped && tl) tl.restart();  /* the timer starts again on the current slide */
      sync();
    }
    function pick(k, focusDot) {
      if (tl) stop(true);
      show(k, focusDot);
    }

    dots.forEach(function (d, n) { d.addEventListener('click', function () { pick(n, false); }); });
    sec.querySelector('[data-hslides-dots]').addEventListener('keydown', function (e) {
      var k = { ArrowRight: cur + 1, ArrowDown: cur + 1, ArrowLeft: cur - 1, ArrowUp: cur - 1, Home: 0, End: m - 1 }[e.key];
      if (k == null) return;
      e.preventDefault();
      pick((k + m) % m, true);
    });
    if (toggle) toggle.addEventListener('click', function () { stop(!stopped); });
    sec.addEventListener('pointerenter', function (e) { if (e.pointerType === 'mouse') { holds.hover = true; sync(); } });
    sec.addEventListener('pointerleave', function () { holds.hover = false; sync(); });
    sec.addEventListener('focusin', function () { holds.focus = true; sync(); });
    sec.addEventListener('focusout', function () {
      setTimeout(function () { holds.focus = sec.contains(document.activeElement); sync(); }, 0);
    });
    if ('IntersectionObserver' in window) {
      new IntersectionObserver(function (entries) { holds.off = entries[0].intersectionRatio < 0.5; sync(); }, { threshold: [0, 0.5, 1] }).observe(sec);
    }
    document.addEventListener('bl:motion', sync);
    if (header && 'MutationObserver' in window) {
      new MutationObserver(function () { paintHeader(); }).observe(header, { attributes: true, attributeFilter: ['class'] });
    }
    /* QA adds bl-shot to <html> before section screenshots: show the first slide so previews carry the headline */
    if ('MutationObserver' in window) {
      new MutationObserver(function () {
        if (document.documentElement.classList.contains('bl-shot') && cur !== 0) show(0, false);
      }).observe(document.documentElement, { attributes: true, attributeFilter: ['class'] });
    }
    paint();

    if (!BL || !gsap) return;
    BL.motion.media(function (reduced) {
      if (reduced) return;
      var st = { p: 0 };
      /* one 6 s run per slide: when it completes the next slide shows and the run starts again. (A repeating tween
         fired its repeat callback on resume after a restart, skipping a slide.) */
      tl = gsap.to(st, {
        p: 1, duration: 6, ease: 'none',
        onUpdate: function () { if (!stopped && bars[cur]) bars[cur].style.transform = 'scaleX(' + st.p.toFixed(4) + ')'; },
        onComplete: function () { if (stopped) return; show((cur + 1) % m, false); tl.restart(); sync(); }
      });
      BL.motion.ambient(tl);
      if (toggle) toggle.hidden = false;
      sync();
      return function () { if (tl) tl.kill(); tl = null; if (toggle) toggle.hidden = true; show(cur, false); };
    });
  });
})();
