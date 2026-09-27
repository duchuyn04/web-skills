/* bpo-landing-builder: shared runtime. Section scripts run after this file. */
(function () {
  'use strict';
  var doc = document;
  var root = doc.documentElement;
  var RM = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var FINE = window.matchMedia && window.matchMedia('(pointer: fine)').matches;
  var LOCALE = root.lang || 'en';

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

  function tween(duration, onFrame, onDone) {
    if (RM) { onFrame(1); if (onDone) onDone(); return; }
    var start = null;
    function step(ts) {
      if (start === null) start = ts;
      var p = Math.min((ts - start) / duration, 1);
      onFrame(1 - Math.pow(1 - p, 3));
      if (p < 1) requestAnimationFrame(step); else if (onDone) onDone();
    }
    requestAnimationFrame(step);
  }

  window.BL = { RM: RM, FINE: FINE, onVisible: onVisible, formatNumber: formatNumber, tween: tween };

  /* Page-wide motion switch (WCAG 2.2.2: one control pauses every moving element).
     Sets data-motion="paused" on <html>, which freezes CSS animations, and fires "bl:motion" for JS loops and videos. */
  BL.paused = false;
  BL.setPaused = function (state) {
    BL.paused = !!state;
    root.setAttribute('data-motion', BL.paused ? 'paused' : 'on');
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
    var ticking = false;
    var sync = function () {
      header.classList.toggle('is-scrolled', window.scrollY > 50);
      ticking = false;
    };
    window.addEventListener('scroll', function () {
      if (!ticking) { ticking = true; requestAnimationFrame(sync); }
    }, { passive: true });
    sync();
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

  /* Reveal on scroll, with stagger inside [data-reveal-group] */
  doc.querySelectorAll('[data-reveal-group]').forEach(function (group) {
    group.querySelectorAll('[data-reveal]').forEach(function (el, i) { el.style.setProperty('--reveal-i', String(i)); });
  });
  doc.querySelectorAll('[data-reveal]').forEach(function (el) {
    if (RM) { el.classList.add('is-in'); return; }
    onVisible(el, function (t) { t.classList.add('is-in'); }, 0.12);
  });

  /* odometer-number-counter: HTML holds the final value, JS counts up once */
  doc.querySelectorAll('[data-count]').forEach(function (el) {
    var target = parseFloat(el.getAttribute('data-count'));
    if (isNaN(target) || RM) return;
    var dec = parseInt(el.getAttribute('data-decimals') || '0', 10);
    var pre = el.getAttribute('data-prefix') || '';
    var suf = el.getAttribute('data-suffix') || '';
    var final = el.textContent;
    el.textContent = pre + formatNumber(0, dec) + suf;
    onVisible(el, function () {
      tween(2000, function (p) { el.textContent = pre + formatNumber(target * p, dec) + suf; }, function () { el.textContent = final; });
    }, 0.3);
  });

  /* magnetic-cta-button: pull up to 8px x 6px when the pointer is within 30px */
  if (FINE && !RM) {
    doc.querySelectorAll('[data-magnetic]').forEach(function (btn) {
      var raf = null;
      window.addEventListener('pointermove', function (e) {
        if (raf) return;
        raf = requestAnimationFrame(function () {
          raf = null;
          var r = btn.getBoundingClientRect();
          var cx = r.left + r.width / 2, cy = r.top + r.height / 2;
          var dx = e.clientX - cx, dy = e.clientY - cy;
          var near = Math.abs(dx) < r.width / 2 + 30 && Math.abs(dy) < r.height / 2 + 30;
          btn.style.transform = near ? 'translate(' + Math.max(-8, Math.min(8, dx * 0.18)).toFixed(1) + 'px,' + Math.max(-6, Math.min(6, dy * 0.25)).toFixed(1) + 'px)' : '';
        });
      }, { passive: true });
    });
  }
})();
