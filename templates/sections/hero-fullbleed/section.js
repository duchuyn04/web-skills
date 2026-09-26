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
