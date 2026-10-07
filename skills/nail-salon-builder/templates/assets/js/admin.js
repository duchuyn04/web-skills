/* Salon admin: login, shell, overview, day calendar by technician, appointment list and detail, customers,
   services, technicians, reports, settings. Reads appointments through NS (common.js); every change is an
   override kept in localStorage, so the public lookup page sees the same status. */
(function () {
  var N = window.NS, S = N.S, $ = N.$, $$ = N.$$, esc = N.esc, vnd = N.vnd;
  var page = document.body.getAttribute('data-admin');
  var Q = new URLSearchParams(location.search);

  /* ------------------------------------------------------------------ login */
  if (page === 'login') {
    var lf = $('[data-login]');
    lf.addEventListener('submit', function (e) {
      e.preventDefault();
      var pw = lf.elements.namedItem('pw').value;
      if (pw !== N.get('adm:pw', 'demo')) { $('[data-login-err]').hidden = false; return; }
      var st = (S.staff || [])[+lf.elements.namedItem('staff').value] || { name: 'Quản lý', role: '' };
      N.set('adm:staff', st);
      location.href = Q.get('next') || 'index.html';
    });
    return;
  }
  var staff = N.get('adm:staff', null);
  if (!staff) { location.replace('login.html?next=' + encodeURIComponent(location.pathname.split('/').pop() + location.search)); return; }

  /* ------------------------------------------------------------------ helpers */
  function short(n) {
    n = Math.round(n || 0);
    if (n >= 1e9) return (n / 1e9).toFixed(1).replace('.', ',').replace(',0', '') + ' tỷ';
    if (n >= 1e6) return (n / 1e6).toFixed(1).replace('.', ',').replace(',0', '') + ' tr';
    if (n >= 1e3) return Math.round(n / 1e3) + 'k';
    return String(n);
  }
  /* 232.040.000 -> '232,04 triệu' for tiles; tables keep full amounts */
  function money(n) {
    if (n >= 1e9) return (Math.round(n / 1e7) / 100).toString().replace('.', ',') + ' tỷ';
    if (n >= 1e6) return (Math.round(n / 1e4) / 100).toString().replace('.', ',') + ' triệu';
    return vnd(n);
  }
  function pct(a, b) { return b ? Math.round(a / b * 1000) / 10 : 0; }
  function pctText(x) { return String(x).replace('.', ',') + '%'; }
  function badge(s) { return '<span class="badge st-' + s + '">' + esc(N.STATUS[s] || s) + '</span>'; }
  function techName(id) { return N.TECH[id] ? N.TECH[id].name : 'Chưa xếp'; }
  function locName(id) { return N.LOC[id] ? N.LOC[id].name : ''; }
  function svcText(a) { return a.services.map(function (s) { return s.name; }).join(', ') + (a.addons && a.addons.length ? ' + ' + a.addons.map(function (x) { return x.name; }).join(', ') : ''); }
  function net(a) { return a.total - (a.discount || 0); }
  function inRange(a, f, t) { return a.date >= f && a.date <= t; }
  function sum(list, fn) { return list.reduce(function (t, x) { return t + fn(x); }, 0); }
  function by(list, key) { var o = {}; list.forEach(function (x) { var k = key(x); (o[k] = o[k] || []).push(x); }); return o; }
  function el(html) { var d = document.createElement('div'); d.innerHTML = html; return d.firstElementChild; }
  var NEXT = {
    pending: [['confirmed', 'Xác nhận'], ['cancelled', 'Hủy']],
    confirmed: [['arrived', 'Khách đã đến'], ['no_show', 'Không đến'], ['cancelled', 'Hủy']],
    arrived: [['done', 'Hoàn thành']],
    done: [], cancelled: [['confirmed', 'Mở lại']], no_show: [['confirmed', 'Mở lại']]
  };
  function setStatus(code, status, after) {
    var before = N.find(code).status;
    var patch = { status: status };
    if (status === 'done' && !N.find(code).pay) patch.pay = 'cash';
    N.update(code, patch, staff.name);
    N.toast(code + ': ' + N.STATUS[status], { undo: function () { N.update(code, { status: before }, staff.name + ' (hoàn tác)'); if (after) after(); } });
    if (after) after();
  }
  function actionBtns(a, primaryOnly) {
    var list = NEXT[a.status] || [];
    if (primaryOnly) list = list.slice(0, 1);
    return list.map(function (x, i) {
      return '<button type="button" class="btn btn-sm' + (i ? ' btn-ghost' : '') + (x[0] === 'cancelled' || x[0] === 'no_show' ? ' danger' : '') + '" data-act="' + x[0] + '" data-code="' + a.code + '">' + esc(x[1]) + '</button>';
    }).join('');
  }
  function bindActions(root, after) {
    root.addEventListener('click', function (e) {
      var b = e.target.closest('[data-act]'); if (!b) return;
      e.stopPropagation();
      var st = b.getAttribute('data-act'), code = b.getAttribute('data-code');
      if ((st === 'cancelled' || st === 'no_show') && !confirm((st === 'cancelled' ? 'Hủy' : 'Đánh dấu không đến cho') + ' lịch hẹn ' + code + '?')) return;
      setStatus(code, st, after);
    });
  }
  function download(name, rows) {
    var csv = '﻿' + rows.map(function (r) { return r.map(function (c) { c = String(c == null ? '' : c); return /[",\n;]/.test(c) ? '"' + c.replace(/"/g, '""') + '"' : c; }).join(','); }).join('\n');
    var a = document.createElement('a');
    a.href = URL.createObjectURL(new Blob([csv], { type: 'text/csv;charset=utf-8' }));
    a.download = name;
    document.body.appendChild(a); a.click(); a.remove();
  }
  function empty(text) { return '<p class="empty">' + esc(text) + '</p>'; }

  /* capacity in technician-minutes between two dates */
  function capacity(f, t, loc) {
    var total = 0, techs = S.technicians || [];
    for (var d = f; d <= t; d = N.addDays(d, 1)) {
      (S.locations || []).forEach(function (l) {
        if (loc && l.id !== loc) return;
        var h = N.hoursOn(l.id, d); if (!h) return;
        var w = N.weekday(d);
        var n = techs.length ? techs.filter(function (x) { return x.locations.indexOf(l.id) >= 0 && (x.off_days || []).indexOf(w) < 0; }).length : 2;
        total += (h[1] - h[0]) * n;
      });
    }
    return total;
  }
  function metrics(list, f, t) {
    var inP = list.filter(function (a) { return inRange(a, f, t); });
    var done = inP.filter(function (a) { return a.status === 'done'; });
    var lost = inP.filter(function (a) { return a.status === 'cancelled' || a.status === 'no_show'; });
    var booked = inP.filter(N.busy);
    var rev = sum(done, net);
    return {
      list: inP, done: done, revenue: rev, visits: done.length, booked: booked.length, avg: done.length ? rev / done.length : 0,
      lostRate: pct(lost.length, inP.length), occupancy: pct(sum(booked, function (a) { return a.end - a.start; }), capacity(f, t))
    };
  }

  /* ------------------------------------------------------------------ period picker */
  var PERIODS = [['today', 'Hôm nay'], ['7', '7 ngày'], ['30', '30 ngày'], ['month', 'Tháng này'], ['90', '90 ngày']];
  function period() {
    var k = N.get('adm:period', '30'), t = N.today(), f, pf, pt, days;
    if (k === 'today') { f = t; pf = pt = N.addDays(t, -1); }
    else if (k === 'month') {
      f = t.slice(0, 8) + '01'; days = N.dayDiff(f, t) + 1;
      var pm = N.parse(f); pm.setMonth(pm.getMonth() - 1); pf = N.iso(pm); pt = N.addDays(pf, days - 1);
    } else {
      days = +k; f = N.addDays(t, -(days - 1)); pt = N.addDays(f, -1); pf = N.addDays(pt, -(days - 1));
    }
    var label = (PERIODS.filter(function (p) { return p[0] === k; })[0] || [0, ''])[1];
    return { key: k, from: f, to: t, pfrom: pf, pto: pt, label: label };
  }
  function periodControl(onChange) {
    $$('[data-period]').forEach(function (box) {
      var cur = N.get('adm:period', '30');
      box.innerHTML = '<div class="seg" role="group" aria-label="Khoảng thời gian">' + PERIODS.map(function (p) {
        return '<button type="button" data-p="' + p[0] + '" aria-pressed="' + (p[0] === cur) + '">' + p[1] + '</button>';
      }).join('') + '</div>';
      box.addEventListener('click', function (e) {
        var b = e.target.closest('[data-p]'); if (!b) return;
        N.set('adm:period', b.getAttribute('data-p'));
        $$('[data-p]', box).forEach(function (x) { x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); });
        onChange();
      });
    });
  }
  function delta(cur, prev, invert) {
    if (!prev) return '<span class="delta flat">Kỳ trước chưa có</span>';
    var d = Math.round((cur - prev) / prev * 1000) / 10;
    var up = d >= 0, good = invert ? !up : up;
    return '<span class="delta ' + (d === 0 ? 'flat' : good ? 'up' : 'down') + '">' + (up ? '+' : '') + pctText(d) + ' so với kỳ trước</span>';
  }

  /* ------------------------------------------------------------------ charts (inline SVG) */
  function lineChart(box, labels, a, b, fmt) {
    var W = 800, H = 260, pl = 54, pr = 12, pt = 14, pb = 30;
    var max = Math.max.apply(null, a.concat(b || [], [1]));
    var step = Math.pow(10, Math.floor(Math.log10(max))), top = Math.ceil(max / step) * step;
    var x = function (i) { return pl + (labels.length < 2 ? 0 : i * (W - pl - pr) / (labels.length - 1)); };
    var y = function (v) { return pt + (H - pt - pb) * (1 - v / top); };
    var path = function (s) { return s.map(function (v, i) { return (i ? 'L' : 'M') + x(i).toFixed(1) + ',' + y(v).toFixed(1); }).join(''); };
    var g = '';
    for (var k = 0; k <= 4; k++) { var v = top * k / 4; g += '<line x1="' + pl + '" x2="' + (W - pr) + '" y1="' + y(v) + '" y2="' + y(v) + '" class="grid"/><text x="' + (pl - 8) + '" y="' + (y(v) + 4) + '" text-anchor="end">' + short(v) + '</text>'; }
    var every = Math.max(1, Math.ceil(labels.length / 8));
    labels.forEach(function (l, i) { var last = i === labels.length - 1; if ((i % every === 0 && (last || labels.length - 1 - i >= every / 2)) || last) g += '<text x="' + x(i) + '" y="' + (H - 8) + '" text-anchor="middle">' + esc(l) + '</text>'; });
    var hits = labels.map(function (l, i) {
      var w = (W - pl - pr) / Math.max(1, labels.length - 1);
      return '<rect x="' + (x(i) - w / 2) + '" y="' + pt + '" width="' + w + '" height="' + (H - pt - pb) + '" class="hit"><title>' + esc(l) + ': ' + fmt(a[i]) + (b ? ' (kỳ trước ' + fmt(b[i] || 0) + ')' : '') + '</title></rect>';
    }).join('');
    box.innerHTML = '<svg viewBox="0 0 ' + W + ' ' + H + '" class="svg-chart" role="img" aria-label="Biểu đồ">' + g +
      (b ? '<path d="' + path(b) + '" class="s2"/>' : '') + '<path d="' + path(a) + '" class="s1"/>' + hits + '</svg>';
  }
  function barList(box, rows, fmt) {
    if (!rows.length) { box.innerHTML = empty('Chưa có dữ liệu trong kỳ.'); return; }
    var max = Math.max.apply(null, rows.map(function (r) { return r[1]; }).concat([1]));
    box.innerHTML = '<ul class="bars">' + rows.map(function (r) {
      return '<li><div class="bar-top"><span>' + esc(r[0]) + '</span><b>' + fmt(r[1]) + (r[2] ? '<small>' + esc(r[2]) + '</small>' : '') + '</b></div><span class="bar"><i style="width:' + (r[1] / max * 100).toFixed(1) + '%"></i></span></li>';
    }).join('') + '</ul>';
  }

  /* ------------------------------------------------------------------ shell */
  $('[data-staff-name]').textContent = staff.name;
  $('[data-staff-role]').textContent = staff.role || '';
  $('[data-staff-initial]').textContent = (staff.name || 'Q').charAt(0);
  $('[data-logout]').addEventListener('click', function () { N.set('adm:staff', null); location.href = 'login.html'; });
  var side = $('[data-side]'), scrim = $('[data-side-close]');
  $('[data-side-open]').addEventListener('click', function () { side.classList.add('open'); scrim.hidden = false; });
  scrim.addEventListener('click', function () { side.classList.remove('open'); scrim.hidden = true; });
  function badges() {
    var t = N.today();
    var pend = N.all().filter(function (a) { return a.status === 'pending' && a.date >= t; }).length;
    $$('[data-badge=pending]').forEach(function (b) { b.textContent = pend; b.hidden = !pend; });
  }
  badges();
  document.addEventListener('nail:change', badges);
  var qInput = $('#q'); if (qInput && Q.get('q')) qInput.value = Q.get('q');

  /* new appointment (walk-in, phone, Zalo) */
  var modal = $('[data-new-modal]'), nf = $('[data-new-form]');
  function fillTechs() {
    var sel = $('[data-new-tech]');
    var ids = $$('option:checked', nf.elements.namedItem('svc')).map(function (o) { return o.value; });
    var cur = sel.value;
    sel.innerHTML = '<option value="">Chưa xếp thợ</option>' + N.techsFor(nf.elements.namedItem('loc').value, ids).map(function (t) { return '<option value="' + t.id + '">' + esc(t.name) + '</option>'; }).join('');
    sel.value = cur;
  }
  function openNew(preset) {
    preset = preset || {};
    nf.reset();
    var now = N.nowMin(), step = (S.booking.slot_minutes || 15);
    nf.elements.namedItem('date').value = preset.date || N.today();
    nf.elements.namedItem('time').value = N.hm(preset.time != null ? preset.time : Math.min(1260, Math.ceil(now / step) * step));
    if (preset.loc) nf.elements.namedItem('loc').value = preset.loc;
    fillTechs();
    if (preset.tech) $('[data-new-tech]').value = preset.tech;
    $('[data-new-err]').hidden = true;
    modal.showModal();
  }
  $$('[data-new-appt]').forEach(function (b) { b.addEventListener('click', function () { openNew(window.CAL_PRESET ? window.CAL_PRESET() : {}); }); });
  $$('[data-modal-close]', modal).forEach(function (b) { b.addEventListener('click', function () { modal.close(); }); });
  nf.addEventListener('change', function (e) { if (e.target.name === 'loc' || e.target.name === 'svc') fillTechs(); });
  nf.addEventListener('submit', function (e) {
    e.preventDefault();
    var f = nf.elements, ids = $$('option:checked', f.namedItem('svc')).map(function (o) { return o.value; });
    var err = $('[data-new-err]'), name = f.namedItem('name').value.trim(), phone = f.namedItem('phone').value.replace(/\D/g, '');
    var msg = !name ? 'Nhập tên khách.' : !/^0\d{9,10}$/.test(phone) ? 'Số điện thoại gồm 10 chữ số, bắt đầu bằng 0.' : !ids.length ? 'Chọn ít nhất một dịch vụ.' : !f.namedItem('date').value || !f.namedItem('time').value ? 'Chọn ngày và giờ.' : '';
    if (msg) { err.textContent = msg; err.hidden = false; return; }
    var p = N.priceOf(ids, []), start = N.toMin(f.namedItem('time').value), tech = f.namedItem('tech').value, date = f.namedItem('date').value, loc = f.namedItem('loc').value;
    var clash = tech && N.all().some(function (a) { return a.tech === tech && a.date === date && N.busy(a) && a.start < start + p.minutes && a.end > start; });
    if (clash && !confirm(techName(tech) + ' đã có lịch trùng giờ này. Vẫn lưu?')) return;
    var b = N.book({
      date: date, start: start, end: start + p.minutes, loc: loc, tech: tech,
      services: ids.map(function (id) { var s = N.svc(id); return { id: id, name: s.name, price: s.price || 0, minutes: s.minutes }; }),
      addons: [], total: p.total, discount: 0, source: f.namedItem('source').value, customer: { name: name, phone: phone }, note: f.namedItem('note').value.trim()
    }, { status: 'confirmed', by: staff.name, mine: false });
    modal.close();
    N.toast('Đã thêm lịch hẹn ' + b.code);
    if (window.RERENDER) window.RERENDER();
  });

  /* ------------------------------------------------------------------ pages */
  var pages = {};

  pages.index = function () {
    $('[data-today-label]').textContent = N.dateLabel(N.today(), true);
    function render() {
      var p = period(), all = N.all();
      var m = metrics(all, p.from, p.to), pm = metrics(all, p.pfrom, p.pto);
      var tiles = [
        ['Doanh thu', '<span title="' + vnd(m.revenue) + '">' + money(m.revenue) + '</span>', delta(m.revenue, pm.revenue)],
        ['Lượt khách đã làm', m.visits, delta(m.visits, pm.visits)],
        ['Giá trị trung bình', vnd(m.avg), delta(m.avg, pm.avg)],
        ['Tỷ lệ lấp đầy', pctText(m.occupancy), delta(m.occupancy, pm.occupancy)],
        ['Lịch hẹn', m.booked, delta(m.booked, pm.booked)],
        ['Hủy và không đến', pctText(m.lostRate), delta(m.lostRate, pm.lostRate, true)]
      ];
      $('[data-kpis]').innerHTML = tiles.map(function (t) { return '<div class="kpi"><span>' + t[0] + '</span><b>' + t[1] + '</b>' + t[2] + '</div>'; }).join('');
      // chart: daily revenue, the same number of days before as dashed line
      var f = p.key === 'today' ? N.addDays(p.to, -13) : p.from, n = N.dayDiff(f, p.to) + 1;
      var labels = [], cur = [], prev = [];
      var doneBy = by(all.filter(function (a) { return a.status === 'done'; }), function (a) { return a.date; });
      for (var i = 0; i < n; i++) {
        var d = N.addDays(f, i), dp = N.addDays(f, i - n);
        labels.push(N.dateLabel(d));
        cur.push(sum(doneBy[d] || [], net)); prev.push(sum(doneBy[dp] || [], net));
      }
      $('[data-chart-title]').textContent = 'Doanh thu theo ngày' + (p.key === 'today' ? ' (14 ngày gần nhất)' : '');
      $('[data-legend]').innerHTML = '<span class="lg s1">Kỳ này</span><span class="lg s2">Kỳ trước</span>';
      lineChart($('[data-chart]'), labels, cur, prev, vnd);
      // sources
      var srcs = by(m.list.filter(N.busy), function (a) { return a.source; });
      barList($('[data-sources]'), Object.keys(srcs).map(function (k) { return [N.SOURCE[k] || k, srcs[k].length, pctText(pct(srcs[k].length, m.list.filter(N.busy).length))]; }).sort(function (a, b) { return b[1] - a[1]; }), function (v) { return v + ' lượt'; });
      // services by revenue
      var rev = {};
      m.done.forEach(function (a) { a.services.forEach(function (s) { rev[s.name] = (rev[s.name] || 0) + s.price; }); });
      barList($('[data-top-services]'), Object.keys(rev).map(function (k) { return [k, rev[k]]; }).sort(function (a, b) { return b[1] - a[1]; }).slice(0, 6), vnd);
      // technicians
      var cap = {};
      var techRows = (S.technicians || []).map(function (t) {
        var mine = m.done.filter(function (a) { return a.tech === t.id; });
        return [t.name, sum(mine, net), mine.length + ' lượt'];
      }).sort(function (a, b) { return b[1] - a[1]; });
      barList($('[data-tech-perf]'), techRows, vnd);
      // new and returning
      var custs = N.customers(), firstBy = {};
      custs.forEach(function (c) { firstBy[c.key] = c.first; });
      var newC = {}, retC = {};
      m.done.forEach(function (a) { var k = a.customer.phone || a.customer.name; if (firstBy[k] >= p.from) newC[k] = 1; else retC[k] = 1; });
      var nn = Object.keys(newC).length, rr = Object.keys(retC).length;
      $('[data-returning]').innerHTML = '<div class="split"><div><b>' + nn + '</b><span>Khách mới</span></div><div><b>' + rr + '</b><span>Khách quay lại</span></div></div>' +
        '<span class="bar two"><i style="width:' + pct(nn, nn + rr) + '%"></i></span><p class="muted small">Khách quay lại chiếm ' + pctText(pct(rr, nn + rr)) + ' số khách đã làm trong kỳ.</p>';
      // heatmap
      var heat = {}, maxH = 1, hours = [];
      for (var hh = 8; hh <= 21; hh++) hours.push(hh);
      m.list.filter(N.busy).forEach(function (a) { var k = N.weekday(a.date) + '-' + Math.floor(a.start / 60); heat[k] = (heat[k] || 0) + 1; maxH = Math.max(maxH, heat[k]); });
      $('[data-heat]').innerHTML = '<table><thead><tr><th></th>' + hours.map(function (h) { return '<th>' + h + 'h</th>'; }).join('') + '</tr></thead><tbody>' +
        [1, 2, 3, 4, 5, 6, 7].map(function (w) {
          return '<tr><th>' + N.DAYS_SHORT[w] + '</th>' + hours.map(function (h) { var v = heat[w + '-' + h] || 0; return '<td style="--a:' + (v / maxH).toFixed(2) + '" title="' + N.DAYS[w] + ' ' + h + 'h: ' + v + ' lượt"></td>'; }).join('') + '</tr>';
        }).join('') + '</tbody></table>';
      renderToday();
    }
    function renderToday() {
      var t = N.today(), all = N.all();
      // still to come first, finished ones after
      var todays = all.filter(function (a) { return a.date === t && N.busy(a); }).sort(function (a, b) { return ((a.status === 'done') - (b.status === 'done')) || a.start - b.start; });
      var box = $('[data-today-list]');
      box.innerHTML = todays.length ? '<ul class="tl">' + todays.slice(0, 12).map(function (a) {
        return '<li class="tl-row" data-go="' + a.code + '"><span class="tl-time">' + N.hm(a.start) + '</span><span class="tl-main"><b>' + esc(a.customer.name) + '</b><small>' + esc(svcText(a)) + ' · ' + esc(techName(a.tech)) + '</small></span>' + badge(a.status) + '<span class="tl-act">' + actionBtns(a, true) + '</span></li>';
      }).join('') + '</ul>' + (todays.length > 12 ? '<p class="more-line"><a class="link" href="calendar.html">Còn ' + (todays.length - 12) + ' lịch nữa</a></p>' : '') : empty('Hôm nay chưa có lịch hẹn.');
      var pend = all.filter(function (a) { return a.status === 'pending' && a.date >= t; }).sort(function (a, b) { return (a.date + N.hm(a.start)).localeCompare(b.date + N.hm(b.start)); });
      $('[data-todo]').innerHTML = pend.length ? pend.slice(0, 6).map(function (a) {
        return '<li data-go="' + a.code + '"><span><b>' + esc(a.customer.name) + '</b><small>' + N.dateLabel(a.date) + ' ' + N.hm(a.start) + ' · ' + esc(a.services[0].name) + '</small></span>' + actionBtns(a, true) + '</li>';
      }).join('') + (pend.length > 6 ? '<li class="muted small">Còn ' + (pend.length - 6) + ' lịch chờ xác nhận</li>' : '') : '<li class="muted">Không có lịch chờ xác nhận.</li>';
    }
    $('.main').addEventListener('click', function (e) { var r = e.target.closest('[data-go]'); if (r && !e.target.closest('button')) location.href = 'appointment.html?code=' + r.getAttribute('data-go'); });
    bindActions($('.main'), renderToday);
    periodControl(render);
    window.RERENDER = render;
    render();
  };

  pages.calendar = function () {
    var K = 1.3; // px per minute
    var st = { date: Q.get('date') || N.today(), loc: Q.get('loc') || (S.locations[0] || {}).id };
    var locSel = $('[data-cal-loc]'); if (locSel) { locSel.value = st.loc; locSel.addEventListener('change', function () { st.loc = locSel.value; render(); }); }
    var dateIn = $('[data-cal-date]');
    dateIn.addEventListener('change', function () { if (dateIn.value) { st.date = dateIn.value; render(); } });
    $('[data-cal-prev]').onclick = function () { st.date = N.addDays(st.date, -1); render(); };
    $('[data-cal-next]').onclick = function () { st.date = N.addDays(st.date, 1); render(); };
    $('[data-cal-today]').onclick = function () { st.date = N.today(); render(); };
    window.CAL_PRESET = function () { return { date: st.date, loc: st.loc }; };
    $('[data-cal-legend]').innerHTML = ['pending', 'confirmed', 'arrived', 'done', 'no_show'].map(function (s) { return '<span class="lg-st st-' + s + '">' + N.STATUS[s] + '</span>'; }).join('');
    var panel = $('[data-panel]');
    function openPanel(code) {
      var a = N.find(code); if (!a) return;
      var techs = N.techsFor(a.loc, a.services.map(function (s) { return s.id; }));
      $('[data-panel-body]').innerHTML = '<header class="panel-h"><div><p class="muted small">' + a.code + '</p><h2>' + esc(a.customer.name) + '</h2></div><button class="icon-btn" type="button" data-panel-close aria-label="Đóng">' + N.icon('x') + '</button></header>' +
        '<p>' + badge(a.status) + '</p><dl class="dl"><div><dt>Giờ</dt><dd>' + N.dateLabel(a.date, true) + ', ' + N.hm(a.start) + ' - ' + N.hm(a.end) + '</dd></div><div><dt>Điện thoại</dt><dd><a href="tel:' + a.customer.phone + '">' + esc(a.customer.phone) + '</a></dd></div>' +
        '<div><dt>Dịch vụ</dt><dd>' + esc(svcText(a)) + '</dd></div><div><dt>Tạm tính</dt><dd>' + vnd(net(a)) + '</dd></div>' + (a.note ? '<div><dt>Ghi chú</dt><dd>' + esc(a.note) + '</dd></div>' : '') + '</dl>' +
        '<label class="field"><span>Thợ</span><select data-assign><option value="">Chưa xếp thợ</option>' + techs.map(function (t) { return '<option value="' + t.id + '"' + (t.id === a.tech ? ' selected' : '') + '>' + esc(t.name) + '</option>'; }).join('') + '</select></label>' +
        '<div class="btn-row">' + actionBtns(a) + '</div><a class="link" href="appointment.html?code=' + a.code + '">Mở trang chi tiết</a>';
      panel.hidden = false;
      $('[data-panel-close]', panel).onclick = function () { panel.hidden = true; };
      $('[data-assign]', panel).onchange = function (e) { N.update(a.code, { tech: e.target.value }, staff.name); N.toast('Đã xếp ' + techName(e.target.value) + ' cho ' + a.code); render(); openPanel(a.code); };
    }
    bindActions(panel, function () { render(); openPanel(panel.querySelector('[data-code]') ? panel.querySelector('[data-code]').getAttribute('data-code') : null); });
    function render() {
      dateIn.value = st.date;
      var h = N.hoursOn(st.loc, st.date), cal = $('[data-cal]');
      var list = N.all().filter(function (a) { return a.date === st.date && a.loc === st.loc && a.status !== 'cancelled'; });
      var live = list.filter(N.busy);
      $('[data-cal-sum]').textContent = N.dateLabel(st.date, true) + ': ' + live.length + ' lịch hẹn, ' + live.filter(function (a) { return a.status === 'pending'; }).length + ' chờ xác nhận, dự kiến ' + vnd(sum(live, net));
      if (!h) { cal.innerHTML = empty('Chi nhánh nghỉ ngày này.'); return; }
      var w = N.weekday(st.date);
      var cols = (S.technicians || []).filter(function (t) { return t.locations.indexOf(st.loc) >= 0; }).map(function (t) { return { id: t.id, name: t.name, off: (t.off_days || []).indexOf(w) >= 0 }; });
      if (list.some(function (a) { return !a.tech || !N.TECH[a.tech]; }) || !cols.length) cols.push({ id: '', name: 'Chưa xếp thợ' });
      var open = h[0], close = h[1], height = (close - open) * K;
      var times = '';
      for (var m = open; m <= close; m += 30) times += '<span style="top:' + ((m - open) * K) + 'px">' + N.hm(m) + '</span>';
      var now = N.nowMin(), nowLine = st.date === N.today() && now > open && now < close ? '<i class="now" style="top:' + ((now - open) * K) + 'px"></i>' : '';
      cal.style.setProperty('--cols', cols.length);
      cal.innerHTML = '<div class="cal-head"><span></span>' + cols.map(function (c) {
        var n = list.filter(function (a) { return (a.tech || '') === c.id || (!c.id && !N.TECH[a.tech]); }).filter(N.busy).length;
        return '<b>' + esc(c.name) + (c.off ? ' <small>(nghỉ)</small>' : '') + '<small>' + n + ' lịch</small></b>';
      }).join('') + '</div><div class="cal-body" style="height:' + height + 'px"><div class="cal-times">' + times + '</div>' + cols.map(function (c) {
        var mine = list.filter(function (a) { return c.id ? a.tech === c.id : !N.TECH[a.tech]; });
        return '<div class="cal-col' + (c.off ? ' off' : '') + '" data-col="' + c.id + '">' + mine.map(function (a) {
          var top = (Math.max(a.start, open) - open) * K, hgt = Math.max(28, (a.end - a.start) * K - 3);
          return '<button type="button" class="blk st-' + a.status + '" style="top:' + top + 'px;height:' + hgt + 'px" data-open="' + a.code + '"><b>' + N.hm(a.start) + ' ' + esc(a.customer.name) + '</b><span>' + esc(svcText(a)) + '</span></button>';
        }).join('') + '</div>';
      }).join('') + nowLine + '</div>';
      $$('[data-open]', cal).forEach(function (b) { b.onclick = function () { openPanel(b.getAttribute('data-open')); }; });
      $$('.cal-col', cal).forEach(function (col) {
        col.addEventListener('dblclick', function (e) {
          if (e.target.closest('.blk')) return;
          var r = col.getBoundingClientRect(), step = S.booking.slot_minutes || 15;
          var t = open + Math.floor((e.clientY - r.top) / K / step) * step;
          openNew({ date: st.date, loc: st.loc, tech: col.getAttribute('data-col'), time: t });
        });
      });
    }
    window.RERENDER = render;
    render();
  };

  pages.appointments = function () {
    var PER = 40, pageNo = 1;
    var st = { status: Q.get('status') || '', q: Q.get('q') || '', range: Q.get('q') ? 'all' : (Q.get('range') || (Q.get('status') === 'pending' ? 'upcoming' : 'upcoming')), loc: '', tech: '' };
    $$('[data-f]').forEach(function (i) {
      var k = i.getAttribute('data-f'); i.value = st[k];
      i.addEventListener(i.tagName === 'INPUT' ? 'input' : 'change', function () { st[k] = i.value; if (k === 'q' && i.value) { st.range = 'all'; $('[data-f=range]').value = 'all'; } pageNo = 1; render(); });
    });
    function rows() {
      var t = N.today(), q = N.norm(st.q);
      return N.all().filter(function (a) {
        if (st.loc && a.loc !== st.loc) return false;
        if (st.tech && a.tech !== st.tech) return false;
        if (st.range === 'upcoming' && a.date < t) return false;
        if (st.range === 'today' && a.date !== t) return false;
        if (st.range === 'week' && (a.date < t || a.date > N.addDays(t, 6))) return false;
        if (st.range === 'past30' && (a.date > t || a.date < N.addDays(t, -29))) return false;
        if (q && N.norm(a.code + ' ' + a.customer.name + ' ' + a.customer.phone).indexOf(q) < 0) return false;
        return true;
      });
    }
    var tabs = $('[data-status-tabs]');
    tabs.addEventListener('click', function (e) { var b = e.target.closest('[data-s]'); if (!b) return; st.status = b.getAttribute('data-s'); pageNo = 1; render(); });
    $('[data-csv]').onclick = function () {
      var list = rows().filter(function (a) { return !st.status || a.status === st.status; });
      download('lich-hen.csv', [['Mã', 'Ngày', 'Giờ', 'Khách', 'Điện thoại', 'Dịch vụ', 'Thợ', 'Chi nhánh', 'Tạm tính', 'Nguồn', 'Trạng thái']].concat(list.map(function (a) {
        return [a.code, a.date, N.hm(a.start), a.customer.name, a.customer.phone, svcText(a), techName(a.tech), locName(a.loc), net(a), N.SOURCE[a.source], N.STATUS[a.status]];
      })));
    };
    function render() {
      var base = rows(), counts = by(base, function (a) { return a.status; });
      tabs.innerHTML = [['', 'Tất cả', base.length]].concat((S.statuses || []).map(function (s) { return [s[0], s[1], (counts[s[0]] || []).length]; })).map(function (x) {
        return '<button type="button" role="tab" data-s="' + x[0] + '" aria-selected="' + (st.status === x[0]) + '">' + x[1] + '<small>' + x[2] + '</small></button>';
      }).join('');
      var list = base.filter(function (a) { return !st.status || a.status === st.status; });
      var asc = st.range === 'upcoming' || st.range === 'today' || st.range === 'week';
      list.sort(function (a, b) { var x = (a.date + N.hm(a.start)).localeCompare(b.date + N.hm(b.start)); return asc ? x : -x; });
      $('[data-list-sum]').textContent = list.length + ' lịch hẹn';
      var pages = Math.max(1, Math.ceil(list.length / PER)); pageNo = Math.min(pageNo, pages);
      var slice = list.slice((pageNo - 1) * PER, pageNo * PER);
      $('[data-table]').innerHTML = slice.length ? '<table class="tbl"><thead><tr><th>Mã</th><th>Ngày giờ</th><th>Khách</th><th>Dịch vụ</th><th>Thợ</th>' + (S.locations.length > 1 ? '<th>Chi nhánh</th>' : '') + '<th class="num">Tạm tính</th><th>Trạng thái</th><th><span class="sr">Thao tác</span></th></tr></thead><tbody>' +
        slice.map(function (a) {
          return '<tr data-go="' + a.code + '"><td data-label="Mã"><a class="link" href="appointment.html?code=' + a.code + '">' + a.code + '</a></td><td data-label="Ngày giờ">' + N.dateLabel(a.date) + ' ' + N.hm(a.start) + '</td>' +
            '<td data-label="Khách"><b>' + esc(a.customer.name) + '</b><small>' + esc(a.customer.phone) + '</small></td><td data-label="Dịch vụ" class="clip">' + esc(svcText(a)) + '</td><td data-label="Thợ">' + esc(techName(a.tech)) + '</td>' +
            (S.locations.length > 1 ? '<td data-label="Chi nhánh">' + esc(locName(a.loc)) + '</td>' : '') + '<td data-label="Tạm tính" class="num">' + vnd(net(a)) + '</td><td data-label="Trạng thái">' + badge(a.status) + '</td><td class="act">' + actionBtns(a, true) + '</td></tr>';
        }).join('') + '</tbody></table>' : empty('Không có lịch hẹn khớp bộ lọc.');
      var pg = $('[data-pager]');
      pg.innerHTML = pages > 1 ? '<button class="btn btn-ghost btn-sm" type="button" data-pg="-1"' + (pageNo === 1 ? ' disabled' : '') + '>Trước</button><span>Trang ' + pageNo + ' / ' + pages + '</span><button class="btn btn-ghost btn-sm" type="button" data-pg="1"' + (pageNo === pages ? ' disabled' : '') + '>Sau</button>' : '';
    }
    $('[data-pager]').addEventListener('click', function (e) { var b = e.target.closest('[data-pg]'); if (!b) return; pageNo += +b.getAttribute('data-pg'); render(); window.scrollTo({ top: 0 }); });
    $('[data-table]').addEventListener('click', function (e) { var r = e.target.closest('[data-go]'); if (r && !e.target.closest('button,a')) location.href = 'appointment.html?code=' + r.getAttribute('data-go'); });
    bindActions($('[data-table]'), render);
    window.RERENDER = render;
    render();
  };

  pages.appointment = function () {
    var box = $('[data-appt]');
    function render() {
      var a = N.find(Q.get('code'));
      if (!a) { box.innerHTML = empty('Không tìm thấy lịch hẹn này.'); return; }
      var techs = N.techsFor(a.loc, a.services.map(function (s) { return s.id; }));
      var notes = N.get('adm:notes', {});
      var cust = N.customers().filter(function (c) { return c.key === (a.customer.phone || a.customer.name); })[0] || { visits: 0, spent: 0 };
      var hist = (a.history || []).slice();
      if (a.seed && !hist.length) hist = [[N.parse(a.created).getTime() + 9 * 3600000, a.status === 'pending' ? 'pending' : 'confirmed', N.SOURCE[a.source] || '']];
      box.innerHTML = '<div class="page-top"><div><h1>' + a.code + ' ' + badge(a.status) + '</h1><p class="muted">' + N.dateLabel(a.date, true) + ', ' + N.hm(a.start) + ' - ' + N.hm(a.end) + ' · ' + esc(locName(a.loc)) + '</p></div><div class="btn-row">' + actionBtns(a) + '</div></div>' +
        '<div class="grid-main"><section class="card span2"><header class="card-h"><h2>Dịch vụ</h2></header><table class="tbl lines"><tbody>' +
        a.services.map(function (s) { return '<tr><td>' + esc(s.name) + '<small>' + N.mins(s.minutes) + '</small></td><td class="num">' + vnd(s.price) + '</td></tr>'; }).join('') +
        (a.addons || []).map(function (x) { return '<tr><td>' + esc(x.name) + (x.qty > 1 ? ' x' + x.qty : '') + '</td><td class="num">' + vnd(x.price * (x.qty || 1)) + '</td></tr>'; }).join('') +
        (a.discount ? '<tr><td>Mã ' + esc(a.promo || '') + '</td><td class="num">-' + vnd(a.discount) + '</td></tr>' : '') +
        '<tr class="total"><td>Tạm tính</td><td class="num">' + vnd(net(a)) + '</td></tr></tbody></table>' +
        '<div class="grid2 mt"><label class="field"><span>Thợ</span><select data-assign><option value="">Chưa xếp thợ</option>' + techs.map(function (t) { return '<option value="' + t.id + '"' + (t.id === a.tech ? ' selected' : '') + '>' + esc(t.name) + '</option>'; }).join('') + '</select></label>' +
        '<label class="field"><span>Thanh toán</span><select data-pay' + (a.status === 'done' ? '' : ' disabled') + '>' + (S.payments || []).map(function (p) { return '<option value="' + p[0] + '"' + (a.pay === p[0] ? ' selected' : '') + '>' + p[1] + '</option>'; }).join('') + '</select></label></div>' +
        (a.note ? '<p class="note"><b>Khách ghi chú:</b> ' + esc(a.note) + '</p>' : '') + (a.photo ? '<p class="note"><b>Ảnh mẫu:</b> ' + esc(a.photo) + '</p>' : '') +
        '</section><section class="card"><header class="card-h"><h2>Khách</h2><a class="link" href="customer.html?key=' + encodeURIComponent(a.customer.phone || a.customer.name) + '">Hồ sơ</a></header>' +
        '<p><b>' + esc(a.customer.name) + '</b></p><p><a class="link" href="tel:' + esc(a.customer.phone) + '">' + esc(a.customer.phone) + '</a></p>' +
        '<dl class="dl"><div><dt>Đã làm</dt><dd>' + cust.visits + ' lần</dd></div><div><dt>Đã chi</dt><dd>' + vnd(cust.spent) + '</dd></div><div><dt>Nguồn</dt><dd>' + esc(N.SOURCE[a.source] || '') + '</dd></div></dl>' +
        '<label class="field"><span>Ghi chú nội bộ</span><textarea rows="3" data-note placeholder="Chỉ nhân viên thấy">' + esc(notes[a.code] || '') + '</textarea></label></section>' +
        '<section class="card span3"><header class="card-h"><h2>Lịch sử</h2></header><ol class="timeline">' + hist.map(function (h) {
          var d = new Date(h[0]);
          return '<li><b>' + esc(N.STATUS[h[1]] || h[1]) + '</b><span>' + N.dateLabel(N.iso(d)) + ' ' + N.hm(d.getHours() * 60 + d.getMinutes()) + (h[2] ? ' · ' + esc(h[2]) : '') + '</span></li>';
        }).join('') + '</ol></section></div>';
      $('[data-assign]', box).onchange = function (e) { N.update(a.code, { tech: e.target.value }, staff.name); N.toast('Đã xếp thợ ' + techName(e.target.value)); };
      $('[data-pay]', box).onchange = function (e) { N.update(a.code, { pay: e.target.value }, staff.name); N.toast('Đã lưu cách thanh toán'); };
      $('[data-note]', box).onchange = function (e) { var o = N.get('adm:notes', {}); o[a.code] = e.target.value; N.set('adm:notes', o); N.toast('Đã lưu ghi chú'); };
    }
    bindActions(box, render);
    window.RERENDER = render;
    render();
  };

  pages.customers = function () {
    var PER = 50, pageNo = 1, seg = '', q = '';
    var t = N.today();
    var SEGS = [['', 'Tất cả'], ['new', 'Khách mới 30 ngày'], ['loyal', 'Khách quen (từ 3 lần)'], ['lapsed', 'Hơn 60 ngày chưa quay lại'], ['risky', 'Hay hủy hoặc không đến']];
    function test(c, s) {
      if (s === 'new') return c.first >= N.addDays(t, -29);
      if (s === 'loyal') return c.visits >= 3;
      if (s === 'lapsed') return c.last && c.last < N.addDays(t, -60) && !c.next;
      if (s === 'risky') return c.noShow + c.cancelled >= 2;
      return true;
    }
    var all = N.customers().sort(function (a, b) { return (b.last || b.first).localeCompare(a.last || a.first); });
    $('[data-c-q]').addEventListener('input', function (e) { q = N.norm(e.target.value); pageNo = 1; render(); });
    $('[data-seg-tabs]').addEventListener('click', function (e) { var b = e.target.closest('[data-seg]'); if (!b) return; seg = b.getAttribute('data-seg'); pageNo = 1; render(); });
    function list() { return all.filter(function (c) { return test(c, seg) && (!q || N.norm(c.name + ' ' + c.phone).indexOf(q) >= 0); }); }
    $('[data-csv]').onclick = function () {
      download('khach-hang.csv', [['Tên', 'Điện thoại', 'Số lần làm', 'Đã chi', 'Lần đầu', 'Lần gần nhất', 'Lịch sắp tới', 'Ghi chú']].concat(list().map(function (c) { return [c.name, c.phone, c.visits, c.spent, c.first, c.last, c.next, c.note]; })));
    };
    function fav(c) { var k = Object.keys(c.techs).sort(function (a, b) { return c.techs[b] - c.techs[a]; })[0]; return k ? techName(k) : ''; }
    function render() {
      $('[data-seg-tabs]').innerHTML = SEGS.map(function (s) { return '<button type="button" role="tab" data-seg="' + s[0] + '" aria-selected="' + (seg === s[0]) + '">' + s[1] + '<small>' + all.filter(function (c) { return test(c, s[0]); }).length + '</small></button>'; }).join('');
      var l = list();
      $('[data-cust-sum]').textContent = l.length + ' khách';
      var pages = Math.max(1, Math.ceil(l.length / PER)); pageNo = Math.min(pageNo, pages);
      $('[data-table]').innerHTML = l.length ? '<table class="tbl"><thead><tr><th>Khách</th><th class="num">Số lần làm</th><th class="num">Đã chi</th><th>Lần gần nhất</th><th>Lịch sắp tới</th><th>Thợ quen</th><th>Ghi chú</th></tr></thead><tbody>' +
        l.slice((pageNo - 1) * PER, pageNo * PER).map(function (c) {
          return '<tr data-go="' + esc(c.key) + '"><td data-label="Khách"><a class="link" href="customer.html?key=' + encodeURIComponent(c.key) + '">' + esc(c.name) + '</a><small>' + esc(c.phone) + '</small></td><td data-label="Số lần làm" class="num">' + c.visits + '</td><td data-label="Đã chi" class="num">' + vnd(c.spent) + '</td>' +
            '<td data-label="Lần gần nhất">' + (c.last ? N.dateLabel(c.last) + '/' + c.last.slice(0, 4) : 'Chưa làm') + '</td><td data-label="Lịch sắp tới">' + (c.next ? N.dateLabel(c.next) : '') + '</td><td data-label="Thợ quen">' + esc(fav(c)) + '</td><td data-label="Ghi chú" class="clip">' + esc(c.note) + '</td></tr>';
        }).join('') + '</tbody></table>' : empty('Không có khách khớp bộ lọc.');
      $('[data-pager]').innerHTML = pages > 1 ? '<button class="btn btn-ghost btn-sm" type="button" data-pg="-1"' + (pageNo === 1 ? ' disabled' : '') + '>Trước</button><span>Trang ' + pageNo + ' / ' + pages + '</span><button class="btn btn-ghost btn-sm" type="button" data-pg="1"' + (pageNo === pages ? ' disabled' : '') + '>Sau</button>' : '';
    }
    $('[data-pager]').addEventListener('click', function (e) { var b = e.target.closest('[data-pg]'); if (!b) return; pageNo += +b.getAttribute('data-pg'); render(); window.scrollTo({ top: 0 }); });
    $('[data-table]').addEventListener('click', function (e) { var r = e.target.closest('[data-go]'); if (r && !e.target.closest('a')) location.href = 'customer.html?key=' + encodeURIComponent(r.getAttribute('data-go')); });
    window.RERENDER = function () { all = N.customers(); render(); };
    render();
  };

  pages.customer = function () {
    var key = Q.get('key'), box = $('[data-customer]');
    function render() {
      var c = N.customers().filter(function (x) { return x.key === key; })[0];
      if (!c) { box.innerHTML = empty('Không tìm thấy khách này.'); return; }
      var hist = N.all().filter(function (a) { return (a.customer.phone || a.customer.name) === key; }).sort(function (a, b) { return (b.date + N.hm(b.start)).localeCompare(a.date + N.hm(a.start)); });
      box.innerHTML = '<div class="page-top"><div><h1>' + esc(c.name) + '</h1><p class="muted"><a class="link" href="tel:' + esc(c.phone) + '">' + esc(c.phone) + '</a> · Khách từ ' + N.dateLabel(c.first) + '/' + c.first.slice(0, 4) + '</p></div><button class="btn btn-sm" type="button" data-book-again>' + N.icon('plus', 'i-sm') + 'Đặt lịch cho khách</button></div>' +
        '<section class="kpis small">' + [['Đã làm', c.visits + ' lần'], ['Đã chi', vnd(c.spent)], ['Trung bình mỗi lần', vnd(c.visits ? c.spent / c.visits : 0)], ['Hủy hoặc không đến', c.cancelled + c.noShow + ' lần']].map(function (k) { return '<div class="kpi"><span>' + k[0] + '</span><b>' + k[1] + '</b></div>'; }).join('') + '</section>' +
        '<div class="grid-main"><section class="card span2 flush"><header class="card-h pad"><h2>Lịch hẹn</h2></header><div class="table-wrap"><table class="tbl"><thead><tr><th>Mã</th><th>Ngày giờ</th><th>Dịch vụ</th><th>Thợ</th><th class="num">Tạm tính</th><th>Trạng thái</th></tr></thead><tbody>' +
        hist.map(function (a) { return '<tr><td data-label="Mã"><a class="link" href="appointment.html?code=' + a.code + '">' + a.code + '</a></td><td data-label="Ngày giờ">' + N.dateLabel(a.date) + '/' + a.date.slice(0, 4) + ' ' + N.hm(a.start) + '</td><td data-label="Dịch vụ" class="clip">' + esc(svcText(a)) + '</td><td data-label="Thợ">' + esc(techName(a.tech)) + '</td><td data-label="Tạm tính" class="num">' + vnd(net(a)) + '</td><td data-label="Trạng thái">' + badge(a.status) + '</td></tr>'; }).join('') +
        '</tbody></table></div></section><section class="card"><header class="card-h"><h2>Ghi chú về khách</h2></header><label class="field"><span class="sr">Ghi chú</span><textarea rows="5" data-cnote placeholder="Dị ứng, form móng hay làm, màu yêu thích">' + esc(c.note) + '</textarea></label><p class="muted small">Thợ xem ghi chú này trước khi làm.</p></section></div>';
      $('[data-cnote]', box).onchange = function (e) { var o = N.get('adm:cnotes', {}); o[key] = e.target.value; N.set('adm:cnotes', o); N.toast('Đã lưu ghi chú'); };
      $('[data-book-again]', box).onclick = function () { openNew({}); nf.elements.namedItem('name').value = c.name; nf.elements.namedItem('phone').value = c.phone; };
    }
    window.RERENDER = render;
    render();
  };

  pages.services = function () {
    var box = $('[data-services]');
    function render() {
      var t = N.today(), f = N.addDays(t, -29);
      var done = N.all().filter(function (a) { return a.status === 'done' && inRange(a, f, t); });
      var cnt = {}, rev = {};
      done.forEach(function (a) { a.services.forEach(function (s) { cnt[s.id] = (cnt[s.id] || 0) + 1; rev[s.id] = (rev[s.id] || 0) + s.price; }); });
      box.innerHTML = (S.categories || []).map(function (c) {
        var items = (S.services || []).filter(function (s) { return s.category === c.id; });
        return '<section class="card flush mb"><header class="card-h pad"><h2>' + esc(c.name) + '</h2><span class="muted small">' + items.length + ' dịch vụ</span></header><div class="table-wrap"><table class="tbl"><thead><tr><th>Dịch vụ</th><th>Thời lượng (phút)</th><th>Giá (đ)</th><th>Hiện trên web</th><th class="num">Lượt 30 ngày</th><th class="num">Doanh thu 30 ngày</th></tr></thead><tbody>' +
          items.map(function (s0) {
            var s = N.svc(s0.id);
            return '<tr><td data-label="Dịch vụ"><b>' + esc(s.name) + '</b>' + (s.price_type === 'from' ? '<small>Giá từ</small>' : '') + '</td><td data-label="Thời lượng"><input class="cell-in" type="number" min="5" max="480" step="5" value="' + s.minutes + '" data-edit="minutes" data-id="' + s.id + '" aria-label="Thời lượng ' + esc(s.name) + '"></td>' +
              '<td data-label="Giá"><input class="cell-in" type="number" min="0" step="1000" value="' + (s.price == null ? '' : s.price) + '" data-edit="price" data-id="' + s.id + '" aria-label="Giá ' + esc(s.name) + '"></td>' +
              '<td data-label="Hiện trên web"><label class="switch"><input type="checkbox" data-edit="hidden" data-id="' + s.id + '"' + (s.hidden ? '' : ' checked') + '><span class="sr">Hiện ' + esc(s.name) + '</span><i></i></label></td>' +
              '<td data-label="Lượt 30 ngày" class="num">' + (cnt[s.id] || 0) + '</td><td data-label="Doanh thu 30 ngày" class="num">' + vnd(rev[s.id] || 0) + '</td></tr>';
          }).join('') + '</tbody></table></div></section>';
      }).join('');
    }
    box.addEventListener('change', function (e) {
      var i = e.target.closest('[data-edit]'); if (!i) return;
      var o = N.get('adm:svc', {}), id = i.getAttribute('data-id'), k = i.getAttribute('data-edit');
      o[id] = o[id] || {};
      if (k === 'hidden') o[id].hidden = !i.checked;
      else { var v = parseInt(i.value, 10); if (isNaN(v) || v < 0) { N.toast('Nhập một số hợp lệ', { bad: true }); return; } o[id][k] = v; }
      N.set('adm:svc', o);
      N.toast('Đã lưu ' + N.SVC[id].name);
    });
    render();
  };

  pages.staff = function () {
    var box = $('[data-staff]');
    function render() {
      var p = period(), all = N.all(), t = N.today(), rate = N.get('adm:settings', {}).commission;
      if (!(S.technicians || []).length) { box.innerHTML = empty('Salon.json chưa có danh sách thợ.'); return; }
      box.innerHTML = S.technicians.map(function (tc) {
        var mine = all.filter(function (a) { return a.tech === tc.id; });
        var inP = mine.filter(function (a) { return inRange(a, p.from, p.to); });
        var done = inP.filter(function (a) { return a.status === 'done'; }), rev = sum(done, net);
        var cap = 0;
        for (var d = p.from; d <= p.to; d = N.addDays(d, 1)) {
          if ((tc.off_days || []).indexOf(N.weekday(d)) >= 0) continue;
          tc.locations.forEach(function (l) { var h = N.hoursOn(l, d); if (h) cap += h[1] - h[0]; });
        }
        var busyMin = sum(inP.filter(N.busy), function (a) { return a.end - a.start; });
        var today = mine.filter(function (a) { return a.date === t && N.busy(a); }).sort(function (a, b) { return a.start - b.start; });
        var next = today.filter(function (a) { return a.end > N.nowMin(); })[0];
        var top = {}; done.forEach(function (a) { a.services.forEach(function (s) { top[s.name] = (top[s.name] || 0) + 1; }); });
        var topName = Object.keys(top).sort(function (a, b) { return top[b] - top[a]; })[0];
        return '<article class="card staff"><header class="staff-h"><span class="avatar lg">' + esc(tc.name.charAt(0)) + '</span><div><h2>' + esc(tc.name) + '</h2><p class="muted small">' + esc(tc.title || '') + ' · ' + tc.locations.map(locName).join(', ') + '</p></div></header>' +
          '<p class="staff-today">' + N.icon('calendar', 'i-sm') + '<span>Hôm nay ' + today.length + ' lịch' + (next ? ', tiếp theo ' + N.hm(next.start) + ' ' + esc(next.customer.name) : '') + '</span></p>' +
          '<dl class="dl"><div><dt>Doanh thu ' + p.label.toLowerCase() + '</dt><dd>' + vnd(rev) + '</dd></div><div><dt>Lượt khách</dt><dd>' + done.length + '</dd></div><div><dt>Tỷ lệ lấp đầy</dt><dd>' + pctText(pct(busyMin, cap)) + '</dd></div>' +
          '<div><dt>Hoa hồng</dt><dd>' + (rate != null ? vnd(rev * rate / 100) + ' (' + rate + '%)' : '<a class="link" href="settings.html">Đặt tỷ lệ</a>') + '</dd></div>' + (topName ? '<div><dt>Làm nhiều nhất</dt><dd>' + esc(topName) + '</dd></div>' : '') + '</dl>' +
          '<a class="link" href="calendar.html?loc=' + tc.locations[0] + '">Xem lịch</a></article>';
      }).join('');
    }
    periodControl(render);
    window.RERENDER = render;
    render();
  };

  pages.reports = function () {
    var dayRows = [];
    function render() {
      var p = period(), all = N.all(), m = metrics(all, p.from, p.to), rate = N.get('adm:settings', {}).commission;
      var cat = {};
      m.done.forEach(function (a) { a.services.forEach(function (s) { var c = (N.SVC[s.id] || {}).category; cat[c] = (cat[c] || 0) + s.price; }); });
      var catName = {}; (S.categories || []).forEach(function (c) { catName[c.id] = c.name; });
      var totalCat = sum(Object.keys(cat), function (k) { return cat[k]; });
      barList($('[data-by-cat]'), Object.keys(cat).map(function (k) { return [catName[k] || 'Khác', cat[k], pctText(pct(cat[k], totalCat))]; }).sort(function (a, b) { return b[1] - a[1]; }), vnd);
      var pay = by(m.done, function (a) { return a.pay || 'cash'; });
      barList($('[data-by-pay]'), Object.keys(pay).map(function (k) { return [N.PAY[k] || k, sum(pay[k], net), pay[k].length + ' lượt']; }).sort(function (a, b) { return b[1] - a[1]; }), vnd);
      $('[data-by-tech]').innerHTML = '<table class="tbl"><thead><tr><th>Thợ</th><th class="num">Lượt làm</th><th class="num">Doanh thu</th><th class="num">Trung bình</th><th class="num">Hủy, không đến</th>' + (rate != null ? '<th class="num">Hoa hồng ' + rate + '%</th>' : '') + '</tr></thead><tbody>' +
        (S.technicians || []).map(function (t) {
          var l = m.list.filter(function (a) { return a.tech === t.id; }), d = l.filter(function (a) { return a.status === 'done'; }), r = sum(d, net);
          var lost = l.filter(function (a) { return a.status === 'cancelled' || a.status === 'no_show'; }).length;
          return '<tr><td data-label="Thợ"><b>' + esc(t.name) + '</b></td><td data-label="Lượt làm" class="num">' + d.length + '</td><td data-label="Doanh thu" class="num">' + vnd(r) + '</td><td data-label="Trung bình" class="num">' + vnd(d.length ? r / d.length : 0) + '</td><td data-label="Hủy, không đến" class="num">' + lost + '</td>' + (rate != null ? '<td data-label="Hoa hồng" class="num">' + vnd(r * rate / 100) + '</td>' : '') + '</tr>';
        }).join('') + '</tbody></table>';
      var byDay = by(m.list, function (a) { return a.date; });
      dayRows = [];
      for (var d = p.to; d >= p.from; d = N.addDays(d, -1)) {
        var l = byDay[d] || [], done = l.filter(function (a) { return a.status === 'done'; });
        dayRows.push([d, l.length, done.length, l.filter(function (a) { return a.status === 'cancelled' || a.status === 'no_show'; }).length, sum(done, net)]);
      }
      $('[data-by-day]').innerHTML = '<table class="tbl"><thead><tr><th>Ngày</th><th class="num">Lịch hẹn</th><th class="num">Hoàn thành</th><th class="num">Hủy, không đến</th><th class="num">Doanh thu</th></tr></thead><tbody>' +
        dayRows.map(function (r) { return '<tr><td data-label="Ngày">' + N.DAYS_SHORT[N.weekday(r[0])] + ' ' + N.dateLabel(r[0]) + '</td><td data-label="Lịch hẹn" class="num">' + r[1] + '</td><td data-label="Hoàn thành" class="num">' + r[2] + '</td><td data-label="Hủy, không đến" class="num">' + r[3] + '</td><td data-label="Doanh thu" class="num">' + vnd(r[4]) + '</td></tr>'; }).join('') +
        '<tr class="total"><td>Cộng</td><td class="num">' + sum(dayRows, function (r) { return r[1]; }) + '</td><td class="num">' + sum(dayRows, function (r) { return r[2]; }) + '</td><td class="num">' + sum(dayRows, function (r) { return r[3]; }) + '</td><td class="num">' + vnd(sum(dayRows, function (r) { return r[4]; })) + '</td></tr></tbody></table>';
    }
    $('[data-csv]').onclick = function () { download('doanh-thu-theo-ngay.csv', [['Ngày', 'Lịch hẹn', 'Hoàn thành', 'Hủy, không đến', 'Doanh thu']].concat(dayRows)); };
    periodControl(render);
    window.RERENDER = render;
    render();
  };

  pages.settings = function () {
    var cf = $('[data-commission]'), set0 = N.get('adm:settings', {});
    if (set0.commission != null) cf.elements.namedItem('rate').value = set0.commission;
    cf.addEventListener('submit', function (e) {
      e.preventDefault();
      var v = parseInt(cf.elements.namedItem('rate').value, 10), s = N.get('adm:settings', {});
      if (isNaN(v)) delete s.commission; else s.commission = Math.max(0, Math.min(80, v));
      N.set('adm:settings', s); N.toast('Đã lưu tỷ lệ hoa hồng');
    });
    var pf = $('[data-password]');
    pf.addEventListener('submit', function (e) {
      e.preventDefault();
      var v = pf.elements.namedItem('pw').value;
      if (v.length < 4) { N.toast('Mật khẩu từ 4 ký tự', { bad: true }); return; }
      N.set('adm:pw', v); pf.reset(); N.toast('Đã đổi mật khẩu');
    });
    $('[data-reset]').addEventListener('click', function () {
      if (!confirm('Xóa lịch đặt thử, trạng thái đã đổi, ghi chú và giá đã sửa trên trình duyệt này?')) return;
      ['bookings', 'mine', 'adm:ov', 'adm:notes', 'adm:cnotes', 'adm:svc'].forEach(function (k) { N.set(k, k === 'bookings' || k === 'mine' ? [] : {}); });
      N.toast('Đã xóa dữ liệu thử');
    });
  };

  if (pages[page]) pages[page]();
  document.addEventListener('nail:change', function () { /* other tabs write the same storage */ });
  window.addEventListener('storage', function () { N.invalidate(); if (window.RERENDER) window.RERENDER(); });
})();
