/* image-cards, slider mode: cards-slide-in (BL.motion.trackIn); each photo then opens upward as its card enters the
   screen (data-wipe in the partial). */
(function () {
  document.querySelectorAll('.bl-icards--slider').forEach(function (track) {
    BL.motion.trackIn(track);
  });
})();
