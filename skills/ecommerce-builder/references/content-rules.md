# Content rules

## How Vietnamese electronics stores write

- Product names are the plain model name: "Lumen X9 Pro 5G 12GB/256GB". No adjectives in names.
- Prices are numbers with dot thousands and "đ": the templates format them, so shop.json holds plain numbers.
- Promotions are concrete and short, one benefit per line: "Giảm thêm 300.000 đ khi thanh toán bằng thẻ tín dụng", "Thu cũ đổi mới: trợ giá thêm 500.000 đ". No "ưu đãi hấp dẫn", no "cơ hội vàng".
- `highlights` and `description` state specs and what they mean for use: "Pin 5.000 mAh dùng trọn một ngày với nhu cầu thông thường". Avoid "trải nghiệm đỉnh cao", "hiệu năng vượt trội", "thiết kế sang trọng" with nothing behind them.
- Section titles are labels: "Điện thoại nổi bật", "Laptop", "Phụ kiện bán chạy", "Giờ vàng giá sốc". Banner titles name the product or the offer.
- Buttons use the standard words the templates already carry: "Mua ngay", "Thêm vào giỏ", "Trả góp 0%", "Xem tất cả".

## Facts and the brief

- Everything about the real shop comes from the brief: contacts, stores, products, prices, stock, warranty, shipping fees, payment methods, policies, vouchers.
- A missing contact or address becomes a bracket placeholder (`"[Địa chỉ trụ sở]"`, `"[Số tài khoản]"`) and is listed in the report. Do not invent a phone number, address, tax code or bank account.
- A missing spec stays out of the table. Do not fill gaps with plausible numbers.
- Reviews, star ratings, "đã bán" counts and flash-sale sold counts: only on a demo shop (`"demo": true`), or on a real shop when the brief contains the review text word for word. The build enforces this.
- `benefits` and `announcement` are promises (delivery time, return window, installment terms). Write only those the brief makes.
- Demo shops use fictional brands. Do not put real brand names on made-up products, prices or specs.

## What the build and lint reject

- Unless `"sample_content": true`: figures and model codes in product texts, promotions, benefits, announcements, shipping times, policies and banners that are not in the brief; promises ("chính hãng", "tặng", "quà", "miễn phí", "trả góp", "hoàn tiền", "trong ngày", "2 giờ", "lắp đặt", "tại nhà", "trọn đời", "thu cũ", "VAT", "hóa đơn", "rẻ nhất", "cam kết", "tuyệt đối") the brief does not make; sentences copied from the example shop
- Decimals written with a dot in Vietnamese text ("15.6 inch" must be "15,6 inch")
- Emoji, emoji flags, unicode arrows and text arrows (`->`, `=>`), em and en dashes, curly quotes
- Banned stock AI words (delve, crucial, robust, seamless and the rest of the list in `scripts/rules.py`) and Vietnamese translated-from-English phrases ("hãy để chúng tôi", "nâng tầm", "trong bối cảnh", "không chỉ ... mà còn")
- "Not X but Y" framing and chatbot phrases
- Banner backgrounds too light for white text
- In the stylesheets (`references/flat-style.md`): gradient text, colour-to-colour gradients and glows, a shadow on anything that does not float or that appears on hover; a card that rises on hover and frosted glass on content print warnings
- Unknown keys, unknown ids (brand, category, product, icon, device, badge), old prices not above the selling price, prices that are not VND numbers
