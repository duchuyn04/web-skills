/* checkout 'split-pay': payment radios live in the sticky card (form="co-form"); keep the accordions honest */
(function () {
  var root = document.querySelector('.csp');
  if (!root) return;
  var form = root.querySelector('[data-co-form]');
  if (!form) return;

  // the installment quick buy from a product page pre-selects a payment; store.js looks inside the form only
  try {
    var pref = window.Shop && window.Shop.get('pay_pref', null);
    if (pref) {
      var r = root.querySelector('input[name=payment][value="' + pref + '"]');
      if (r) r.checked = true;
    }
  } catch (e) { /* storage unavailable */ }

  // an invalid field inside a folded accordion opens it and takes focus
  var focusing = false;
  new MutationObserver(function (list) {
    list.forEach(function (m) {
      var el = m.target;
      if (!el.getAttribute('aria-invalid')) return;
      var d = el.closest('details');
      if (d && !d.open) d.open = true;
      if (!focusing) {
        focusing = true;
        el.focus();
        setTimeout(function () { focusing = false; }, 0);
      }
    });
  }).observe(form, { attributes: true, attributeFilter: ['aria-invalid'], subtree: true });

  function val(sel) { var e = form.querySelector(sel); return e && e.value ? e.value.trim() : ''; }
  function summary() {
    var buyer = [val('input[name=name]'), val('input[name=phone]')].filter(Boolean).join(', ');
    var rc = form.querySelector('input[name=receive]:checked'), ship;
    if (rc && rc.value === 'pickup') {
      var st = form.querySelector('input[name=store]:checked');
      var nm = st && st.closest('label') && st.closest('label').querySelector('b');
      ship = 'Nhận tại ' + (nm ? nm.textContent : 'cửa hàng');
    } else {
      ship = [val('input[name=street]'), val('input[name=ward]'), val('select[name=province]')].filter(Boolean).join(', ');
    }
    var b = root.querySelector('[data-csp-sum=buyer]'), s = root.querySelector('[data-csp-sum=ship]');
    if (b) b.textContent = buyer;
    if (s) s.textContent = ship;
  }
  form.addEventListener('input', summary);
  form.addEventListener('change', summary);
  summary();
})();
