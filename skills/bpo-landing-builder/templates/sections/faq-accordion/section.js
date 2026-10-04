/* smooth-accordion-expansion: toggles aria-expanded; CSS animates grid rows */
(function () {
  document.querySelectorAll('[data-accordion]').forEach(function (root) {
    root.querySelectorAll('.bl-acc__btn').forEach(function (btn) {
      btn.addEventListener('click', function () {
        btn.setAttribute('aria-expanded', String(btn.getAttribute('aria-expanded') !== 'true'));
      });
    });
  });
})();
