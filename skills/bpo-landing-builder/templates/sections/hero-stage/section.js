/* hero-stage: stage-scroll-open (wide screens: --hst-p runs 0 to 1 over the first 55% of a screen of scrolling, so the
   stage opens from the text column to the screen edges and its picture settles from 108%), hero-ambient-video-mask
   (pause button, Pause animations, paused while off screen). Reduced motion: the stage stays at the column width and the
   video does not start. */
(function () {
  var BL = window.BL, gsap = window.gsap;
  if (!BL) return;
  document.querySelectorAll('[data-hstage]').forEach(function (sec) {
    var frame = sec.querySelector('[data-hstage-frame]');
    var video = sec.querySelector('video');
    var btn = sec.querySelector('[data-video-toggle]');
    if (video && btn) {
      var userPaused = false;
      var show = function (playing) {
        sec.classList.toggle('is-paused', !playing);
        btn.setAttribute('aria-pressed', String(!playing));
        btn.setAttribute('aria-label', playing ? btn.getAttribute('data-label-pause') : btn.getAttribute('data-label-play'));
      };
      var play = function () { var p = video.play(); if (p && p.catch) p.catch(function () { show(false); }); show(true); };
      var pause = function () { video.pause(); show(false); };
      if (BL.RM) { video.removeAttribute('autoplay'); userPaused = true; pause(); }
      btn.addEventListener('click', function () {
        if (video.paused) { userPaused = false; play(); } else { userPaused = true; pause(); }
      });
      document.addEventListener('bl:motion', function (e) { if (e.detail.paused) pause(); else if (!userPaused) play(); });
      if ('IntersectionObserver' in window) {
        new IntersectionObserver(function (entries) {
          if (userPaused || BL.paused) return;
          if (entries[0].isIntersecting) play(); else video.pause();
        }, { threshold: 0.1 }).observe(sec);
      }
    }
    if (!frame || !gsap || !window.ScrollTrigger) return;
    var wide = window.matchMedia('(min-width: 769px)');
    BL.motion.media(function (reduce) {
      if (reduce || !wide.matches) return;
      gsap.fromTo(frame, { '--hst-p': 0 }, {
        '--hst-p': 1, ease: 'none',
        scrollTrigger: {
          trigger: sec, start: 'top top', scrub: 0.4, invalidateOnRefresh: true,
          end: function () { return '+=' + Math.round(window.innerHeight * 0.55); }
        }
      });
    });
  });
})();
