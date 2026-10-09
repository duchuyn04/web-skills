/* site-intro-film: once per visit, skipped with reduced motion and in automated browsers (crawlers, audits).
   window.BL.introGate resolves when the layer starts to fade, so the hero opening can wait for it.
   The page stays scrollable while the film plays (the layer sits on the first screen, see section.css). */
(function () {
  var el = document.querySelector('[data-site-intro]');
  if (!el) return;
  var KEY = 'bl_intro_seen';
  var seen = false;
  try { seen = sessionStorage.getItem(KEY) === '1'; } catch (e) { /* storage blocked */ }
  if (window.BL.RM || seen || navigator.webdriver) { el.remove(); return; }

  var video = el.querySelector('video');
  /* pick the film for the screen shape before anything loads: 9:16 on portrait screens, 16:9 elsewhere */
  var tall = video.getAttribute('data-src-portrait') && window.matchMedia('(orientation: portrait)').matches;
  video.preload = 'auto';
  video.src = video.getAttribute(tall ? 'data-src-portrait' : 'data-src');
  var skip = el.querySelector('[data-intro-skip]');
  var done = false;
  var open;
  window.BL.introGate = new Promise(function (resolve) { open = resolve; });

  function finish() {
    if (done) return;
    done = true;
    try { sessionStorage.setItem(KEY, '1'); } catch (e) { /* storage blocked */ }
    el.classList.add('is-done');
    open();
    document.removeEventListener('keydown', onKey);
    window.removeEventListener('scroll', onScroll);
    setTimeout(function () { el.remove(); }, 500);
  }
  function onKey(e) { if (e.key === 'Escape') finish(); }
  /* the page scrolls under the film; once the layer has left the screen nobody is watching it, so the header
     and hero go ahead (this also covers a reload or an anchor link that lands below the first screen) */
  function onScroll() { if (window.scrollY >= el.offsetHeight - 1) finish(); }

  document.addEventListener('keydown', onKey);
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();
  skip.addEventListener('click', finish);
  video.addEventListener('ended', finish);
  video.addEventListener('error', finish);

  function start() {
    if (done) return;
    /* safety net: never hold the page longer than the film plus a margin */
    setTimeout(finish, 7000);
    var p = video.play();
    if (p && p.catch) p.catch(finish);
  }
  /* the film starts when the layer is really on screen: a page loaded ahead of time in a hidden or off-screen
     frame (a showcase that preloads its neighbours) or in a background tab keeps it for the visitor */
  if (!('IntersectionObserver' in window)) { start(); return; }
  var io = new IntersectionObserver(function (entries) {
    if (!entries[0].isIntersecting || document.hidden) return;
    io.disconnect();
    start();
  }, { threshold: 0.6 });
  io.observe(el);
  document.addEventListener('visibilitychange', function () {
    if (!document.hidden && !done) { io.unobserve(el); io.observe(el); }
  });
})();
