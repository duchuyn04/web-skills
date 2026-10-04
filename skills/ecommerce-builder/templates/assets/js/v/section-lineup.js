/* Section 'lineup': "So sánh chi tiết" puts the models of the lineup on the compare page. */
(function () {
  Array.prototype.forEach.call(document.querySelectorAll('[data-lineup-compare]'), function (a) {
    a.addEventListener('click', function () {
      if (window.Shop) window.Shop.set('cmp', a.getAttribute('data-lineup-compare').split(',').slice(0, 3));
    });
  });
})();
