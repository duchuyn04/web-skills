# What real nail salon sites do

From 134 salon websites and fanpages (28 in the USA, 44 in Vietnam, 28 in the UK, Europe, Australia and Canada, 34 in Asia) and 40 booking platforms, templates and brands, read in October 2026. The full tables are in the project at `research/nail-shops/`. Where each pattern lives in the templates is in brackets.

## Navigation and home order

- Menu: Bảng giá, Mẫu nail, Ưu đãi or Thẻ quà, Thợ, Chi nhánh, and a high-contrast Đặt lịch button that stays on screen; on phones a bottom bar with Gọi, Zalo, Đặt lịch [layout/base.html].
- Home order seen most: hero with one booking button, an offer strip, service categories with "từ" prices, recent looks with filters and "book this look", promises (hygiene, products), reviews with a real Google count, packages and gift cards, branches with hours and parking, FAQ and policies, a closing booking band [the example `home` lists].

## Menu and prices

- "từ ..." prices on category cards are the most common (Nailroom, Euphorea, Luxo, Em Nail Studio) [sections/categories.html].
- A full list grouped by category with minutes and what is included builds more trust than prices hidden in a booking widget (Nail Salon Tonic, Milano Nails, Luxo) [pages/bang-gia.html].
- Nail art priced by level (Pixienailsbali levels 1 to 5, Mitty) or per nail [art_levels, addons with per_nail].
- Japanese salons sell fixed-price seasonal designs (Nail Quick, tricia); in this skill a gallery look linked to a service shows its price and books it [gallery.service].
- Service groups that repeat everywhere: manicure and pedicure care, gel (Korean gel, cat eye, chrome, ombre), enhancements (BIAB or builder gel, Gel-X, acrylic, dip, extensions), nail art and stones, removal and repair, combos (bridal, hands and feet); many Vietnamese salons add lashes, brows or head wash.

## Booking

- Vietnam: hotline, Zalo, Messenger and simple forms (service, day, time: Silis). USA, Canada, Europe, Australia: Square, Vagaro, Fresha, Booker, Zenoti, Treatwell, Planity, Phorest. Japan and Thailand: LINE. Hong Kong, Bali, UAE: WhatsApp [booking.mode].
- Platform features worth copying, all in the built-in flow: add-ons per service, choose a technician or any, sample photo upload (Mangomint), new versus returning customers, cancel window, deposit per service.
- Multi-branch salons route every booking button to the branch (Kitchen Nail Bar, Nailology, Pure Nail Bar) [locations[].booking_url, dat-lich.html?loc=].

## Vietnam, read in a real browser (part 6 of the research)

- Booking really happens in chat: Zalo for Vietnamese customers; WhatsApp, Instagram, KakaoTalk and LINE for visitors. Web forms often hand the booking on to WhatsApp (Samélie) [booking.send_to, salon.whatsapp, kakao, line].
- Every phone layout has at least one fixed contact control; the best ones have a call button per branch (Lisa) or Book, Call, Map (Samélie) [the phone bar and its branch sheets].
- Most salons publish the menu as a photo; the few with an HTML menu (Euphorea, Nail Kitchen, 22Spa, Posh) are easier to read on phones [bang-gia.html].
- Warranty and free-removal lines sit right under the prices (Tropicana, Colynn) [price_notes]. Tourist-area salons add USD and "last order" times (Mina, Healing, 22Spa, Posh) [price_usd, locations[].last_order].
- Typical prices in 2026 (thousand đồng): gel on hands 200-260, cut and gel combo 250-300, cat eye 250-300, gel removal 30-50, BIAB 350-450, extensions 250-450, nail art 15-50 per nail, foot spa 190-300. Use them only to sanity-check a brief, never as content.
- Seen and to avoid: expired domains, policy links that go to the home page, leftover template text, two formats for opening hours, figures that contradict each other, sideways scrolling on phones, fake "someone just booked" popups.

## Trust and retention

- Warranty 3 to 7 days and free removal when redone (very common in Vietnam), hygiene steps (The Hills, Pure Nail Bar), product claims (vegan, HEMA-free, brand used), review counts, certificates.
- Gift cards on nearly every site; punch cards and membership (Mitty points, The Art of Nails members, Tips and Toes tiers, Nailroom app vouchers); birthday and first-visit discounts; off-peak discounts (NAILaCARTE early bird).

## Looks

Four looks cover the field, so the four styles follow them: warm luxury (cream, taupe, serif: Townhouse, Nailology), Korean and Japanese minimal (white, soft pink, dense gallery: Nailroom, Nail Quick), dark glam (near-black, raspberry: Dunass Nails, D'Limo), playful bright (Shoreditch Nails, Tropical Popical, Cute Nail Studio).

## Admin

Platforms agree on: a day calendar with one column per technician, statuses (booked, confirmed, arrived, completed, cancelled, no-show), a client profile with notes on allergies and preferences and visit history, service menu with duration and price, staff performance and commission, revenue reports [admin pages].
