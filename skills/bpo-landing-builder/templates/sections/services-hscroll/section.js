/* services-hscroll: horizontal-scroll-pin, track-progress-fill.
   Wide screens with motion: the block pins under the header and the vertical scroll moves the row sideways (one
   ScrollTrigger, scrub), the bar fills with it. Tablets, phones and reduced motion: a native scroll-snap row whose bar
   follows scrollLeft. qa_screenshot.py adds .bl-shot before element shots: the pin is undone so the row lays out flat. */
(function () {
  var BL = window.BL, gsap = window.gsap;
  var root = document.documentElement;
  function shot() { return root.classList.contains('bl-shot'); }
  function headerH() { return parseFloat(getComputedStyle(root).getPropertyValue('--header-h')) || 72; }

  document.querySelectorAll('[data-hscroll]').forEach(function (sec) {
    var pin = sec.querySelector('[data-hs-pin]');
    var vp = sec.querySelector('[data-hs-viewport]');
    var track = sec.querySelector('[data-hs-track]');
    var fill = sec.querySelector('[data-hs-fill]');
    if (!pin || !vp || !track) return;
    if (!track.hasAttribute('aria-label')) {
      var h = sec.querySelector('.bl-h2');
      if (h) track.setAttribute('aria-label', h.textContent.replace(/\s+/g, ' ').trim());
    }
    function setFill(p) { if (fill) fill.style.setProperty('--hs-p', Math.max(0, Math.min(1, p)).toFixed(4)); }

    /* native row: the bar follows the scroll position of the row itself */
    function syncNative() {
      if (sec.classList.contains('is-pinned')) return;
      var max = vp.scrollWidth - vp.clientWidth;
      setFill(max > 0 ? vp.scrollLeft / max : 1);
    }
    vp.addEventListener('scroll', syncNative, { passive: true });
    syncNative();

    if (!BL || !gsap || !window.ScrollTrigger) return;
    BL.motion.media(function (reduce) {
      if (reduce) return;
      var mm = gsap.matchMedia();
      mm.add('(min-width: 1024px)', function () {
        if (shot()) return;
        sec.classList.add('is-pinned');
        vp.scrollLeft = 0;
        var dist = function () { return Math.max(0, track.scrollWidth - vp.clientWidth); };
        var tw = gsap.to(track, {
          x: function () { return -dist(); }, ease: 'none',
          scrollTrigger: {
            trigger: pin, pin: pin, start: function () { return 'top top+=' + headerH(); },
            end: function () { return '+=' + dist(); }, scrub: 0.6, invalidateOnRefresh: true,
            onUpdate: function (self) { setFill(self.progress); }, onRefresh: function (self) { setFill(self.progress); }
          }
        });
        /* keyboard: a focused card off to the side is brought in by scrolling the page, not the clipped row */
        var onFocus = function (e) {
          var card = e.target.closest('.bl-services-hscroll__card');
          var st = tw.scrollTrigger, d = dist();
          vp.scrollLeft = 0;
          if (!card || !st || !d) return;
          var p = Math.max(0, Math.min(1, (card.offsetLeft - track.firstElementChild.offsetLeft) / d));
          window.scrollTo({ top: st.start + p * (st.end - st.start), behavior: 'instant' });
        };
        track.addEventListener('focusin', onFocus);
        return function () { track.removeEventListener('focusin', onFocus); sec.classList.remove('is-pinned'); syncNative(); };
      });
      var onShot = function () { if (shot()) mm.revert(); };
      window.addEventListener('resize', onShot);
      return function () { window.removeEventListener('resize', onShot); mm.revert(); };
    });
  });
})();
