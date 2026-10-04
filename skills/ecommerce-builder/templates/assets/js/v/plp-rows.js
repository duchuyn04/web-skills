/* Listing 'rows': switch between rows and grid; the choice is remembered in this browser. */
(function () {
  var list = document.querySelector('.plr-list'); if (!list) return;
  var btns = Array.prototype.slice.call(document.querySelectorAll('[data-view]'));
  function set(v) {
    list.classList.toggle('is-rows', v === 'rows');
    btns.forEach(function (b) { b.setAttribute('aria-pressed', b.dataset.view === v ? 'true' : 'false'); });
    try { localStorage.setItem('plp-view', v); } catch (e) { /* private mode */ }
  }
  btns.forEach(function (b) { b.addEventListener('click', function () { set(b.dataset.view); }); });
  var saved = 'rows';
  try { saved = localStorage.getItem('plp-view') || 'rows'; } catch (e) { /* ignore */ }
  set(saved === 'grid' ? 'grid' : 'rows');
})();
