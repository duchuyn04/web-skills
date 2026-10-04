/* Listing 'chips': each filter chip opens its own panel on wide screens; on phones the whole filter block is the bottom sheet from store.js. */
(function () {
  var bar = document.querySelector('.plc-filters'); if (!bar) return;
  var chips = Array.prototype.slice.call(bar.querySelectorAll('[data-chip]'));
  function wide() { return window.matchMedia('(min-width: 1024px)').matches; }
  function close(except) {
    chips.forEach(function (c) {
      if (c === except) return;
      c.classList.remove('is-open');
      c.querySelector('[data-chip-btn]').setAttribute('aria-expanded', 'false');
    });
  }
  function count(c) {
    var n = c.querySelectorAll('input:checked').length + Array.prototype.filter.call(c.querySelectorAll('input[type=number]'), function (i) { return i.value; }).length;
    c.classList.toggle('has-value', n > 0);
    var b = c.querySelector('[data-chip-btn]'), tag = b.querySelector('.plc-n');
    if (n && !tag) { tag = document.createElement('b'); tag.className = 'plc-n'; b.insertBefore(tag, b.lastChild); }
    if (tag) { if (n) tag.textContent = n; else tag.remove(); }
  }
  chips.forEach(function (c) {
    var btn = c.querySelector('[data-chip-btn]');
    btn.addEventListener('click', function (e) {
      if (!wide()) return;
      e.stopPropagation();
      var open = !c.classList.contains('is-open');
      close(c);
      c.classList.toggle('is-open', open);
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    c.addEventListener('change', function () { count(c); });
    count(c);
  });
  document.addEventListener('click', function (e) { if (!bar.contains(e.target)) close(); });
  document.addEventListener('keydown', function (e) {
    if (e.key !== 'Escape') return;
    var open = chips.filter(function (c) { return c.classList.contains('is-open'); })[0];
    if (open) { close(); open.querySelector('[data-chip-btn]').focus(); }
  });
  // reset buttons clear the chip counts too
  Array.prototype.forEach.call(document.querySelectorAll('[data-filter-reset]'), function (b) {
    b.addEventListener('click', function () { setTimeout(function () { chips.forEach(count); }, 0); });
  });
  document.addEventListener('click', function (e) { if (e.target.closest('[data-active-filters] button')) setTimeout(function () { chips.forEach(count); }, 0); });
})();
