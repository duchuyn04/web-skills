/* Section 'new-arrivals' (tabs): switch the rail shown under the category tabs. */
(function () {
  Array.prototype.forEach.call(document.querySelectorAll('[data-na]'), function (box) {
    var tabs = Array.prototype.slice.call(box.querySelectorAll('[data-na-tab]'));
    var panels = Array.prototype.slice.call(box.querySelectorAll('[data-na-panel]'));
    if (tabs.length < 2) return;
    function show(i, focus) {
      tabs.forEach(function (t, k) {
        var on = k === i;
        t.classList.toggle('is-on', on);
        t.setAttribute('aria-selected', on ? 'true' : 'false');
        t.tabIndex = on ? 0 : -1;
      });
      panels.forEach(function (p, k) { p.hidden = k !== i; });
      var track = panels[i].querySelector('[data-rail-track]');
      if (track) { track.scrollLeft = 0; track.dispatchEvent(new Event('scroll')); }
      if (focus) tabs[i].focus();
    }
    tabs.forEach(function (t, i) {
      t.tabIndex = i === 0 ? 0 : -1;
      t.addEventListener('click', function () { show(i, false); });
      t.addEventListener('keydown', function (e) {
        var n = tabs.length;
        if (e.key === 'ArrowRight') { e.preventDefault(); show((i + 1) % n, true); }
        else if (e.key === 'ArrowLeft') { e.preventDefault(); show((i - 1 + n) % n, true); }
        else if (e.key === 'Home') { e.preventDefault(); show(0, true); }
        else if (e.key === 'End') { e.preventDefault(); show(n - 1, true); }
      });
    });
  });
})();
