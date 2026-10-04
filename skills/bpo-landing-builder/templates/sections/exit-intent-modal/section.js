/* exit-intent-spring-modal: desktop pointers only, after 8s, once per 7 days */
(function () {
  var dlg = document.querySelector('[data-exit]');
  if (!dlg || typeof dlg.showModal !== 'function' || !window.BL.FINE) return;
  var KEY = 'bl_exit_seen';
  var WEEK = 7 * 24 * 3600 * 1000;
  function seenRecently() {
    try { return Date.now() - Number(localStorage.getItem(KEY) || 0) < WEEK; } catch (e) { return false; }
  }
  function remember() { try { localStorage.setItem(KEY, String(Date.now())); } catch (e) { /* storage blocked */ } }
  if (seenRecently()) return;
  var armed = false;
  setTimeout(function () { armed = true; }, 8000);
  document.addEventListener('mouseout', function (e) {
    if (!armed || e.relatedTarget || e.clientY > 8 || dlg.open) return;
    armed = false;
    remember();
    dlg.showModal();
  });
  dlg.addEventListener('click', function (e) {
    if (e.target === dlg || e.target.closest('[data-exit-close]')) dlg.close();
  });
})();
