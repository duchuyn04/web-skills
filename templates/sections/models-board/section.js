/* models-board: tabs move one token per task row between Your team, Shared and the vendor column */
(function () {
  var POS = { you: 0, shared: 1, us: 2 };
  document.querySelectorAll('[data-mboard]').forEach(function (sec) {
    var tabs = Array.prototype.slice.call(sec.querySelectorAll('[role="tab"]'));
    var panels = tabs.map(function (t) { return document.getElementById(t.getAttribute('aria-controls')); });
    var rows = Array.prototype.slice.call(sec.querySelectorAll('[data-task]'));
    var cols = {};
    sec.querySelectorAll('[data-count-col]').forEach(function (b) {
      cols[b.getAttribute('data-count-col')] = { el: b, name: b.parentNode.textContent.replace(b.textContent, '').trim() };
    });

    function select(i, focus) {
      var owners = (tabs[i].getAttribute('data-owners') || '').trim().split(/\s+/);
      var counts = { you: 0, shared: 0, us: 0 };
      tabs.forEach(function (t, k) {
        var on = k === i;
        t.setAttribute('aria-selected', String(on));
        t.tabIndex = on ? 0 : -1;
        panels[k].hidden = !on;
        panels[k].classList.toggle('is-in', on);
      });
      rows.forEach(function (row, r) {
        var owner = POS.hasOwnProperty(owners[r]) ? owners[r] : 'shared';
        counts[owner]++;
        var token = row.querySelector('[data-token]');
        token.setAttribute('data-owner', owner);
        token.style.setProperty('--pos', String(POS[owner]));
        row.querySelector('[data-owner-text]').textContent = cols[owner] ? ': ' + cols[owner].name : '';
      });
      Object.keys(counts).forEach(function (key) {
        var c = cols[key];
        if (!c || c.el.textContent === String(counts[key])) return;
        c.el.textContent = String(counts[key]);
        c.el.classList.remove('is-bump'); void c.el.offsetWidth; c.el.classList.add('is-bump');
      });
      if (focus) tabs[i].focus();
    }

    tabs.forEach(function (t, i) {
      t.addEventListener('click', function () { select(i, false); });
      t.addEventListener('keydown', function (e) {
        var k = { ArrowDown: 1, ArrowRight: 1, ArrowUp: -1, ArrowLeft: -1 }[e.key];
        if (e.key === 'Home') k = -i; else if (e.key === 'End') k = tabs.length - 1 - i;
        if (k === undefined) return;
        e.preventDefault();
        select((i + k + tabs.length) % tabs.length, true);
      });
    });

    /* tokens start stacked on the left and slide into place when the board is first seen */
    rows.forEach(function (row) { row.querySelector('[data-token]').setAttribute('data-owner', 'you'); });
    if (window.BL && !window.BL.RM) window.BL.onVisible(sec.querySelector('.bl-models-board__board'), function () { select(0, false); }, 0.3);
    else select(0, false);
  });
})();
