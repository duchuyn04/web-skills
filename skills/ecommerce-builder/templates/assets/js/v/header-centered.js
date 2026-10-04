/* Header 'centered': the search panel opens from the search icon. */
(function () {
  var btn = document.querySelector('[data-hc-search]'), panel = document.getElementById('hc-search');
  if (!btn || !panel) return;
  var input = panel.querySelector('[data-search-input]');
  function open(v) {
    panel.hidden = !v; btn.setAttribute('aria-expanded', v ? 'true' : 'false');
    if (v && input) input.focus();
  }
  btn.addEventListener('click', function () { open(panel.hidden); });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && !panel.hidden) { open(false); btn.focus(); }
  });
  // open the panel when the page was reached with a query (search page)
  if (input && input.value) open(true);
})();
