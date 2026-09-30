/* hero-tabs: tab-stage-crossfade and tab-progress-autoadvance. ARIA tabs (arrow keys, Home, End). While nobody has
   picked a tab, one GSAP tween fills the active tab's progress bar over 7 s and moves to the next tab when it repeats.
   It is registered as ambient, so Pause animations stops it; it also holds on hover, on focus and off screen, stops
   for good once a tab is picked, and is never built with reduced motion. */
(function () {
  var BL = window.BL, gsap = window.gsap;
  document.querySelectorAll('[data-htabs]').forEach(function (sec) {
    var tabs = [].slice.call(sec.querySelectorAll('[role="tab"]'));
    if (tabs.length < 2) return;
    var panels = tabs.map(function (t) { return document.getElementById(t.getAttribute('aria-controls')); });
    var bars = tabs.map(function (t) { return t.querySelector('[data-htabs-bar]'); });
    var cur = 0, stopped = false, tl = null, holds = { hover: false, focus: false, off: false };

    function show(k, focus) {
      tabs.forEach(function (t, n) {
        var on = n === k;
        t.setAttribute('aria-selected', String(on));
        t.tabIndex = on ? 0 : -1;
        t.classList.toggle('is-active', on);
        panels[n].classList.toggle('is-active', on);
        if (on) { panels[n].removeAttribute('aria-hidden'); panels[n].removeAttribute('inert'); }
        else { panels[n].setAttribute('aria-hidden', 'true'); panels[n].setAttribute('inert', ''); }
        if (bars[n]) bars[n].style.transform = '';
      });
      cur = k;
      if (focus) tabs[k].focus();
    }
    function sync() {
      if (!tl) return;
      if (stopped || BL.paused || holds.hover || holds.focus || holds.off) tl.pause(); else tl.resume();
    }
    function pick(k, focus) {
      stopped = true;
      if (tl) tl.pause();
      show(k, focus);
    }

    tabs.forEach(function (t, n) { t.addEventListener('click', function () { pick(n, false); }); });
    sec.querySelector('[role="tablist"]').addEventListener('keydown', function (e) {
      var k = { ArrowRight: cur + 1, ArrowDown: cur + 1, ArrowLeft: cur - 1, ArrowUp: cur - 1, Home: 0, End: tabs.length - 1 }[e.key];
      if (k == null) return;
      e.preventDefault();
      pick((k + tabs.length) % tabs.length, true);
    });
    sec.addEventListener('pointerenter', function () { holds.hover = true; sync(); });
    sec.addEventListener('pointerleave', function () { holds.hover = false; sync(); });
    sec.addEventListener('focusin', function () { holds.focus = true; sync(); });
    sec.addEventListener('focusout', function () {
      setTimeout(function () { holds.focus = sec.contains(document.activeElement); sync(); }, 0);
    });
    if ('IntersectionObserver' in window) {
      new IntersectionObserver(function (entries) { holds.off = !entries[0].isIntersecting; sync(); }, { threshold: 0.15 }).observe(sec);
    }
    document.addEventListener('bl:motion', sync);
    /* QA adds bl-shot to <html> before section screenshots: show the first tab so previews carry the headline */
    if ('MutationObserver' in window) {
      new MutationObserver(function () {
        if (document.documentElement.classList.contains('bl-shot') && !stopped) pick(0, false);
      }).observe(document.documentElement, { attributes: true, attributeFilter: ['class'] });
    }

    if (!BL || !gsap) return;
    BL.motion.media(function (reduce) {
      if (reduce) return;
      var st = { p: 0 };
      tl = gsap.to(st, {
        p: 1, duration: 7, ease: 'none', repeat: -1,
        onUpdate: function () { if (!stopped && bars[cur]) bars[cur].style.transform = 'scaleX(' + st.p.toFixed(4) + ')'; },
        onRepeat: function () { if (!stopped) show((cur + 1) % tabs.length); }
      });
      BL.motion.ambient(tl);
      sync();
      return function () { if (tl) tl.kill(); tl = null; show(cur); };
    });
  });
})();
