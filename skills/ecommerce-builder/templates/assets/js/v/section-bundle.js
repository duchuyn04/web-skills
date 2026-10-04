/* Section 'bundle': add every item of a combo to the cart. */
(function () {
  var X = window.Shop; if (!X) return;
  X.$$('[data-bundle]').forEach(function (box) {
    var btn = X.$('[data-bundle-add]', box); if (!btn) return;
    btn.addEventListener('click', function () {
      var added = 0, failed = [];
      X.$$('[data-bundle-sku]', box).forEach(function (li) {
        var r = X.addToCart(li.dataset.bundleSku, 1);
        if (r.ok) added++; else failed.push(r.msg);
      });
      var msg = added ? 'Đã thêm ' + added + ' sản phẩm vào giỏ. <a href="' + X.root + 'cart.html">Xem giỏ hàng</a>' : '';
      if (failed.length) msg += (msg ? ' ' : '') + X.esc(failed[0]);
      X.toast(X.icon(added ? 'check' : 'alert') + msg);
    });
  });
})();
