# salon.json

Every key the build accepts. Unknown keys are errors. Money is a whole number of đồng (`150000`), times are minutes, hours are `"HH:MM"`, weekdays are `1` (Thứ 2) to `7` (Chủ nhật).

## Top level

| Key | Required | What |
|:---|:---|:---|
| `brief` | yes | The client's brief as given. Prices, figures and promises are checked against it |
| `demo` | no | `true` for a sample: noindex, "Website mẫu" in the footer, generated admin history |
| `sample_content` | no | `true` only when the user asked you to invent the whole salon. Needs `demo` |
| `lang` | no | `"vi"` |
| `style` | yes | `warm-luxury`, `k-minimal`, `dark-glam`, `playful` |
| `layout` | no | `{"header": "classic" or "centered", "hero": "split", "stack", "full" or "collage", "card": "line" or "soft", "footer": "plain" or "matrix"}`. `matrix` puts the salon's initials on a moving LED dot panel in the footer of every page; the build refuses it unless the brief asks for an LED or dot-matrix panel or a large logo |
| `theme` | no | `accent` (logo colour; the build darkens it where text must stay readable), `preset` (borrow another style's colours), `font_head`, `font_body`, `font_accent` (a script font for the hero line only), `head_weight`, `han` (`zh`, `zh-Hant` or `ja`: how Chinese characters without kana are read). Fonts come from `data/fonts.json`; see `references/fonts.md` |
| `salon` | yes | see below |
| `announcement` | no | One line above the header: an offer or notice from the brief |
| `price_notes` | no | Short lines shown under the price list on Bảng giá and in the `price-list` section: warranty, free removal, surcharges, "giá USD để tham khảo". Checked against the brief like other promises |
| `booking` | no | see below |
| `locations` | yes | branches, at least one |
| `categories`, `services` | yes | the menu |
| `addons`, `art_levels` | no | extras and nail art price levels |
| `technicians` | no | the team; without it, booking skips the technician step |
| `gallery` | no | looks (photos or drawn) |
| `packages`, `membership`, `gift_cards`, `promotions` | no | offers; `uu-dai.html` is built when any exists |
| `reviews`, `trust`, `policies`, `faq` | no | proof, promises, policies |
| `home` | yes | home sections in order, the first is `hero` |
| `staff` | no | admin users `[{"name": "Chủ tiệm", "role": "Chủ tiệm"}]` |

## salon

`name`*, `hotline`*, `tagline`, `intro` (one paragraph, used by the `story` section and meta description), `zalo` (number), `messenger` (link), `whatsapp` (number with country code), `kakao` and `line` (links, for Korean and Japanese or Thai visitors), `email`, `socials` (`facebook`, `instagram`, `tiktok`, `youtube`: links), `legal` (company or household business line in the footer), `logo` (image next to salon.json; without it a nail-shaped mark and the name are shown).

## booking

| Key | Default | What |
|:---|:---|:---|
| `mode` | `native` | `native`: booking form on the site. `external`: every Đặt lịch button opens `external_url` (Fresha, Booksy, Square). `chat`: buttons open Zalo (or `salon.messenger`) |
| `external_url` | | required with `external` |
| `send_to` | first of zalo, whatsapp, messenger the salon has | the chat offered on the confirmation screen ("Gửi lịch hẹn qua Zalo"); WhatsApp gets the booking text in the link, Zalo and Messenger get it copied for pasting. `none` hides the button |
| `slot_minutes` | 15 | 10, 15, 20 or 30 |
| `lead_minutes` | 60 | earliest booking from now, today |
| `days_ahead` | 21 | 1 to 90 |
| `choose_technician` | true | show the technician step |
| `photo_upload` | true | a file field for a sample photo (the name is kept; the file is not uploaded on a static site) |
| `cancel_hours` | 4 | customers can cancel online until this many hours before |
| `deposit` | none | `{"percent": 30}` or `{"amount": 100000}`, optional `"over": 500000`; shown as a note in the booking summary (no payment is taken on a static site) |
| `note` | | a line under the price list and in the contact step (from the brief) |

## locations[]

`id`*, `name`*, `address`*, `last_order` (last time a new customer is taken, such as `"20:30"`; shown with the hours and no booking starts later), `hours`* (`[{"days": [1,2,3,4,5], "open": "10:00", "close": "20:00"}, {"days": [6,7], "open": "09:00", "close": "21:00"}]`; a day in no row is shown as Nghỉ), `phone`, `parking`, `map` (Google Maps link), `booking_url` (per-branch platform link), `note`.

## Images

Every `image` key takes a file next to salon.json or `lib:<id>` from the skill's photo library (`build.py --photos` lists about 110 photos in five groups: interior, polish, tools, nails, pedicure). Library photos are credited automatically on `nguon-anh.html`. Not allowed: library photos for technicians, and for gallery items on a real salon.

## categories[] and services[]

Category: `id`*, `name`*, `name_en` (English name for bilingual menus), `intro`, `art` (drawn picture), `image` (photo). A category without visible services is left out.

Service: `id`*, `category`*, `name`*, `name_en`, `price_usd` (dollar price shown beside the đồng price; must be in the brief), `minutes`* (5 to 480; slots are planned from it), `price` (đồng, or `null` for "Báo giá khi tư vấn"), `price_type` (`fixed` or `from`), `price_max` (shows "150.000 - 250.000 đ"), `includes` (list of short steps), `note`, `popular` (shown in the `popular` section and marked Hay đặt), `addons` (ids allowed with this service; default all), `technicians` (ids who do it; default all at the branch), `hidden`, `image`.

## addons[] and art_levels[]

Add-on: `id`*, `name`*, `name_en`, `price`*, `price_usd`, `per_nail` (price per nail; the booking form asks how many), `minutes`.

Art level: `name`* ("Cấp 1"), `text`, `price`*, `price_usd`, `price_type`, `price_max`.

## technicians[]

`id`*, `name`*, `title`, `specialties` (list), `locations` (branch ids; default all), `level` (`junior`, `senior`, `master`), `off_days` (weekdays), `image` (only a photo the owner sends; otherwise an initial is shown).

## gallery[]

`id`, `title`*, `tags` (filters on Mẫu nail), `service` (links "Đặt mẫu này" and shows the price), and either `image` (photo next to salon.json; `lib:<id>` only on a demo) or `art`:

`{"shape": "almond", "length": "medium", "style": "french", "colors": ["#f3d9cf", "#ffffff"], "bg": "#f6efe9"}`

- shape: square, squoval, oval, almond, coffin, stiletto
- length: short, medium, long
- style: solid, french, ombre, chrome, cat-eye, glitter, dots, floral, marble, stripes, heart, gem, aura
- colors: first is the base; second and third are the pattern, tip, glow or stones

Pick drawn looks that match the salon's real services and colours when they have no photos yet, and say so in the report.

## Offers

- `packages[]`: `name`*, `items` (lines), `price`*, `old_price`, `note`
- `membership[]`: `name`*, `price`*, `period` ("tháng", "năm"), `perks`, `note`
- `gift_cards`: `{"amounts": [200000, 500000], "note": "..."}`
- `promotions[]`: `title`*, `text`, `code` (capitals and digits; typed in the booking form), `percent` or `amount` (the discount the booking summary applies)

## Proof and policies

- `reviews`: `{"rating": 4.9, "count": 312, "source": "Google", "quotes": [{"name": "Ngọc A.", "text": "...", "service": "gel-tron"}]}`; on a real salon every value must be in the brief
- `trust[]`: `icon`, `title`*, `text` (hygiene, products, warranty, timing; from the brief)
- `policies[]`: `id`*, `title`*, `body` (paragraphs); each becomes `chinh-sach/<id>.html`
- `faq[]`: `q`, `a`

## home[]

| type | Data | Options |
|:---|:---|:---|
| `hero` | title, text | `variant`, `art`, `image` |
| `story` | salon.intro or `text` | `items` (up to three facts from the brief); `variant`: `plain`, `ink` |
| `categories` | categories | `variant`: `grid`, `scroll`, `fan` |
| `popular` | services with `popular` | `services` (ids); `variant`: `grid`, `marquee` |
| `price-list` | menu in tabs | `categories` (ids); `variant`: `tabs`, `spy` |
| `gallery` | gallery | `limit`, `tags`; `variant`: `grid`, `canvas`, `checker` |
| `art-levels` | art_levels | |
| `trust` | trust | `variant`: `grid`, `drop` |
| `team` | technicians | |
| `reviews` | reviews | |
| `offers` | packages, membership, gift_cards | |
| `locations` | locations | |
| `faq` | faq | |
| `cta` | title, text | |

Every section takes `title` and `text`. A section whose data is empty is a build error: leave it out instead.

`variant` picks a motion layout; leave it out for the plain one (the first value). What each does and when it suits a salon is in `references/patterns.md`, Motion. Only the sections above take a variant; any other value is a build error.

| variant | What moves |
|:---|:---|
| story `ink` | the intro paragraph turns from pale to full ink word by word as it scrolls up the screen |
| categories `scroll` | tall category cards in one row; on wide screens the section pins and the page scroll moves the row sideways, a bar shows how far; phones swipe |
| categories `fan` | three looks per category card (looks of its services, drawn ones when there are fewer); the back looks slide out once, hover gathers them |
| popular `marquee` | service names drift in two rows in opposite directions; hover or focus slows the row and shows the look with its price; each name books that service |
| price-list `spy` | the whole menu as one list by category; the row being read lights up and a panel beside it shows the look, price, time and Đặt lịch; phones show the look in the row |
| gallery `canvas` | looks scattered on a board to drag (it glides on), arrow keys pan; phones swipe a row |
| gallery `checker` | looks and flat tinted tiles in a checkerboard that turn over; one look moves a square every 3 s |
| trust `drop` | the promise cards drop one by one onto a tilted pile while the section is pinned; a list on phones |

Marquee, checker and the matrix footer move on their own, so the footer gets a "Tạm dừng chuyển động" switch on the pages that have them. Promo codes on Ưu đãi resolve from scrambled letters once when seen; this needs no option.
