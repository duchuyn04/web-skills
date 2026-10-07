# Words on the screen

Write in the language the product uses (grep the existing labels first; Vietnamese by default for this kit's
users). The person reading is busy and is not a developer.

## Labels

- A button names the action and its object when there are several: "Tạo đơn", "Xuất CSV", "Gửi yêu cầu làm website". Not "OK", not "Tiếp tục →".
- Destructive actions say what goes: "Xoá website", and the dialog title asks the question: "Xoá website Hải Đăng Digital?". The confirm button repeats the verb; the other is "Giữ lại", not "Huỷ" when Huỷ is itself the action.
- Field labels are nouns ("Số điện thoại"), hints say why or in what format ("Khách gọi số này khi cần đổi đơn"), placeholders show an example or stay empty; a placeholder is never the label.
- Status words are past participles or states: "Đã giao", "Chờ xác nhận", "Đang tạo", "Chưa tạo được".
- Plain words over system words: "Lượt tạo hôm nay" not "Quota"; "Không mở được trang" not "Lỗi 500" (the code may sit small above the title).

## Messages

- Errors say what happened, why if known, and what to do: "Chưa lưu được vì mất kết nối. Dữ liệu vẫn còn trên máy, bấm Thử lại khi có mạng."
- A sign-in error never says which of email or password was wrong.
- Empty states say what will appear here and the one next step: "Đơn khách đặt trên website sẽ hiện ở đây."
- Success is short and offers undo when undo exists: "Đã xác nhận 3 đơn. Hoàn tác".
- No exclamation marks, no "Oops", no jokes in errors, no emoji, no arrows, no em or en dashes, no stock phrases (the list in `scripts/lint_ui.py`).

## Numbers, dates, names

- Money: `1.284.500 đ` (dot thousands, space, `đ`); short form only in charts and tight figures: `18,4 tr đ`.
- Dates: `07/10/2026`, with the year only when it is not this year; times 24 h: `09:12`; relative only within a day: "10 phút trước".
- Counts agree with their noun and drop at zero: "Chưa có bình luận", not "0 bình luận".
- Phone numbers grouped: `0912 345 678`.

## Sample data

Recipes and prototypes use invented data that looks real and covers the edge cases: one name long enough to
wrap, a `0`, a number with nine digits, a missing phone or photo, an empty list, an item past its deadline.
Records that appear on two screens agree with each other (the order cancelled in the history is not counted as
delivered in the figures). Say in the report which data is invented. Photos of places or products come from
the project first, else from Unsplash with a checked URL; never a real brand's logo for an invented company.
