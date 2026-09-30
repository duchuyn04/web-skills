/* hero-chat: agent-chat-playback. Plays once when seen; Pause stops it on the current bubble, Replay starts again.
   Focus inside the window and the page-wide motion switch also stop it. Reduced motion shows the whole transcript. */
(function () {
  document.querySelectorAll('[data-chat]').forEach(function (win) {
    var BL = window.BL || {};
    var msgs = Array.prototype.slice.call(win.querySelectorAll('[data-msg]'));
    var typing = win.querySelector('[data-typing]');
    var ctl = win.querySelector('[data-chat-ctl]');
    var step = 0, timer = 0, playing = false;
    if (BL.RM || !msgs.length || !BL.gsap) { if (ctl) ctl.hidden = true; return; }

    function label(done) { ctl.textContent = ctl.getAttribute(done ? 'data-label-replay' : 'data-label-pause'); }
    function stop(done) {
      if (timer) timer.kill(); timer = 0; playing = false;
      typing.classList.remove('is-on');
      if (done) msgs.forEach(function (m) { m.classList.add('is-shown'); });
      label(true);
    }
    function next() {
      if (step >= msgs.length) { stop(false); return; }
      var m = msgs[step];
      var isAgent = m.classList.contains('bl-chatwin__msg--agent');
      var wait = step === 0 ? 400 : (isAgent ? 1400 : 900);
      if (isAgent) { m.parentNode.insertBefore(typing, m); typing.classList.add('is-on'); }
      timer = BL.gsap.delayedCall(wait / 1000, function () {
        typing.classList.remove('is-on');
        m.classList.add('is-shown');
        step++;
        next();
      });
    }
    function play() {
      if (BL.paused) return;
      if (timer) timer.kill();
      step = 0; playing = true;
      win.classList.add('is-playing');
      msgs.forEach(function (m) { m.classList.remove('is-shown'); });
      label(false);
      next();
    }
    ctl.addEventListener('click', function () { if (playing) stop(true); else play(); });
    win.addEventListener('focusin', function (e) { if (playing && e.target !== ctl) stop(true); });
    document.addEventListener('bl:motion', function (e) { if (e.detail.paused && playing) stop(true); });
    document.addEventListener('visibilitychange', function () { if (document.hidden && playing) stop(true); });
    win.classList.add('is-playing');
    label(false);
    if (BL.onVisible) BL.onVisible(win, play, 0.4); else play();
  });
})();
