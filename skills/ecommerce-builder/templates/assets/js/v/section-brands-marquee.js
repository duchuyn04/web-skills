/* Section 'brands' marquee: the pause button stops the band for visitors who cannot use hover. */
(function () {
  Array.prototype.forEach.call(document.querySelectorAll('[data-marquee-pause]'), function (btn) {
    var band = btn.closest('section').querySelector('[data-marquee]');
    btn.addEventListener('click', function () {
      var on = band.classList.toggle('is-paused');
      btn.setAttribute('aria-pressed', on ? 'true' : 'false');
      btn.querySelector('span').textContent = on ? 'Chạy tiếp' : 'Tạm dừng';
    });
  });
})();
