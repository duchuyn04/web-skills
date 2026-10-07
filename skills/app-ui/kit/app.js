/* app-ui behaviour. Plain JavaScript, no build step. Pages declare behaviour with data attributes; logic
   that talks to a server (save, load, send) is left to the project: hooks fire a "ui:" event and stop there.

   States: <body data-states="default empty error"> lists the states a page draws. Elements with
   data-state="empty" show only in that state, elements without data-state always show. Open a state with
   ?state=empty; qa.py walks every state. */
(function () {
  "use strict";
  var UI = (window.UI = window.UI || {});
  var $ = function (sel, root) { return (root || document).querySelector(sel); };
  var $$ = function (sel, root) { return Array.prototype.slice.call((root || document).querySelectorAll(sel)); };

  /* ---------- Icons: one inline sprite from icons.js ---------- */
  function mountIcons() {
    if (!window.UI_ICONS || document.getElementById("ui-icons")) return;
    var out = ['<svg id="ui-icons" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" style="position:absolute;width:0;height:0;overflow:hidden">'];
    Object.keys(window.UI_ICONS).forEach(function (k) {
      out.push('<symbol id="i-' + k + '" viewBox="0 0 24 24">' + window.UI_ICONS[k] + "</symbol>");
    });
    out.push("</svg>");
    document.body.insertAdjacentHTML("afterbegin", out.join(""));
  }
  UI.icon = function (name, cls) {
    return '<svg class="ico' + (cls ? " " + cls : "") + '" aria-hidden="true"><use href="#i-' + name + '"/></svg>';
  };

  /* ---------- States ---------- */
  UI.states = function () { return (document.body.getAttribute("data-states") || "default").split(/\s+/).filter(Boolean); };
  UI.setState = function (name) {
    var all = UI.states();
    if (all.indexOf(name) < 0) name = all[0];
    document.body.setAttribute("data-current-state", name);
    $$("[data-state]").forEach(function (el) {
      var on = el.getAttribute("data-state").split(/\s+/).indexOf(name) >= 0;
      if (el.tagName === "DIALOG") {
        /* a dialog or drawer that belongs to a state opens as a modal in that state, so nothing paints over it */
        el.hidden = false;
        if (on && el.showModal && !el.open) el.showModal();
        if (!on && el.open) el.close();
        return;
      }
      el.hidden = !on;
    });
    document.dispatchEvent(new CustomEvent("ui:state", { detail: { state: name } }));
  };

  /* ---------- Menus ---------- */
  function closeMenus(except) {
    $$("[data-menu]").forEach(function (btn) {
      var menu = document.getElementById(btn.getAttribute("aria-controls"));
      if (!menu || menu === except) return;
      menu.hidden = true;
      btn.setAttribute("aria-expanded", "false");
    });
  }
  document.addEventListener("click", function (e) {
    var btn = e.target.closest("[data-menu]");
    if (btn) {
      var menu = document.getElementById(btn.getAttribute("aria-controls"));
      if (!menu) return;
      var open = menu.hidden;
      closeMenus(menu);
      menu.hidden = !open;
      btn.setAttribute("aria-expanded", String(open));
      if (open) { var first = menu.querySelector("a, button"); if (first) first.focus(); }
      return;
    }
    if (!e.target.closest(".menu")) closeMenus();
  });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") closeMenus();
  });

  /* ---------- Dialogs and drawers (native <dialog>) ---------- */
  document.addEventListener("click", function (e) {
    var opener = e.target.closest("[data-open]");
    if (opener) {
      var d = document.getElementById(opener.getAttribute("data-open"));
      if (d && d.showModal) { e.preventDefault(); d.showModal(); }
      return;
    }
    var closer = e.target.closest("[data-close]");
    if (closer) { var dlg = closer.closest("dialog"); if (dlg) dlg.close(closer.getAttribute("data-close") || ""); return; }
    /* a click on the backdrop lands on the dialog element itself */
    if (e.target.tagName === "DIALOG" && e.target.open) {
      var r = e.target.getBoundingClientRect();
      if (e.clientX < r.left || e.clientX > r.right || e.clientY < r.top || e.clientY > r.bottom) e.target.close();
    }
  });

  /* ---------- Tabs ---------- */
  function selectTab(tab) {
    var list = tab.closest('[role="tablist"]');
    $$('[role="tab"]', list).forEach(function (t) {
      var on = t === tab;
      t.setAttribute("aria-selected", String(on));
      t.tabIndex = on ? 0 : -1;
      var panel = document.getElementById(t.getAttribute("aria-controls"));
      if (panel) panel.hidden = !on;
    });
    document.dispatchEvent(new CustomEvent("ui:tab", { detail: { tab: tab } }));
  }
  document.addEventListener("click", function (e) {
    var tab = e.target.closest('[role="tab"]');
    if (tab && !tab.getAttribute("href")) selectTab(tab);
  });
  document.addEventListener("keydown", function (e) {
    var tab = e.target.closest && e.target.closest('[role="tab"]');
    if (!tab || (e.key !== "ArrowRight" && e.key !== "ArrowLeft")) return;
    var tabs = $$('[role="tab"]', tab.closest('[role="tablist"]'));
    var next = tabs[(tabs.indexOf(tab) + (e.key === "ArrowRight" ? 1 : tabs.length - 1)) % tabs.length];
    next.focus();
    if (!next.getAttribute("href")) selectTab(next);
  });

  /* ---------- Pressed buttons: .seg picks one, .filter toggles ---------- */
  document.addEventListener("click", function (e) {
    var b = e.target.closest(".seg button, button.filter");
    if (!b) return;
    if (b.closest(".seg")) $$("button", b.closest(".seg")).forEach(function (x) { x.setAttribute("aria-pressed", String(x === b)); });
    else b.setAttribute("aria-pressed", String(b.getAttribute("aria-pressed") !== "true"));
    document.dispatchEvent(new CustomEvent("ui:press", { detail: { button: b } }));
    /* a view switch drawn as states (Máy tính / Điện thoại): data-to-state opens that state, keeps it in the
       address and moves focus to the same button in the seg that state shows */
    var to = b.getAttribute("data-to-state");
    if (to && to !== document.body.getAttribute("data-current-state")) {
      UI.setState(to);
      var url = new URL(location.href);
      url.searchParams.set("state", to);
      history.replaceState(null, "", url);
      var twin = $$('.seg button[data-to-state="' + to + '"]').filter(function (x) { return x.offsetParent; })[0];
      if (twin) twin.focus();
    }
  });

  /* ---------- Sidebar on narrow screens ---------- */
  document.addEventListener("click", function (e) {
    var t = e.target.closest("[data-side-toggle]");
    var shell = $(".app-side");
    if (!shell) return;
    if (t) { shell.classList.toggle("side-open"); return; }
    if (shell.classList.contains("side-open") && !e.target.closest(".sidebar")) shell.classList.remove("side-open");
  });

  /* ---------- Table: select rows, bulk bar ---------- */
  function syncBulk(table) {
    var boxes = $$("tbody .pick input", table).filter(function (b) { return !b.closest("[hidden]"); });
    var on = boxes.filter(function (b) { return b.checked; }).length;
    var all = $(".pick [data-select-all]", table);
    if (all) { all.checked = on > 0 && on === boxes.length; all.indeterminate = on > 0 && on < boxes.length; }
    var bulk = document.getElementById(table.getAttribute("data-bulk") || "");
    if (bulk) {
      bulk.hidden = on === 0;
      var n = $("[data-bulk-count]", bulk);
      if (n) n.textContent = on;
    }
  }
  document.addEventListener("change", function (e) {
    var table = e.target.closest("table.data");
    if (!table || !e.target.closest(".pick")) return;
    if (e.target.hasAttribute("data-select-all")) $$("tbody .pick input", table).forEach(function (b) { if (!b.closest("[hidden]")) b.checked = e.target.checked; });
    syncBulk(table);
  });
  document.addEventListener("click", function (e) {
    var clear = e.target.closest("[data-bulk-clear]");
    if (!clear) return;
    var bulk = clear.closest(".bulk");
    var table = bulk && $('table.data[data-bulk="' + bulk.id + '"]');
    if (!table) return;
    $$(".pick input", table).forEach(function (b) { b.checked = false; });
    syncBulk(table);
  });

  /* the icon says the order: up, down, or both ways for a column not sorted */
  function sortIcons(tr) {
    $$("th .sort use", tr).forEach(function (u) {
      var s = u.closest("th").getAttribute("aria-sort");
      u.setAttribute("href", s === "ascending" ? "#i-chevron-up" : s === "descending" ? "#i-chevron-down" : "#i-arrow-up-down");
    });
  }
  UI.sortIcons = sortIcons;
  /* ---------- Sortable headers: aria-sort cycles; sorting the data is the project's job ---------- */
  document.addEventListener("click", function (e) {
    var b = e.target.closest("th .sort");
    if (!b) return;
    var th = b.closest("th");
    var next = th.getAttribute("aria-sort") === "ascending" ? "descending" : "ascending";
    $$("th[aria-sort]", th.closest("tr")).forEach(function (x) { x.removeAttribute("aria-sort"); });
    th.setAttribute("aria-sort", next);
    sortIcons(th.closest("tr"));
    document.dispatchEvent(new CustomEvent("ui:sort", { detail: { key: b.getAttribute("data-sort"), dir: next } }));
  });

  /* ---------- Toast, with an optional action such as Undo ---------- */
  UI.toast = function (text, opts) {
    opts = opts || {};
    var box = $(".toasts");
    if (!box) { box = document.createElement("div"); box.className = "toasts"; box.setAttribute("role", "status"); document.body.appendChild(box); }
    var t = document.createElement("div");
    t.className = "toast";
    var span = document.createElement("span");
    span.textContent = text;
    t.appendChild(span);
    if (opts.action) {
      var b = document.createElement("button");
      b.type = "button";
      b.textContent = opts.action;
      b.addEventListener("click", function () { if (opts.onAction) opts.onAction(); t.remove(); });
      t.appendChild(b);
    }
    box.appendChild(t);
    setTimeout(function () { t.remove(); }, opts.timeout || 5000);
  };
  document.addEventListener("click", function (e) {
    var b = e.target.closest("[data-toast]");
    if (b) UI.toast(b.getAttribute("data-toast"), { action: b.getAttribute("data-toast-action") || "" });
  });

  /* ---------- Device preview: draw the page at its real width, scale it into the frame ---------- */
  var sbw = null;
  function scrollbar() {
    if (sbw === null) {
      var d = document.createElement("div");
      d.style.cssText = "position:absolute;top:-200px;width:100px;height:100px;overflow:scroll";
      document.body.appendChild(d);
      sbw = d.offsetWidth - d.clientWidth;
      d.remove();
    }
    return sbw;
  }
  /* the status bar takes the colour at the top of the page, like Safari does, when the frame is same origin */
  function tintPhone(f) {
    var screen = f.closest(".dev-screen");
    if (!screen) return;
    try {
      var doc = f.contentDocument, el = doc && doc.elementFromPoint(4, 4), bg = "";
      while (el && el.nodeType === 1) {
        bg = doc.defaultView.getComputedStyle(el).backgroundColor;
        if (bg && !/rgba\(.*,\s*0\)|transparent/.test(bg)) break;
        el = el.parentElement; bg = "";
      }
      if (!bg) return;
      var c = bg.match(/\d+(\.\d+)?/g).map(Number);
      var dark = (0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]) < 140;
      screen.style.setProperty("--status-bg", bg);
      screen.style.setProperty("--status-ink", dark ? "var(--surface)" : "var(--ink)");
    } catch (err) { /* another origin, or a file opened from disk: data-screen decides */ }
  }
  $$(".dev-screen iframe").forEach(function (f) { f.addEventListener("load", function () { tintPhone(f); }); });
  function fitFrames() {
    $$(".vp[data-w]").forEach(function (vp) {
      var f = $("iframe", vp);
      if (!f) return;
      if (!vp.clientWidth) return; /* hidden in this state: fit it when it shows */
      var w = +vp.getAttribute("data-w");
      var s = vp.clientWidth / w || 1;
      /* in a phone frame the page's scroll bar falls outside the screen, as on a real phone */
      f.style.width = w + (vp.closest(".dev-phone") ? scrollbar() : 0) + "px";
      f.style.height = vp.clientHeight / s + "px";
      f.style.transform = "scale(" + s + ")";
    });
  }
  UI.fitFrames = fitFrames;
  window.addEventListener("resize", fitFrames);
  document.addEventListener("ui:state", function () { requestAnimationFrame(fitFrames); });
  document.addEventListener("ui:press", function () { requestAnimationFrame(fitFrames); });

  /* ---------- Live tables: search, tabs, filters, sort, date range, pages, CSV, keys ----------
     <table class="data" data-live="req" data-live-sort="sent:desc">, rows <tr data-row data-date="2026-10-07T08:05"
     data-k-sent="2026-10-07T08:05" data-f-stage="new" data-find="extra words">. Controls name the table:
       <input data-live-search="req">                      accent-free search in the row text and data-find
       [role=tab][data-live-tab="req"][data-f="stage"][data-v="new"]   one value per tab list, data-v="" for all;
                                                          a .count inside the tab keeps the live number
       button.filter[data-live-filter="req"][data-f="mock"][data-v="1"]   pressed filters must all match
       <select data-live-select="req" data-f="industry">  "" for all
       th > button.sort[data-sort="sent"]                  sorts by data-k-sent (numbers when they read as numbers)
       [data-period="req"]                                 date range picker; rows outside data-date hide
       <nav class="pager" data-live-pager="req" data-size="8" data-noun="yêu cầu">
       [data-live-empty="req"]  shown when nothing matches; [data-live-reset="req"] clears search and filters
       [data-live-count="req"]  "8 yêu cầu"; button[data-live-csv="req"][data-name="yeu-cau"] downloads the matches
     Search, tab, sort and page stay in the address. Keys: / search, j and k move, Enter opens, x picks the row. */
  function norm(s) { return String(s || "").toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "").replace(/đ/g, "d"); }
  UI.norm = norm;
  var lives = {};
  function liveParam(id, k) { var p = new URLSearchParams(location.search); return p.get(id + "." + k); }
  function liveSave(id, vals) {
    var u = new URL(location.href);
    Object.keys(vals).forEach(function (k) { if (vals[k]) u.searchParams.set(id + "." + k, vals[k]); else u.searchParams.delete(id + "." + k); });
    try { history.replaceState(null, "", u); } catch (err) { /* some browsers refuse on file:// */ }
  }
  function Live(table) {
    var id = table.getAttribute("data-live"), self = this;
    this.id = id; this.table = table; this.tbody = $("tbody", table);
    this.rows = $$("tr[data-row]", this.tbody);
    this.rows.forEach(function (r, i) { r.__i = i; });
    var s = (liveParam(id, "sort") || table.getAttribute("data-live-sort") || "").split(":");
    this.sort = s[0] ? { key: s[0], dir: s[1] === "asc" ? 1 : -1 } : null;
    this.page = +(liveParam(id, "page") || 1);
    this.range = null; this.cur = -1;
    this.search = $('[data-live-search="' + id + '"]');
    if (this.search && liveParam(id, "q")) this.search.value = liveParam(id, "q");
    var tab = liveParam(id, "tab");
    if (tab != null) $$('[data-live-tab="' + id + '"]').forEach(function (t) { var on = t.getAttribute("data-v") === tab; t.setAttribute("aria-selected", String(on)); t.tabIndex = on ? 0 : -1; });
    if (this.sort) $$("th .sort", table).forEach(function (b) {
      var th = b.closest("th");
      if (b.getAttribute("data-sort") === self.sort.key) th.setAttribute("aria-sort", self.sort.dir > 0 ? "ascending" : "descending"); else th.removeAttribute("aria-sort");
    });
    if ($("thead tr", table)) sortIcons($("thead tr", table));
  }
  Live.prototype.value = function (r, key) { return r.getAttribute("data-k-" + key) || ""; };
  Live.prototype.match = function (r, skipTab) {
    var id = this.id;
    if (this.search && this.search.value.trim()) {
      /* data-live-search-in="td.main" narrows the search to those cells (plus data-find), so "Lan" does not match "lần đầu" */
      var scope = this.table.getAttribute("data-live-search-in"), text = scope ? $$(scope, r).map(function (c) { return c.textContent; }).join(" ") : r.textContent;
      var words = norm(this.search.value).split(/\s+/).filter(Boolean), hay = norm(text + " " + (r.getAttribute("data-find") || ""));
      for (var w = 0; w < words.length; w++) if (hay.indexOf(words[w]) < 0) return false;
    }
    if (!skipTab) {
      var t = $('[data-live-tab="' + id + '"][aria-selected="true"]');
      if (t && t.getAttribute("data-v") && r.getAttribute("data-f-" + t.getAttribute("data-f")) !== t.getAttribute("data-v")) return false;
    }
    var groups = {};
    $$('button.filter[data-live-filter="' + id + '"][aria-pressed="true"]').forEach(function (b) { (groups[b.getAttribute("data-f")] = groups[b.getAttribute("data-f")] || []).push(b.getAttribute("data-v")); });
    for (var f in groups) if (groups[f].indexOf(r.getAttribute("data-f-" + f)) < 0) return false;
    var sels = $$('[data-live-select="' + id + '"]');
    for (var i = 0; i < sels.length; i++) if (sels[i].value && r.getAttribute("data-f-" + sels[i].getAttribute("data-f")) !== sels[i].value) return false;
    if (this.range) {
      var d = r.getAttribute("data-date");
      if (d && (d.slice(0, 10) < this.range.from || d.slice(0, 10) > this.range.to)) return false;
    }
    return true;
  };
  Live.prototype.draw = function () {
    var self = this, id = this.id;
    $$('[data-live-tab="' + id + '"]').forEach(function (t) {
      var c = $(".count", t); if (!c) return;
      var f = t.getAttribute("data-f"), v = t.getAttribute("data-v");
      c.textContent = self.rows.filter(function (r) { return self.match(r, true) && (!v || r.getAttribute("data-f-" + f) === v); }).length;
    });
    var list = this.rows.filter(function (r) { return self.match(r); });
    if (this.sort) {
      var k = this.sort.key, d = this.sort.dir;
      list.sort(function (a, b) {
        var x = self.value(a, k), y = self.value(b, k), nx = parseFloat(x), ny = parseFloat(y);
        if (!isNaN(nx) && !isNaN(ny) && /^-?[\d.]+$/.test(x) && /^-?[\d.]+$/.test(y)) { x = nx; y = ny; } else { x = norm(x); y = norm(y); }
        return x < y ? -d : x > y ? d : a.__i - b.__i;
      });
    } else list.sort(function (a, b) { return a.__i - b.__i; });
    var pager = $('[data-live-pager="' + id + '"]'), size = pager ? +pager.getAttribute("data-size") || 20 : 1e9;
    var pages = Math.max(1, Math.ceil(list.length / size));
    this.page = Math.min(Math.max(1, this.page), pages);
    var shown = list.slice((this.page - 1) * size, this.page * size);
    this.rows.forEach(function (r) { r.hidden = true; r.classList.remove("is-cur"); });
    shown.forEach(function (r) { r.hidden = false; self.tbody.appendChild(r); });
    this.shown = shown; this.matches = list; this.cur = -1;
    var noun = pager ? pager.getAttribute("data-noun") || "dòng" : "dòng";
    if (pager) {
      var from = list.length ? (this.page - 1) * size + 1 : 0, to = Math.min(list.length, this.page * size);
      pager.innerHTML = "<span>" + (list.length ? from + "-" + to + " trong " + list.length + " " + noun : "Không có " + noun + " nào khớp") + "</span>" +
        (pages > 1 ? '<span class="spacer"></span><button class="btn sm icon" type="button" data-live-page="-1" aria-label="Trang trước"' + (this.page <= 1 ? " disabled" : "") + ">" + UI.icon("chevron-left", "sm") + "</button>" +
          '<span class="nowrap">Trang ' + this.page + " trên " + pages + "</span>" +
          '<button class="btn sm icon" type="button" data-live-page="1" aria-label="Trang sau"' + (this.page >= pages ? " disabled" : "") + ">" + UI.icon("chevron-right", "sm") + "</button>" : "");
    }
    $$('[data-live-count="' + id + '"]').forEach(function (el) { el.textContent = list.length + " " + noun; });
    $$('[data-live-empty="' + id + '"]').forEach(function (el) { el.hidden = list.length > 0; });
    var t = $('[data-live-tab="' + id + '"][aria-selected="true"]');
    liveSave(id, { q: this.search ? this.search.value.trim() : "", tab: t ? t.getAttribute("data-v") : "", sort: this.sort ? this.sort.key + ":" + (this.sort.dir > 0 ? "asc" : "desc") : "", page: this.page > 1 ? String(this.page) : "" });
    syncBulk(this.table);
    document.dispatchEvent(new CustomEvent("ui:live", { detail: { id: id, shown: shown, matches: list } }));
  };
  Live.prototype.move = function (d) {
    if (!this.shown.length) return;
    this.cur = Math.max(0, Math.min(this.shown.length - 1, this.cur < 0 ? (d > 0 ? 0 : this.shown.length - 1) : this.cur + d));
    this.shown.forEach(function (r, i) { r.classList.toggle("is-cur", i === this.cur); }, this);
    this.shown[this.cur].scrollIntoView({ block: "nearest" });
    document.dispatchEvent(new CustomEvent("ui:row", { detail: { id: this.id, row: this.shown[this.cur] } }));
  };
  Live.prototype.csv = function (name) {
    var heads = $$("thead th", this.table).map(function (th) { return th.textContent.trim(); });
    var ths = $$("thead th", this.table);
    var keep = heads.map(function (h, i) { return h && !ths[i].classList.contains("pick") && !ths[i].classList.contains("end"); });
    var lines = [heads.filter(function (h, i) { return keep[i]; })].concat(this.matches.map(function (r) {
      return $$("td", r).filter(function (td, i) { return keep[i]; }).map(function (td) { return td.innerText.replace(/\s*\n+\s*/g, " · ").trim(); });
    }));
    var text = "﻿" + lines.map(function (l) { return l.map(function (c) { return /[",\n]/.test(c) ? '"' + c.replace(/"/g, '""') + '"' : c; }).join(","); }).join("\n");
    var a = document.createElement("a");
    a.href = URL.createObjectURL(new Blob([text], { type: "text/csv;charset=utf-8" }));
    a.download = (name || this.id) + ".csv";
    document.body.appendChild(a); a.click(); a.remove();
    UI.toast("Đã xuất " + this.matches.length + " dòng ra " + a.download);
  };
  UI.live = function (id) { return lives[id]; };
  function liveOf(el, attr) { return lives[el.getAttribute(attr)]; }
  document.addEventListener("input", function (e) {
    var l = e.target.hasAttribute && e.target.hasAttribute("data-live-search") && liveOf(e.target, "data-live-search");
    if (l) { l.page = 1; l.draw(); }
  });
  document.addEventListener("change", function (e) {
    var l = e.target.hasAttribute && e.target.hasAttribute("data-live-select") && liveOf(e.target, "data-live-select");
    if (l) { l.page = 1; l.draw(); }
  });
  document.addEventListener("ui:tab", function (e) { var l = e.detail.tab.hasAttribute("data-live-tab") && liveOf(e.detail.tab, "data-live-tab"); if (l) { l.page = 1; l.draw(); } });
  document.addEventListener("ui:press", function (e) { var l = e.detail.button.hasAttribute("data-live-filter") && liveOf(e.detail.button, "data-live-filter"); if (l) { l.page = 1; l.draw(); } });
  document.addEventListener("ui:sort", function (e) {
    var th = $$("th .sort").filter(function (b) { return b.getAttribute("data-sort") === e.detail.key; })[0];
    var table = th && th.closest("table[data-live]"), l = table && lives[table.getAttribute("data-live")];
    if (l) { l.sort = { key: e.detail.key, dir: e.detail.dir === "ascending" ? 1 : -1 }; l.page = 1; l.draw(); }
  });
  document.addEventListener("click", function (e) {
    var pg = e.target.closest("[data-live-page]");
    if (pg) { var l = liveOf(pg.closest("[data-live-pager]"), "data-live-pager"); if (l) { l.page += +pg.getAttribute("data-live-page"); l.draw(); } return; }
    var rs = e.target.closest("[data-live-reset]");
    if (rs) {
      var lr = liveOf(rs, "data-live-reset"); if (!lr) return;
      if (lr.search) lr.search.value = "";
      $$('button.filter[data-live-filter="' + lr.id + '"]').forEach(function (b) { b.setAttribute("aria-pressed", "false"); });
      $$('[data-live-select="' + lr.id + '"]').forEach(function (s) { s.value = ""; });
      lr.page = 1; lr.draw(); return;
    }
    var cv = e.target.closest("[data-live-csv]");
    if (cv) { var lc = liveOf(cv, "data-live-csv"); if (lc) lc.csv(cv.getAttribute("data-name")); return; }
    /* a click anywhere on a row opens it, through the row's own open button or link */
    var tr = e.target.closest("table[data-live] tr[data-row]");
    if (tr && !e.target.closest("a, button, input, label, select")) { var go = $(".end [data-open], .end a, .end button", tr); if (go) go.click(); }
  });
  document.addEventListener("keydown", function (e) {
    var t = e.target, typing = t && (t.isContentEditable || /^(INPUT|TEXTAREA|SELECT)$/.test(t.tagName));
    if (typing || e.ctrlKey || e.metaKey || e.altKey || $("dialog[open]")) return;
    var l = lives[Object.keys(lives)[0]];
    if (!l) return;
    if (e.key === "/" && l.search) { e.preventDefault(); l.search.focus(); }
    else if (e.key === "j") { e.preventDefault(); l.move(1); }
    else if (e.key === "k") { e.preventDefault(); l.move(-1); }
    else if (e.key === "Enter" && l.cur >= 0) { e.preventDefault(); var go = $(".end [data-open], .end a, .end button", l.shown[l.cur]); if (go) go.click(); }
    else if (e.key === "x" && l.cur >= 0) { var box = $(".pick input", l.shown[l.cur]); if (box) { box.checked = !box.checked; box.dispatchEvent(new Event("change", { bubbles: true })); } }
  });

  /* ---------- Date range picker: <div class="period" data-period="req" data-default="30d"></div> ----------
     Presets, or two dates of your own. Today comes from <body data-today="2026-10-07"> on a prototype with fixed data.
     The choice stays in the address (req.p, or req.from and req.to) and fires ui:period {id, from, to, label}. */
  function today() {
    var t = document.body.getAttribute("data-today");
    var d = t ? new Date(t + "T00:00:00") : new Date(); d.setHours(0, 0, 0, 0); return d;
  }
  function addDays(d, n) { var x = new Date(d); x.setDate(x.getDate() + n); return x; }
  function isoDay(d) { return d.getFullYear() + "-" + ("0" + (d.getMonth() + 1)).slice(-2) + "-" + ("0" + d.getDate()).slice(-2); }
  function dm(d) { return ("0" + d.getDate()).slice(-2) + "/" + ("0" + (d.getMonth() + 1)).slice(-2); }
  var CMP = [["prev", "Kỳ liền trước"], ["year", "Cùng kỳ năm trước"], ["none", "Không so sánh"]];
  var PRESETS = [
    ["today", "Hôm nay", function (t) { return [t, t]; }],
    ["yesterday", "Hôm qua", function (t) { var y = addDays(t, -1); return [y, y]; }],
    ["7d", "7 ngày qua", function (t) { return [addDays(t, -6), t]; }],
    ["30d", "30 ngày qua", function (t) { return [addDays(t, -29), t]; }],
    ["month", "Tháng này", function (t) { return [new Date(t.getFullYear(), t.getMonth(), 1), t]; }],
    ["lastmonth", "Tháng trước", function (t) { return [new Date(t.getFullYear(), t.getMonth() - 1, 1), new Date(t.getFullYear(), t.getMonth(), 0)]; }],
    ["quarter", "Quý này", function (t) { return [new Date(t.getFullYear(), Math.floor(t.getMonth() / 3) * 3, 1), t]; }],
    ["year", "Năm nay", function (t) { return [new Date(t.getFullYear(), 0, 1), t]; }],
    ["all", "Mọi lúc", function () { return [new Date(2000, 0, 1), new Date(2100, 0, 1)]; }]
  ];
  function Period(box) {
    var id = box.getAttribute("data-period"), self = this, t = today();
    this.id = id; this.box = box;
    var p = liveParam(id, "p") || box.getAttribute("data-default") || "30d", f = liveParam(id, "from"), to = liveParam(id, "to");
    this.sel = f && to ? { preset: "custom", from: f, to: to } : this.preset(p);
    this.sel.cmp = box.hasAttribute("data-compare") ? liveParam(id, "cmp") || "prev" : "none";
    box.innerHTML = '<button class="btn period-btn" type="button" aria-haspopup="dialog" aria-expanded="false">' + UI.icon("calendar", "sm") +
      '<span class="period-txt"><b></b><small></small></span>' + UI.icon("chevron-down", "sm") + "</button>" +
      '<div class="period-pop" role="dialog" aria-label="Chọn khoảng thời gian" hidden><ul class="period-presets">' +
      PRESETS.map(function (x) {
        var r = x[2](t), label = x[0] === "all" ? "" : r[0].getTime() === r[1].getTime() ? dm(r[0]) : dm(r[0]) + " đến " + dm(r[1]);
        return '<li><button type="button" data-preset="' + x[0] + '">' + UI.icon("check", "sm") + "<span>" + x[1] + "</span><small>" + label + "</small></button></li>";
      }).join("") +
      '<li><button type="button" data-preset="custom">' + UI.icon("check", "sm") + "<span>Tự chọn ngày</span><small></small></button></li></ul>" +
      '<div class="period-dates"><label class="field"><span class="label">Từ ngày</span><input class="input" type="text" inputmode="numeric" maxlength="10" placeholder="dd/mm/yyyy" data-p-from></label>' +
      '<label class="field"><span class="label">Đến ngày</span><input class="input" type="text" inputmode="numeric" maxlength="10" placeholder="dd/mm/yyyy" data-p-to></label>' +
      '<p class="error-text" data-p-err hidden></p>' +
      (box.hasAttribute("data-compare") ? '<fieldset class="period-cmp"><legend class="label">So sánh với</legend>' + CMP.map(function (c) {
        return '<label class="check"><input type="radio" name="' + id + '-cmp" value="' + c[0] + '">' + c[1] + "</label>";
      }).join("") + '<p class="small muted" data-p-cmp></p></fieldset>' : "") +
      '<div class="row tight end"><button class="btn sm" type="button" data-p-cancel>Huỷ</button><button class="btn sm primary" type="button" data-p-apply>Áp dụng</button></div></div></div>';
    var btn = $(".period-btn", box), pop = $(".period-pop", box), fIn = $("[data-p-from]", box), tIn = $("[data-p-to]", box), err = $("[data-p-err]", box);
    /* dates read day/month/year, as people write them in Vietnam; slashes come in by themselves */
    function toIso(v) {
      var m = String(v || "").trim().match(/^(\d{1,2})\/(\d{1,2})\/(\d{4})$/);
      if (!m) return "";
      var d = new Date(+m[3], +m[2] - 1, +m[1]);
      return d.getDate() === +m[1] && d.getMonth() === +m[2] - 1 ? isoDay(d) : "";
    }
    function toDmy(iso) { return iso ? iso.slice(8, 10) + "/" + iso.slice(5, 7) + "/" + iso.slice(0, 4) : ""; }
    [fIn, tIn].forEach(function (inp) {
      inp.addEventListener("input", function () {
        var v = inp.value.replace(/[^0-9]/g, "").slice(0, 8);
        inp.value = v.length > 4 ? v.slice(0, 2) + "/" + v.slice(2, 4) + "/" + v.slice(4) : v.length > 2 ? v.slice(0, 2) + "/" + v.slice(2) : v;
      });
    });
    function mark(preset) { $$("[data-preset]", box).forEach(function (b) { b.setAttribute("aria-pressed", String(b.getAttribute("data-preset") === preset)); }); }
    function open(v) {
      pop.hidden = !v; btn.setAttribute("aria-expanded", String(v));
      if (v) {
        mark(self.sel.preset); fIn.value = self.sel.preset === "all" ? "" : toDmy(self.sel.from); tIn.value = self.sel.preset === "all" ? "" : toDmy(self.sel.to); err.hidden = true;
        /* open toward the side with room */
        $$(".period-cmp input", box).forEach(function (r) { r.checked = r.value === self.sel.cmp; });
        pop.classList.remove("end");
        if (pop.getBoundingClientRect().right > innerWidth - 8) pop.classList.add("end");
        ($('[data-preset][aria-pressed="true"]', box) || fIn).focus();
      }
    }
    btn.addEventListener("click", function (e) { e.stopPropagation(); open(pop.hidden); });
    document.addEventListener("click", function (e) { if (!pop.hidden && !box.contains(e.target)) open(false); });
    box.addEventListener("keydown", function (e) { if (e.key === "Escape" && !pop.hidden) { e.stopPropagation(); open(false); btn.focus(); } });
    $$("[data-preset]", box).forEach(function (b) {
      b.addEventListener("click", function () {
        var k = b.getAttribute("data-preset");
        if (k === "custom") { mark("custom"); fIn.focus(); return; }
        var ns = self.preset(k); ns.cmp = self.cmpChoice(); self.set(ns); open(false); btn.focus();
      });
    });
    $("[data-p-cancel]", box).addEventListener("click", function () { open(false); btn.focus(); });
    /* the comparison applies at once to the range already chosen */
    $$(".period-cmp input", box).forEach(function (r) { r.addEventListener("change", function () { var ns = Object.assign({}, self.sel); ns.cmp = r.value; self.set(ns); }); });
    $("[data-p-apply]", box).addEventListener("click", function () {
      var a = toIso(fIn.value), z = toIso(tIn.value);
      if (!a || !z) { err.hidden = false; err.textContent = "Nhập ngày theo dạng ngày/tháng/năm, ví dụ " + toDmy(isoDay(addDays(t, -6))) + "."; return; }
      if (a > z) { err.hidden = false; err.textContent = "Ngày bắt đầu phải trước hoặc bằng ngày kết thúc."; return; }
      if (z > isoDay(t)) { err.hidden = false; err.textContent = "Ngày kết thúc không được sau hôm nay, " + toDmy(isoDay(t)) + "."; return; }
      self.set({ preset: "custom", from: a, to: z, cmp: self.cmpChoice() }); open(false); btn.focus();
    });
    this.paint();
  }
  /* comparison: the period just before with the same length (for Tháng này, Quý này, Năm nay: the same days of the
     previous month, quarter or year, as Shopify and Sapo do), the same dates last year, or none */
  function parseIso(s) { return new Date(s + "T00:00:00"); }
  function shiftMonths(d, n) { var x = new Date(d.getFullYear(), d.getMonth() - n, 1); x.setDate(Math.min(d.getDate(), new Date(x.getFullYear(), x.getMonth() + 1, 0).getDate())); return x; }
  Period.prototype.cmpChoice = function () { var r = $(".period-cmp input:checked", this.box); return r ? r.value : this.sel.cmp; };
  Period.prototype.compare = function () {
    var s = this.sel, f = parseIso(s.from), t = parseIso(s.to);
    if (!s.cmp || s.cmp === "none" || s.preset === "all") return null;
    if (s.cmp === "year") return [isoDay(new Date(f.getFullYear() - 1, f.getMonth(), f.getDate())), isoDay(new Date(t.getFullYear() - 1, t.getMonth(), t.getDate()))];
    if (s.preset === "month") return [isoDay(shiftMonths(f, 1)), isoDay(shiftMonths(t, 1))];
    if (s.preset === "quarter") return [isoDay(shiftMonths(f, 3)), isoDay(shiftMonths(t, 3))];
    if (s.preset === "year") return [isoDay(new Date(f.getFullYear() - 1, 0, 1)), isoDay(new Date(t.getFullYear() - 1, t.getMonth(), t.getDate()))];
    var len = Math.round((t - f) / 864e5) + 1;
    return [isoDay(addDays(f, -len)), isoDay(addDays(f, -1))];
  };
  Period.prototype.preset = function (k) {
    var x = PRESETS.filter(function (p) { return p[0] === k; })[0] || PRESETS[3], r = x[2](today());
    return { preset: x[0], from: isoDay(r[0]), to: isoDay(r[1]) };
  };
  Period.prototype.label = function () {
    var x = PRESETS.filter(function (p) { return p[0] === this.sel.preset; }, this)[0];
    var f = new Date(this.sel.from + "T00:00:00"), t = new Date(this.sel.to + "T00:00:00");
    return { name: x ? x[1] : "Tự chọn", range: this.sel.preset === "all" ? "" : this.sel.from === this.sel.to ? dm(f) + "/" + f.getFullYear() : dm(f) + " đến " + dm(t) + "/" + t.getFullYear() };
  };
  Period.prototype.paint = function () {
    var l = this.label();
    $(".period-txt b", this.box).textContent = l.name;
    $(".period-txt small", this.box).textContent = l.range;
    var c = this.compare();
    var d = { id: this.id, from: this.sel.from, to: this.sel.to, preset: this.sel.preset, label: l.name, range: l.range,
      cmp: this.sel.cmp, cmpFrom: c ? c[0] : null, cmpTo: c ? c[1] : null,
      cmpRange: c ? (c[0] === c[1] ? dm(parseIso(c[0])) + "/" + c[0].slice(0, 4) : dm(parseIso(c[0])) + " đến " + dm(parseIso(c[1])) + "/" + c[1].slice(0, 4)) : "" };
    var note = $("[data-p-cmp]", this.box);
    if (note) note.textContent = d.cmpRange ? "Kỳ so sánh: " + d.cmpRange : "";
    $$('[data-period-note="' + this.id + '"]').forEach(function (el) { el.textContent = (d.range ? "Từ " + d.range : "Mọi lúc") + (d.cmpRange ? ", so với " + d.cmpRange : "") + "."; });
    var live = lives[this.id];
    if (live) { live.range = this.sel.preset === "all" ? null : { from: this.sel.from, to: this.sel.to }; live.page = 1; live.draw(); }
    document.dispatchEvent(new CustomEvent("ui:period", { detail: d }));
  };
  Period.prototype.set = function (sel) {
    this.sel = sel;
    var keep = sel.preset === "custom" ? { p: "", from: sel.from, to: sel.to } : { p: sel.preset, from: "", to: "" };
    if (this.box.hasAttribute("data-compare")) keep.cmp = sel.cmp === "prev" ? "" : sel.cmp;
    liveSave(this.id, keep);
    this.paint();
  };

  /* ---------- Quick find: Ctrl K, or any [data-cmdk] button ----------
     Finds the pages in the sidebar and the records in window.UI_FIND: [{group, label, sub, href, find}]. */
  function quickFind() {
    var dlg = document.createElement("dialog");
    dlg.className = "cmdk";
    dlg.setAttribute("aria-label", "Tìm nhanh");
    dlg.innerHTML = '<label class="search">' + UI.icon("search", "sm") + '<span class="sr-only">Tìm nhanh</span><input class="input" type="search" placeholder="Tìm trang, khách, người dùng" data-cmdk-q></label><ul class="cmdk-list" role="listbox"></ul>' +
      '<p class="cmdk-foot"><span><kbd>Lên</kbd><kbd>Xuống</kbd> chọn</span><span><kbd>Enter</kbd> mở</span><span><kbd>Esc</kbd> đóng</span></p>';
    document.body.appendChild(dlg);
    var input = $("[data-cmdk-q]", dlg), list = $(".cmdk-list", dlg), sel = 0;
    var pages = $$(".sidebar a.side-link").map(function (a) {
      var u = $("use", a);
      return { group: "Trang", label: a.textContent.trim().replace(/\s*\d+$/, ""), href: a.getAttribute("href"), icon: u ? u.getAttribute("href").replace("#i-", "") : "" };
    });
    function draw() {
      var q = norm(input.value.trim()), html = "", items = [];
      var recs = (window.UI_FIND || []).filter(function (r) { return q && norm(r.label + " " + (r.sub || "") + " " + (r.find || "")).indexOf(q) >= 0; }).slice(0, 8);
      var pg = pages.filter(function (p) { return !q || norm(p.label).indexOf(q) >= 0; });
      var groups = {};
      recs.concat(pg).forEach(function (r) { (groups[r.group] = groups[r.group] || []).push(r); });
      Object.keys(groups).forEach(function (g) {
        html += '<li class="cmdk-group" role="presentation">' + g + "</li>";
        groups[g].forEach(function (r) {
          items.push(r);
          html += '<li><a role="option" href="' + r.href + '">' + UI.icon(r.icon || "search", "sm") + "<span>" + r.label.replace(/</g, "&lt;") + "</span>" + (r.sub ? "<small>" + r.sub.replace(/</g, "&lt;") + "</small>" : "") + "</a></li>";
        });
      });
      list.innerHTML = html || '<li class="cmdk-empty">Không có kết quả cho "' + input.value.replace(/</g, "&lt;") + '"</li>';
      sel = 0; mark();
    }
    function links() { return $$("a", list); }
    function mark() { links().forEach(function (a, i) { a.setAttribute("aria-selected", String(i === sel)); if (i === sel) a.scrollIntoView({ block: "nearest" }); }); }
    function open() { if (dlg.open) return; input.value = ""; draw(); dlg.showModal(); input.focus(); }
    UI.quickFind = open;
    input.addEventListener("input", draw);
    input.addEventListener("keydown", function (e) {
      var ls = links();
      if (e.key === "ArrowDown") { e.preventDefault(); sel = Math.min(ls.length - 1, sel + 1); mark(); }
      else if (e.key === "ArrowUp") { e.preventDefault(); sel = Math.max(0, sel - 1); mark(); }
      else if (e.key === "Enter" && ls[sel]) { e.preventDefault(); location.href = ls[sel].getAttribute("href"); }
      /* a search field clears itself on Escape; here Escape closes the finder at once */
      else if (e.key === "Escape") { e.preventDefault(); dlg.close(); }
    });
    document.addEventListener("keydown", function (e) {
      if ((e.ctrlKey || e.metaKey) && (e.key === "k" || e.key === "K")) { e.preventDefault(); open(); }
    });
    document.addEventListener("click", function (e) { if (e.target.closest("[data-cmdk]")) { e.preventDefault(); open(); } });
  }

  /* ---------- Settings nav: the section in view is marked current while the page scrolls ---------- */
  function settingsSpy() {
    if (!("IntersectionObserver" in window)) return;
    $$(".settings-nav").forEach(function (nav) {
      var links = $$('a[href^="#"]', nav);
      var secs = links.map(function (a) { return document.getElementById(a.getAttribute("href").slice(1)); }).filter(Boolean);
      var seen = {};
      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (en) { seen[en.target.id] = en.isIntersecting; });
        var cur = secs.filter(function (x) { return seen[x.id]; })[0];
        if (!cur) return;
        links.forEach(function (a) { if (a.getAttribute("href") === "#" + cur.id) a.setAttribute("aria-current", "true"); else a.removeAttribute("aria-current"); });
      }, { rootMargin: "-15% 0px -55% 0px" });
      secs.forEach(function (x) { io.observe(x); });
    });
  }

  /* ---------- Start ---------- */
  function start() {
    mountIcons();
    var m = /[?&]state=([\w-]+)/.exec(location.search);
    UI.setState(m ? m[1] : UI.states()[0]);
    $$("table.data[data-bulk]").forEach(syncBulk);
    fitFrames();
    settingsSpy();
    /* live tables first, then the date pickers that filter them, then the tables without a picker */
    $$("table[data-live]").forEach(function (t) { lives[t.getAttribute("data-live")] = new Live(t); });
    $$("[data-period]").forEach(function (b) { new Period(b); });
    Object.keys(lives).forEach(function (k) { if (!$('[data-period="' + k + '"]')) lives[k].draw(); });
    if ($(".sidebar") || window.UI_FIND || $("[data-cmdk]")) quickFind();
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start);
  else start();
})();
