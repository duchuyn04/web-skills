/* Section 'store-hours': open-now badge from the hours text, e.g. "8:00 - 21:30". */
(function () {
  document.querySelectorAll('[data-sh]').forEach(function (el) {
    var m = (el.dataset.shHours || '').match(/(\d{1,2})[:h](\d{2})\s*-\s*(\d{1,2})[:h](\d{2})/), badge = el.querySelector('[data-sh-state]');
    if (!m || !badge) return;
    var now = new Date(), t = now.getHours() * 60 + now.getMinutes(), open = t >= +m[1] * 60 + +m[2] && t < +m[3] * 60 + +m[4];
    badge.textContent = open ? 'Đang mở cửa' : 'Đã đóng cửa';
    badge.className = 'open-state ' + (open ? 'is-open' : 'is-closed');
  });
})();
