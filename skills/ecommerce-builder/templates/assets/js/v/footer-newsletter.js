/* Footer 'newsletter': keep the address in this browser and confirm with a toast. */
(function () {
  var X = window.Shop, f = document.querySelector('[data-newsletter]');
  if (!X || !f) return;
  f.addEventListener('submit', function (e) {
    e.preventDefault();
    if (!f.reportValidity()) return;
    var list = X.get('newsletter', []), v = f.email.value.trim();
    if (list.indexOf(v) < 0) list.push(v);
    X.set('newsletter', list);
    f.reset();
    X.toast(X.icon('check') + 'Đã đăng ký ' + X.esc(v));
  });
})();
