# Components of the kit

Every class lives in `kit/app.css`; `gallery/index.html` shows each one in its states. Copy the markup below
and change the words. Icons: `<svg class="ico" aria-hidden="true"><use href="#i-NAME"/></svg>`, names in
`kit/icons.js` (`.ico.sm` 16 px, `.ico.lg` 28 px). Behaviour comes from `kit/app.js` through data attributes.

## Buttons

```html
<button class="btn" type="button">Xuất CSV</button>                         <!-- outline: the default -->
<button class="btn primary" type="button">Tạo đơn</button>                  <!-- one per view, one per dialog -->
<button class="btn quiet" type="button">Bỏ qua</button>                      <!-- low weight, in toolbars -->
<button class="btn danger" type="button">Huỷ đơn</button>                    <!-- opens the confirm dialog -->
<button class="btn danger solid" type="button">Huỷ đơn</button>             <!-- only as the confirm inside that dialog -->
<button class="btn icon quiet" type="button" aria-label="Thêm thao tác"><svg class="ico"><use href="#i-more"/></svg></button>
<button class="link" type="button">Sửa</button>                              <!-- an action inside text -->
<a class="back" href="table.html"><svg class="ico sm"><use href="#i-arrow-left"/></svg>Đơn hàng</a>
```
Default 36 px; `.sm` 32 px in rows and toolbars, `.lg` 40 px for a lone call to action. The primary takes
`--primary` (brand colour or near-black, `theme.py --primary`). `.block` fills the width.
An icon goes left of the label when the glyph names the action (download, plus, external); never an arrow after.
Danger is red because it deletes, ends something running or takes away access; anything else is outline.

## Status, counts, badges

```html
<span class="status ok"><svg class="ico"><use href="#i-check-circle"/></svg>Đã giao</span>
<span class="status warn"><svg class="ico"><use href="#i-clock"/></svg>Chờ xác nhận</span>
<span class="status bad"><svg class="ico"><use href="#i-x-circle"/></svg>Đã huỷ</span>
<span class="status run"><svg class="ico spin"><use href="#i-loader"/></svg>Đang tạo</span>
<span class="count">128</span> <span class="count new">6</span>              <!-- a number beside a tab or link -->
<span class="badge">Mặc định</span> <span class="badge accent">Mới</span>     <!-- a short tag, used sparingly -->
```
A status is a soft pill with its word (an icon inside is optional), as in Browserbase and Airtable. One table of
status words and colours for the whole product: done `ok`, waiting `warn`, failed or cancelled `bad`, running
`run`, anything neutral without a class.

## Frames

Top bar (end-user area): `header.topbar > a.logo + nav.topnav + .top-right`, then `main.page` (`.narrow` 760 px,
`.wide` 1360 px). Sidebar (admin area): `.app-side > nav.sidebar + .side-main > header.side-top + main.side-page`;
links are `a.side-link` with an icon, a `span` label and an optional `.count`; groups start with `p.side-group`;
the current page has `aria-current="page"`. Under 860 px the sidebar slides in from `[data-side-toggle]`.
Copy both frames from the recipes; they carry the account menu and the mobile bar.

## Page heads and sections

```html
<div class="page-head">
  <div><h1>Đơn hàng</h1><p class="sub">128 đơn trong 30 ngày qua.</p></div>
  <div class="actions"><button class="btn">Xuất CSV</button><a class="btn primary" href="#">Tạo đơn</a></div>
</div>
<section class="section"><div class="section-head"><h2>Đơn mới nhất</h2><a href="table.html">Xem tất cả</a></div>…</section>
```
A record page uses `.record-head` (h1, `.meta` line with the status, `.actions`).

## Panels, cards, notices

`.panel` (`.pad` for 20 px inside) and `.card` with `.card-head` (h2 + an action), `.card-body`, `.card-foot`.
A card is a container, not decoration: no grid of cards that lead nowhere.

```html
<div class="notice warn"><svg class="ico"><use href="#i-alert"/></svg>
  <div class="grow"><strong>Hôm nay đã dùng hết 5 lần tạo</strong>Lượt mới có lúc 00:00.</div></div>
```
Notice kinds: none (information, accent), `ok`, `warn`, `bad`: a soft flat fill and the icon in the status
colour, no border and no side stripe. One notice per screen at most; put it on top.

## Forms

```html
<div class="field">
  <label class="label" for="name">Tên cửa hàng<span class="req" aria-hidden="true">*</span></label>
  <span class="hint" id="name-hint">Hiện trên đầu website và trong email gửi khách.</span>
  <input class="input" id="name" aria-describedby="name-hint">
</div>
<div class="field">
  <label class="label" for="cat">Ngành hàng</label>
  <div class="select-wrap"><select class="select" id="cat">…</select><svg class="ico sm"><use href="#i-chevron-down"/></svg></div>
</div>
<div class="field">
  <label class="label" for="phone">Số điện thoại</label>
  <input class="input" id="phone" aria-invalid="true" aria-describedby="phone-err">
  <p class="error-text" id="phone-err"><svg class="ico sm"><use href="#i-alert"/></svg>Số điện thoại cần 10 chữ số.</p>
</div>
```
Also: `.textarea`, `.grid-2` / `.grid-3` for fields side by side (one column under 640 px; `.grid-3.wide-first` for line items whose first field is a name), `.input-unit.range` for a from-to pair in one control column (use selects in 24-hour steps for times; `type="time"` shows 12-hour SA/CH on some machines and does not fit), `.label .opt` for
"không bắt buộc", `.search` (a label wrapping an icon and `input.input[type=search]`), `.input-unit` (input +
unit word), `.check` (checkbox or radio with its label, `.sub` for a second line), `.switch`, `.tags` with
`.tag-item`, `.form-actions` (outline back, `.spacer`, `.autosave`, the primary). Inputs have a surface fill and
a visible border; a field is never transparent on the page background.

## Choices, tabs, filters

- `.options > label.option` with a radio or checkbox, `.o-title`, `.o-desc`, `.o-note`; `.option.pic` adds a picture. The checked option is outlined in dark. For a choice judged by its look (a style, a template), put the picture above
  the words with `<img class="o-pic">` inside the option's text block.
- `.palettes` > `label.palette` (a hidden radio, `.chips` with one `<i data-c="#hex">` per colour, `.p-name`): pick a colour set, as in Podia and The Leap; add one `.palette` holding `<input type="color">` for a colour of your own, and offer "Lấy màu từ logo". Never ask for a typed hex code.
- `.option .o-frame` > `.vp[data-w]` > iframe: a live preview inside an option card, for choices whose result is the user's own page (a style, a layout). Show their name and content, not another company's site.
- `.seg` (one choice of two to four, `aria-pressed`), for views: Máy tính / Điện thoại, Hôm nay / 7 ngày. When each view is a state of the page (the review recipe draws `desktop` and `mobile`), give each button `data-to-state="<state>"`: a click opens that state and keeps it in the address. A seg that only presses buttons shows nothing new, so never leave a view switch unwired.
- `.tabs[role=tablist]` with `button[role=tab][aria-selected]` and a `.count`; links work too (`a[role=tab]`).
- `.toolbar` holds `.search` and `.filters`; a `button.filter[aria-pressed]` toggles; a filter with options opens a `.menu` of `.check` boxes.

## Tables

```html
<div class="table-box">
  <div class="bulk" id="bulk-x" hidden><strong><span data-bulk-count>0</span> đã chọn</strong>…<button class="btn sm quiet" data-bulk-clear>Bỏ chọn</button></div>
  <table class="data cards" data-bulk="bulk-x">
    <thead><tr><th class="pick"><input type="checkbox" data-select-all aria-label="Chọn tất cả"></th><th>Đơn</th><th class="num">Tổng tiền</th><th class="end"><span class="sr-only">Thao tác</span></th></tr></thead>
    <tbody><tr><td class="pick"><input type="checkbox" aria-label="Chọn đơn DH1042"></td>
      <td class="main"><a href="#">DH1042</a><span class="sub">Lê Minh Châu</span></td>
      <td class="num" data-label="Tổng tiền">2.490.000 đ</td><td class="end"><a class="btn sm" href="#">Xem</a></td></tr></tbody>
  </table>
  <nav class="pager" aria-label="Phân trang">…</nav>
</div>
```
`.cards` turns each row into a block under 640 px; every cell then needs `data-label`, and a cell holding a value plus a
`.sub` line wraps both in one `<div>` so they stay together on the right. Numbers use `.num`
(right aligned, tabular). Sortable headers: `th > button.sort[data-sort]`, `aria-sort` on the th. Row hover and
the selected row are drawn by the kit.

### Live tables: search, tabs, filters, sort, date range, pages, CSV, keys

A list that people work through (requests, orders, users) should behave like a real admin, as the ecommerce-builder
admin does: give the table `data-live="<id>"` and the kit does the rest from data attributes, with no page script.

```html
<div class="tabs" role="tablist" aria-label="Giai đoạn">
  <button role="tab" aria-selected="true" type="button" data-live-tab="req" data-f="stage" data-v="">Tất cả <span class="count">0</span></button>
  <button role="tab" aria-selected="false" tabindex="-1" type="button" data-live-tab="req" data-f="stage" data-v="new">Mới <span class="count new">0</span></button>
</div>
<div class="toolbar">
  <label class="search">…<input class="input" type="search" placeholder="Tên, số điện thoại" data-live-search="req"></label>
  <div class="select-wrap"><select class="select" data-live-select="req" data-f="industry"><option value="">Mọi ngành</option>…</select>…</div>
  <div class="filters"><button class="filter" type="button" aria-pressed="false" data-live-filter="req" data-f="due" data-v="late">Quá giờ nhắc gọi</button></div>
  <span class="spacer"></span>
  <div class="period" data-period="req" data-default="30d"></div>
  <button class="btn" type="button" data-live-csv="req" data-name="yeu-cau">…Xuất CSV</button>
</div>
<div class="table-box">
  <table class="data cards" data-live="req" data-live-sort="sent:desc" data-live-search-in="td.main">
    <thead><tr><th><button class="sort" type="button" data-sort="name">Khách<svg class="ico" aria-hidden="true"><use href="#i-arrow-up-down"/></svg></button></th>…</tr></thead>
    <tbody><tr data-row data-date="2026-10-07T08:05" data-k-sent="2026-10-07T08:05" data-k-name="Nguyễn Minh Anh" data-f-stage="new" data-f-due="late" data-f-industry="Cửa hàng bán lẻ" data-find="minhanh@haidang.vn 0912345678">…</tr></tbody>
  </table>
  <div class="empty" data-live-empty="req" hidden>…<button class="btn sm" type="button" data-live-reset="req">Xoá tìm kiếm và bộ lọc</button></div>
  <nav class="pager" aria-label="Phân trang" data-live-pager="req" data-size="8" data-noun="yêu cầu"></nav>
</div>
```

- Search ignores Vietnamese marks ("diep" finds Diệp). `data-live-search-in` limits it to some cells plus `data-find`,
  so a name search does not match words in other columns.
- Tabs count live, with the other filters applied. Filters with the same `data-f` are "any of", different ones "all of".
- `data-k-<key>` is the sort value; numbers sort as numbers. The header icon follows the order.
- Search, tab, sort, page and date range stay in the address (`?req.q=…&req.sort=name:asc`), so a link or a reload opens
  the same view, and the quick finder can link straight to a record.
- Click anywhere on a row to open it (through the row's `.end` button or link). Keys: `/` search, `j` and `k` move,
  Enter opens, `x` picks the row. `[data-live-count="req"]` shows "8 yêu cầu"; `ui:live` fires after each draw.
- `data-period` draws the date range picker: Hôm nay, Hôm qua, 7 ngày qua, 30 ngày qua, Tháng này, Tháng trước, Quý này,
  Năm nay, Mọi lúc, or two dates typed as ngày/tháng/năm. It filters rows by `data-date` and fires `ui:period`. A
  prototype with fixed data sets `<body data-today="2026-10-07">`.
- Quick find (Ctrl K, or any `[data-cmdk]` button such as a "Tìm nhanh" side link with `<kbd>Ctrl K</kbd>`) searches the
  sidebar pages and the records a page lists in `window.UI_FIND = [{group, label, sub, href, find, icon}]`.

## Lists of records

`ul.list > li.list-item` with `.thumb` (an `img` or two words when there is none), a text block (`.item-title`,
`.item-meta`), a status, and `.item-actions` (one outline button and a `.menu` behind a quiet icon button).
`.list-item.no-thumb` drops the picture column. `.bar > i` with `style="width:40%"` is a progress bar
(`.ok`, `.warn`, `.bad`). `.plain-list` is a list with lines and no box. `.avatar` (`.sm`, `.lg`) holds initials
or a photo; `.who` pairs it with a name.

## One record

`dl.kv` (label column 180 px, one column on phones; `.kv.stacked` puts each label above its value for a narrow side column; `dd.unset` for a missing value written as "Chưa có"),
`.stepper` (horizontal steps with `span` labels: `.done`, `.now`, `.fail`), `.timeline` (icon, text,
`time`), `.steps` (a vertical checklist of a job: `.done`, `.now`, `.fail`, `.sub` note), `.log` (time + line),
`details.more` for what most people do not need, `pre.tech` for technical detail.

## Figures and charts

`.figures > .figure` (`.f-label`, `.f-value`, `.f-delta` with `.up` / `.down`); four in a row, two on tablets;
`.figures.three` for three. `.attention > li` for a to-do list (icon in `.a-bad`, `.a-warn` or `.a-info`,
`.a-title`, `.a-sub`, one outline action). Which chart for which data, what an overview must have and how the date range works: `references/charts.md`. Charts are inline SVG drawn with `.chart` and the classes `.c1`
(accent), `.c2` (lighter accent, for the part still running such as today), `.cm` (muted, the comparison),
`.cb` (failures), `.l1` / `.lm` for lines, `.grid-line`; a `.legend` names each colour. Every chart has an axis
or labels that give the numbers; a chart without figures is decoration. SVG text scales with the
`viewBox`: set its width close to the narrowest box the chart sits in (about 400 for a half-width card) so
labels stay readable there.

## Wizard and preview

Wizard: `.wizard-top` (`.w-count` "Bước 2 trên 5" and a `.bar`), the question as h1, `.form-panel`,
`.review-group` blocks for the check step, `.form-actions` at the bottom. Preview: `.ws` workspace with
`.ws-main` (`.ws-bar`, `.ws-stage` holding `.dev-desktop` or, with `.mobile`, `.dev-phone`) and `.ws-side`
(plain sections such as notes and `.ver-list`). The one primary (Xuất bản, Duyệt) sits at the right end of
`.ws-bar`, as in GoDaddy, Webflow and Canva; the side column holds settings and history, never a coloured call-out box. Put the iframe in `.vp[data-w="1440"]`;
app.js scales it to the frame. `.expired` fills the stage when there is nothing to show. The phone is an
iPhone frame: `.dev-phone[data-screen="dark|light"]` > `.dev-screen` > `.dev-status` (9:41, `.dev-island`,
`.dev-sys` signal, wifi and battery), `.vp[data-w="390"]`, `.dev-home`; copy it from `recipes/review.html`.
Set `data-screen` to the colour at the top of the site; on the same origin app.js reads that colour itself, and it
keeps the page's scroll bar off the screen.

## Settings, sign in, empty and error pages

Settings: `.settings` (`.settings-nav` + content), `.panel > .setting` rows (`.s-title`, `.s-desc`, control on
the right), `.savebar` (sticky, appears when something changed). Sign in: `.auth > .auth-box` (`.logo`, h1,
`.intro`, `.auth-form`, `.or`, `.auth-switch`); a Google button shows the real logo:
`<img class="logo-img" src="kit/img/google.svg" alt="">`. Empty: `.empty` (icon `.ico.lg`, h2, `p`, `.row` of
buttons). Error page: `.error-page` (`.code`, h1, `p`, `.row`).

## Overlays and feedback

```html
<div class="menu-wrap">
  <button class="btn icon quiet" type="button" data-menu aria-controls="m1" aria-expanded="false" aria-label="Thêm thao tác"><svg class="ico"><use href="#i-more"/></svg></button>
  <div class="menu" id="m1" hidden><button type="button">Đổi tên</button><hr><button class="danger" type="button" data-open="confirm-delete">Xoá</button></div>
</div>
<dialog class="dialog" id="confirm-delete" aria-labelledby="cd-title">
  <h2 id="cd-title">Xoá website này?</h2><p class="body">Không lấy lại được sau khi xoá.</p>
  <div class="actions"><button class="btn" type="button" data-close>Giữ lại</button><button class="btn danger solid" type="button" data-close="ok">Xoá</button></div>
</dialog>
```
`.menu.left` opens from the left edge. `dialog.drawer` is a side panel (header, `.content`, footer). A dialog or drawer
with `data-state` opens as a modal when that state is shown, which is how a recipe draws "the detail panel is open". Toasts come
from script: `UI.toast("Đã xác nhận 3 đơn", {action: "Hoàn tác", onAction})`, or a button with
`data-toast="…" data-toast-action="Hoàn tác"` in a recipe. App events for the project to wire: `ui:state`,
`ui:tab`, `ui:press`, `ui:sort`.
