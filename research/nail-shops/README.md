# Nghiên cứu ngành nail: tổng hợp để build skill

Thu thập ngày 2026-10-07. Tổng hợp từ 5 file trong thư mục này. File này là đầu vào cho skill builder ngành nail (dự kiến `nail-salon-builder`, cùng kiểu với `ecommerce-builder`: một file `salon.json`, script build ra site).

## 1. Nguồn và độ tin cậy

| File | Phạm vi | Số mục | Mức xác minh |
|---|---|---|---|
| `part-1-usa.md` | Mỹ | 28 salon | Site đã mở; 5 mục mỏng (bị chặn bot hoặc ít thông tin) |
| `part-2-vietnam.md` | Việt Nam | 44 (gồm 4 học viện) | Chỉ 4 site mở được; còn lại theo mytour.vn, toplist.vn, Vietcetera |
| `part-3-uk-eu-au-ca.md` | Anh, Ireland, Pháp, Đức, Hà Lan, Tây Ban Nha, Ý, Thụy Điển, Úc, NZ, Canada | 28 salon | Site đã mở; màu và font đọc từ CSS |
| `part-4-asia.md` | Nhật, Singapore, HK, Malaysia, Philippines, Thái, Bali, UAE, Hàn | 34 | 32 site đã mở |
| `part-5-platforms-and-templates.md` | Nền tảng đặt lịch, template, thương hiệu, học viện, dịch vụ tận nhà | 40 | Trang vendor; số liệu vendor là lời quảng cáo |
| `part-6-vietnam-browser.md` | Việt Nam, xem bằng trình duyệt thật: bảng giá chi tiết, tên dịch vụ, câu chữ chính sách, bố cục mobile | 41 tiệm cũ kiểm tra lại, 10 tiệm mới | Ảnh chụp 17 site trong `screens-vn/` (chỉ lưu ở máy, không đưa lên repo); có đính chính cho part 2 |

Tổng: 134 salon và tiệm, cộng 40 mục nền tảng và template. Không có domain trùng giữa các file.

Lưu ý chung: cột "phong cách thiết kế" được suy từ mã trang và nội dung, không phải ảnh chụp. Trước khi chép bố cục cụ thể của site nào, mở site đó trong trình duyệt.

Chỗ còn thiếu: dịch vụ nail tận nhà ở Việt Nam, Đài Loan, Hàn Quốc (chỉ có ohora và Unistella), giá và phong cách của phần lớn tiệm Việt Nam.

## 2. Cấu trúc trang

### Menu chính

Gần như mọi site dùng cùng một bộ: **Dịch vụ và bảng giá / Mẫu nail (gallery) / Chi nhánh / Thẻ quà tặng / Đặt lịch**. Nút Đặt lịch nằm góc phải, màu tương phản, dính khi cuộn; trên điện thoại là thanh đặt lịch dính đáy màn hình.

Chuỗi và boutique lớn thêm: Cửa hàng, Thẻ thành viên, Học viện, Báo chí, Nhượng quyền, Tuyển dụng, Blog.

### Thứ tự section trang chủ (mẫu lặp lại nhiều nhất)

1. Hero: ảnh cận cảnh móng hoặc không gian tiệm (hoặc video ngắn), tagline 3 đến 8 chữ, một nút Đặt lịch.
2. Dải thông báo hoặc ưu đãi khách mới (Dear Sundays, Varnish Nail Shoppe dùng marquee).
3. Nhóm dịch vụ dạng thẻ, mỗi thẻ có giá "từ ..." (Luxo, NAILaCARTE, Em Nail Studio, Nailroom).
4. Gallery mẫu gần đây, có lọc (Tất cả / Tối giản / Chrome / Nail art) và nút "Đặt mẫu này" (Brisa Nail Spa).
5. Giới thiệu và cam kết: sản phẩm thuần chay, 10-free, quy trình tiệt trùng dụng cụ.
6. Đánh giá: điểm Google thật kèm số lượt, vài câu trích có tên.
7. Gói, thẻ thành viên, thẻ quà tặng.
8. Chi nhánh: địa chỉ, giờ mở cửa, chỗ đỗ xe, bản đồ, nút đặt lịch riêng từng chi nhánh.
9. FAQ và chính sách (hủy lịch, bảo hành, trễ giờ).
10. Footer: tên, địa chỉ, số điện thoại lặp lại (local SEO), mạng xã hội.

### Các trang con nên có

Trang chủ, Bảng giá đầy đủ, Gallery, Đặt lịch (nhiều bước), Chi nhánh (một trang mỗi chi nhánh nếu là chuỗi), Đội ngũ thợ, Thẻ quà tặng, Thẻ thành viên và gói, Chính sách, FAQ, Blog xu hướng, Liên hệ. Tùy chọn: Cửa hàng (sơn, móng úp, dưỡng), Học viện (khóa học), Đặt nhóm và tiệc (cô dâu, sinh nhật, công ty).

## 3. Nhóm dịch vụ chuẩn

Gộp từ cả 5 khu vực. Tên tiếng Việt dùng cho site, tên tiếng Anh để đối chiếu.

| Nhóm | Dịch vụ thường gặp |
|---|---|
| Chăm sóc tay (Manicure) | Cắt da, sửa form, sơn thường, chăm sóc tay spa, paraffin |
| Chăm sóc chân (Pedicure) | Ngâm chân, chà gót, spa pedicure, pedicure collagen hoặc đá nóng, pedicure không nước |
| Sơn gel | Gel trơn, gel Hàn, gel Nhật, cat eye, ombre, tráng gương (chrome), nhũ |
| Úp và nối móng (Enhancements) | Đắp bột (acrylic), nhúng bột (dip), đắp gel, BIAB / builder gel, Gel-X / móng úp mềm, polygel |
| Nail art | Vẽ tay, đính đá và charm, 3D, theo mẫu khách gửi; tính giá theo cấp độ hoặc theo ngón |
| Chuyên môn riêng | Russian manicure (làm da khô), phục hồi móng, móng cho người cắn móng, an toàn cho bà bầu, nail cho nam, nail trẻ em |
| Tháo và sửa | Tháo gel, tháo bột, sửa móng gãy, bảo hành |
| Dịch vụ kèm | Nối mi, mày, gội đầu dưỡng sinh, massage đầu, wax, chăm sóc da |
| Dịp đặc biệt | Nail cô dâu, tiệc, nhóm, công ty |

Thêm phụ phí (add-on) là đối tượng riêng, gắn vào dịch vụ: vẽ theo ngón, French, chrome, thêm độ dài, paraffin, tháo móng cũ.

## 4. Cách trình bày giá

Năm cách, theo mức độ phổ biến:

1. **Giá "từ ..."** trên thẻ nhóm dịch vụ (phổ biến nhất ở mọi khu vực, kể cả Nailroom, Euphorea).
2. **Bảng giá chia nhóm** có thời lượng và nội dung bao gồm (Luxo, Milano Nails, Nail Salon Tonic). Site nào ghi rõ thời lượng và những gì bao gồm thì tạo tin tưởng hơn.
3. **Bậc nail art** theo cấp 1 đến 5 hoặc từ miễn phí đến mức cao nhất (Pixienailsbali, Mitty).
4. **Gói theo thời lượng hoặc mẫu cố định** kiểu Nhật: 60/90/120 phút, hoặc mẫu theo mùa giá cố định (Nail Maison, tricia, Nail Quick).
5. **Gói hạng theo thời gian**: Express / Signature / Luxury (Townhouse).

Một số tiệm ẩn giá trong widget đặt lịch; nghiên cứu cho thấy cách này kém tin tưởng hơn. Builder nên mặc định hiển thị giá.

Giá theo trình độ thợ (junior, senior, master) có ở nền tảng (Fresha, Mangomint), nên đưa vào schema dưới dạng tùy chọn.

## 5. Kênh đặt lịch theo thị trường

| Thị trường | Kênh chính |
|---|---|
| Việt Nam | Hotline, Zalo, Messenger, form đơn giản (chọn dịch vụ, ngày, khung giờ như Silis) |
| Mỹ, Canada | Square, Vagaro, Fresha, Booker, Zenoti, Mangomint, Boulevard (nhúng hoặc link) |
| Anh, châu Âu, Úc | Fresha, Treatwell, Planity, Phorest, Zenoti, Square |
| Nhật, Thái | Form online, LINE |
| HK, Bali, UAE | WhatsApp, Zenoti, Fresha |

Kết luận cho builder: hỗ trợ ba chế độ đặt lịch: form có sẵn trong site (chạy demo bằng localStorage như ecommerce-builder), link hoặc nhúng nền tảng ngoài theo từng chi nhánh, và nút chat (Zalo, Messenger, WhatsApp, LINE). Với thị trường Việt Nam, mặc định là form trong site kèm nút Zalo và hotline.

Tính năng đặt lịch đáng làm (từ part-5): chọn dịch vụ và phụ phí, chọn thợ hoặc "thợ bất kỳ", tải ảnh mẫu tham khảo (Mangomint), ghi chú dị ứng, đặt cọc theo dịch vụ, khách mới và khách quen tách luồng (Elana Jade), đặt nhóm, danh sách chờ.

## 6. Phong cách thị giác

Bốn nhóm phong cách xuất hiện ở mọi khu vực. Đây là các style preset nên có trong builder.

| Preset | Đặc điểm | Font gặp nhiều | Màu gặp nhiều | Ví dụ |
|---|---|---|---|---|
| Sang trọng ấm (warm luxury) | Nền kem, chữ serif lớn, nhiều khoảng trắng | Cormorant Garamond, Italiana, Playfair Display, Libre Baskerville, Fraunces + sans mảnh | Kem #fdf9f5, be #e9e1db, taupe #6f5f5a, than chì, điểm vàng hoặc xanh rêu | Townhouse, Nailology, The Art of Nails, Kitchen Nail Bar |
| Tối giản Hàn Nhật | Trắng, xám nhạt, ảnh cận cảnh mẫu móng, gallery dày | Sans sạch (Pretendard, Noto Sans), serif nhẹ | Trắng, xám, hồng phấn, be | Nail Quick, tricia, From M Tokyo, Nailroom |
| Quyến rũ tối (dark glam) | Nền gần đen hoặc tím đậm, điểm hồng mâm xôi | Cinzel, Poppins | #1f1346, #cd2653, đen | Dunass Nails, D'Limo, Feather Nails |
| Vui tươi rực rỡ | Pastel hoặc cầu vồng, font tròn, giọng văn có cá tính | Baloo, Inter | Đỏ #c71536, vàng #ffdc38, hồng, xanh lá | Shoreditch Nails, Tropical Popical, Cute Nail Studio |

Ảnh: ưu tiên ảnh cận cảnh móng, dụng cụ, chai sơn, không gian tiệm; tránh ảnh chân dung người mẫu.

## 7. Yếu tố tạo tin tưởng và giữ khách

- **Đánh giá:** điểm Google thật kèm số lượt, trích dẫn có tên. Chỉ hiển thị khi có số thật từ chủ tiệm.
- **Bảo hành:** 3 đến 7 ngày, tháo gel miễn phí trong 7 ngày (rất phổ biến ở Việt Nam).
- **Vệ sinh:** quy trình tiệt trùng dụng cụ giải thích theo bước (The Hills, Pure Nail Bar).
- **Sản phẩm:** thuần chay, 10-free, không HEMA, thương hiệu sơn đang dùng (CND, OPI, The GelBottle).
- **Chứng chỉ và giải thưởng.**
- **Chính sách rõ ràng:** hủy trước 24 giờ, trễ giờ, đặt cọc.
- **Giữ khách:**
  - Thẻ quà tặng (gần như tiệm nào cũng có).
  - Thẻ tích điểm hoặc tem.
  - Thẻ thành viên theo tháng hoặc theo hạng.
  - Giới thiệu bạn bè, giảm giá sinh nhật, giảm khi đặt lại lịch, ưu đãi khung giờ vắng (NAILaCARTE early bird).
- **Nội dung:** blog xu hướng theo mùa, bộ sưu tập mẫu theo tháng (kiểu Nhật), bảng màu (chuỗi UAE).

## 8. Doanh thu phụ cần có trong builder

- Cửa hàng: sơn, móng úp, dưỡng móng, bộ kit (Townhouse, Buff, Manucurist, Top Coat).
- Học viện: khóa học có cấp độ, học phí, số chỗ còn lại (Seoul Academy, Shoreditch Nails, Mitty).
- Tiệc và nhóm: cô dâu, sinh nhật, công ty (Tropical Popical, POSH Nail Spa, Nail Garden).
- Dịch vụ tận nhà: vùng phục vụ, phí di chuyển (Glamsquad, LA LOGE).

## 9. Bản nháp `salon.json`

Phác thảo theo data model ở part-5, rút gọn cho bản đầu. Quy tắc về số liệu giống ecommerce-builder: mọi giá, số điện thoại, địa chỉ, số lượt đánh giá, thời hạn bảo hành phải đến từ brief.

```json
{
  "demo": true,
  "locale": "vi",
  "currency": "VND",
  "style": "warm-luxury",
  "brand": {
    "name": "", "tagline": "", "logo": "", "primary": "#",
    "hotline": "", "zalo": "", "email": "", "socials": {}
  },
  "booking": {
    "mode": "native | external | chat",
    "external_url": "",
    "slot_minutes": 15, "lead_time_minutes": 60, "max_advance_days": 30,
    "choose_technician": true, "inspiration_upload": true,
    "deposit": null, "cancel_hours": 24
  },
  "locations": [
    { "id": "", "name": "", "address": "", "map_url": "", "phone": "",
      "hours": [{ "days": "T2-CN", "open": "09:00", "close": "21:00" }],
      "booking_url": "", "parking": "" }
  ],
  "categories": [
    { "id": "gel", "name": "Sơn gel", "image": "", "description": "" }
  ],
  "services": [
    { "id": "", "category": "gel", "name": "", "description": "",
      "duration_min": 60, "price": 0, "price_type": "fixed | from | range",
      "price_max": null, "includes": [], "tags": [], "popular": false,
      "addons": [] }
  ],
  "addons": [
    { "id": "", "name": "", "price": 0, "per_nail": false, "extra_min": 0 }
  ],
  "art_levels": [
    { "level": 1, "name": "", "price": 0, "example": "" }
  ],
  "technicians": [
    { "id": "", "name": "", "title": "", "specialties": [], "locations": [] }
  ],
  "gallery": [
    { "image": "", "style": "", "shape": "", "length": "", "service": "" }
  ],
  "packages": [], "membership": [], "gift_cards": { "amounts": [] },
  "loyalty": null,
  "promotions": [],
  "reviews": { "rating": null, "count": null, "source": "", "quotes": [] },
  "policies": { "warranty_days": null, "cancellation": "", "late": "", "hygiene": "" },
  "faq": [],
  "shop": null,
  "academy": null,
  "events": null
}
```

## 10. Site mẫu nên mở khi thiết kế

| Site | Lấy gì |
|---|---|
| brisanailspa.com | Gallery có lọc, nút "Đặt mẫu này", huy hiệu đánh giá Google |
| luxonailspa.com | Thẻ nhóm dịch vụ có giá "từ", trang thợ, banner giới thiệu |
| kitchennailbar.com | Lưới chi nhánh, mỗi thẻ có nút đặt lịch, thẻ quà và thẻ thành viên |
| townhouse.co.uk | Gói hạng theo thời gian, đặt lịch và cửa hàng chung menu |
| mittynailsbeauty.com | Bậc giá nail art, chính sách hủy, tích điểm |
| emnailstudio.nl | Bảng giá "từ" ngắn ngay trang chủ, phong cách tối giản serif |
| nailology.com.au | Bảng màu be ấm, chọn chi nhánh |
| nailquick.co.jp | Danh mục mẫu lọc theo màu, dịp, ngân sách, thợ |
| tricia.jp | Trang mẫu theo mùa với giá từng mẫu và phụ phí |
| nailsalontonic.com | Bảng giá có thời lượng và nội dung bao gồm |
| pixienailsbali.com | Bậc nail art 1 đến 5, đặt lịch WhatsApp |
| nailroom.vn | Giá "từ" trên trang chủ, chuỗi nhiều chi nhánh, bảo hành 5 ngày |
| silisnail.com | Form đặt lịch đơn giản kiểu Việt Nam |
| seoulacademy.edu.vn | Trang học viện: số chỗ còn lại, quyền lợi học viên |
| shoreditchnails.com | Phong cách vui tươi, thẻ thành viên, học viện |

## 11. Bước tiếp theo

1. Chốt phạm vi bản đầu: trang công khai + đặt lịch demo, hay thêm trang quản trị (lịch hẹn, thợ, khách, doanh thu) như ecommerce-builder.
2. Viết `salon-schema.md` từ bản nháp mục 9.
3. Dựng 4 style preset ở mục 6 và một file ví dụ `demo-nail.salon.json`.
4. Bổ sung nghiên cứu Việt Nam bằng trình duyệt thật (giá, ảnh, cấu trúc fanpage) nếu cần mặc định sát thị trường hơn.
