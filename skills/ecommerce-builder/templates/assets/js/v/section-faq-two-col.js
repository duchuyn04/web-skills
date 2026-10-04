/* Section 'faq' variant two-col: show one answer at a time; keyboard arrows move between questions. */
(function () {
  Array.prototype.forEach.call(document.querySelectorAll('[data-fq2]'), function (root) {
    var tabs = Array.prototype.slice.call(root.querySelectorAll('[data-fq2-tab]'));
    var panels = Array.prototype.slice.call(root.querySelectorAll('[data-fq2-panel]'));
    if (!tabs.length) return;
    root.classList.add('js-fq2');
    function show(i, focus) {
      tabs.forEach(function (t, k) { t.setAttribute('aria-selected', k === i ? 'true' : 'false'); t.tabIndex = k === i ? 0 : -1; });
      panels.forEach(function (p, k) { p.hidden = k !== i; });
      if (focus) tabs[i].focus();
    }
    tabs.forEach(function (t, i) {
      t.addEventListener('click', function () { show(i, false); });
      t.addEventListener('keydown', function (e) {
        if (e.key === 'ArrowDown' || e.key === 'ArrowRight') { e.preventDefault(); show((i + 1) % tabs.length, true); }
        else if (e.key === 'ArrowUp' || e.key === 'ArrowLeft') { e.preventDefault(); show((i + tabs.length - 1) % tabs.length, true); }
      });
    });
    show(0, false);
  });
})();
