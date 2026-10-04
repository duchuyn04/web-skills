/* multi-step-form-slide: step validation, progress bar, autofocus, demo or real submit */
(function () {
  document.querySelectorAll('[data-wizard]').forEach(function (form) {
    var steps = Array.prototype.slice.call(form.querySelectorAll('[data-step]'));
    var bars = form.querySelectorAll('.bl-wizard__progress span');
    var count = form.querySelector('[data-wizard-count]');
    var done = form.querySelector('.bl-wizard__done');
    var i = 0;

    function show(n, dir) {
      steps[i].classList.remove('is-active', 'is-forward', 'is-back');
      i = n;
      var s = steps[i];
      s.classList.add('is-active');
      if (!window.BL.RM) s.classList.add(dir > 0 ? 'is-forward' : 'is-back');
      bars.forEach(function (b, k) { b.classList.toggle('is-on', k <= i); });
      if (count) count.textContent = String(i + 1);
      var first = s.querySelector('input:checked, input, textarea');
      if (first) first.focus({ preventScroll: true });
    }
    function valid(step) {
      var err = step.querySelector('.bl-wizard__error');
      var radios = step.querySelectorAll('input[type="radio"]');
      if (radios.length) {
        var ok = Array.prototype.some.call(radios, function (r) { return r.checked; });
        if (err) err.hidden = ok;
        return ok;
      }
      var fields = step.querySelectorAll('input, textarea');
      for (var k = 0; k < fields.length; k++) {
        if (!fields[k].checkValidity()) { fields[k].reportValidity(); return false; }
      }
      return true;
    }
    form.addEventListener('change', function (e) {
      if (e.target.type === 'radio') {
        var err = e.target.closest('[data-step]').querySelector('.bl-wizard__error');
        if (err) err.hidden = true;
      }
    });
    form.addEventListener('click', function (e) {
      if (e.target.closest('[data-next]')) { if (valid(steps[i])) show(i + 1, 1); }
      if (e.target.closest('[data-back]')) show(i - 1, -1);
    });
    form.addEventListener('submit', function (e) {
      if (!valid(steps[i])) { e.preventDefault(); return; }
      if (form.getAttribute('action')) return;
      e.preventDefault();
      steps[i].classList.remove('is-active');
      form.querySelector('.bl-wizard__top').hidden = true;
      if (done) { done.hidden = false; }
    });
  });
})();
