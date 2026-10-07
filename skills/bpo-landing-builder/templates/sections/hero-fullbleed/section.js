/* hero-ambient-video-mask: pause control (WCAG 2.2.2), reduced motion, pause while off-screen */
(function () {
  document.querySelectorAll('[data-hero-full]').forEach(function (sec) {
    var video = sec.querySelector('video');
    var btn = sec.querySelector('[data-video-toggle]');
    if (!video || !btn) return;
    var userPaused = false;
    function show(playing) {
      sec.classList.toggle('is-paused', !playing);
      btn.setAttribute('aria-pressed', String(!playing));
      btn.setAttribute('aria-label', playing ? btn.getAttribute('data-label-pause') : btn.getAttribute('data-label-play'));
    }
    function play() { var p = video.play(); if (p && p.catch) p.catch(function () { show(false); }); show(true); }
    function pause() { video.pause(); show(false); }
    if (window.BL.RM) { video.removeAttribute('autoplay'); userPaused = true; pause(); }
    btn.addEventListener('click', function () {
      if (video.paused) { userPaused = false; play(); } else { userPaused = true; pause(); }
    });
    if ('IntersectionObserver' in window) {
      new IntersectionObserver(function (entries) {
        if (userPaused) return;
        if (entries[0].isIntersecting) play(); else video.pause();
      }, { threshold: 0.1 }).observe(sec);
    }
  });
})();

/* hero-frame-intro (layout frame): the frame, header and buttons run on CSS; here the headline and lead rise line by line
   out of masks from 1.6 s after the page started (0.8 s power2.out, 50 ms apart), and the media grows to 115% as the hero
   scrolls away. CSS shows the copy after 4 s if this never runs. */
(function () {
  var sec = document.querySelector('[data-hero-frame]');
  if (!sec) return;
  var gsap = window.gsap;
  var blocks = [].slice.call(sec.querySelectorAll('[data-frame-lines]'));
  function show() { blocks.forEach(function (b) { b.style.opacity = '1'; }); }
  if (window.BL.RM || !gsap) { show(); return; }
  var fonts = document.fonts && document.fonts.ready ? document.fonts.ready : Promise.resolve();
  var box = sec.querySelector('.bl-hero-frame__box');
  fonts.then(function () {
    /* keep time with the CSS frame opening, which started when the stylesheet applied */
    var open = box && box.getAnimations ? box.getAnimations()[0] : null;
    var elapsed = open && open.currentTime != null ? open.currentTime / 1000 : performance.now() / 1000;
    var tl = gsap.timeline({ delay: Math.max(0.05, 1.6 - elapsed) });
    blocks.forEach(function (b) {
      var lines = [];
      window.BL.motion.split(b).words.forEach(function (w) {
        var top = w.getBoundingClientRect().top, last = lines[lines.length - 1];
        if (!last || Math.abs(top - last.top) > 4) lines.push(last = { top: top, els: [] });
        last.els.push(w.firstChild);
      });
      lines.forEach(function (line, i) {
        gsap.set(line.els, { yPercent: 170 }); /* clears the mask's room for Vietnamese marks */
        tl.to(line.els, { yPercent: 0, duration: 0.8, ease: 'power2.out', clearProps: 'transform' }, i * 0.05);
      });
      b.style.opacity = '1';
    });
  });
  var media = sec.querySelector('.bl-hero-frame__media');
  window.BL.motion.media(function (reduce) {
    if (reduce || !window.ScrollTrigger || !media) return;
    gsap.fromTo(media, { scale: 1 }, { scale: 1.15, ease: 'none', scrollTrigger: { trigger: sec, start: 'top top', end: 'bottom top', scrub: true } });
  });
})();
