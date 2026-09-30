/* faq-fold: paper-fold-open-3d. APG accordion (button in a heading, aria-expanded, aria-controls, region). Opening
   runs a one-shot fold under 0.8s: strips hold aria-hidden, inert copies of the answer, so screen readers and
   find-in-page only ever meet the real text. Reduced motion or the Pause switch: the answer opens without strips.
   Fold count (2 or 3) and crease depth come from the brand name; long answers always use 2 folds. */
(function () {
  var BL = window.BL;
  if (!BL || !BL.stage3d) return;
  document.querySelectorAll('[data-fxfold]').forEach(function (sec) {
    var items = Array.prototype.slice.call(sec.querySelectorAll('[data-fold-item]'));
    var buttons = items.map(function (it) { return it.querySelector('.bl-fxfold__btn'); });
    var st = BL.stage3d(sec);
    var rnd = st.rnd;
    var folds = rnd() < 0.5 ? 2 : 3;
    var crease = (0.55 + rnd() * 0.35).toFixed(2);
    var touched = false;
    sec.style.setProperty('--folds', String(folds));

    function finish(it) {
      if (it._fold) { it._fold.remove(); it._fold = null; }
      it.classList.remove('is-folding');
    }
    st.onMotion(function (paused) { if (paused) items.forEach(finish); });

    function fold(it) {
      var clip = it.querySelector('[data-fold-clip]'), sheet = it.querySelector('[data-fold-sheet]');
      var H = sheet.offsetHeight, W = sheet.offsetWidth;
      if (!H || !W) return;
      var k = H > 150 && folds === 3 && sheet.textContent.length <= 420 ? 3 : 2;
      sheet.style.setProperty('--folds', String(k));
      var stage = document.createElement('div');
      stage.className = 'bl-fxfold__fold';
      stage.setAttribute('aria-hidden', 'true');
      stage.inert = true;
      stage.style.left = sheet.offsetLeft + 'px';
      stage.style.top = sheet.offsetTop + 'px';
      stage.style.width = W + 'px';
      stage.style.height = H + 'px';
      var parent = stage, top = 0, strips = [];
      for (var i = 0; i < k; i++) {
        var h = i === k - 1 ? H - top : Math.round(H / k);
        var strip = document.createElement('div');
        strip.className = 'bl-fxfold__strip' + (i === 0 ? ' is-first' : '') + (i === k - 1 ? ' is-last' : '');
        strip.style.top = i === 0 ? '0px' : '100%';
        strip.style.height = h + 'px';
        var paper = document.createElement('div');
        paper.className = 'bl-fxfold__paper';
        var copy = sheet.cloneNode(true);
        copy.removeAttribute('data-fold-sheet');
        copy.style.top = (-top) + 'px';
        paper.appendChild(copy);
        var shade = document.createElement('span');
        shade.className = 'bl-fxfold__crease';
        paper.appendChild(shade);
        strip.appendChild(paper);
        parent.appendChild(strip);
        strips.push({ strip: strip, shade: shade });
        parent = strip;
        top += h;
      }
      clip.appendChild(stage);
      it._fold = stage;
      it.classList.add('is-folding');
      var last = null;
      strips.forEach(function (s, i) {
        var timing = { duration: 420, delay: 60 + i * 170, easing: 'cubic-bezier(.3, .6, .25, 1)', fill: 'both' };
        last = s.strip.animate([{ transform: 'rotateX(-90deg)' }, { transform: 'rotateX(0deg)' }], timing);
        s.shade.animate([{ opacity: crease }, { opacity: 0 }], timing);
      });
      last.finished.then(function () { if (it._fold === stage) finish(it); }, function () {});
    }
    function set(it, open, animate) {
      var btn = it.querySelector('.bl-fxfold__btn');
      if (open === it.classList.contains('is-open')) return;
      finish(it);
      btn.setAttribute('aria-expanded', String(open));
      it.classList.toggle('is-open', open);
      if (open && animate && !BL.RM && !st.paused) fold(it);
    }

    buttons.forEach(function (btn, i) {
      btn.addEventListener('click', function () {
        touched = true;
        set(items[i], btn.getAttribute('aria-expanded') !== 'true', true);
      });
      btn.addEventListener('keydown', function (e) {
        var k = { ArrowDown: 1, ArrowUp: -1 }[e.key];
        if (e.key === 'Home') k = -i; else if (e.key === 'End') k = buttons.length - 1 - i;
        if (k === undefined) return;
        e.preventDefault();
        buttons[(i + k + buttons.length) % buttons.length].focus();
      });
    });

    /* the first answer unfolds once when the list is first seen */
    if (sec.hasAttribute('data-open-first') && items.length) {
      if (BL.RM) set(items[0], true, false);
      else BL.onVisible(sec.querySelector('[data-fxfold-list]'), function () {
        if (!touched) setTimeout(function () { if (!touched) set(items[0], true, true); }, 450);
      }, 0.4);
    }
  });
})();
