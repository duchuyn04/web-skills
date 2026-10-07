# Content rules

## How Vietnamese nail salons write

- Service names are what the menu board says: "Sơn gel trơn tay", "Úp móng gel", "Đắp bột", "Tháo gel", "Chăm sóc chân spa". No adjectives in names.
- Prices are numbers in salon.json; the templates write "150.000 đ", "từ 150.000 đ" and "150.000 - 250.000 đ". Prices by nail say "/ngón".
- `includes` are short steps the client lists ("Cắt da", "Sửa form", "Ngâm chân thảo mộc"), not praise.
- Promises are concrete and come from the owner: "Bảo hành 7 ngày", "Tháo gel miễn phí khi làm lại", "Dũa và buffer dùng một lần". No "đẳng cấp", "hoàn hảo", "trải nghiệm đỉnh cao", "nâng tầm vẻ đẹp".
- Section titles are labels: "Bảng giá", "Mẫu mới làm", "Thợ của tiệm", "Hai chi nhánh". Buttons use the words the templates carry: "Đặt lịch", "Đặt mẫu này", "Xem bảng giá".
- Professional register: no slang such as "ưng", "xịn xò", "chill".
- Warranty, free removal and surcharges go in `price_notes`, right under the prices, in the owner's words: "Sơn gel, úp móng và nail art bảo hành 7 ngày", "Tháo gel miễn phí khi làm lại cùng dịch vụ", "Nền gel cao cấp cộng 50.000 đ". Real Vietnamese salons put these lines next to the menu, not on a policy page.
- Salons near tourist streets often print a dollar price beside the đồng price; use `price_usd` only when the owner's menu has it, and say how they take payment if the brief does.

## Facts and the brief

- Everything about the real salon comes from the brief: contacts, branches, hours, services, prices, minutes, add-ons, art levels, packages, membership, gift cards, codes, warranty, hygiene, reviews.
- A missing contact or address becomes a bracket placeholder and goes in the report. Do not invent a phone number, an address or a Zalo number.
- Missing minutes: ask. Booking slots are planned from them; a guess double-books technicians.
- Reviews, ratings and counts: only on a demo, or on a real salon when the brief gives them (quotes word for word).
- Demo salons use fictional names. Do not put a real salon's name on made-up prices.
- Numbers that are limits rather than proof (number of colours, years, chairs) belong in the copy only when the owner gives them; do not turn them into headline figures.

## Pictures

- Without photos the build draws nail tips on a display wheel and polish bottles in the salon's colours. They are honest placeholders: say in the report that real photos of the salon's work should replace them.
- Owner photos: nails, tools, the room. A technician's portrait only when the owner sends it.

## What the build and lint reject

- Unless `"sample_content": true`: prices not written in the brief (150k, 150.000, 150 nghìn, 1tr2, 1,5 triệu are all read), figures in texts not in the brief, promises the brief does not make ("miễn phí", "bảo hành", "thuần chay", "vegan", "không HEMA", "hữu cơ", "tiệt trùng", "hấp", "dùng một lần", "chính hãng", "bà bầu", "cam kết", "tặng", "làm lại", "đặt cọc", "rẻ nhất", "tốt nhất", "số 1", "hàng đầu"), sentences copied from the example salons
- Decimals with a dot in Vietnamese text ("1.5 triệu" must be "1,5 triệu")
- Emoji, arrows, em and en dashes, curly quotes, banned AI words and translated phrases (see `scripts/rules.py`)
- Unknown keys and ids, prices under 1.000 (write the full amount), old prices not above the price, a home page that does not start with a hero, sections with no data
