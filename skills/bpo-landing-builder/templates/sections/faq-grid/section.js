/* smooth-accordion-expansion for faq-grid: toggles aria-expanded; CSS animates the grid rows and the plus sign */
(function () {
  document.querySelectorAll('[data-faq-grid]').forEach(function (root) {
    root.querySelectorAll('.bl-fgrid__btn').forEach(function (btn) {
      btn.addEventListener('click', function () {
        btn.setAttribute('aria-expanded', String(btn.getAttribute('aria-expanded') !== 'true'));
      });
    });
  });
})();
