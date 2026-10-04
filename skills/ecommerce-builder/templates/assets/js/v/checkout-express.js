/* checkout 'express': fold the summary on phones, show the total in its header, keep invalid fields visible */
(function () {
  var root = document.querySelector('.cex');
  if (!root) return;
  var sum = root.querySelector('.cex-sum');
  if (sum && window.matchMedia && window.matchMedia('(max-width: 700px)').matches) sum.open = false;
  var tot = root.querySelector('[data-totals]'), out = root.querySelector('[data-cex-total]');
  function sync() {
    var g = tot && tot.querySelector('dd.grand');
    if (g && out) out.textContent = g.textContent;
  }
  if (tot) new MutationObserver(sync).observe(tot, { childList: true, subtree: true });
  var form = root.querySelector('[data-co-form]');
  if (form) {
    new MutationObserver(function (list) {
      list.forEach(function (m) {
        var d = m.target.getAttribute('aria-invalid') && m.target.closest('details');
        if (d && !d.open) d.open = true;
      });
    }).observe(form, { attributes: true, attributeFilter: ['aria-invalid'], subtree: true });
  }
  sync();
})();
