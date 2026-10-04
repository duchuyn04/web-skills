/* case-slider: cases-slide-in (BL.motion.trackIn). Drag, snap and the buttons are the shared slider's. */
(function () {
  document.querySelectorAll('.bl-cases__track').forEach(function (track) {
    BL.motion.trackIn(track);
  });
})();
