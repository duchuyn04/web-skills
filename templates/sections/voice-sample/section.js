/* soundwave-audio-bars: one sample plays at a time; without an audio file the bars run for 8s as a preview */
(function () {
  var items = Array.prototype.slice.call(document.querySelectorAll('[data-sample]'));
  if (!items.length) return;
  function stop(item) {
    var btn = item.querySelector('.bl-sample__play');
    var audio = item.querySelector('audio');
    item.classList.remove('is-playing');
    btn.setAttribute('aria-pressed', 'false');
    btn.setAttribute('aria-label', btn.getAttribute('data-play-label'));
    if (audio) audio.pause();
    clearTimeout(item._t);
  }
  items.forEach(function (item) {
    var btn = item.querySelector('.bl-sample__play');
    var audio = item.querySelector('audio');
    if (audio) audio.addEventListener('ended', function () { stop(item); });
    btn.addEventListener('click', function () {
      if (item.classList.contains('is-playing')) { stop(item); return; }
      items.forEach(function (o) { if (o !== item) stop(o); });
      item.classList.add('is-playing');
      btn.setAttribute('aria-pressed', 'true');
      btn.setAttribute('aria-label', btn.getAttribute('data-pause-label'));
      if (audio) { audio.currentTime = 0; audio.play().catch(function () { stop(item); }); }
      else { item._t = setTimeout(function () { stop(item); }, 8000); }
    });
  });
})();
