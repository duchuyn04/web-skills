/* toggle-model-flip */
(function () {
  document.querySelectorAll('[data-models]').forEach(function (root) {
    var opts = Array.prototype.slice.call(root.querySelectorAll('.bl-switch__opt'));
    opts.forEach(function (opt) {
      opt.addEventListener('click', function () {
        if (opt.getAttribute('aria-selected') === 'true') return;
        opts.forEach(function (o) {
          var on = o === opt;
          o.setAttribute('aria-selected', String(on));
          var panel = document.getElementById(o.getAttribute('aria-controls'));
          if (!panel) return;
          panel.hidden = !on;
          if (on && !window.BL.RM) { panel.classList.remove('is-entering'); void panel.offsetWidth; panel.classList.add('is-entering'); }
        });
      });
    });
  });
})();
