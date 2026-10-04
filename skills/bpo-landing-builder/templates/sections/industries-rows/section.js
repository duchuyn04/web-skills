/* industries-rows: cursor-follow-card with a velocity tilt. With row photos the card also shows the photo of the row
   being hovered or focused, cross-fading between two image layers (the picture follows the industry being read). */
(function () {
  document.querySelectorAll('[data-irows]').forEach(function (sec) {
    var card = sec.querySelector('[data-icard]');
    var wrap = card && card.parentNode;
    if (!card || !window.matchMedia('(hover: hover) and (pointer: fine)').matches) return;
    var RM = window.BL && window.BL.RM;
    var imgs = card.querySelectorAll('[data-icard-img]');
    if (imgs.length && RM) return; /* reduced motion: rows show thumbnails, CSS hides the card */
    var slots = {
      icon: card.querySelector('[data-icard-icon]'), title: card.querySelector('[data-icard-title]'),
      text: card.querySelector('[data-icard-text]')
    };
    var pos = { x: 0, y: 0, tx: 0, ty: 0, r: 0 }, raf = 0, active = false, layer = 0;

    function frame() {
      raf = 0;
      var k = RM ? 1 : 0.16;
      var dx = pos.tx - pos.x;
      pos.x += dx * k; pos.y += (pos.ty - pos.y) * k;
      pos.r += (Math.max(-12, Math.min(12, dx * 0.12)) - pos.r) * 0.2;
      card.style.setProperty('--x', pos.x.toFixed(1) + 'px');
      card.style.setProperty('--y', pos.y.toFixed(1) + 'px');
      card.style.setProperty('--r', (RM ? 0 : pos.r).toFixed(2) + 'deg');
      if (active && (Math.abs(dx) > 0.3 || Math.abs(pos.r) > 0.05)) raf = requestAnimationFrame(frame);
    }
    function aim(e) {
      var r = wrap.getBoundingClientRect();
      pos.tx = Math.min(r.width - card.offsetWidth, e.clientX - r.left + 28);
      pos.ty = e.clientY - r.top - card.offsetHeight / 2;
      if (!raf) raf = requestAnimationFrame(frame);
    }
    function fill(row) {
      slots.icon.innerHTML = row.querySelector('.bl-industries-rows__icon').innerHTML;
      slots.title.textContent = row.querySelector('.bl-industries-rows__title').textContent;
      slots.text.textContent = row.querySelector('.bl-industries-rows__text').textContent;
      var ph = row.querySelector('[data-irow-photo]');
      if (!imgs.length || !ph) return;
      var cur = imgs[layer];
      if (cur.classList.contains('is-on') && cur.getAttribute('src') === ph.getAttribute('src')) return;
      layer = cur.classList.contains('is-on') ? 1 - layer : layer;
      var next = imgs[layer];
      next.setAttribute('src', ph.getAttribute('src'));
      imgs[1 - layer].classList.remove('is-on');
      next.classList.add('is-on');
    }
    function show(row, x, y) {
      fill(row);
      if (!active) { pos.x = pos.tx = x; pos.y = pos.ty = y; }
      active = true;
      card.classList.add('is-on');
    }
    function hide() {
      active = false;
      card.classList.remove('is-on');
    }

    sec.querySelectorAll('[data-irow]').forEach(function (row) {
      row.addEventListener('pointerenter', function (e) {
        if (e.pointerType !== 'mouse') return;
        var r = wrap.getBoundingClientRect();
        show(row, e.clientX - r.left + 28, e.clientY - r.top - card.offsetHeight / 2);
        aim(e);
      });
      row.addEventListener('pointermove', aim);
      /* keyboard: park the card at the right edge under the focused row (above it near the end of the list) */
      row.addEventListener('focus', function () {
        if (!row.matches(':focus-visible')) return;
        var r = wrap.getBoundingClientRect(), rr = row.getBoundingClientRect();
        var x = Math.max(0, r.width - card.offsetWidth), y = rr.bottom - r.top + 8;
        if (y + card.offsetHeight > r.height) y = rr.top - r.top - card.offsetHeight - 8;
        show(row, x, y);
        pos.tx = x; pos.ty = y;
        if (!raf) raf = requestAnimationFrame(frame);
      });
      row.addEventListener('blur', hide);
    });
    sec.querySelector('.bl-industries-rows__list').addEventListener('pointerleave', hide);
  });
})();
