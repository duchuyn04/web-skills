/* cart 'stacked': the fixed bottom bar on phones mirrors the grand total and presses the real checkout link */
(function () {
  var bar = document.querySelector('[data-cs-bar]');
  if (!bar) return;
  var tot = document.querySelector('[data-totals]'), full = document.querySelector('[data-cart-full]');
  var out = bar.querySelector('[data-cs-total]');
  function sync() {
    var g = tot && tot.querySelector('dd.grand');
    if (g) out.textContent = g.textContent;
    bar.hidden = !!(full && full.hidden);
  }
  if (tot) new MutationObserver(sync).observe(tot, { childList: true, subtree: true });
  if (full) new MutationObserver(sync).observe(full, { attributes: true, attributeFilter: ['hidden'] });
  bar.querySelector('[data-cs-go]').addEventListener('click', function () {
    var l = document.querySelector('[data-checkout-link]');
    if (l) l.click();
  });
  sync();
})();
