/* Shared state for the public site and the admin. Everything lives in localStorage under one prefix per salon,
   so the demo works from file:// and a booking made on the site shows up in the admin.

   Appointment: {code, date 'YYYY-MM-DD', start (minutes from midnight), end, loc, tech ('' = any), services [{id,name,price,minutes}],
                 addons [{id,name,price,qty}], total, discount, status, source, customer {name, phone}, note, pay, history [[ts, status, by]]}
   Demo history comes from SEED (build.py seed_data); its days are relative to the build date and are moved forward by whole
   weeks so today always has bookings and weekdays keep their rhythm. */
(function () {
  var S = window.SALON || {};
  var P = 'nail:' + ((S.salon && S.salon.slug) || 'x') + ':';

  function get(k, d) {
    try { var v = localStorage.getItem(P + k); return v == null ? d : JSON.parse(v); } catch (e) { return d; }
  }
  function set(k, v) {
    try { localStorage.setItem(P + k, JSON.stringify(v)); } catch (e) { /* private mode: lasts for this page only */ }
    cache = null;
    document.dispatchEvent(new CustomEvent('nail:change', { detail: { key: k } }));
  }

  var fmt = new Intl.NumberFormat('vi-VN');
  function vnd(n) { return fmt.format(Math.round(n || 0)) + ' đ'; }
  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }
  function norm(s) { return String(s || '').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/đ/g, 'd'); }
  function $(sel, el) { return (el || document).querySelector(sel); }
  function $$(sel, el) { return Array.prototype.slice.call((el || document).querySelectorAll(sel)); }
  function pad(n) { return (n < 10 ? '0' : '') + n; }
  function hm(m) { return pad(Math.floor(m / 60)) + ':' + pad(m % 60); }
  function toMin(s) { var p = String(s).split(':'); return (+p[0]) * 60 + (+p[1]); }
  function iso(d) { return d.getFullYear() + '-' + pad(d.getMonth() + 1) + '-' + pad(d.getDate()); }
  function parse(s) { var p = s.split('-'); return new Date(+p[0], +p[1] - 1, +p[2]); }
  function addDays(s, n) { var d = parse(s); d.setDate(d.getDate() + n); return iso(d); }
  function dayDiff(a, b) { return Math.round((parse(b) - parse(a)) / 864e5); }
  function weekday(s) { var w = parse(s).getDay(); return w === 0 ? 7 : w; } /* 1 = Thứ 2 ... 7 = Chủ nhật */
  var DAYS = ['', 'Thứ 2', 'Thứ 3', 'Thứ 4', 'Thứ 5', 'Thứ 6', 'Thứ 7', 'Chủ nhật'];
  var DAYS_SHORT = ['', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'CN'];
  function dateLabel(s, long) {
    var d = parse(s);
    var t = pad(d.getDate()) + '/' + pad(d.getMonth() + 1);
    return long ? DAYS[weekday(s)] + ', ' + t + '/' + d.getFullYear() : t;
  }
  function today() { return iso(new Date()); }
  function nowMin() { var d = new Date(); return d.getHours() * 60 + d.getMinutes(); }
  function mins(m) { m = Math.round(m || 0); if (m < 60) return m + ' phút'; var h = Math.floor(m / 60), r = m % 60; return h + ' giờ' + (r ? ' ' + r + ' phút' : ''); }

  var byId = function (list) { var o = {}; (list || []).forEach(function (x) { o[x.id] = x; }); return o; };
  var SVC = byId(S.services), ADD = byId(S.addons), TECH = byId(S.technicians), LOC = byId(S.locations);
  var STATUS = {}; (S.statuses || []).forEach(function (s) { STATUS[s[0]] = s[1]; });
  var SOURCE = {}; (S.sources || []).forEach(function (s) { SOURCE[s[0]] = s[1]; });
  var PAY = {}; (S.payments || []).forEach(function (s) { PAY[s[0]] = s[1]; });

  /* admin edits to the menu (price, minutes, hidden) */
  function svc(id) {
    var s = SVC[id]; if (!s) return null;
    var o = (get('adm:svc', {})[id]) || {};
    return Object.assign({}, s, o);
  }

  /* ------------------------------------------------------------- seed */
  var seedCache = null;
  function seedShift() {
    var SD = window.SEED;
    if (!SD || !SD.anchor) return 0;
    var d = dayDiff(SD.anchor, today());
    return Math.floor(d / 7) * 7;
  }
  function seed() {
    if (seedCache) return seedCache;
    var SD = window.SEED || { appts: [], customers: [] };
    var shift = seedShift();
    var svcList = S.services || [], addList = S.addons || [], techList = S.technicians || [], locList = S.locations || [];
    var srcKeys = (S.sources || []).map(function (s) { return s[0]; });
    var payKeys = (S.payments || []).map(function (s) { return s[0]; });
    var out = SD.appts.map(function (a, i) {
      var services = a[4].map(function (k) { var s = svcList[k]; return { id: s.id, name: s.name, price: s.price || 0, minutes: s.minutes }; });
      var addons = a[5].map(function (k) { var x = addList[k]; return { id: x.id, name: x.name, price: x.price, qty: 1 }; });
      var dur = services.reduce(function (t, s) { return t + s.minutes; }, 0) + addons.reduce(function (t, x) { return t + (ADD[x.id].minutes || 0); }, 0);
      var c = SD.customers[a[9]] || ['Khách', '', 0, ''];
      var date = addDays(SD.anchor, a[0] + shift);
      return {
        code: 'LH' + (200000 + (a[11] != null ? a[11] : i)), date: date, start: a[1], end: a[1] + dur, loc: (locList[a[2]] || {}).id,
        tech: (techList[a[3]] || {}).id || '', services: services, addons: addons, total: a[6] * 1000, discount: 0,
        code0: a[7], source: srcKeys[a[8]] || 'web', cust: a[9], customer: { name: c[0], phone: c[1] }, note: c[3] || '',
        pay: payKeys[a[10]] || 'cash', created: addDays(date, -(a[0] % 5 === 0 ? 3 : 1)), seed: true, history: []
      };
    });
    seedCache = { appts: out, customers: SD.customers, shift: shift };
    return seedCache;
  }
  function resolveStatus(a, t, now) {
    if (a.code0 === 1) return 'cancelled';
    if (a.code0 === 2) return 'no_show';
    if (a.date < t) return 'done';
    if (a.date === t) {
      if (a.end <= now) return 'done';
      if (a.start <= now) return 'arrived';
    }
    return a.code0 === 4 ? 'pending' : 'confirmed';
  }

  /* ------------------------------------------------------------- appointments */
  var cache = null;
  function all() {
    if (cache) return cache;
    var t = today(), now = nowMin();
    var ov = get('adm:ov', {});
    var list = seed().appts.map(function (a) {
      var x = Object.assign({}, a, { status: resolveStatus(a, t, now) });
      if (ov[a.code]) Object.assign(x, ov[a.code]);
      return x;
    });
    get('bookings', []).forEach(function (b) {
      var x = Object.assign({}, b);
      if (ov[b.code]) Object.assign(x, ov[b.code]);
      list.push(x);
    });
    cache = list;
    return list;
  }
  function find(code) {
    code = String(code || '').trim().toUpperCase();
    var l = all();
    for (var i = l.length - 1; i >= 0; i--) if (l[i].code === code) return l[i];
    return null;
  }
  function update(code, patch, by) {
    var ov = get('adm:ov', {});
    var cur = find(code); if (!cur) return null;
    var o = ov[code] || {};
    Object.assign(o, patch);
    if (patch.status && patch.status !== cur.status) {
      o.history = (cur.history || []).concat([[Date.now(), patch.status, by || '']]);
    }
    ov[code] = o;
    set('adm:ov', ov);
    return find(code);
  }
  function busy(a) { return a.status !== 'cancelled' && a.status !== 'no_show'; }

  /* customers: seed customers plus anyone who booked in this browser, keyed by phone */
  function customers() {
    var map = {};
    all().forEach(function (a) {
      var k = a.customer.phone || a.customer.name;
      var c = map[k];
      if (!c) c = map[k] = { key: k, name: a.customer.name, phone: a.customer.phone, visits: 0, spent: 0, first: a.date, last: '', next: '', count: 0, noShow: 0, cancelled: 0, note: a.note || '', techs: {} };
      c.count++;
      if (a.status === 'done') { c.visits++; c.spent += a.total; if (a.date > c.last) c.last = a.date; if (a.tech) c.techs[a.tech] = (c.techs[a.tech] || 0) + 1; }
      if (a.status === 'no_show') c.noShow++;
      if (a.status === 'cancelled') c.cancelled++;
      if ((a.status === 'pending' || a.status === 'confirmed') && a.date >= today() && (!c.next || a.date < c.next)) c.next = a.date;
      if (a.date < c.first) c.first = a.date;
    });
    var notes = get('adm:cnotes', {});
    return Object.keys(map).map(function (k) { var c = map[k]; if (notes[k] != null) c.note = notes[k]; return c; });
  }

  /* ------------------------------------------------------------- booking rules */
  function hoursOn(locId, date) {
    var l = LOC[locId]; if (!l) return null;
    var w = weekday(date);
    for (var i = 0; i < l.hours.length; i++) if (l.hours[i].days.indexOf(w) >= 0) {
      var close = toMin(l.hours[i].close);
      return [toMin(l.hours[i].open), close, l.last_order ? Math.min(close, toMin(l.last_order)) : close];
    }
    return null;
  }
  function techsFor(locId, serviceIds, date) {
    var w = date ? weekday(date) : 0;
    return (S.technicians || []).filter(function (t) {
      if (t.locations.indexOf(locId) < 0) return false;
      if (w && (t.off_days || []).indexOf(w) >= 0) return false;
      return (serviceIds || []).every(function (id) { var s = SVC[id]; return !s || !s.technicians.length || s.technicians.indexOf(t.id) >= 0; });
    });
  }
  /* free start times on a date for a total duration; techId '' means any technician who can do every service */
  function slots(locId, date, techId, duration, serviceIds) {
    var h = hoursOn(locId, date); if (!h) return [];
    var b = S.booking || {}, step = b.slot_minutes || 15;
    var start = h[0];
    if (date === today()) start = Math.max(start, Math.ceil((nowMin() + (b.lead_minutes || 0)) / step) * step);
    var pool = techsFor(locId, serviceIds, date);
    if (techId) pool = pool.filter(function (t) { return t.id === techId; });
    var hasTechs = (S.technicians || []).length > 0;
    var day = all().filter(function (a) { return a.date === date && a.loc === locId && busy(a); });
    var out = [];
    // a booking starts no later than the last order time and ends before closing
    for (var m = start; m + duration <= h[1] && m <= h[2]; m += step) {
      var free;
      if (!hasTechs) {
        free = day.filter(function (a) { return a.start < m + duration && a.end > m; }).length < 2 ? [''] : [];
      } else {
        free = pool.filter(function (t) {
          return !day.some(function (a) { return a.tech === t.id && a.start < m + duration && a.end > m; });
        }).map(function (t) { return t.id; });
      }
      if (free.length) out.push({ time: m, techs: free });
    }
    return out;
  }
  function priceOf(serviceIds, addons) {
    var total = 0, from = false, dur = 0;
    serviceIds.forEach(function (id) { var s = svc(id); if (!s) return; total += s.price || 0; dur += s.minutes; if (s.price_type === 'from' || s.price == null) from = true; });
    (addons || []).forEach(function (x) { var a = ADD[x.id]; if (!a) return; total += a.price * (x.qty || 1); dur += a.minutes || 0; });
    return { total: total, from: from, minutes: dur };
  }
  function promo(code) {
    code = String(code || '').trim().toUpperCase();
    return (S.promotions || []).filter(function (p) { return p.code === code; })[0] || null;
  }
  function discountFor(p, total) {
    if (!p) return 0;
    if (p.percent) return Math.round(total * p.percent / 100 / 1000) * 1000;
    return Math.min(total, p.amount || 0);
  }
  function newCode() {
    var c;
    do { c = 'LH' + (100000 + Math.floor(Math.random() * 99999)); } while (find(c));
    return c;
  }
  /* o: {status, by, mine} - the admin adds walk-ins as confirmed and does not list them as the visitor's own */
  function book(b, o) {
    o = o || {};
    var list = get('bookings', []);
    b.code = newCode();
    b.status = o.status || 'pending';
    b.created = today();
    b.createdAt = Date.now();
    b.history = [[Date.now(), b.status, o.by || 'Khách đặt online']];
    list.push(b);
    set('bookings', list);
    if (o.mine !== false) { var mine = get('mine', []); mine.push(b.code); set('mine', mine); }
    return b;
  }

  function icon(name, cls) {
    var P2 = {
      check: '<path d="M20 6 9 17l-5-5"/>', x: '<path d="M18 6 6 18"/><path d="m6 6 12 12"/>',
      clock: '<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>',
      user: '<path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>',
      pin: '<path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/>',
      phone: '<path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/>',
      calendar: '<rect width="18" height="18" x="3" y="4" rx="2"/><line x1="16" x2="16" y1="2" y2="6"/><line x1="8" x2="8" y1="2" y2="6"/><line x1="3" x2="21" y1="10" y2="10"/>',
      chev_r: '<path d="m9 18 6-6-6-6"/>', chev_l: '<path d="m15 18-6-6 6-6"/>', plus: '<path d="M5 12h14"/><path d="M12 5v14"/>',
      search: '<circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>', alert: '<circle cx="12" cy="12" r="10"/><line x1="12" x2="12" y1="8" y2="12"/><line x1="12" x2="12.01" y1="16" y2="16"/>',
      undo: '<path d="M3 7v6h6"/><path d="M21 17a9 9 0 0 0-9-9 9 9 0 0 0-6 2.3L3 13"/>', note: '<path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/><polyline points="14 2 14 8 20 8"/>'
    };
    return '<svg class="i ' + (cls || '') + '" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' + (P2[name] || '') + '</svg>';
  }

  function toast(msg, opts) {
    var box = $('[data-toasts]'); if (!box) return;
    var t = document.createElement('div');
    t.className = 'toast' + (opts && opts.bad ? ' bad' : '');
    t.setAttribute('role', 'status');
    t.innerHTML = '<span>' + esc(msg) + '</span>' + (opts && opts.undo ? '<button type="button" class="toast-undo">Hoàn tác</button>' : '');
    box.appendChild(t);
    if (opts && opts.undo) t.querySelector('button').onclick = function () { opts.undo(); t.remove(); };
    setTimeout(function () { t.classList.add('out'); setTimeout(function () { t.remove(); }, 300); }, (opts && opts.undo) ? 6000 : 3200);
  }

  window.NS = {
    S: S, get: get, set: set, vnd: vnd, esc: esc, norm: norm, $: $, $$: $$, pad: pad, hm: hm, toMin: toMin, iso: iso, parse: parse,
    addDays: addDays, dayDiff: dayDiff, weekday: weekday, DAYS: DAYS, DAYS_SHORT: DAYS_SHORT, dateLabel: dateLabel, today: today, nowMin: nowMin, mins: mins,
    SVC: SVC, ADD: ADD, TECH: TECH, LOC: LOC, STATUS: STATUS, SOURCE: SOURCE, PAY: PAY, svc: svc,
    all: all, find: find, update: update, busy: busy, customers: customers, seed: seed,
    hoursOn: hoursOn, techsFor: techsFor, slots: slots, priceOf: priceOf, promo: promo, discountFor: discountFor, book: book,
    icon: icon, toast: toast, invalidate: function () { cache = null; seedCache = null; }
  };
})();
