/* Section 'bundle-offers': add every item of one combo to the cart. */
(function () {
  var X = window.Shop; if (!X) return;
  X.$$('[data-bo]').forEach(function (box) {
    var btn = X.$('[data-bo-add]', box); if (!btn) return;
    btn.addEventListener('click', function () {
      var added = 0, failed = [];
      X.$$('[data-bo-sku]', box).forEach(function (li) {
        var r = X.addToCart(li.dataset.boSku, 1);
        if (r.ok) added++; else failed.push(r.msg);
      });
      var msg = added ? 'Đã thêm ' + added + ' sản phẩm vào giỏ. <a href="' + X.root + 'cart.html">Xem giỏ hàng</a>' : '';
      if (failed.length) msg += (msg ? ' ' : '') + X.esc(failed[0]);
      X.toast(X.icon(added ? 'check' : 'alert') + msg);
    });
  });
})();
