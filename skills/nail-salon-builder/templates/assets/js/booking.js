/* Booking form (dat-lich.html) and booking lookup (lich-hen.html). */
(function () {
  var N = window.NS, S = N.S, $ = N.$, $$ = N.$$, esc = N.esc;
  var params = new URLSearchParams(location.search);

  function phoneOk(p) { var d = String(p || '').replace(/\D/g, ''); return /^0\d{9,10}$/.test(d); }
  function digits(p) { return String(p || '').replace(/\D/g, ''); }

  function statusBadge(s) { return '<span class="badge st-' + s + '">' + esc(N.STATUS[s] || s) + '</span>'; }

  function apptCard(a, opts) {
    var loc = N.LOC[a.loc] || {}, tech = N.TECH[a.tech];
    var rows = a.services.map(function (s) { return '<li><span>' + esc(s.name) + '</span><b>' + N.vnd(s.price) + '</b></li>'; })
      .concat((a.addons || []).map(function (x) { return '<li><span>' + esc(x.name) + (x.qty > 1 ? ' x' + x.qty : '') + '</span><b>' + N.vnd(x.price * (x.qty || 1)) + '</b></li>'; }));
    if (a.discount) rows.push('<li><span>Mã ưu đãi ' + esc(a.promo || '') + '</span><b>-' + N.vnd(a.discount) + '</b></li>');
    return '<article class="appt">' +
      '<header><div><p class="eyebrow">Mã ' + esc(a.code) + '</p><h2>' + N.dateLabel(a.date, true) + ', ' + N.hm(a.start) + '</h2></div>' + statusBadge(a.status) + '</header>' +
      '<ul class="appt-meta"><li>' + N.icon('pin', 'i-sm') + '<span>' + esc(loc.name || '') + (loc.address ? ', ' + esc(loc.address) : '') + '</span></li>' +
      '<li>' + N.icon('user', 'i-sm') + '<span>' + (tech ? 'Thợ ' + esc(tech.name) : 'Tiệm xếp thợ') + '</span></li>' +
      '<li>' + N.icon('clock', 'i-sm') + '<span>' + N.mins(a.end - a.start) + '</span></li></ul>' +
      '<ul class="appt-lines">' + rows.join('') + '</ul>' +
      '<p class="appt-total"><span>Tạm tính</span><b>' + N.vnd(a.total - (a.discount || 0)) + '</b></p>' +
      (opts && opts.actions ? '<div class="appt-act" data-appt-act></div>' : '') +
      '</article>';
  }

  /* Send the booking to the salon's chat: WhatsApp takes the text in the link; Zalo and Messenger links cannot carry
     text, so it is copied first and the visitor pastes it. */
  function bookingText(b) {
    var loc = N.LOC[b.loc] || {}, tech = N.TECH[b.tech];
    return 'Đặt lịch ' + b.code + ': ' + N.dateLabel(b.date, true) + ' lúc ' + N.hm(b.start) + ', ' +
      b.services.map(function (s) { return s.name; }).join(', ') + (loc.name ? ', ' + loc.name : '') + (tech && b.techChosen ? ', thợ ' + tech.name : '') +
      '. ' + b.customer.name + ', ' + b.customer.phone + '.' + (b.note ? ' Ghi chú: ' + b.note : '');
  }
  function sendBooking(kind, b) {
    var text = bookingText(b), s = S.salon;
    if (kind === 'whatsapp') { window.open('https://wa.me/' + String(s.whatsapp).replace(/\D/g, '') + '?text=' + encodeURIComponent(text), '_blank', 'noopener'); return; }
    var url = kind === 'zalo' ? 'https://zalo.me/' + String(s.zalo).replace(/\s/g, '') : s.messenger;
    var go = function () { N.toast('Đã chép nội dung lịch hẹn. Dán vào khung chat để gửi.'); window.open(url, '_blank', 'noopener'); };
    if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(text).then(go, go); else go();
  }

  /* ---------------------------------------------------------------- booking form */
  var root = $('[data-booking]');
  if (root) {
    var form = $('[data-bk-form]', root);
    var st = { step: 1, loc: (S.locations[0] || {}).id, tech: '', date: '', time: null, slotTechs: [] };
    var look = params.get('look') && (S.gallery || []).filter(function (g) { return g.id === params.get('look'); })[0];

    if (params.get('loc') && N.LOC[params.get('loc')]) {
      st.loc = params.get('loc');
      var r = form.querySelector('input[name=loc][value="' + st.loc + '"]'); if (r) r.checked = true;
    }
    if (params.get('service')) {
      var cb = form.querySelector('input[name=svc][value="' + params.get('service') + '"]');
      if (cb) { cb.checked = true; var d = cb.closest('details'); if (d) d.open = true; }
    }
    if (look) {
      var box = $('[data-bk-look]', root);
      box.hidden = false;
      box.innerHTML = '<img src="' + (window.ROOT || '') + 'assets/art/look-' + esc(look.id) + '.svg" alt="" width="64" height="64" onerror="this.remove()"><div><b>Mẫu: ' + esc(look.title) + '</b><small>Thợ làm theo mẫu này, chỉnh màu và form theo tay bạn.</small></div>';
    }

    function chosen() { return $$('input[name=svc]:checked', form).map(function (x) { return x.value; }); }
    function chosenAddons() {
      return $$('input[name=addon]:checked', form).filter(function (x) {
        return chosen().indexOf(x.value.split(':')[0]) >= 0;
      }).map(function (x) {
        var q = form.querySelector('select[data-qty="' + x.value + '"]');
        return { svc: x.value.split(':')[0], id: x.value.split(':')[1], qty: q ? +q.value : 1 };
      });
    }
    function totals() { return N.priceOf(chosen(), chosenAddons()); }

    function renderTechs() {
      var box = $('[data-bk-techs]', root); if (!box) return;
      var list = N.techsFor(st.loc, chosen());
      if (st.tech && !list.some(function (t) { return t.id === st.tech; })) st.tech = '';
      box.innerHTML = '<label class="bk-opt"><input type="radio" name="tech" value=""' + (st.tech ? '' : ' checked') + '><span><b>Thợ bất kỳ</b><small>Tiệm xếp thợ còn trống</small></span></label>' +
        list.map(function (t) {
          return '<label class="bk-opt"><input type="radio" name="tech" value="' + esc(t.id) + '"' + (st.tech === t.id ? ' checked' : '') + '><span class="bk-tech"><i aria-hidden="true">' + esc(t.name.charAt(0)) + '</i><span><b>' + esc(t.name) + '</b><small>' + esc(t.title || '') + '</small></span></span></label>';
        }).join('');
    }

    function renderDays() {
      var box = $('[data-bk-days]', root), n = (S.booking.days_ahead || 21), t = N.today(), html = [];
      for (var i = 0; i < n; i++) {
        var d = N.addDays(t, i), open = !!N.hoursOn(st.loc, d);
        html.push('<label class="day' + (open ? '' : ' off') + '"><input type="radio" name="date" value="' + d + '"' + (open ? '' : ' disabled') + (st.date === d ? ' checked' : '') + '>' +
          '<span><small>' + (i === 0 ? 'Hôm nay' : i === 1 ? 'Ngày mai' : N.DAYS_SHORT[N.weekday(d)]) + '</small><b>' + N.dateLabel(d) + '</b></span></label>');
      }
      box.innerHTML = html.join('');
      if (!st.date || !N.hoursOn(st.loc, st.date)) {
        var first = box.querySelector('input:not([disabled])');
        if (first) { first.checked = true; st.date = first.value; }
      }
      renderSlots();
    }

    function renderSlots() {
      var box = $('[data-bk-slots]', root);
      if (!st.date) { box.innerHTML = ''; return; }
      var list = N.slots(st.loc, st.date, st.tech, Math.max(15, totals().minutes), chosen());
      if (st.time != null && !list.some(function (s) { return s.time === st.time; })) st.time = null;
      if (!list.length) { box.innerHTML = '<p class="empty">Ngày này đã hết giờ trống' + (st.tech ? ' của thợ đã chọn' : '') + '. Chọn ngày khác.</p>'; return; }
      var groups = [['Sáng', 0, 720], ['Chiều', 720, 1020], ['Tối', 1020, 1440]];
      box.innerHTML = groups.map(function (g) {
        var items = list.filter(function (s) { return s.time >= g[1] && s.time < g[2]; });
        if (!items.length) return '';
        return '<div class="slot-group"><h3>' + g[0] + '</h3><div class="slots">' + items.map(function (s) {
          return '<label class="slot"><input type="radio" name="time" value="' + s.time + '"' + (st.time === s.time ? ' checked' : '') + ' data-techs="' + s.techs.join(',') + '"><span>' + N.hm(s.time) + '</span></label>';
        }).join('') + '</div></div>';
      }).join('');
    }

    function renderSummary() {
      var ids = chosen(), ad = chosenAddons(), t = totals();
      var list = $('[data-sum-list]', root);
      if (!ids.length) list.innerHTML = '<li class="muted">Chưa chọn dịch vụ</li>';
      else list.innerHTML = ids.map(function (id) {
        var s = N.svc(id);
        return '<li><span>' + esc(s.name) + '</span><b>' + (s.price == null ? 'Báo giá' : (s.price_type === 'from' ? 'từ ' : '') + N.vnd(s.price)) + '</b></li>';
      }).join('') + ad.map(function (x) {
        var a = N.ADD[x.id];
        return '<li class="sub"><span>' + esc(a.name) + (a.per_nail ? ' x' + x.qty : '') + '</span><b>' + N.vnd(a.price * x.qty) + '</b></li>';
      }).join('');
      var loc = N.LOC[st.loc], tech = N.TECH[st.tech];
      $('[data-sum-loc]', root).textContent = loc ? loc.name : '';
      if ($('[data-sum-tech]', root)) $('[data-sum-tech]', root).textContent = tech ? tech.name : 'Tiệm xếp thợ';
      $('[data-sum-time]', root).textContent = st.date && st.time != null ? N.dateLabel(st.date, true) + ', ' + N.hm(st.time) : 'Chưa chọn';
      $('[data-sum-dur]', root).textContent = N.mins(t.minutes);
      var codeInput = $('[data-code-input]', root);
      var p = codeInput && N.promo(codeInput.value), disc = N.discountFor(p, t.total);
      $('[data-sum-total]', root).textContent = (t.from ? 'từ ' : '') + N.vnd(t.total - disc);
      $('[data-bar-text]', root).textContent = ids.length ? ids.length + ' dịch vụ, ' + N.mins(t.minutes) : 'Chưa chọn dịch vụ';
      $('[data-bar-total]', root).textContent = $('[data-sum-total]', root).textContent;
      $$('details[data-bk-cat]', root).forEach(function (d) {
        var c = $$('input[name=svc]:checked', d).length;
        $('[data-cat-count]', d).textContent = c ? c + ' đã chọn' : '';
      });
      $$('[data-addons-for]', root).forEach(function (b) { b.hidden = ids.indexOf(b.getAttribute('data-addons-for')) < 0; });
    }

    function go(step) {
      // a step with nothing to choose (one branch, no technician choice) is passed in the direction of travel
      var f = $('[data-step="' + step + '"]', root);
      if (f && f.hasAttribute('data-skip')) step += step > st.step ? 1 : -1;
      st.step = step;
      $$('[data-step]', root).forEach(function (f) { f.hidden = +f.getAttribute('data-step') !== step; });
      $$('[data-step-dot]', root).forEach(function (d) {
        var k = +d.getAttribute('data-step-dot');
        if (k === step) d.setAttribute('aria-current', 'step'); else d.removeAttribute('aria-current');
        d.classList.toggle('done', k < step);
      });
      if (step === 2) renderTechs();
      if (step === 3) renderDays();
      var top = root.getBoundingClientRect().top + window.scrollY - 80;
      if (window.scrollY > top) window.scrollTo({ top: top });
      var leg = $('[data-step="' + step + '"] legend', root); if (leg) { leg.tabIndex = -1; leg.focus({ preventScroll: true }); }
    }
    function valid(step) {
      var ok = true;
      if (step === 1) ok = chosen().length > 0;
      if (step === 3) ok = !!st.date && st.time != null;
      if (step === 4) ok = !!form.elements.namedItem('name').value.trim() && phoneOk(form.elements.namedItem('phone').value);
      var e = $('[data-err="' + step + '"]', root); if (e) e.hidden = ok;
      return ok;
    }

    form.addEventListener('change', function (e) {
      var t = e.target;
      if (t.name === 'loc') { st.loc = t.value; st.time = null; }
      if (t.name === 'tech') { st.tech = t.value; st.time = null; }
      if (t.name === 'date') { st.date = t.value; st.time = null; renderSlots(); }
      if (t.name === 'time') { st.time = +t.value; st.slotTechs = (t.getAttribute('data-techs') || '').split(',').filter(Boolean); $('[data-err="3"]', root).hidden = true; }
      if (t.name === 'svc') $('[data-err="1"]', root).hidden = true;
      renderSummary();
    });
    form.addEventListener('input', function (e) { if (e.target.hasAttribute('data-code-input')) renderSummary(); });
    $$('[data-next]', root).forEach(function (b) { b.addEventListener('click', function () { if (valid(st.step)) go(st.step + 1); }); });
    $$('[data-prev]', root).forEach(function (b) { b.addEventListener('click', function () { go(st.step - 1); }); });

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      if (!valid(4)) return;
      var ids = chosen(), ad = chosenAddons(), t = totals();
      var dur = Math.max(15, t.minutes);
      // the slot may have been taken in another tab since it was shown
      var still = N.slots(st.loc, st.date, st.tech, dur, ids).filter(function (s) { return s.time === st.time; })[0];
      if (!still) { N.toast('Giờ này vừa có người đặt. Chọn giờ khác.', { bad: true }); go(3); return; }
      var codeInput = $('[data-code-input]', root), p = codeInput && N.promo(codeInput.value);
      var note = form.elements.namedItem('note').value.trim();
      if (look) note = ('Mẫu: ' + look.title + (note ? '. ' + note : ''));
      var photo = form.elements.namedItem('photo') && form.elements.namedItem('photo').files[0] ? form.elements.namedItem('photo').files[0].name : '';
      var b = N.book({
        date: st.date, start: st.time, end: st.time + dur, loc: st.loc, tech: st.tech || (still.techs[0] || ''), techChosen: !!st.tech,
        services: ids.map(function (id) { var s = N.svc(id); return { id: id, name: s.name, price: s.price || 0, minutes: s.minutes }; }),
        addons: ad.map(function (x) { var a = N.ADD[x.id]; return { id: x.id, name: a.name, price: a.price, qty: x.qty }; }),
        total: t.total, discount: N.discountFor(p, t.total), promo: p ? p.code : '', source: 'web',
        customer: { name: form.elements.namedItem('name').value.trim(), phone: digits(form.elements.namedItem('phone').value) }, note: note, photo: photo, look: look ? look.id : ''
      });
      $('.bk-grid', root).hidden = true;
      $('.bk-steps', root).hidden = true;
      $('[data-bk-bar]', root).hidden = true;
      var done = $('[data-bk-done]', root);
      done.hidden = false;
      $('[data-done-code]', done).textContent = b.code;
      $('[data-done-card]', done).innerHTML = apptCard(b);
      $('[data-done-link]', done).href = 'lich-hen.html?code=' + b.code + '&phone=' + b.customer.phone;
      var send = $('[data-send]', done);
      if (send) send.onclick = function () { sendBooking(send.getAttribute('data-send'), b); };
      done.focus();
      window.scrollTo({ top: 0 });
    });

    renderSummary();
  }

  /* ---------------------------------------------------------------- lookup */
  var lk = $('[data-lookup]');
  if (lk) {
    var lf = $('[data-lookup-form]', lk), out = $('[data-lookup-result]', lk), err = $('[data-lookup-err]', lk);
    function show(a) {
      out.innerHTML = apptCard(a, { actions: true });
      var act = $('[data-appt-act]', out);
      var hours = (S.booking.cancel_hours || 0);
      var startAt = N.parse(a.date).getTime() + a.start * 60000;
      var open = a.status === 'pending' || a.status === 'confirmed';
      if (open && startAt - Date.now() > hours * 3600000) {
        act.innerHTML = '<button class="btn btn-ghost" type="button" data-cancel>' + N.icon('x', 'i-sm') + 'Hủy lịch hẹn</button><span class="muted small">Đổi giờ: hủy lịch này rồi đặt lại, hoặc gọi ' + esc(S.salon.hotline) + '.</span>';
        $('[data-cancel]', act).onclick = function () {
          if (!confirm('Hủy lịch hẹn ' + a.code + '?')) return;
          show(N.update(a.code, { status: 'cancelled' }, 'Khách hủy online'));
          N.toast('Đã hủy lịch hẹn ' + a.code);
        };
      } else if (open) {
        act.innerHTML = '<p class="muted small">Còn dưới ' + hours + ' tiếng đến giờ hẹn. Cần đổi hoặc hủy, gọi ' + esc(S.salon.hotline) + '.</p>';
      }
    }
    lf.addEventListener('submit', function (e) {
      e.preventDefault();
      var a = N.find(lf.code.value);
      var ok = a && digits(a.customer.phone) === digits(lf.phone.value);
      err.hidden = !!ok;
      out.innerHTML = '';
      if (ok) show(a);
    });
    if (params.get('code')) {
      lf.code.value = params.get('code');
      lf.phone.value = params.get('phone') || '';
      if (lf.phone.value) lf.requestSubmit ? lf.requestSubmit() : lf.dispatchEvent(new Event('submit'));
    }
    var mine = N.get('mine', []).map(N.find).filter(Boolean).reverse();
    if (mine.length) {
      $('[data-mine]', lk).hidden = false;
      $('[data-mine-list]', lk).innerHTML = mine.slice(0, 6).map(function (a) {
        return '<li><a href="lich-hen.html?code=' + a.code + '&phone=' + a.customer.phone + '"><b>' + a.code + '</b><span>' + N.dateLabel(a.date, true) + ', ' + N.hm(a.start) + '</span>' + statusBadge(a.status) + '</a></li>';
      }).join('');
    }
  }
})();
