/* hero-form: validate, then submit to the endpoint or show the thank-you panel */
(function () {
  document.querySelectorAll('[data-hform-form]').forEach(function (form) {
    form.addEventListener('submit', function (e) {
      var fields = form.querySelectorAll('input, select, textarea');
      for (var i = 0; i < fields.length; i++) {
        if (!fields[i].checkValidity()) { e.preventDefault(); fields[i].reportValidity(); return; }
      }
      if (form.getAttribute('action')) return;
      e.preventDefault();
      form.querySelector('.bl-hform__fields').hidden = true;
      var done = form.querySelector('.bl-hform__done');
      if (done) { done.hidden = false; done.setAttribute('tabindex', '-1'); done.focus(); }
    });
  });
})();
