/* checkout 'steps': shows one step of form#co-form at a time; Continue checks only the visible step */
(function () {
  var root = document.querySelector('.cst');
  if (!root) return;
  var form = root.querySelector('[data-co-form]');
  if (!form) return;
  var steps = [].slice.call(form.querySelectorAll('[data-step]'));
  var dots = [].slice.call(root.querySelectorAll('.cst-progress li'));
  var cur = 0;

  function show(n, moved) {
    cur = Math.max(0, Math.min(steps.length - 1, n));
    steps.forEach(function (s, i) { s.hidden = i !== cur; });
    dots.forEach(function (li, i) {
      li.classList.toggle('is-on', i === cur);
      li.classList.toggle('is-done', i < cur);
      if (i === cur) li.setAttribute('aria-current', 'step'); else li.removeAttribute('aria-current');
      var b = li.querySelector('button');
      if (b) b.disabled = !(i < cur);
    });
    if (moved) {
      window.scrollTo(0, Math.max(0, root.getBoundingClientRect().top + window.pageYOffset - 80));
      var f = steps[cur].querySelector('input:not([type=hidden]):not([disabled]),select,textarea');
      if (f && cur < steps.length - 1) f.focus({ preventScroll: true });
    }
  }

  function fail(el, msg) {
    el.setAttribute('aria-invalid', 'true');
    var f = el.closest('.field'), m = f && f.querySelector('.err');
    if (f && !m) { m = document.createElement('small'); m.className = 'err'; f.appendChild(m); }
    if (m) m.textContent = msg;
  }

  function validate(step) {
    [].forEach.call(step.querySelectorAll('[aria-invalid]'), function (el) { el.removeAttribute('aria-invalid'); });
    [].forEach.call(step.querySelectorAll('.err'), function (el) { el.remove(); });
    var bad = null;
    [].forEach.call(step.querySelectorAll('input,select,textarea'), function (el) {
      // skip fields inside a hidden block (pickup hides the address, delivery hides the store list)
      if (el.disabled || el.closest('[hidden]')) return;
      if (!el.checkValidity()) {
        fail(el, el.validity.valueMissing ? 'Vui lòng nhập thông tin này' : el.name === 'phone' ? 'Số điện thoại gồm 10 số, bắt đầu bằng 03, 05, 07, 08 hoặc 09' : 'Thông tin chưa đúng định dạng');
        bad = bad || el;
      }
    });
    if (bad) { bad.focus(); return false; }
    return true;
  }

  function next() { if (validate(steps[cur])) show(cur + 1, true); }

  root.addEventListener('click', function (e) {
    if (e.target.closest('[data-step-next]')) { e.preventDefault(); next(); return; }
    if (e.target.closest('[data-step-prev]')) { e.preventDefault(); show(cur - 1, true); return; }
    var go = e.target.closest('[data-step-go]');
    if (go && !go.disabled) show(+go.dataset.stepGo - 1, true);
  });

  // Enter inside a field, or any submit before the last step, only moves forward. This listener is registered
  // before store.js binds its own submit handler, so stopImmediatePropagation keeps the order from being placed early.
  form.addEventListener('submit', function (e) {
    if (cur < steps.length - 1) {
      e.preventDefault();
      e.stopImmediatePropagation();
      next();
    }
  });
  form.addEventListener('input', function (e) {
    var el = e.target;
    if (el.getAttribute && el.getAttribute('aria-invalid')) {
      el.removeAttribute('aria-invalid');
      var f = el.closest('.field'), m = f && f.querySelector('.err');
      if (m) m.remove();
    }
  });
  show(0, false);
})();
