/* country-cards: country-cards-slide-in (BL.motion.trackIn); --ccard-i times each flag-pop. */
(function () {
  document.querySelectorAll('.bl-ccards').forEach(function (track) {
    [].forEach.call(track.children, function (c, i) { c.style.setProperty('--ccard-i', String(Math.min(i, 5))); });
    BL.motion.trackIn(track);
  });
})();
