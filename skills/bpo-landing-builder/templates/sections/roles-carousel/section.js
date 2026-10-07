/* roles-carousel: roles-slide-in (BL.motion.trackIn) and roles-scroll-bar. Drag, snap and the buttons are the shared slider's. */
(function () {
  document.querySelectorAll('.bl-roles-sec').forEach(function (sec) {
    var track = sec.querySelector('.bl-roles');
    var thumb = sec.querySelector('.bl-roles__thumb');
    if (!track) return;
    BL.motion.trackIn(track);
    /* all cards fit: centre them and drop the scroll bar and arrows; otherwise the track slides as before */
    function fit() { sec.classList.toggle('is-fit', track.scrollWidth <= track.clientWidth + 1); }
    fit();
    window.addEventListener('resize', fit);
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(fit);
    if (!thumb) return;
    var queued = false;
    function sync() {
      queued = false;
      var max = track.scrollWidth - track.clientWidth;
      var w = max > 1 ? track.clientWidth / track.scrollWidth : 1;
      var p = max > 1 ? Math.min(1, Math.max(0, track.scrollLeft / max)) : 0;
      thumb.style.setProperty('--roles-w', w.toFixed(4));
      thumb.style.setProperty('--roles-x', (p * (1 - w) * 100).toFixed(2) + '%');
    }
    function queue() { if (!queued) { queued = true; requestAnimationFrame(sync); } }
    track.addEventListener('scroll', queue, { passive: true });
    window.addEventListener('resize', queue);
    sync();
  });
})();
