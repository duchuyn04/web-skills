/* bpo-landing-builder: shared runtime. vendor/gsap.js runs before this file, section scripts after it.
   GSAP drives every tween; IntersectionObserver decides when one-shot effects start (it copes with sticky and
   horizontally scrolled parents); ScrollTrigger is for scroll-linked work (scrub, pin) through BL.motion.media. */
(function () {
  'use strict';
  var doc = document;
  var root = doc.documentElement;
  var gsap = window.gsap;
  var ST = window.ScrollTrigger;
  var rmQuery = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)');
  var FINE = window.matchMedia && window.matchMedia('(pointer: fine)').matches;
  var LOCALE = root.lang || 'en';
  var EASE = 'expo.out'; /* matches --ease-out: cubic-bezier(0.16, 1, 0.3, 1) */

  function reduced() { return !!(rmQuery && rmQuery.matches); }

  function onVisible(el, cb, threshold) {
    if (!('IntersectionObserver' in window)) { cb(el); return; }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) { io.unobserve(entry.target); cb(entry.target); }
      });
    }, { threshold: threshold == null ? 0.2 : threshold, rootMargin: '0px 0px -8% 0px' });
    io.observe(el);
  }

  function formatNumber(value, decimals) {
    return Number(value).toLocaleString(LOCALE, { minimumFractionDigits: decimals, maximumFractionDigits: decimals });
  }

  /* tween(ms, onFrame(p), onDone): p runs 0 to 1 on a cubic ease-out. Kept for section scripts written before GSAP. */
  function tween(duration, onFrame, onDone) {
    if (reduced() || !gsap) { onFrame(1); if (onDone) onDone(); return null; }
    var state = { p: 0 };
    return gsap.to(state, {
      p: 1, duration: duration / 1000, ease: 'power2.out',
      onUpdate: function () { onFrame(state.p); },
      onComplete: function () { if (onDone) onDone(); }
    });
  }

  window.BL = { FINE: FINE, onVisible: onVisible, formatNumber: formatNumber, tween: tween, gsap: gsap };
  Object.defineProperty(BL, 'RM', { get: reduced, enumerable: true });

  /* BL.motion: shared GSAP helpers.
     ambient(anim)  registers a looping or long (over 5 s) tween or timeline; the Pause button pauses it.
     media(fn)      runs fn(reduce) inside one gsap.matchMedia; tweens and ScrollTriggers made in fn are reverted and
                    fn runs again when prefers-reduced-motion changes. Build pins and scrubs only when reduce is false.
     reveal(els)    reveals elements added after load (filters, tabs) with the page reveal. */
  var ambient = [];
  var mm = gsap ? gsap.matchMedia() : null;
  BL.motion = {
    ease: EASE,
    ambient: function (anim) {
      if (!anim) return anim;
      ambient.push(anim);
      if (BL.paused && anim.pause) anim.pause();
      return anim;
    },
    media: function (fn) {
      if (!mm) { fn(reduced()); return; }
      mm.add({ reduce: '(prefers-reduced-motion: reduce)', motion: '(prefers-reduced-motion: no-preference)' }, function (c) {
        return fn(!!c.conditions.reduce);
      });
    },
    reveal: function (els) { [].forEach.call(els, function (el) { revealNow(el, 0); }); },
    /* Cards of a horizontal track (case-slider, country-cards, image-cards slider) arrive from the right one after
       another when the track comes into view: 0.8 s power3.out, 100 ms apart up to the sixth card. The "fade" style
       keeps them in place. Adds .is-in to the track when they start (and at once for reduced motion). Cards off to the
       right of a scrolling track never intersect, so the track is watched, not the cards. */
    trackIn: function (track) {
      var cards = [].slice.call(track.children);
      if (reduced() || !gsap) { track.classList.add('is-in'); return; }
      onVisible(track, function () {
        gsap.fromTo(cards, { opacity: 0, x: BL.motion.style === 'fade' ? 0 : 64 }, {
          opacity: 1, x: 0, duration: 0.8, ease: 'power3.out',
          stagger: function (i) { return Math.min(i, 5) * 0.1; },
          clearProps: 'opacity,transform'
        });
        track.classList.add('is-in');
      }, 0.2);
    },
    /* QA: the registered ambient tweens */
    ambientList: function () { return ambient.slice(); },
    /* Split a heading into words (or characters) for a rise-in. Text is normalised to NFC first so a Vietnamese
       letter with its marks stays one character; inline markup such as the .bl-hl accent is kept; the heading gets an
       aria-label and the pieces are hidden from screen readers. Returns {targets, words, chars}: animate targets
       (the inner spans, e.g. from yPercent: 110). Calling it twice returns the first result. */
    split: function (el, mode) {
      if (el.__blSplit) return el.__blSplit;
      var label = el.textContent.replace(/\s+/g, ' ').trim(), words = [], chars = [], targets = [];
      (function walk(node) {
        [].slice.call(node.childNodes).forEach(function (n) {
          if (n.nodeType === 1) { if (n.tagName !== 'BR') walk(n); return; }
          if (n.nodeType !== 3) return;
          var frag = doc.createDocumentFragment();
          n.nodeValue.normalize('NFC').split(/(\s+)/).forEach(function (part) {
            if (!part) return;
            if (/^\s+$/.test(part)) { frag.appendChild(doc.createTextNode(' ')); return; }
            var w = doc.createElement('span');
            w.className = 'bl-split__w';
            w.setAttribute('aria-hidden', 'true');
            if (mode === 'chars') {
              Array.from(part).forEach(function (ch) {
                var c = doc.createElement('span');
                c.className = 'bl-split__i';
                c.textContent = ch;
                w.appendChild(c); chars.push(c); targets.push(c);
              });
            } else {
              var i = doc.createElement('span');
              i.className = 'bl-split__i';
              i.textContent = part;
              w.appendChild(i); targets.push(i);
            }
            words.push(w); frag.appendChild(w);
          });
          n.parentNode.replaceChild(frag, n);
        });
      })(el);
      el.setAttribute('aria-label', label);
      el.classList.add('bl-split-text');
      el.__blSplit = { targets: targets, words: words, chars: chars };
      return el.__blSplit;
    }
  };

  /* Page-wide motion switch (WCAG 2.2.2: one control pauses every moving element).
     Sets data-motion="paused" on <html>, which freezes CSS animations, pauses registered GSAP ambient tweens and fires
     "bl:motion" for canvas loops and videos. One-shot reveals and scroll-linked tweens keep working. */
  BL.paused = false;
  BL.setPaused = function (state) {
    BL.paused = !!state;
    root.setAttribute('data-motion', BL.paused ? 'paused' : 'on');
    ambient.forEach(function (a) { if (BL.paused) a.pause(); else a.resume(); });
    doc.querySelectorAll('video[autoplay]').forEach(function (v) { if (BL.paused) v.pause(); });
    doc.querySelectorAll('[data-motion-toggle]').forEach(function (b) {
      b.setAttribute('aria-pressed', String(BL.paused));
      var label = b.querySelector('[data-motion-label]');
      if (label) label.textContent = b.getAttribute(BL.paused ? 'data-label-play' : 'data-label-pause');
    });
    doc.dispatchEvent(new CustomEvent('bl:motion', { detail: { paused: BL.paused } }));
  };
  doc.addEventListener('click', function (e) {
    var b = e.target.closest && e.target.closest('[data-motion-toggle]');
    if (b) BL.setPaused(!BL.paused);
  });

  /* header-shrink-blur */
  var header = doc.querySelector('[data-bl-header]');
  if (header) {
    if (ST) {
      ST.create({ start: 50, end: 'max', onToggle: function (self) { header.classList.toggle('is-scrolled', self.isActive); } });
    } else {
      var sync = function () { header.classList.toggle('is-scrolled', window.scrollY > 50); };
      window.addEventListener('scroll', sync, { passive: true });
      sync();
    }
  }

  /* Mobile drawer */
  var toggle = doc.querySelector('[data-nav-toggle]');
  var drawer = doc.querySelector('[data-nav-drawer]');
  if (toggle && drawer) {
    var setOpen = function (open) {
      toggle.setAttribute('aria-expanded', String(open));
      drawer.classList.toggle('is-open', open);
      root.classList.toggle('bl-lock', open);
      if (open) { var first = drawer.querySelector('a, button'); if (first) first.focus(); }
    };
    toggle.addEventListener('click', function () { setOpen(toggle.getAttribute('aria-expanded') !== 'true'); });
    drawer.addEventListener('click', function (e) {
      if (e.target.closest('a[href^="#"]') || e.target.closest('[data-nav-close]')) setOpen(false);
    });
    doc.addEventListener('keydown', function (e) { if (e.key === 'Escape' && drawer.classList.contains('is-open')) { setOpen(false); toggle.focus(); } });
    window.addEventListener('resize', function () { if (window.innerWidth > 1024) setOpen(false); });
  }

  /* megamenu-slide-fade with 120ms hover intent */
  doc.querySelectorAll('[data-mega]').forEach(function (item) {
    var btn = item.querySelector('[data-mega-trigger]');
    var timer = null;
    var set = function (open) {
      item.classList.toggle('is-open', open);
      if (btn) btn.setAttribute('aria-expanded', String(open));
    };
    var later = function (open) { clearTimeout(timer); timer = setTimeout(function () { set(open); }, open ? 120 : 150); };
    item.addEventListener('pointerenter', function (e) { if (e.pointerType === 'mouse') later(true); });
    item.addEventListener('pointerleave', function (e) { if (e.pointerType === 'mouse') later(false); });
    if (btn) btn.addEventListener('click', function () { clearTimeout(timer); set(!item.classList.contains('is-open')); });
    item.addEventListener('focusout', function (e) { if (!item.contains(e.relatedTarget)) set(false); });
    item.addEventListener('keydown', function (e) { if (e.key === 'Escape') { set(false); if (btn) btn.focus(); } });
  });
  doc.addEventListener('click', function (e) {
    doc.querySelectorAll('[data-mega].is-open').forEach(function (item) { if (!item.contains(e.target)) item.classList.remove('is-open'); });
  });

  /* Reveal on scroll. The page's motion style (root class bl-motion-*, set by build.py from theme.motion_style or the
     brand seed) decides how elements arrive. The four styles come from 92 real BPO homepages
     (references/motion-research.md): most that animate rise 30-60 px over 0.8-0.9 s, cards in a row often slide in
     from the side, some split section titles into masked words, and many only fade.
     [data-reveal] values: "" (the style's default), "pop", "fade", "left", "right". Children of [data-reveal-group]
     stagger. GSAP moves the element with transform, so resting offsets set with the CSS translate property stay put.
     CSS keeps the hidden start state (.js [data-reveal] { opacity: 0 }) and .is-in still marks revealed elements. */
  var STYLE = (root.className.match(/\bbl-motion-(rise|slide|mask|fade)\b/) || [0, 'rise'])[1];
  var MS = {
    rise: { y: 40, dur: 0.8, ease: 'power3.out', gap: 0.08 },
    slide: { y: 24, dur: 0.8, ease: 'power3.out', gap: 0.1, x: 56 },
    mask: { y: 24, dur: 0.9, ease: 'expo.out', gap: 0.08 },
    fade: { y: 0, dur: 0.7, ease: 'power1.out', gap: 0.08 }
  }[STYLE];
  BL.motion.style = STYLE;
  var WIDE = window.matchMedia ? window.matchMedia('(min-width: 769px)') : { matches: true };
  var FROM = { pop: { scale: 0.96 }, fade: {}, left: { x: -32 }, right: { x: 32 } };
  function fromFor(el) {
    var kind = el.getAttribute('data-reveal');
    if (FROM[kind]) return FROM[kind];
    /* slide: cards in a row come in from the right on wide screens; one column rises */
    if (MS.x && WIDE.matches && el.style.getPropertyValue('--reveal-i')) return { x: MS.x };
    return MS.y ? { y: MS.y } : {};
  }
  /* mask: section titles rise word by word out of a mask as their head arrives */
  function maskTitles(el) {
    if (STYLE !== 'mask' || !gsap) return;
    var titles = el.matches('.bl-h2') ? [el] : el.querySelectorAll('.bl-h2');
    [].forEach.call(titles, function (h) {
      if (h.__blMasked) return;
      h.__blMasked = true;
      var t = BL.motion.split(h).targets;
      gsap.fromTo(t, { yPercent: 105 }, { yPercent: 0, duration: 0.9, ease: 'expo.out', stagger: 0.045, clearProps: 'transform' });
    });
  }
  function revealNow(el, i) {
    el.classList.add('is-in');
    if (!gsap || reduced()) { el.style.opacity = ''; return; }
    gsap.set(el, { transition: 'none' });
    gsap.fromTo(el, Object.assign({ opacity: 0 }, fromFor(el)), {
      opacity: 1, x: 0, y: 0, scale: 1, duration: MS.dur, ease: MS.ease, delay: Math.min(i, 5) * MS.gap,
      clearProps: 'opacity,transform,transition'
    });
    maskTitles(el);
  }
  doc.querySelectorAll('[data-reveal-group]').forEach(function (group) {
    group.querySelectorAll('[data-reveal]').forEach(function (el, i) { el.style.setProperty('--reveal-i', String(i)); });
  });
  doc.querySelectorAll('[data-reveal]').forEach(function (el) {
    if (reduced()) { el.classList.add('is-in'); return; }
    onVisible(el, function (t) { revealNow(t, parseInt(t.style.getPropertyValue('--reveal-i') || '0', 10)); }, 0.12);
  });

  /* One-shot entrances drawn in CSS: base.js only adds .is-seen when the element comes into view.
     data-draw   a rule or line grows from its start edge ("x", default, or "y")
     data-wipe   the element is uncovered by a clip ("right", default: left to right; "left", "up", "down")
     data-seq    its children arrive one after another (each child gets --seq-i); the section's CSS says how */
  var SEEN = '[data-draw],[data-wipe],[data-seq]';
  doc.querySelectorAll('[data-seq]').forEach(function (el) {
    [].forEach.call(el.children, function (c, i) { c.style.setProperty('--seq-i', String(i)); });
  });
  /* a clipped or scaleX(0) element has no visible area for IntersectionObserver, so watch its parent */
  doc.querySelectorAll(SEEN).forEach(function (el) {
    if (reduced()) { el.classList.add('is-seen'); return; }
    onVisible(el.parentElement || el, function () {
      el.classList.add('is-seen');
      /* a sequence hands its children's transitions back once it has played */
      if (el.hasAttribute('data-seq')) setTimeout(function () { el.classList.add('is-settled'); }, 150 + el.children.length * 120 + 1800);
    }, 0.15);
  });
  if (rmQuery && rmQuery.addEventListener) {
    rmQuery.addEventListener('change', function () {
      if (!reduced()) return;
      doc.querySelectorAll('[data-reveal]').forEach(function (el) { el.classList.add('is-in'); });
      doc.querySelectorAll(SEEN).forEach(function (el) { el.classList.add('is-seen'); });
    });
  }

  /* Scroll-linked, wide screens only, off for reduced motion:
     data-parallax="8"  a photo drifts 8% of its height inside its frame while the frame crosses the screen
     data-grow          a video or photo block widens from 90% to full size as it scrolls up to the middle */
  BL.motion.media(function (reduce) {
    if (reduce || !gsap || !ST || !WIDE.matches) return;
    doc.querySelectorAll('[data-parallax]').forEach(function (img) {
      var amt = Math.min(12, parseFloat(img.getAttribute('data-parallax')) || 8);
      gsap.fromTo(img, { yPercent: -amt, scale: 1 + amt / 40 }, {
        yPercent: amt, scale: 1 + amt / 40, ease: 'none',
        scrollTrigger: { trigger: img.parentElement, start: 'top bottom', end: 'bottom top', scrub: true }
      });
    });
    doc.querySelectorAll('[data-grow]').forEach(function (el) {
      gsap.fromTo(el, { scale: 0.9 }, {
        scale: 1, ease: 'none',
        scrollTrigger: { trigger: el, start: 'top bottom', end: 'center 60%', scrub: true }
      });
    });
  });

  /* odometer-number-counter: HTML holds the final value, GSAP counts up once over 2 s */
  doc.querySelectorAll('[data-count]').forEach(function (el) {
    var target = parseFloat(el.getAttribute('data-count'));
    if (isNaN(target) || reduced() || !gsap) return;
    var dec = parseInt(el.getAttribute('data-decimals') || '0', 10);
    var pre = el.getAttribute('data-prefix') || '';
    var suf = el.getAttribute('data-suffix') || '';
    var final = el.textContent;
    el.textContent = pre + formatNumber(0, dec) + suf;
    onVisible(el, function () {
      var n = { v: 0 };
      gsap.to(n, {
        v: target, duration: 2, ease: 'power2.out',
        onUpdate: function () { el.textContent = pre + formatNumber(n.v, dec) + suf; },
        onComplete: function () { el.textContent = final; }
      });
    }, 0.3);
  });

  /* magnetic-cta-button: pull up to 8px x 6px when the pointer is within 30px */
  if (FINE && !reduced() && gsap) {
    doc.querySelectorAll('[data-magnetic]').forEach(function (btn) {
      var toX = gsap.quickTo(btn, 'x', { duration: 0.3, ease: 'power3.out' });
      var toY = gsap.quickTo(btn, 'y', { duration: 0.3, ease: 'power3.out' });
      window.addEventListener('pointermove', function (e) {
        var r = btn.getBoundingClientRect();
        var dx = e.clientX - (r.left + r.width / 2), dy = e.clientY - (r.top + r.height / 2);
        var near = Math.abs(dx) < r.width / 2 + 30 && Math.abs(dy) < r.height / 2 + 30;
        toX(near ? Math.max(-8, Math.min(8, dx * 0.18)) : 0);
        toY(near ? Math.max(-6, Math.min(6, dy * 0.25)) : 0);
      }, { passive: true });
    });
  }

  /* Recalculate scroll-linked positions once images and fonts have settled */
  if (ST) window.addEventListener('load', function () { ST.refresh(); });
})();
