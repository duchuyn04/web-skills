/* floating-assistant: answers come from page.json (data-topics), matched by words without accents; no match offers the
   hand-off form. The teaser shows once per visit, 8 s after load. Esc closes and gives focus back to the button. */
(function () {
  var box = document.querySelector('[data-assist]');
  if (!box) return;
  var topics = JSON.parse(box.getAttribute('data-topics') || '[]');
  var hand = JSON.parse(box.getAttribute('data-handoff') || '{}');
  var fallback = box.getAttribute('data-fallback') || '';
  var more = box.getAttribute('data-more') || '';
  var panel = box.querySelector('.bl-assist__panel'), log = box.querySelector('[data-assist-log]');
  var fab = box.querySelector('.bl-assist__fab'), q = box.querySelector('[data-assist-q]');
  var teaser = box.querySelector('[data-assist-teaser]');
  var still = window.BL && window.BL.RM;
  var asked = {}, started = false;

  function norm(s) { return String(s || '').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/đ/g, 'd').replace(/[^a-z0-9 ]+/g, ' '); }
  function el(tag, cls, text) { var e = document.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; }
  function add(node) { var li = el('li'); li.appendChild(node); log.appendChild(li); log.scrollTop = log.scrollHeight; return li; }
  function say(text, who) { var m = el('li', 'bl-assist__msg ' + (who === 'me' ? 'is-me' : 'is-bot'), text); log.appendChild(m); log.scrollTop = log.scrollHeight; return m; }
  function chips(list) {
    var wrap = el('div', 'bl-assist__chips');
    list.forEach(function (c) {
      var b = el('button', 'bl-assist__chip' + (c.main ? ' is-main' : ''), c.label);
      b.type = 'button';
      b.addEventListener('click', function () { clearChips(); c.run(); });
      wrap.appendChild(b);
    });
    add(wrap);
  }
  /* suggestions belong to the last answer: once the visitor picks or types, the old ones go */
  function clearChips() { [].forEach.call(log.querySelectorAll('.bl-assist__chips'), function (c) { c.closest('li').remove(); }); }
  function topicChips(exclude) {
    var list = topics.filter(function (t, i) { return !asked[i] && t !== exclude; }).slice(0, 4).map(function (t) {
      return { label: t.q, run: function () { ask(t.q, t); } };
    });
    list.push({ label: hand.button, main: true, run: function () { say(hand.button, 'me'); reply(handoff); } });
    chips(list);
  }
  /* a short pause with typing dots, so an instant wall of text does not jump at the visitor */
  function reply(fn) {
    if (still) { fn(); return; }
    var t = el('li', 'bl-assist__msg is-bot is-typing'); t.innerHTML = '<i></i><i></i><i></i>'; t.setAttribute('aria-hidden', 'true');
    log.appendChild(t); log.scrollTop = log.scrollHeight;
    setTimeout(function () { t.remove(); fn(); }, 650);
  }
  function answer(t) {
    asked[topics.indexOf(t)] = true;
    say(t.a);
    if (t.link && t.link.href) { var a = el('a', 'bl-assist__link', t.link.label); a.href = t.link.href; add(a); a.addEventListener('click', function () { if (t.link.href.charAt(0) === '#') close(); }); }
    if (t.handoff) handoff(); else topicChips(t);
  }
  /* words that say nothing about the topic (Vietnamese and English) are left out of the match */
  var STOP = ' co khong la gi the nao cho toi minh ban duoc lam web website trang va cua voi nhu thi o tai sao vay a oi nhe khi nay do mot cac nhung de hay hoac the is the a an do you can i my me for to of and or what how '.split(' ');
  function match(text) {
    var words = norm(text).split(/\s+/).filter(function (w) { return w.length > 1 && STOP.indexOf(w) < 0; });
    var best = null, score = 0;
    topics.forEach(function (t) {
      var hay = ' ' + norm(t.q + ' ' + (t.keys || '')) + ' ';
      var s = words.reduce(function (n, w) { return n + (hay.indexOf(' ' + w + ' ') >= 0 ? 1 : 0); }, 0);
      if (s > score) { score = s; best = t; }
    });
    return score >= 1 ? best : null;
  }
  function ask(text, t) {
    clearChips();
    say(text, 'me');
    t = t || match(text);
    reply(function () {
      if (t) answer(t);
      else { say(fallback); chips([{ label: hand.button, main: true, run: function () { say(hand.button, 'me'); reply(handoff); } }, { label: more, run: function () { topicChips(); } }]); }
    });
  }
  /* call-back form inside the conversation */
  function handoff() {
    say(hand.intro);
    var f = el('form', 'bl-assist__form');
    f.noValidate = true;
    f.innerHTML = '<label><span></span><input name="name" autocomplete="name"></label><label><span></span><input name="phone" inputmode="tel" autocomplete="tel" required></label><p class="bl-assist__err" hidden></p><button class="bl-btn bl-btn--primary" type="submit"></button>';
    var spans = f.querySelectorAll('label span');
    spans[0].textContent = hand.name_label; spans[1].textContent = hand.phone_label;
    f.querySelector('button').textContent = hand.submit_label;
    add(f);
    f.querySelector('input').focus();
    f.addEventListener('submit', function (e) {
      e.preventDefault();
      var phone = f.phone.value.replace(/[^0-9+]/g, ''), err = f.querySelector('.bl-assist__err');
      if (phone.replace(/\D/g, '').length < 9) { err.hidden = false; err.textContent = hand.phone_error; f.phone.focus(); return; }
      if (hand.action) { try { fetch(hand.action, { method: 'POST', body: new FormData(f), mode: 'no-cors' }); } catch (x) { /* the thanks still shows */ } }
      f.closest('li').remove();
      say((f.name.value ? f.name.value.trim() + ', ' : '') + f.phone.value.trim(), 'me');
      reply(function () { say(hand.success); q.focus(); });
    });
  }

  function open() {
    if (teaser) teaser.hidden = true;
    try { sessionStorage.setItem('bl-assist-seen', '1'); } catch (x) { /* private mode */ }
    panel.hidden = false; box.classList.add('is-open'); fab.setAttribute('aria-expanded', 'true');
    if (!started) { started = true; topicChips(); }
    /* on a touch screen the keyboard would cover the suggestions: focus the panel, not the field */
    if (window.matchMedia('(pointer: fine)').matches) q.focus(); else panel.querySelector('[data-assist-close]').focus();
  }
  function close() { panel.hidden = true; box.classList.remove('is-open'); fab.setAttribute('aria-expanded', 'false'); fab.focus(); }
  box.addEventListener('click', function (e) {
    if (e.target.closest('[data-assist-open]')) open();
    else if (e.target.closest('[data-assist-close]')) close();
    else if (e.target.closest('[data-assist-dismiss]')) { teaser.hidden = true; try { sessionStorage.setItem('bl-assist-seen', '1'); } catch (x) { /* ignore */ } }
  });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && !panel.hidden) { e.stopPropagation(); close(); } });
  box.querySelector('[data-assist-ask]').addEventListener('submit', function (e) {
    e.preventDefault();
    var v = q.value.trim(); if (!v) return;
    q.value = ''; ask(v);
  });
  if (teaser) {
    var seen = false; try { seen = !!sessionStorage.getItem('bl-assist-seen'); } catch (x) { /* ignore */ }
    if (!seen) setTimeout(function () { if (panel.hidden) teaser.hidden = false; }, 8000);
  }
})();
