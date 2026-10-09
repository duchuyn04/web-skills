/* services-marquee: word-row-drift (two or three rows of service names drift in opposite directions, one GSAP loop per
   row registered as ambient so Pause stops it) and word-hover-photo (hover or focus turns a name full ink, dims the
   rest, slows its row to a fifth and pops that service's photo over it). The real links stay in the first copy of each
   row; the copies that make the loop seamless are aria-hidden and out of the tab order. Reduced motion keeps the
   still, wrapped list from the HTML. */
(function () {
  var gsap = window.gsap;
  document.querySelectorAll('[data-smarq]').forEach(function (sec) {
    var stage = sec.querySelector('.bl-services-marquee__stage');
    var list = sec.querySelector('[data-smarq-list]');
    var card = sec.querySelector('[data-smarq-card]');
    var imgs = [].slice.call(card.querySelectorAll('[data-smarq-img]'));
    var items = [].slice.call(list.children);
    if (!gsap || !window.BL || items.length < 2) return;
    var built = null;

    function build() {
      var n = items.length >= 9 ? 3 : 2;
      var rows = document.createElement('div');
      rows.className = 'bl-services-marquee__rows';
      var made = [];
      for (var r = 0; r < n; r++) {
        var row = document.createElement('div'); row.className = 'bl-services-marquee__row';
        var track = document.createElement('div'); track.className = 'bl-services-marquee__track';
        var set = document.createElement('ul'); set.className = 'bl-services-marquee__set';
        track.appendChild(set); row.appendChild(track); rows.appendChild(row);
        made.push({ row: row, track: track, set: set, dir: r % 2 ? 1 : -1, own: [] });
      }
      items.forEach(function (li, i) { var m = made[i % n]; m.set.appendChild(li); m.own.push(li); });
      list.replaceWith(rows);
      /* wide enough for the screen, so a window made wider later never shows the end of a row */
      var width = Math.max(stage.clientWidth, (window.screen && window.screen.width) || 0);
      made.forEach(function (m) {
        /* repeat the names until one copy is wider than the stage, then add a second copy for the seam */
        var k = 0; /* whole rounds only, so the same name never meets itself at the seam */
        while (m.set.scrollWidth < width + 40 && k < 8) { m.own.forEach(function (li) { m.set.appendChild(clone(li)); }); k++; }
        var copy = m.set.cloneNode(true);
        copy.setAttribute('aria-hidden', 'true');
        [].forEach.call(copy.querySelectorAll('a'), function (a) { a.tabIndex = -1; });
        m.track.appendChild(copy);
        var px = m.set.scrollWidth;
        var from = m.dir < 0 ? 0 : -50, to = m.dir < 0 ? -50 : 0;
        m.tween = window.BL.motion.ambient(gsap.fromTo(m.track, { xPercent: from }, { xPercent: to, duration: px / 46, ease: 'none', repeat: -1 }));
      });
      return { rows: rows, made: made };
    }
    function clone(li) {
      var c = li.cloneNode(true);
      c.setAttribute('aria-hidden', 'true');
      c.querySelector('a').tabIndex = -1;
      return c;
    }
    function teardown() {
      if (!built) return;
      built.made.forEach(function (m) { m.tween.kill(); });
      stage.appendChild(card);
      items.forEach(function (li) { list.appendChild(li); });
      built.rows.replaceWith(list);
      built = null;
    }

    var hot = null;
    function on(link) {
      if (!built || hot === link) return;
      off();
      hot = link;
      var li = link.parentNode, rowEl = li.closest('.bl-services-marquee__row');
      var m = built.made.filter(function (x) { return x.row === rowEl; })[0];
      var i = link.getAttribute('data-smarq-i');
      imgs.forEach(function (im) { var me = im.getAttribute('data-smarq-img') === i; im.classList.toggle('is-on', me); if (me) im.loading = 'eager'; });
      card.classList.remove('is-on');
      li.appendChild(card);
      void card.offsetWidth;
      card.classList.add('is-on');
      link.classList.add('is-hot');
      rowEl.classList.add('is-hot');
      stage.classList.add('has-hot');
      if (m) gsap.to(m.tween, { timeScale: 0.2, duration: 0.4, overwrite: true });
    }
    function off() {
      if (!hot) return;
      var rowEl = hot.parentNode.closest('.bl-services-marquee__row');
      var m = built && built.made.filter(function (x) { return x.row === rowEl; })[0];
      hot.classList.remove('is-hot');
      if (rowEl) rowEl.classList.remove('is-hot');
      stage.classList.remove('has-hot');
      card.classList.remove('is-on');
      if (m) gsap.to(m.tween, { timeScale: 1, duration: 0.6, overwrite: true });
      hot = null;
    }

    stage.addEventListener('pointerover', function (e) {
      var a = e.target.closest && e.target.closest('.bl-services-marquee__link');
      if (a && e.pointerType === 'mouse') on(a);
    });
    stage.addEventListener('pointerleave', off);
    stage.addEventListener('focusin', function (e) {
      var a = e.target.closest('.bl-services-marquee__link');
      if (a && a.matches(':focus-visible')) on(a);
    });
    stage.addEventListener('focusout', function (e) { if (!stage.contains(e.relatedTarget)) off(); });
    /* the photos load once the section is near, so the first hover never shows an empty frame */
    window.BL.onVisible(sec, function () { imgs.forEach(function (im) { im.loading = 'eager'; }); }, 0);

    window.BL.motion.media(function (reduce) {
      if (reduce) return;
      built = build();
      return function () { off(); teardown(); };
    });
  });
})();
