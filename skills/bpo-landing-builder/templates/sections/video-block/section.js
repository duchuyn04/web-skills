/* video-block: the player (file or embed iframe) is created only when the visitor clicks play */
(function () {
  document.querySelectorAll('[data-vblock]').forEach(function (block) {
    var sec = block.closest('section');
    var btn = block.querySelector('.bl-vblock__trigger');
    var dlg = sec && sec.querySelector('[data-vmodal]');
    if (!btn || !dlg) return;
    var frame = dlg.querySelector('[data-vmodal-frame]');
    function open() {
      frame.innerHTML = '';
      var embed = btn.getAttribute('data-embed');
      var src = btn.getAttribute('data-src');
      var title = btn.getAttribute('data-title') || '';
      var el;
      if (embed) {
        el = document.createElement('iframe');
        el.src = embed;
        el.title = title;
        el.allow = 'autoplay; fullscreen; picture-in-picture';
        el.setAttribute('allowfullscreen', '');
      } else {
        el = document.createElement('video');
        el.src = src;
        el.controls = true;
        el.autoplay = true;
        el.playsInline = true;
        el.setAttribute('aria-label', title);
      }
      frame.appendChild(el);
      if (typeof dlg.showModal === 'function') dlg.showModal(); else dlg.setAttribute('open', '');
    }
    function close() { if (dlg.open) { if (typeof dlg.close === 'function') dlg.close(); else dlg.removeAttribute('open'); } }
    btn.addEventListener('click', open);
    dlg.addEventListener('close', function () { frame.innerHTML = ''; btn.focus(); });
    dlg.addEventListener('click', function (e) { if (e.target === dlg || e.target.closest('[data-vmodal-close]')) close(); });
  });
})();
