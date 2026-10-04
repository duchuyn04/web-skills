/* Account shell 'hub': the side menu is a bottom sheet on phones. */
(function () {
  var open = document.querySelector('[data-acc-menu-open]'), sheet = document.querySelector('[data-acc-sheet]'), scrim = document.querySelector('[data-acc-scrim]');
  if (!open || !sheet || !scrim) return;
  function set(v) {
    sheet.classList.toggle('is-open', v);
    scrim.hidden = !v;
    open.setAttribute('aria-expanded', v ? 'true' : 'false');
    if (v) { var a = sheet.querySelector('a'); if (a) a.focus(); } else if (document.activeElement && sheet.contains(document.activeElement)) open.focus();
  }
  open.addEventListener('click', function () { set(!sheet.classList.contains('is-open')); });
  scrim.addEventListener('click', function () { set(false); });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && sheet.classList.contains('is-open')) set(false); });
  addEventListener('resize', function () { if (innerWidth > 1023) set(false); });
})();
