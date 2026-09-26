/* floating-chat: show once the first section in <main> leaves the viewport */
(function () {
  var fab = document.querySelector('[data-fab]');
  var hero = document.querySelector('main > :first-child');
  if (!fab) return;
  if (!hero || !('IntersectionObserver' in window)) { fab.classList.add('is-shown'); return; }
  new IntersectionObserver(function (entries) {
    fab.classList.toggle('is-shown', !entries[0].isIntersecting);
  }, { threshold: 0.05 }).observe(hero);
})();
