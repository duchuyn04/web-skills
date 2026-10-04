/* Section 'installment' (calc): amount per period for the chosen product and term. */
(function () {
  var fmt = new Intl.NumberFormat('vi-VN');
  function vnd(n) { return fmt.format(Math.round(n)) + '\u00a0đ'; }
  document.querySelectorAll('[data-inst]').forEach(function (box) {
    var sel = box.querySelector('[data-inst-product]'); if (!sel) return;
    var out = box.querySelector('[data-inst-amount]'), sub = box.querySelector('[data-inst-sub]'), link = box.querySelector('[data-inst-link]');
    function update() {
      var price = +sel.value, m = box.querySelector('[data-inst-months]:checked'), n = m ? +m.value : 1;
      out.textContent = vnd(Math.round(price / n / 1000) * 1000);
      sub.textContent = vnd(price) + ' chia ' + n + ' kỳ';
      link.href = sel.options[sel.selectedIndex].dataset.href;
    }
    sel.addEventListener('change', update);
    box.querySelectorAll('[data-inst-months]').forEach(function (r) { r.addEventListener('change', update); });
    update();
  });
})();
