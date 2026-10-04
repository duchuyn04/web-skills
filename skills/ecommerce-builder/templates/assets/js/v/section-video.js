/* Section 'video': load the YouTube player only after a click (no third-party request before). */
(function () {
  var buttons = document.querySelectorAll('[data-yt]');
  Array.prototype.forEach.call(buttons, function (btn) {
    btn.addEventListener('click', function () {
      var box = btn.closest('[data-yt-box]');
      if (!box || !/^[\w-]{6,20}$/.test(btn.dataset.yt)) return;
      var f = document.createElement('iframe');
      f.src = 'https://www.youtube-nocookie.com/embed/' + btn.dataset.yt + '?autoplay=1&rel=0';
      f.title = btn.dataset.ytTitle || 'Video';
      f.allow = 'autoplay; encrypted-media; picture-in-picture';
      f.allowFullscreen = true;
      f.referrerPolicy = 'strict-origin-when-cross-origin';
      box.appendChild(f);
      btn.remove();
      f.focus();
    });
  });
})();
