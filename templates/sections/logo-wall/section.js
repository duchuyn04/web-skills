/* logo-wall: group logos into 8 or 12 cells, flip once in a cascade when seen; mode "cycle" keeps flipping one cell
   every 2.5s while the wall is on screen. The cycle is a GSAP tween registered with BL.motion.ambient, so the
   page-wide motion switch holds it; GSAP's ticker stops with the tab hidden. */
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
    if (BL.RM || !BL.gsap) return;
    var gsap = BL.gsap;

    function flip(cell) {
      if (cell.items.length < 2) return;
      var cur = cell.items[cell.at];
      cell.at = (cell.at + 1) % cell.items.length;
      var nxt = cell.items[cell.at];
      cur.classList.remove('is-on'); cur.classList.add('is-off');
      nxt.classList.remove('is-off');
      void nxt.offsetWidth;
      nxt.classList.add('is-on');
      gsap.delayedCall(0.65, function () { cur.classList.remove('is-off'); });
    }
    var visible = false;
    if (wall.getAttribute('data-mode') === 'cycle') {
      BL.motion.ambient(gsap.to({}, { duration: 2.5, repeat: -1, onRepeat: function () {
        if (!visible) return;
        var flippable = cells.filter(function (x) { return x.items.length > 1; });
        if (flippable.length) flip(flippable[Math.floor(Math.random() * flippable.length)]);
      } }));
    }
    BL.onVisible(wall, function () {
      cells.forEach(function (cell, i) { gsap.delayedCall(0.3 + i * 0.08, function () { flip(cell); }); });
    }, 0.35);
    if ('IntersectionObserver' in window) {
      new IntersectionObserver(function (entries) { visible = entries[0].isIntersecting; }, { threshold: 0.2 }).observe(wall);
    } else visible = true;
  });
})();
