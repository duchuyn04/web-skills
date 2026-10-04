# Home sections, group F: blog, trade-in, installment, store-hours, payment-methods

Five section types, each with a default design (`sections/<type>.html`) and one or two extra designs (`sections/<type>/<variant>.html`, chosen with `"variant"` on the section). All work in every style and preset (colour tokens only). Examples: `examples/variants/sections-f.shop.json` (defaults) and `sections-f-2.shop.json` (variants).

Text inside these sections goes through the brief check like every home section (figures and promise words must appear in the brief unless `sample_content` is true), so write only what the client's brief says.

## blog

Technology news, buying guides, reviews. Designs: default `cards` (three cards in a row), `list` (rows with a small picture on the left), `featured` (first story large, the rest as a short list).

```json
{"type": "blog", "variant": "list", "title": "Tin công nghệ",
 "items": [{"title": "Cách chọn laptop cho sinh viên", "text": "Hai dòng ngắn tóm tắt bài.", "tag": "Hướng dẫn",
            "product": "kaze-air-14", "href": "https://..."}]}
```

Item keys: `title` (required), `text`, `tag`, `href` (without it the title is plain text), and one picture source: `product` (its photo) or `device` plus optional `device_color` (drawn art). Items without a picture show no picture.

## trade-in

Thu cũ đổi mới. Designs: default `steps` (heading, text, button and numbered steps, optional accepted models), `banner` (tinted band, steps in one row).

```json
{"type": "trade-in", "title": "Thu cũ đổi mới", "text": "...", "cta": "Tìm cửa hàng", "href": "optional",
 "steps": [{"title": "Mang máy tới cửa hàng", "text": "..."}],
 "items": [{"title": "Điện thoại", "text": "Các dòng còn bật nguồn", "product": "lumen-x9"}]}
```

The button goes to the stores page when the shop has stores, otherwise to the deals page, unless `href` is set. `items` (accepted models) are used by `steps` only. The template states no prices or percentages.

## installment

Amount per period for each product. Designs: default `calc` (select a product and a number of periods, the amount updates in the browser; `js/v/section-installment.js`), `table` (products by periods, no script).

```json
{"type": "installment", "title": "Tính tiền trả góp", "months": [3, 6, 12], "rate_text": "Trả góp 0% qua thẻ tín dụng",
 "products": ["lumen-x9-pro", "kaze-air-14"]}
```

`months` defaults to 3, 6, 12. `products` defaults to the four (calc) or six (table) most expensive products. Amount = price divided by periods, rounded to thousands. A rate line appears only when `rate_text` is set, so a shop never shows "0%" without the brief saying so. Both designs end with the fixed line "Số tiền mỗi kỳ chia đều, chưa gồm phí của ngân hàng hoặc công ty tài chính." Prices are the product's lowest variant price.

## store-hours

Shop stores with opening hours. Designs: default `cards` (a card per store with address, hours, phone and a directions link), `strip` (one line per store). Both show an "Đang mở cửa" or "Đã đóng cửa" badge worked out in the browser from the hours text (format `8:00 - 21:30`; `js/v/section-store-hours.js`). The section draws nothing when the shop has no `stores`. Data: `stores` of shop.json; only `title` is read from the section.

## payment-methods

The shop's `payments` list as tiles (default) or a wrapped list (`list`), with each method's icon, name and note. Display only; only `title` is read from the section.

## Verification

`py -3.11 scripts/variants.py` passes for these files; both examples build, pass `lint_output.py` and `qa.py --quick` (including the buying flow), and were screenshotted at 1440 and 390 px in the retail preset and in `gaming-dark`.
