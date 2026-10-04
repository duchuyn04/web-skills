/* services-cube: block-quarter-turn-3d, block-entry-wave. Each block is a square column. A turn puts the target face
   on the side of the column (rotateY(90deg) translateZ(w / 2), or rotateX for the top-down axis), moves the rig back
   by the same depth so the front face stays at z = 0, turns the rig a quarter turn, then snaps back to a flat card
   (rig transform none) with the target face in front. Axis, wave order and wave side come from the brand name. */
(function () {
  var BL = window.BL;
  if (!BL || !BL.stage3d) return;
  document.querySelectorAll('[data-fxcube]').forEach(function (sec) {
    var blocks = [];
    var st = BL.stage3d(sec, {
      reveal: function (el) {
        var face = el.closest && el.closest('[data-face]');
        if (!face) return;
        blocks.forEach(function (b) { var i = b.faces.indexOf(face); if (i >= 0 && i !== b.cur) go(b, i, 1, true); });
      }
    });
    var rnd = st.rnd;
    var axisY = rnd() < 0.62;
    var waveBack = rnd() < 0.5;
    var waveLast = rnd() < 0.5;
    var PEEK = 13;

    function depth(b) { return (axisY ? b.rig.offsetWidth : b.rig.offsetHeight) / 2; }
    function rot(deg) { return (axisY ? 'rotateY(' : 'rotateX(') + deg + 'deg)'; }
    /* dir 1: the target comes from the right (or from below); dir -1: from the left (or from above) */
    function sideAngle(dir) { return axisY ? 90 * dir : -90 * dir; }
    function rigAngle(dir, part) { return (axisY ? -90 : 90) * dir * part; }

    function still(b, fn) {
      b.rig.style.transition = 'none';
      fn();
      void b.rig.offsetWidth;
      b.rig.style.transition = '';
    }
    function rest(b) {
      clearTimeout(b.timer);
      still(b, function () {
        b.rig.style.transform = '';
        b.rig.style.willChange = '';
        b.faces.forEach(function (f, i) {
          f.style.transform = '';
          f.classList.toggle('is-front', i === b.cur);
          f.classList.remove('is-next');
        });
      });
      b.el.classList.remove('is-turning', 'is-peek');
      b.state = 'rest';
      b.target = -1;
    }
    function prepare(b, to, dir) {
      /* leaning toward one side and asked for another on the same side: swap the face that waits there */
      if (b.state === 'peek' && b.target !== to && b.dir === dir && to !== b.cur) {
        b.faces[b.target].style.transform = '';
        b.faces[b.target].classList.remove('is-next');
        b.faces[to].style.transform = rot(sideAngle(dir)) + ' translateZ(' + b.d + 'px)';
        b.faces[to].classList.add('is-next');
        b.target = to;
        return;
      }
      if (b.state !== 'rest' && (b.target !== to || b.dir !== dir)) rest(b);
      if (b.state !== 'rest') return;
      var d = depth(b).toFixed(1);
      still(b, function () {
        b.rig.style.transform = 'translateZ(-' + d + 'px)';
        b.faces[b.cur].style.transform = 'translateZ(' + d + 'px)';
        b.faces[to].style.transform = rot(sideAngle(dir)) + ' translateZ(' + d + 'px)';
        b.faces[to].classList.add('is-next');
      });
      b.rig.style.willChange = 'transform';
      b.el.classList.add('is-turning');
      b.target = to; b.dir = dir; b.d = d;
      b.state = 'ready';
    }
    function mark(b) {
      b.buttons.forEach(function (btn, i) { btn.setAttribute('aria-pressed', String(i === b.cur)); });
    }
    function go(b, to, dir, instant, after) {
      if (to === b.cur && b.state === 'rest') return;
      if (BL.RM || instant) {
        b.cur = to; rest(b); mark(b);
        if (after) after();
        return;
      }
      prepare(b, to, dir);
      b.el.classList.remove('is-peek');
      b.state = 'turn';
      b.rig.style.transform = 'translateZ(-' + b.d + 'px) ' + rot(rigAngle(dir, 1));
      clearTimeout(b.timer);
      b.timer = setTimeout(function () {
        b.cur = to; rest(b); mark(b);
        if (after) after();
      }, 680);
      b.cur = to;
      mark(b);
    }

    sec.querySelectorAll('[data-fxcube-block]').forEach(function (el) {
      var b = { el: el, rig: el.querySelector('[data-fxcube-rig]'), faces: Array.prototype.slice.call(el.querySelectorAll('[data-face]')),
        cur: 0, state: 'rest', target: -1, dir: 1, timer: null, buttons: [], touched: false };
      var sides = el.querySelector('[data-fxcube-sides]');
      blocks.push(b);
      if (b.faces.length < 2) { if (sides) sides.setAttribute('aria-hidden', 'true'); return; }
      el.classList.add('has-sides');
      b.faces.forEach(function (f, i) {
        var btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'bl-fxcube__side';
        btn.textContent = f.getAttribute('data-name') || String(i + 1);
        btn.setAttribute('aria-pressed', String(i === 0));
        btn.addEventListener('click', function () {
          b.touched = true;
          if (i !== b.cur) go(b, i, i > b.cur ? 1 : -1);
        });
        sides.appendChild(btn);
        b.buttons.push(btn);
      });
      /* a click anywhere on the card (links excepted) turns to the next side */
      b.rig.addEventListener('click', function (e) {
        if (e.target.closest('a, button')) return;
        b.touched = true;
        go(b, (b.cur + 1) % b.faces.length, 1);
      });
      /* mouse: the column leans toward its next side as a hint */
      if (BL.FINE && !BL.RM) {
        el.querySelector('.bl-fxcube__stage').addEventListener('pointerenter', function (e) {
          if (e.pointerType !== 'mouse' || b.state === 'turn' || st.paused) return;
          var to = (b.cur + 1) % b.faces.length;
          prepare(b, to, 1);
          b.state = 'peek';
          b.el.classList.add('is-peek');
          b.rig.style.transform = 'translateZ(-' + b.d + 'px) ' + rot(rigAngle(1, PEEK / 90));
        });
        el.querySelector('.bl-fxcube__stage').addEventListener('pointerleave', function () {
          if (b.state !== 'peek') return;
          b.rig.style.transform = 'translateZ(-' + b.d + 'px)';
          clearTimeout(b.timer);
          b.timer = setTimeout(function () { if (b.state === 'peek') rest(b); }, 460);
        });
      }
    });

    /* entry wave: each block turns once to a side and back, 90ms apart, about 2s in all */
    if (!BL.RM && !st.paused) {
      var grid = sec.querySelector('.bl-fxcube__grid');
      BL.onVisible(grid, function () {
        var order = blocks.filter(function (b) { return b.faces.length > 1; });
        if (waveBack) order.reverse();
        order.forEach(function (b, k) {
          setTimeout(function () {
            if (b.touched || st.paused || b.state !== 'rest' || b.cur !== 0) return;
            var to = waveLast ? b.faces.length - 1 : 1, dir = waveLast ? -1 : 1;
            go(b, to, dir, false, function () {
              setTimeout(function () { if (!b.touched && b.cur === to && b.state === 'rest') go(b, 0, -dir); }, 520);
            });
          }, 350 + k * 90);
        });
      }, 0.35);
    }

    var rt = null;
    window.addEventListener('resize', function () {
      clearTimeout(rt);
      rt = setTimeout(function () { blocks.forEach(function (b) { if (b.state !== 'rest') rest(b); }); }, 120);
    });
  });
})();
