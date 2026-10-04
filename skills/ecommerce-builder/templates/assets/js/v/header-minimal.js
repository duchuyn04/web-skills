/* Header 'minimal': the search icon opens the search panel under the bar. */
(function () {
  var btn = document.querySelector('[data-hm-search]'), panel = document.getElementById('hm-search');
  if (!btn || !panel) return;
  function set(open) {
    panel.hidden = !open;
    btn.setAttribute('aria-expanded', open ? 'true' : 'false');
    if (open) { var i = panel.querySelector('[data-search-input]'); if (i) i.focus(); }
  }
  btn.addEventListener('click', function (e) { e.stopPropagation(); set(panel.hidden); });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && !panel.hidden) { set(false); btn.focus(); } });
  document.addEventListener('click', function (e) { if (!panel.hidden && !panel.contains(e.target) && !btn.contains(e.target)) set(false); });
  // a search page or a query in the address opens the panel with the query
  if (/[?&]q=/.test(location.search) && !document.body.classList.contains('pg-search')) set(true);
})();
