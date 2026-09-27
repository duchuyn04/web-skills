/* logo-wall: group logos into 8 or 12 cells, flip once in a cascade when seen; mode "cycle" keeps flipping one cell
   every 2.5s while the wall is on screen, the tab is visible and the page-wide motion switch is on. */
(function () {
  document.querySelectorAll('[data-logowall]').forEach(function (wall) {
    var BL = window.BL || {};
    var logos = Array.prototype.slice.call(wall.querySelectorAll('[data-logo]'));
    var count = parseInt(wall.getAttribute('data-cells'), 10) === 12 && logos.length >= 12 ? 12 : 8;
    if (count === 8) wall.classList.remove('bl-logowall__grid--12');
    var cells = [];
    for (var c = 0; c < count; c++) {
      var cell = document.createElement('span');
      cell.className = 'bl-logowall__cell';
      cells.push({ el: cell, items: [], at: 0 });
    }
    logos.forEach(function (logo, i) { cells[i % count].items.push(logo); });
    wall.textContent = '';
    cells.forEach(function (cell) {
      cell.items.forEach(function (logo, k) { if (k === 0) logo.classList.add('is-on'); cell.el.appendChild(logo); });
      wall.appendChild(cell.el);
    });
    if (BL.RM) return;

    function flip(cell) {
      if (cell.items.length < 2) return;
      var cur = cell.items[cell.at];
      cell.at = (cell.at + 1) % cell.items.length;
      var nxt = cell.items[cell.at];
      cur.classList.remove('is-on'); cur.classList.add('is-off');
      nxt.classList.remove('is-off');
      void nxt.offsetWidth;
      nxt.classList.add('is-on');
      setTimeout(function () { cur.classList.remove('is-off'); }, 650);
    }
    var visible = false, timer = 0;
    function tick() {
      timer = 0;
      if (!visible || BL.paused || document.hidden) return;
      var flippable = cells.filter(function (x) { return x.items.length > 1; });
      if (flippable.length) flip(flippable[Math.floor(Math.random() * flippable.length)]);
      timer = setTimeout(tick, 2500);
    }
    function arm() { if (!timer && wall.getAttribute('data-mode') === 'cycle') timer = setTimeout(tick, 2500); }
    if (BL.onVisible) BL.onVisible(wall, function () {
      cells.forEach(function (cell, i) { setTimeout(function () { flip(cell); }, 300 + i * 80); });
    }, 0.35);
    if ('IntersectionObserver' in window) {
      new IntersectionObserver(function (entries) { visible = entries[0].isIntersecting; if (visible) arm(); }, { threshold: 0.2 }).observe(wall);
    }
    document.addEventListener('bl:motion', function (e) { if (!e.detail.paused) arm(); });
    document.addEventListener('visibilitychange', function () { if (!document.hidden) arm(); });
  });
})();
