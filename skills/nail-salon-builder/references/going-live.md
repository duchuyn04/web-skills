# Going live

The build is a static site. Bookings and admin changes live in one browser's localStorage. Before a salon takes real bookings, choose one of these:

## Option A: booking platform (fastest)

Set `booking.mode` to `external` with the salon's booking link, or `locations[].booking_url` per branch. Every Đặt lịch button opens the platform; the site stays a static brochure with the price list and gallery, and the built-in admin is not used.

- Fresha, Booksy, Vagaro, Square Appointments, GlossGenius, Mangomint and Treatwell all give a public booking link; most also offer an embed widget and SMS reminders, deposits and card on file. Fees and plans change: check the vendor's page with the owner.
- In Vietnam many salons take bookings in Zalo. `booking.mode: "chat"` sends every button to Zalo; the owner answers there.

## Option B: keep the built-in booking and admin

Needs a small backend. What has to move from the browser to a server:

| Now (static) | Needed |
|:---|:---|
| `bookings` and `adm:ov` in localStorage | a database table of appointments with the same fields as `common.js` documents, and an API to create, list and update them |
| free slots computed from local data | the same `slots()` logic on the server, with a lock so two customers cannot take one slot |
| admin password checked in the browser | real login (sessions or a hosted auth service), staff roles |
| no messages | SMS or Zalo OA message on booking, confirmation and the day before |
| `photo` keeps a file name | file upload to storage |
| deposit shown only | a payment link (VNPay, MoMo, bank QR) when `booking.deposit` is set |
| demo history | none: the admin starts empty and fills with real bookings |

Until then: do not publish `admin/` on a public host (it is marked noindex, but anyone with the link can open it), and tell the owner that bookings made on the site appear only in the browser that made them.
