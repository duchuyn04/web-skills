/* locations-gmap: map-office-switch. Picking an office points the embedded map and the Open in Google Maps link at it. */
(function () {
  document.querySelectorAll('[data-gmap]').forEach(function (sec) {
    var frame = sec.querySelector('[data-gmap-frame]');
    var open = sec.querySelector('[data-gmap-open]');
    var offices = [].slice.call(sec.querySelectorAll('[data-gmap-office]'));
    if (!frame) return;
    var title = (frame.getAttribute('title') || '').split(':')[0];
    offices.forEach(function (li) {
      var btn = li.querySelector('button');
      btn.addEventListener('click', function () {
        offices.forEach(function (o) {
          var on = o === li;
          o.classList.toggle('is-active', on);
          o.querySelector('button').setAttribute('aria-pressed', String(on));
        });
        if (frame.getAttribute('src') !== btn.getAttribute('data-src')) frame.setAttribute('src', btn.getAttribute('data-src'));
        frame.setAttribute('title', title + ': ' + btn.getAttribute('data-name'));
        if (open) open.setAttribute('href', btn.getAttribute('data-open'));
      });
    });
  });
})();
