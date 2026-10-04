/* proof-book: Next and Previous turn the right-hand leaf over the spine. The leaf is built on demand from copies of
   the two pages it carries (front: the page it lifts, back: the page it lays down), split into two hinged segments
   so the paper bends, and removed when it lands. Resting pages stay flat. Phones turn the whole case about its
   left edge. Reduced motion: a 150 ms crossfade. Turns only on request, so nothing here loops. */
(function () {
  var BL = window.BL;
  if (!BL) return;
  document.querySelectorAll('[data-pbook]').forEach(function (sec) {
    var stage = sec.querySelector('[data-pbook-stage]');
    var wrap = sec.querySelector('[data-pbook-wrap]');
    var cases = Array.prototype.slice.call(sec.querySelectorAll('[data-case]'));
    var live = sec.querySelector('[data-pbook-live]');
    var nowEl = sec.querySelector('[data-pbook-now]');
    var cast = sec.querySelector('[data-pbook-cast]');
    var n = cases.length, cur = 0, running = null;
    var phone = window.matchMedia('(max-width: 760px)');
    var speed = parseFloat(getComputedStyle(sec).getPropertyValue('--pb-speed'));
    var dur = 800 + Math.round((isNaN(speed) ? 0.5 : speed) * 200);
    var st = BL.stage3d ? BL.stage3d(sec) : { onMotion: function () {} };
    /* the page-wide pause switch lands a turn that is in flight instead of freezing it mid-air */
    st.onMotion(function (paused) { if (paused && running) running.forEach(function (a) { a.finish(); }); });

    function pad(i) { return (i < 9 ? '0' : '') + (i + 1); }
    function page(i, side) { return cases[i].querySelector('[data-side="' + side + '"]'); }
    function show(list) {
      cases.forEach(function (c) {
        c.querySelectorAll('[data-side]').forEach(function (p) { p.classList.toggle('is-on', list.indexOf(p) > -1); });
      });
    }
    function settle(i, announce) {
      cur = i;
      cases.forEach(function (c, k) {
        c.inert = k !== i;
        c.setAttribute('aria-label', (k + 1) + ' ' + live.getAttribute('data-of-label') + ' ' + n);
      });
      show([page(i, 'l'), page(i, 'r')]);
      nowEl.textContent = pad(i);
      if (announce) {
        live.textContent = live.getAttribute('data-case-label') + ' ' + (i + 1) + ' ' + live.getAttribute('data-of-label') + ' ' + n +
          ': ' + cases[i].querySelector('.bl-pbook__client').textContent;
      }
    }

    function copy(node, shift) {
      var c = node.cloneNode(true);
      c.removeAttribute('data-case'); c.removeAttribute('data-side'); c.removeAttribute('role');
      c.removeAttribute('aria-roledescription'); c.removeAttribute('aria-label');
      c.querySelectorAll('[id]').forEach(function (e) { e.removeAttribute('id'); });
      c.querySelectorAll('[data-side]').forEach(function (e) { e.classList.add('is-on'); });
      c.classList.add('bl-pbook__leafpage', 'is-on');
      if (shift) c.classList.add('is-shift');
      return c;
    }
    function face(src, shift, back) {
      var f = document.createElement('div');
      f.className = 'bl-pbook__face fx3d-face' + (back ? ' is-back' : '');
      if (src) f.appendChild(copy(src, shift));
      var sh = document.createElement('span');
      sh.className = 'bl-pbook__shade';
      f.appendChild(sh);
      return f;
    }
    /* front: the page seen before the turn (right side); back: the page seen after it lands on the left */
    function buildLeaf(front, back) {
      var leaf = document.createElement('div');
      leaf.className = 'bl-pbook__leaf fx3d-rig';
      leaf.setAttribute('aria-hidden', 'true');
      leaf.inert = true;
      var seg = document.createElement('div');
      seg.className = 'bl-pbook__seg fx3d-rig';
      /* inner half (at the spine): front shows the left half of its page, back shows the right half of its page */
      leaf.appendChild(face(front, false, false));
      leaf.appendChild(face(back, true, true));
      seg.appendChild(face(front, true, false));
      seg.appendChild(face(back, false, true));
      leaf.appendChild(seg);
      stage.appendChild(leaf);
      return { leaf: leaf, seg: seg };
    }

    function turn(to, dir) {
      if (running || to === cur) return;
      var from = cur;
      if (BL.RM) {
        settle(to, true);
        cases[to].animate([{ opacity: 0 }, { opacity: 1 }], { duration: 150, easing: 'linear' });
        return;
      }
      var front, back;
      if (phone.matches) {
        show(dir > 0 ? [page(to, 'l'), page(to, 'r')] : [page(from, 'l'), page(from, 'r')]);
        front = dir > 0 ? cases[from] : cases[to];
        back = null;
      } else if (dir > 0) {
        front = page(from, 'r'); back = page(to, 'l');
        show([page(from, 'l'), page(to, 'r')]);
      } else {
        front = page(to, 'r'); back = page(from, 'l');
        show([page(to, 'l'), page(from, 'r')]);
      }
      var built = buildLeaf(front, back);
      stage.classList.add('is-turning');
      var opts = { duration: dur, fill: 'both', direction: dir > 0 ? 'normal' : 'reverse' };
      var anims = [
        built.leaf.animate([{ transform: 'rotateY(0deg)' }, { transform: 'rotateY(-180deg)' }], Object.assign({ easing: 'cubic-bezier(.45, .05, .25, 1)' }, opts)),
        /* the outer half leads as the page lifts and trails as it falls: that lag is the bend */
        built.seg.animate([
          { transform: 'rotateY(0deg)' }, { transform: 'rotateY(-24deg)', offset: .3 },
          { transform: 'rotateY(4deg)', offset: .62 }, { transform: 'rotateY(10deg)', offset: .82 }, { transform: 'rotateY(0deg)' }
        ], Object.assign({ easing: 'linear' }, opts)),
        cast.animate([{ opacity: 0 }, { opacity: 1, offset: .5 }, { opacity: 0 }], Object.assign({ easing: 'ease-in-out' }, opts))
      ];
      built.leaf.querySelectorAll('.bl-pbook__shade').forEach(function (s) {
        var isBack = s.parentNode.classList.contains('is-back');
        anims.push(s.animate(isBack
          ? [{ opacity: .42 }, { opacity: .18, offset: .6 }, { opacity: 0 }]
          : [{ opacity: 0 }, { opacity: .3, offset: .45 }, { opacity: .5 }], Object.assign({ easing: 'linear' }, opts)));
      });
      running = anims;
      anims[0].onfinish = function () {
        running = null;
        built.leaf.remove();
        stage.classList.remove('is-turning');
        anims.forEach(function (a) { a.cancel(); });
        settle(to, true);
      };
    }
    function next() { turn((cur + 1) % n, 1); }
    function prev() { turn((cur - 1 + n) % n, -1); }

    sec.querySelector('[data-pbook-total]').textContent = pad(n - 1);
    sec.querySelector('[data-pbook-next]').addEventListener('click', next);
    sec.querySelector('[data-pbook-prev]').addEventListener('click', prev);
    sec.querySelector('[data-pbook-corner]').addEventListener('click', next);
    wrap.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowRight') { e.preventDefault(); next(); }
      else if (e.key === 'ArrowLeft') { e.preventDefault(); prev(); }
    });
    settle(0, false);
  });
})();
