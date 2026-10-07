/* app-ui prototype navigator: a "View prototype" button on the right edge that opens every screen and state
   of the prototype, with previous and next screen. Prototype only, never part of the real product.
   This file is a template: scripts/protonav.py writes <out>/kit/proto-nav.js with the screen list in place of
   the DATA marker and adds the script tag to every page. A page outside the kit (a landing page built by
   another skill) loads the same file with its own relative path. Carries its own CSS so it works on any page.
   Keys: Alt+M opens or closes, Alt+Left and Alt+Right go to the previous or next screen, Esc closes. */
(function () {
  "use strict";
  if (window.top !== window) return; /* not inside preview frames */
  var DATA = /*__DATA__*/ null;
  if (!DATA || !DATA.groups) return;

  var me = document.currentScript && document.currentScript.src;
  var root = me ? new URL("..", me) : new URL(".", location.href); /* the prototype folder: kit/.. */
  var vi = !/^en/i.test(document.documentElement.lang || "vi");
  var T = vi ? {
    btn: "Xem prototype", count: function (p, s) { return p + " màn hình, " + s + " trạng thái"; },
    hintT: "Đây là bản prototype", hint: "Bấm Xem prototype để mở danh sách mọi màn hình và đi lần lượt qua từng trạng thái.",
    open: "Mở danh sách", later: "Để sau", title: "Các màn hình prototype", close: "Đóng", aria: "Điều hướng prototype",
    now: "Đang xem", of: function (i, n) { return "màn " + i + " trên " + n; }, pick: "Chọn một màn hình bên dưới",
    prev: "Màn trước", next: "Màn sau", find: "Tìm màn hình hoặc trạng thái", findL: "Tìm màn hình", list: "Màn hình",
    states: function (n) { return n + " trạng thái"; }, none: "Không có màn hình nào khớp.",
    keys: "<kbd>Alt</kbd>+<kbd>M</kbd> mở, đóng · <kbd>Alt</kbd>+<kbd>&larr;</kbd> <kbd>&rarr;</kbd> màn trước, sau"
  } : {
    btn: "View prototype", count: function (p, s) { return p + " screens, " + s + " states"; },
    hintT: "This is a prototype", hint: "Open View prototype to see every screen and step through each state.",
    open: "Open list", later: "Later", title: "Prototype screens", close: "Close", aria: "Prototype navigation",
    now: "Viewing", of: function (i, n) { return "screen " + i + " of " + n; }, pick: "Pick a screen below",
    prev: "Previous", next: "Next", find: "Find a screen or state", findL: "Find a screen", list: "Screens",
    states: function (n) { return n + " states"; }, none: "No screen matches.",
    keys: "<kbd>Alt</kbd>+<kbd>M</kbd> open, close · <kbd>Alt</kbd>+<kbd>&larr;</kbd> <kbd>&rarr;</kbd> previous, next"
  };

  var KEY = "proto-nav-" + (DATA.key || "app") + "-";
  var store = {
    get: function (k) { try { return localStorage.getItem(KEY + k); } catch (e) { return null; } },
    set: function (k, v) { try { localStorage.setItem(KEY + k, v); } catch (e) { /* private mode */ } }
  };
  var q = new URLSearchParams(location.search), curState = q.get("state");
  var SEL = DATA.select || null; /* optional: one select that adds a query parameter to some pages */
  var selVal = SEL ? (q.get(SEL.param) || store.get("sel") || "") : "";
  var still = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  function url(f) { return new URL(f, root); }
  var herePath = location.pathname.replace(/\/$/, "/index.html");
  function isHere(f) { return url(f).pathname.replace(/\/$/, "/index.html") === herePath; }

  /* every stop in order: one per state, or one for a page without states */
  var STOPS = [], nPages = 0;
  DATA.groups.forEach(function (g) {
    g.pages.forEach(function (p) {
      nPages++;
      if (p.s.length) p.s.forEach(function (x) { STOPS.push({ f: p.f, t: p.t, s: x[0], l: x[1] }); });
      else STOPS.push({ f: p.f, t: p.t, s: "", l: "" });
    });
  });
  var hereStop = -1;
  for (var i = 0; i < STOPS.length; i++) if (isHere(STOPS[i].f) && (curState ? STOPS[i].s === curState : true)) { hereStop = i; break; }

  var css = [
    ".pn-btn{--pn:var(--accent,#1f4aa8);position:fixed;right:0;top:50%;z-index:2147483000;transform:translateY(-50%);display:flex;align-items:center;gap:10px;padding:12px 14px 12px 12px;border:0;border-radius:14px 0 0 14px;background:var(--pn);color:#fff;font:400 13px/1.25 system-ui,-apple-system,'Segoe UI',sans-serif;text-align:left;cursor:pointer;box-shadow:0 10px 30px -8px rgba(15,23,42,.55),0 0 0 3px rgba(255,255,255,.9);transition:filter .15s,padding .2s}",
    ".pn-btn:hover{filter:brightness(.88);padding-right:20px}",
    ".pn-btn[hidden],.pn-hint[hidden],.pn[hidden]{display:none}",
    ".pn-ic{display:grid;grid-template-columns:repeat(2,9px);gap:3px;padding:7px;border-radius:9px;background:rgba(255,255,255,.18)}",
    ".pn-ic i{width:9px;height:9px;border-radius:2px;background:#fff}",
    ".pn-ic i:nth-child(2){background:#ffd166}",
    ".pn-btn b{display:block;font-size:14px;font-weight:700}",
    ".pn-btn small{display:block;margin-top:2px;font-size:11.5px;opacity:.88}",
    ".pn-btn::after{content:'';position:absolute;inset:-3px 0 -3px -3px;border-radius:16px 0 0 16px;pointer-events:none}",
    ".pn-btn.is-new::after{animation:pn-ring 1.6s ease-out 2}",
    "@keyframes pn-ring{0%{box-shadow:0 0 0 0 rgba(31,74,168,.55)}100%{box-shadow:0 0 0 16px rgba(31,74,168,0)}}",
    ".pn-hint{position:fixed;right:16px;top:calc(50% + 46px);z-index:2147483000;width:250px;padding:12px 14px;border-radius:12px;background:#18181b;color:#fff;font:400 13px/1.45 system-ui,-apple-system,'Segoe UI',sans-serif;box-shadow:0 12px 30px -8px rgba(0,0,0,.4)}",
    ".pn-hint::before{content:'';position:absolute;right:28px;top:-6px;width:12px;height:12px;background:#18181b;transform:rotate(45deg)}",
    ".pn-hint b{display:block;margin-bottom:2px;font-size:13.5px}",
    ".pn-hint div{display:flex;gap:8px;margin-top:10px}",
    ".pn-hint button{min-height:30px;padding:0 12px;border-radius:6px;border:0;font:600 12.5px system-ui,sans-serif;cursor:pointer}",
    ".pn-hint .go{background:#fff;color:#18181b}.pn-hint .no{background:transparent;color:#d4d4d8}",
    ".pn-btn:focus-visible,.pn-hint button:focus-visible,.pn a:focus-visible,.pn button:focus-visible,.pn select:focus-visible,.pn input:focus-visible{outline:2px solid #ffd166;outline-offset:2px}",
    ".pn{--pn:var(--accent,#1f4aa8);position:fixed;top:0;right:0;bottom:0;z-index:2147483001;width:min(340px,92vw);display:flex;flex-direction:column;background:#fff;color:#18181b;border-left:1px solid #e4e4e7;box-shadow:-12px 0 32px rgba(0,0,0,.16);font:400 13px/1.45 system-ui,-apple-system,'Segoe UI',sans-serif}",
    ".pn *{box-sizing:border-box}",
    ".pn-head{padding:14px 14px 12px;background:var(--pn);color:#fff}",
    ".pn-top{display:flex;align-items:center;gap:8px}.pn-top b{flex:1;font-size:15px}",
    ".pn-x{width:32px;height:32px;border:0;border-radius:6px;background:rgba(255,255,255,.14);color:#fff;font-size:20px;line-height:1;cursor:pointer}",
    ".pn-x:hover{background:rgba(255,255,255,.26)}",
    ".pn-now{margin:8px 0 0;font-size:12.5px;opacity:.92}.pn-now strong{font-weight:600}",
    ".pn-step{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:10px}",
    ".pn-step a{display:flex;align-items:center;justify-content:center;min-height:34px;border-radius:8px;background:#fff;color:var(--pn);font-weight:600;text-decoration:none}",
    ".pn-step a:hover{background:#eef2fb}.pn-step a[aria-disabled]{opacity:.45;pointer-events:none}",
    ".pn-tools{display:grid;gap:8px;padding:10px 14px;border-bottom:1px solid #e4e4e7}",
    ".pn-tools input,.pn-tools select{width:100%;min-height:34px;padding:6px 10px;border:1px solid #d4d4d8;border-radius:6px;background:#fff;color:#18181b;font:inherit}",
    ".pn-sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0,0,0,0)}",
    ".pn-list{flex:1;overflow-y:auto;padding:6px 8px 16px}",
    ".pn-g{margin:12px 6px 4px;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.06em;color:#68686f}",
    ".pn-p{padding:6px;border-radius:8px}.pn-p.on{background:#eef2fb}",
    ".pn-p>a{display:flex;align-items:center;justify-content:space-between;gap:6px;min-height:28px;color:#18181b;text-decoration:none;font-weight:600}",
    ".pn-p>a:hover{color:var(--pn)}.pn-p>a small{font-weight:400;color:#68686f}",
    ".pn-s{display:flex;flex-wrap:wrap;gap:4px;margin-top:4px}",
    ".pn-s a{display:inline-flex;align-items:center;min-height:24px;padding:0 8px;border:1px solid #e4e4e7;border-radius:999px;background:#fff;color:#3f3f46;text-decoration:none;font-size:12px}",
    ".pn-s a:hover{border-color:var(--pn);color:var(--pn)}",
    ".pn-s a[aria-current]{background:var(--pn);border-color:var(--pn);color:#fff}",
    ".pn-empty{padding:12px 6px;color:#68686f}",
    ".pn-foot{padding:10px 14px;border-top:1px solid #e4e4e7;color:#68686f;font-size:12px}",
    ".pn-foot kbd{padding:0 4px;border:1px solid #d4d4d8;border-radius:3px;background:#f4f4f5;font:500 11px/16px system-ui,sans-serif}",
    "@media (max-width:640px){.pn-btn{top:auto;bottom:96px;transform:none;padding:10px}.pn-btn>span:last-child{display:none}.pn-hint{top:auto;bottom:156px}.pn-hint::before{top:auto;bottom:-6px;right:18px}}",
    "@media (prefers-reduced-motion:reduce){.pn-btn.is-new::after{animation:none}}"
  ].join("");
  var st = document.createElement("style"); st.textContent = css; document.head.appendChild(st);

  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", "\"": "&quot;" }[c]; }); }
  function href(f, state) {
    var u = url(f);
    if (state) u.searchParams.set("state", state);
    if (SEL && selVal && SEL.pages.indexOf(f) >= 0) u.searchParams.set(SEL.param, selVal);
    return u.href;
  }

  var tab = document.createElement("button");
  tab.type = "button"; tab.className = "pn-btn"; tab.setAttribute("aria-expanded", "false"); tab.setAttribute("aria-controls", "pn");
  tab.innerHTML = '<span class="pn-ic" aria-hidden="true"><i></i><i></i><i></i><i></i></span><span><b>' + T.btn + "</b><small>" + T.count(nPages, STOPS.length) + "</small></span>";
  var hint = document.createElement("div");
  hint.className = "pn-hint"; hint.hidden = true; hint.setAttribute("role", "status");
  hint.innerHTML = "<b>" + T.hintT + "</b>" + T.hint + '<div><button class="go" type="button">' + T.open + '</button><button class="no" type="button">' + T.later + "</button></div>";

  var prev = hereStop > 0 ? STOPS[hereStop - 1] : null;
  var next = hereStop < 0 ? STOPS[0] : (hereStop < STOPS.length - 1 ? STOPS[hereStop + 1] : null);
  var cur = hereStop >= 0 ? STOPS[hereStop] : null;
  var box = document.createElement("aside");
  box.className = "pn"; box.id = "pn"; box.hidden = true; box.setAttribute("aria-label", T.aria);
  box.innerHTML = '<div class="pn-head"><div class="pn-top"><b>' + T.title + '</b><button class="pn-x" type="button" aria-label="' + T.close + '">&times;</button></div>' +
    '<p class="pn-now">' + (cur ? T.now + " <strong>" + esc(cur.t) + "</strong>" + (cur.l ? ", " + esc(cur.l) : "") + " · " + T.of(hereStop + 1, STOPS.length) : T.pick) + "</p>" +
    '<div class="pn-step"><a data-step="-1"' + (prev ? ' href="' + esc(href(prev.f, prev.s)) + '"' : ' aria-disabled="true"') + ">&lsaquo; " + T.prev + '</a><a data-step="1"' + (next ? ' href="' + esc(href(next.f, next.s)) + '"' : ' aria-disabled="true"') + ">" + T.next + " &rsaquo;</a></div></div>" +
    '<div class="pn-tools"><label><span class="pn-sr">' + T.findL + '</span><input type="search" placeholder="' + T.find + '" data-f></label>' +
    (SEL ? '<label><span class="pn-sr">' + esc(SEL.label) + "</span><select data-sel>" + SEL.options.map(function (o) { return '<option value="' + esc(o[0]) + '"' + (o[0] === selVal ? " selected" : "") + ">" + esc(o[1]) + "</option>"; }).join("") + "</select></label>" : "") +
    '</div><nav class="pn-list" aria-label="' + T.list + '"></nav><div class="pn-foot">' + T.keys + "</div>";
  document.body.appendChild(tab); document.body.appendChild(hint); document.body.appendChild(box);
  var list = box.querySelector(".pn-list"), find = box.querySelector("[data-f]");

  function norm(s) { return String(s).toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "").replace(/đ/g, "d"); }
  function draw() {
    var f = norm(find.value.trim()), h = "";
    DATA.groups.forEach(function (g) {
      var rows = g.pages.filter(function (p) { return !f || norm(p.t + " " + p.f + " " + p.s.map(function (x) { return x[1]; }).join(" ")).indexOf(f) >= 0; });
      if (!rows.length) return;
      if (g.group) h += '<div class="pn-g">' + esc(g.group) + "</div>";
      rows.forEach(function (p) {
        var on = isHere(p.f);
        h += '<div class="pn-p' + (on ? " on" : "") + '"><a href="' + esc(href(p.f)) + '"' + (on ? ' aria-current="page"' : "") + ">" + esc(p.t) + (p.s.length > 1 ? "<small>" + T.states(p.s.length) + "</small>" : "") + "</a>";
        if (p.s.length > 1) h += '<div class="pn-s">' + p.s.map(function (x, i) {
          var c = on && (curState ? curState === x[0] : i === 0);
          return '<a href="' + esc(href(p.f, x[0])) + '"' + (c ? ' aria-current="true"' : "") + ">" + esc(x[1]) + "</a>";
        }).join("") + "</div>";
        h += "</div>";
      });
    });
    list.innerHTML = h || '<p class="pn-empty">' + T.none + "</p>";
  }
  function seen() { store.set("seen", "1"); hint.hidden = true; tab.classList.remove("is-new"); }
  function open(v) {
    seen();
    box.hidden = !v; tab.hidden = v; tab.setAttribute("aria-expanded", String(v));
    store.set("open", v ? "1" : "");
    if (v) { draw(); var c = list.querySelector('[aria-current="page"]'); if (c) c.scrollIntoView({ block: "center" }); find.focus(); } else tab.focus();
  }
  tab.addEventListener("click", function () { open(true); });
  hint.querySelector(".go").addEventListener("click", function () { open(true); });
  hint.querySelector(".no").addEventListener("click", seen);
  box.querySelector(".pn-x").addEventListener("click", function () { open(false); });
  find.addEventListener("input", draw);
  var sel = box.querySelector("[data-sel]");
  if (sel) sel.addEventListener("change", function (e) { selVal = e.target.value; store.set("sel", selVal); draw(); });
  document.addEventListener("keydown", function (e) {
    if (e.altKey && (e.key === "m" || e.key === "M")) { e.preventDefault(); open(box.hidden); }
    else if (e.altKey && (e.key === "ArrowLeft" || e.key === "ArrowRight")) {
      var to = e.key === "ArrowLeft" ? prev : next;
      if (to) { e.preventDefault(); location.href = href(to.f, to.s); }
    } else if (e.key === "Escape" && !box.hidden) open(false);
  });
  /* a reviewer who left the panel open keeps it open on the next screen; a first visitor gets the hint */
  if (store.get("open") === "1" && innerWidth > 1100) { box.hidden = false; tab.hidden = true; tab.setAttribute("aria-expanded", "true"); draw(); }
  else if (!store.get("seen") && !navigator.webdriver) {
    if (!still) tab.classList.add("is-new");
    setTimeout(function () { if (box.hidden) hint.hidden = false; }, 1200);
  }
})();
