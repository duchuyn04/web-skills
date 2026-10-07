# Screens: the brief, the recipe for each screen, the states it must draw

## The brief (the one place the skill stops to ask)

Before any file is written, read what the project has (README, spec, routes, data, existing screens) and send
one message with two parts. Each line says where it came from: *đọc từ code*, *bạn đã nói*, or *đoán*. The brief
holds what was read or said; do not invent personas, interviews or research figures.

**Part 1, five lines:**

- **Sản phẩm:** what it is, in one sentence (and what it is not, when that was misread before: "đơn vị làm web; công cụ mockup là tính năng phụ")
- **Người dùng:** who uses which area (end users, admins, staff), and how used they are to software
- **Việc chính:** the one to three things people come to do
- **Thiết bị:** phone or computer first
- **Điểm khác biệt:** what this product offers that others do not; it must be visible on the main screen

**Part 2, one row per screen:**

| Màn | Đến để làm gì | Quyết định dựa vào gì | Hành động cuối | Công thức |
|:---|:---|:---|:---|:---|
| Website của bạn | Xem các bản đã tạo, mở bản ưng | Ảnh, trạng thái, ngày tạo | Xem website | `list` |

- "Quyết định dựa vào gì" decides what each row or card shows first and largest; what does not help decide moves down or to the detail page.
- "Hành động cuối" is the one primary button of that screen.
- Ask at most five questions, each with a guessed answer, so the user can reply `ok`.

End with: *"Đúng thì trả lời `ok`, sai dòng nào sửa dòng đó."* and stop. A request that already settles the brief
("dựng luôn", a spec with these answers, a reply to an earlier brief) passes the gate without stopping; say the
brief in three lines at the top of the report instead.

## Pick a recipe for each screen

`python scripts/new.py --list` prints the recipes with their states. Pick by what the screen is for, not by
how it looks:

| The screen is for | Recipe | Frame |
|:---|:---|:---|
| many records with several columns to compare, sort, filter and act on in bulk | `table` | sidebar |
| fewer records where each has a picture or its own status and one main action | `list` | top bar |
| one record with parts (items, history, customer, notes) and a next step | `detail` | sidebar |
| creating something that needs several groups of answers | `wizard` | top bar, narrow |
| a long job the user waits for (build, import, export) | `progress` | top bar |
| looking at a produced thing (site, document, design) before accepting it | `review` | top bar, full height |
| the first admin screen: today's figures and what needs doing | `dashboard` | sidebar |
| settings of the account, the shop or the team | `settings` | sidebar |
| sign in, sign up, forgot password | `auth` | none |
| not found, no permission, server error, maintenance | `error` | the frame of the area |

Frames: admin and staff areas use the sidebar; end-user areas use the top bar. One product keeps one frame per
area; do not mix them on one area. Use one recipe twice (`table:orders,table:customers`) rather than inventing a
new layout. A screen no recipe fits: borrow the closest recipe's frame and parts, keep to kit classes, draw all
its states, and say in the report *"X chưa có công thức, mình mượn khung của Y"*.

## States every screen draws

Each state is a static example in the same file (`data-state`), opened with `?state=`. Draw all that apply:

| State | When | What it shows |
|:---|:---|:---|
| default | normal data | realistic rows with edge cases: a long name, `0`, a large number, a missing field |
| empty | nothing yet | an icon, what will appear here, the one next step |
| no-results | a search or filter matched nothing | what was searched, how to widen it, "Xoá tìm kiếm" |
| loading | waiting for data | what is loading in words, a spinner; no grey placeholder bars |
| error | the page could not load or save | what failed, that data is safe if true, "Thử lại" |
| limit | quota or plan reached | what the limit is, when it resets, the action disabled |
| no-access | the user lacks permission | who can grant it |

Time-based states are the ones people forget: something late, overdue or expired is often what the user needs
to see first. When the data has a "now", place it so one item is past due, and draw that.

## Hand-off notes in the report

The report starts with what was chosen for the user, one line each with the reason and an offer to change it:
the frame per area, the recipe per screen, the accent, which sample data is invented. Then: where to change the
brand (`kit/tokens.css` through `scripts/theme.py`), what is static (handlers are empty `ui:` events), and the
`screens.html` link.
