/* industries-rows: cursor-follow-card with a velocity tilt */
(function () {
  document.querySelectorAll('[data-irows]').forEach(function (sec) {
    var card = sec.querySelector('[data-icard]');
    var wrap = card && card.parentNode;
    if (!card || !window.matchMedia('(hover: hover) and (pointer: fine)').matches) return;
    var RM = window.BL && window.BL.RM;
    var slots = {
      icon: card.querySelector('[data-icard-icon]'), title: card.querySelector('[data-icard-title]'),
      text: card.querySelector('[data-icard-text]')
    };
    var pos = { x: 0, y: 0, tx: 0, ty: 0, r: 0 }, raf = 0, active = false;

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

    sec.querySelectorAll('[data-irow]').forEach(function (row) {
      row.addEventListener('pointerenter', function (e) {
        if (e.pointerType !== 'mouse') return;
        slots.icon.innerHTML = row.querySelector('.bl-industries-rows__icon').innerHTML;
        slots.title.textContent = row.querySelector('.bl-industries-rows__title').textContent;
        slots.text.textContent = row.querySelector('.bl-industries-rows__text').textContent;
        if (!active) {
          var r = wrap.getBoundingClientRect();
          pos.x = pos.tx = e.clientX - r.left + 28; pos.y = pos.ty = e.clientY - r.top - card.offsetHeight / 2;
        }
        active = true;
        card.classList.add('is-on');
        aim(e);
      });
      row.addEventListener('pointermove', aim);
    });
    sec.querySelector('.bl-industries-rows__list').addEventListener('pointerleave', function () {
      active = false;
      card.classList.remove('is-on');
    });
  });
})();
