/* Hero 'ticker': the pause button stops the scrolling strip (WCAG 2.2.2). */
(function () {
  var strip = document.querySelector('[data-ht-strip]'), btn = document.querySelector('[data-ht-pause]');
  if (!strip || !btn) return;
  btn.addEventListener('click', function () {
    var on = strip.classList.toggle('is-paused');
    btn.setAttribute('aria-pressed', on ? 'true' : 'false');
    btn.setAttribute('aria-label', on ? 'Tiếp tục cuộn danh sách sản phẩm' : 'Dừng cuộn danh sách sản phẩm');
  });
})();
