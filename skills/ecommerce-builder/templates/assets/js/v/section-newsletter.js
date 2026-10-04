/* Section 'newsletter': keeps the address in this browser and confirms it. */
(function () {
  var X = window.Shop; if (!X) return;
  Array.prototype.forEach.call(document.querySelectorAll('[data-newsletter]'), function (f) {
    var msg = f.querySelector('[data-newsletter-msg]');
    f.addEventListener('submit', function (e) {
      e.preventDefault();
      var email = f.email.value.trim();
      if (!f.email.checkValidity() || !email) {
        msg.textContent = 'Nhập email đúng dạng, ví dụ ten@gmail.com.';
        msg.className = 'bq-nl-msg bad'; f.email.focus(); return;
      }
      var list = X.get('newsletter', []);
      if (list.indexOf(email) < 0) list.push(email);
      X.set('newsletter', list);
      msg.textContent = 'Đã đăng ký ' + email + '.';
      msg.className = 'bq-nl-msg ok';
      f.reset();
      X.toast(X.icon('check') + 'Đã đăng ký nhận tin');
    });
  });
})();
