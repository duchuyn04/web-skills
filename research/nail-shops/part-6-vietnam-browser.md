# Nghiên cứu tiệm nail Việt Nam bằng trình duyệt thật (phần 6)

Ngày xem: **07/10/2026** (mọi điểm đánh giá, số lượt, giờ đóng cửa và giá dưới đây là số hiển thị trong ngày này).

Bổ sung cho `part-2-vietnam.md`. Mục không thấy ghi "?".

## Cách làm và giới hạn

- Playwright MCP báo "Browser is already in use" (đang có phiên khác giữ trình duyệt), nên dùng **Chrome DevTools MCP**: Chrome thật, ngữ cảnh cô lập riêng, không đăng nhập tài khoản nào.
- Website: đọc DOM, `getComputedStyle` của body/h1/h2/nút đặt lịch, phần tử `position: fixed/sticky` trên mobile 390px, mở trang bảng giá và ảnh menu ở kích thước gốc để đọc số.
- Facebook: trang công khai mở được khi chưa đăng nhập, chỉ thấy phần Intro (số người theo dõi, địa chỉ, SĐT, website, % đề xuất) và bài mới nhất. Không mở được tab Giới thiệu/Ảnh đầy đủ. Dòng "Price range" trên FB hiển thị theo ký hiệu tiền của ngôn ngữ trình duyệt nên chỉ ghi số bậc (1, 2 hoặc 3 bậc).
- Google Maps: chế độ hạn chế khi chưa đăng nhập, xem được tên, điểm, số đánh giá, giờ đóng cửa hôm xem, website, vài đánh giá đầu. Không mở được ảnh bảng giá trong album.
- Silis Nail (silisnail.com): bị trang xác minh Cloudflare chặn hiển thị. Không bấm vượt xác minh. Chỉ đọc phần chữ đã tải sẵn trong DOM và hai ảnh bảng giá công khai trên thư mục uploads.
- Ảnh chụp: `screens-vn/<ten>-desktop.png` (1440px) và `<ten>-mobile.png` (390px). Trang quá dài để chụp cả trang thì chỉ chụp màn hình đầu (đã ghi chú). Đã thêm CSS tắt hiệu ứng hiện dần khi cuộn để các section không bị trống trong ảnh. Ảnh chỉ để tham khảo bố cục, không dùng lại ảnh người.

### Đính chính quan trọng so với part 2

| Tiệm | Part 2 ghi | Thực tế 07/10/2026 |
|---|---|---|
| Silis Nail Studio | Đang hoạt động, có web | Google Maps ghi **"Bị đóng vĩnh viễn"** (4,8 / 156 đánh giá). Fanpage fb.com/silisnailstudio báo "This content isn't available". Web còn nhưng bị Cloudflare chặn. |
| Cosmo Nail Spa | Hà Nội 5 cơ sở; web lỗi chứng chỉ | Tên miền cosmonailspa.vn **đã hết hạn** (trang VNNIC). Bài FB 12/9 liệt kê **3 cơ sở**: 107A Đào Tấn, 16A15 Lý Nam Đế (Hà Nội), The Little Thảo Điền 39C Nguyễn Duy Hiệu (TP.HCM). |
| Euphorea | Hà Nội | Công ty ở **TP.HCM** (685/5 Điện Biên Phủ, Bình Thạnh), có chi nhánh cả Hà Nội (La Chapelle 23 Nhà Chung) và TP.HCM (Thảo Điền, Ba Son...). |
| Nachi's Beauty (fb.com/23QuanThanh) | Tiệm Nachi's | Fanpage nay tên **PLUSH.Nail & Beauty**, web plushnail.vn (2 cơ sở: 23 Quán Thánh, 9 Cửa Nam). |
| Kissu Nail Bar | Đang hoạt động | Google Maps: "Ato Nail Bar (former Kissu Nail Bar)", 138 Ký Con, 5,0 (3), không có giờ, không có SĐT. |
| Queen Nail | naildepsaigon.com | Website **không kết nối được** (timeout cả http và https), nhưng FB và Maps vẫn trỏ về domain này. |
| Dịch vụ nail tại nhà | "Không tìm được nguồn" | Có: **Nét Đẹp Thẩm Mỹ** (netdepthammy.com, làm nail tận nơi TP.HCM, có bảng giá). Trên Maps còn có "Kawaii Nail (mobile nail service)" 4,2 (53). |
| Nailroom | 14 cơ sở + 1 Hàn Quốc | Intro FB ghi "Hệ thống 20 cơ sở Toàn quốc & Quốc tế"; bài FB 07/10 liệt kê 4 HN + 6 HCM + 1 Hàn Quốc; form đặt lịch có 10 chi nhánh VN. |

Website chết hoặc không dùng được (đã thử 07/10/2026): cosmonailspa.vn (hết hạn), naildepsaigon.com (timeout), halei.vn (timeout), lamia.vn (Cloudflare 522), denail.vn, snailbeauty.com.vn, johnnynamkiet.vn, lemongrasshanoispa.com (không phân giải tên miền), jolibeautyroom.com (Wix "domain isn't connected"), plushnail.vn và tropicananail.com (chỉ chạy với `www.`).

---

## (a) Bảng cập nhật cho các tiệm đã có

Viết tắt: GM = Google Maps (điểm / số đánh giá, giờ đóng cửa hôm xem). FB = số người theo dõi; "% đề xuất" là số FB hiển thị.

| # | Tiệm | GM | FB | Giá cụ thể đã thấy | Trình bày giá / đặt lịch | Chính sách, ưu đãi, ghi chú |
|---|---|---|---|---|---|---|
| 1 | Nailroom (Mit's House) | CN Quang Trung: 4,0 / 69, đóng 19:00 | 114K; giá 3 bậc | Trang chủ: Nail "từ 40000 VNĐ", Mi "từ 60000 VNĐ", Lông mày "từ 60000 VNĐ". Trang dịch vụ Nail không có bảng giá, chỉ có quy trình 6 bước. | Giá "từ" trên thẻ dịch vụ. Đặt lịch: book.nailroom.vn (SalonHero) chọn chi nhánh, ngày, **thợ**, khung giờ 30 phút (hiện Full/Available), dịch vụ; hotline 1900 066 811; Messenger; app iOS/Android. | Ưu đãi trên trang chủ (bài 2024): "TẢI APP NGAY – SAY VOUCHER", "SƠN MÓNG THUẦN CHAY – NHẬN NGAY DEAL HOT", "VUI CHECK-IN RINH NAIL XỊN". Trang chủ có khối "Khách hàng của Nailroom" toàn người nổi tiếng. Trang chủ có chèn các chữ lạ "EvoSpin / VegasHero / Wbetz" (nghi link spam). Mobile tràn ngang (scrollWidth 3565px). |
| 2 | Euphorea Salon & Spa | La Chapelle: 4,9 / 1.260, đóng 20:00 | ? (không mở) | Thảo Điền: Tháo gel 40.000; tháo móng giả 50.000; tháo gel đắp/bột đắp 100.000; cắt tỉa vệ sinh móng tay 100.000; Vinylux 75.000; Creative Play Gel 200.000; Shellac 250.000; French sơn thường 60.000 / sơn gel 120.000; sticker từ 10.000/ngón; vẽ, vân đá, nhũ từ 20.000/ngón; xà cừ, ẩn nhũ, hoa khô từ 30.000/ngón; đính đá từ 5.000/hạt; spa tay 200.000; spa chân 300.000. La Chapelle (HN): cắt tỉa tay 150.000, chân 150.000; Vinylux/OPI 95.000; Creative Play Gel 240.000; Shellac 300.000; spa tay 300.000; spa chân 380.000. | **Bảng HTML riêng từng chi nhánh** (giá khác nhau giữa HN và HCM). Nút "Đặt hẹn online"; Zalo 0933333925; m.me; hotline 1800-9467. | "(*) Miễn phí đối với móng đã làm tại Euphorea" (áp cho các dòng tháo). Ưu đãi: khi gội đầu, massage toàn thân 60 phút "chỉ 229.000 VNĐ"; "Combo Luxury Touch". |
| 3 | Cosmo Nail Spa | Đào Tấn: 4,8 / 119, đóng 20:30; Lý Nam Đế: 4,8 / 207 | 21K; 2 bậc | ? | Website chết; đặt qua hotline từng cơ sở. | 3 cơ sở (xem đính chính). Mở 9AM-8:30PM. Bài FB song ngữ Việt/Anh. |
| 4 | Halei Shop | ? | 91K | ? | Intro: "Dịch vụ Spa chăm sóc da mặt - Nails - Nối mi và uốn mi"; web halei.vn timeout. | ? |
| 5 | Diory NailsLab | 4,9 / 1.516, đóng 20:00 | 22K; 100% đề xuất (798 đánh giá); có "Online booking" | Bài FB: "Trải Nghiệm Spa Tay Chỉ 150K" | FB có nút đặt lịch online. | Bài FB: "Miễn Phí dịch vụ khi hóa đơn từ 500K trở lên. Tặng 01 Spa Da Mặt trị giá 500K" (phần sau bị cắt). 2 cơ sở: ngõ 88 Trung Kính, 41 Hàng Bài. |
| 6 | Oăn Nails Beauty | 4,5 / 12, đóng 21:00 | 12K | Bài FB: "Giá : 600k đã bao gồm nhặt da sửa móng và làm trên móng thật" (1 mẫu thiết kế) | Giá theo từng mẫu trong bài đăng. | 3 cơ sở (Xã Đàn, Phan Kế Bính, Huỳnh Thúc Kháng); "Open 9am - Close 8pm". |
| 7 | Chic Nail Premium | 223 Hàng Bông: 4,9 / 738, đóng 20:00; 23 Hàng Mắm: 4,9 / 459 | 2.1K | ? | Hotline. | Thương hiệu liên quan "Chic Nail - Eyelashes - Brow Lamination" 52 Hàng Nón 4,9 / 239 chạy quảng cáo trên Maps. |
| 8 | Tropicana Nail Lab | 4,9 / 488, đóng 19:30 | 8.2K; 100% (13) | Xem phụ lục. Ví dụ: sơn gel màu non-toxic 99k + base top 50/100/120k; BIAB 450k; nối Xgel 25k/ngón - 200k/bộ; mắt mèo 15k/ngón - 120k/bộ | **Ảnh menu 2 trang** (đơn vị nghìn đồng, không ghi "k"). Đặt lịch: nút "ĐẶT LỊCH DỊCH VỤ" mở Zalo; Messenger; hotline. Web www.tropicananail.com (LadiPage). | "*Free tháo móng cho khách cũ làm từ 3 dịch vụ." "**Các dịch vụ gel, nối móng, nail art được bảo hành trong 7 ngày." Nhãn "20% OFF" trên Xgel và mắt mèo. Khóa học "HỌC PHÍ 8XXX", "OFF 30%". Có popup "Thanh 0985987xxx đã [đặt] lịch lúc 5h - 2h trước". |
| 9 | Fedi Nail | "Fedi Nail & Lash" 4,9 / 1.344, đóng 22:30 | 5K | ? | FB, IG, TikTok; hotline. | Intro FB "Always open". Bài FB tiếng Anh nhắm khách du lịch phố cổ. |
| 10 | Nachi's Beauty → PLUSH Nail & Beauty | Quán Thánh: 4,9 / 1.301, đóng 20:00 | 4.6K | Xem phụ lục. Sơn gel kèm nhặt da 200.000; nối móng đắp gel + sơn gel 450.000; mắt mèo 250.000 | Ảnh menu song ngữ Anh-Việt (VNĐ). Đặt qua WhatsApp, Messenger, hotline; không có form. | Footer còn sót chữ mẫu "The Noun Project Icon Template..." và chuỗi hashtag SEO tiếng Anh. |
| 11 | Didan Nail Art | 4,2 / 48, đóng 20:00 | 134K; 88% (660); 2 bậc | ? | FB, IG. | Địa chỉ FB và Maps: 89 Vĩnh Phúc. |
| 12 | LAMIA Beauty Boutique | 4,4 / 148, đóng 21:00 | 17K | ? | lamia.vn lỗi 522. | Intro: "Hệ thống làm đẹp theo phong cách Hàn trên toàn quốc". |
| 13 | A+ Nails Studio | 4,8 / 682 | 11K; 2 bậc | ? | Web acongstudio.wordpress.com (chưa mở). | CN1 Lê Thị Hồng Gấm Q1, CN2 Nguyễn Gia Trí Bình Thạnh; "nối mi chỉ có ở quận bình thạnh". |
| 14 | Kolour de Beauty | 4,4 / 144, đóng 20:00 | 25K | ? | FB. | Kèm "Kolour Clinic&Spa" và "Kolour Beauty Academy". |
| 15 | Nailtopia.magic | "Nailtopia Magic Nail Salon" **5,0 / 3.849**, đóng 21:00 | 6.9K; 82% (9) | ? | FB, IG. | Bài FB: "Exceptional Quality, Unbeatable Prices"; có thêm dịch vụ gội đầu. |
| 16 | Joli Beauty Room | Gò Vấp: 5,0 / 35, đóng 21:00 | 8K | ? | jolibeautyroom.com không gắn site (Wix). | Intro: "Nail - Eyelash - Brow Lamination - Hair Wash"; "Open Daily: 9:00 - 21:00". |
| 17 | Quýt Nail | 255 Quang Trung: 4,9 / 1.276, đóng 21:00 | 4.1K; 100% (2.201) | ? (một đánh giá Maps của khách nêu "Úp móng 180", "cắt da 30k" - giá do khách kể, không phải tiệm niêm yết) | Mỗi cơ sở 1 "Hotline/Zalo". | 3 cơ sở (Lê Văn Sỹ, Quang Trung, Nguyễn Duy Cung) + số riêng "Đào tạo học viên". "Open Daily: 9:15 - 20:30". |
| 18 | Mina Nails & Beauty | 2 Bis Bùi Thị Xuân: 4,9 / 1.980, đóng 22:00; có "Đặt chỗ trực tuyến" | 6.6K; 100% (255) | Xem phụ lục. Sơn gel 260.000đ; sơn gel Hàn 280.000đ; mắt mèo 400.000đ; đắp gel 350.000đ | **Ảnh bảng giá song ngữ VNĐ + USD**. Form đặt lịch đầu trang: chi nhánh, dịch vụ, ngày giờ, số người, họ tên, email, mã vùng quốc gia, SĐT. | "No appointment needed to receive guests." "The staff speaks English." Giờ 8h00-23h00. 3 cơ sở Q1 + 1 ở Thụy Sĩ. Web nửa Anh nửa Việt. |
| 19 | Silis Nail Studio | **Bị đóng vĩnh viễn** (4,8 / 156) | Trang FB không còn | Xem phụ lục (ảnh menu: đơn vị nghìn đồng/set hoặc /ngón) | Ảnh menu; form "Đặt Lịch Dịch Vụ" (họ tên, SĐT, dịch vụ, ngày, giờ 9:00-19:00). | Gội đầu: "Mua combo 5 buổi - Giảm 10%... 10 buổi - Giảm 20%... 20 buổi - Giảm 25%". Footer có trang "Chính Sách Ưu Đãi Thành Viên", "Chính Sách Bảo Hành" (bị chặn, chưa đọc). |
| 20 | Queen Nail | Gò Vấp: 4,7 / 205, đóng 21:00 | 4.2K; 100% (22) | ? | Gọi/nhắn 2 số. | Web chết. |
| 21 | De Nail | 5,0 / 152, đóng 20:30 | 19K; 98% (56); 2 bậc | ? | denail.vn không phân giải. | Có số Singapore (+65) trên FB. |
| 22 | Kawaii Nail | Không chắc trùng tiệm: "Kawaii Nail (mobile nail service)" 4,2 / 53, đóng 19:00; "Kawaii Nail" 92 Nguyễn Huệ chưa có đánh giá | ? | ? | ? | Cần xác minh thêm. |
| 23 | Kissu Nail Bar | Xem đính chính | ? | ? | ? | Đã đổi tên. |
| 24 | Lisa Nail & Spa | 416A Hai Bà Trưng: **4,9 / 8.670**, đóng 21:00 | ? | Xem phụ lục. Sơn gel Hàn 200K (An Đông/Tân Hưng/Chánh Hưng) và 250K (Tân Định) | **Ảnh menu theo từng nhóm chi nhánh** (3 trang bảng giá). Đặt lịch: form web, Zalo, WhatsApp, LINE, KakaoTalk, hotline riêng từng chi nhánh. | "Bảng giá áp dụng cho chi nhánh Lisa An Đông, Tân Hưng, Chánh Hưng. Các chi nhánh Lisa Tân Định và Premium – Lê Thánh Tôn & Premium – Sài Gòn sẽ có mức giá cao hơn. Giá chính xác sẽ được hiển thị tự động trong form Booking theo từng chi nhánh bạn chọn!" Có mục Nhượng quyền, Đào tạo gội đầu. |
| 25 | Ruby Nails | 5,0 / 14, đóng 20:00 | 12K; 100% (8) | ? | Hotline. | Intro: "Chuyên đào tạo học viên mở tiệm và đi Nước ngoài". |
| 26 | Nail San | 4,5 / 101, đóng 20:00 | 9.5K; 1 bậc | ? | Web nailsan.business.site (chưa mở). | Intro: "Nail xinh giá rẻ". |
| 27 | Ohara Nail Bar | 4,4 / 64, đóng 21:00 | 4K; 100% (63); 2 bậc | ? | FB. | "Chuyên nails phong cách Hàn". |
| 28 | Sora K-Nail Studio | 4,8 / 479, đóng 20:00 | 3.5K; 2 bậc | ? | Web dạng trang con trên chatgpt.site (chưa mở). | Intro: manicure/pedicure kiểu Hàn-Nhật. |
| 29 | S'Nail Beauty | "S' Nails Beauty (Sương Nails)" 4,9 / 109, đóng 20:30 | 3.8K; 100% (21) | ? | snailbeauty.com.vn chết. | Intro "Open time: 08:00 - 20:00"; bài FB tuyển khóa học tháng 10. |
| 30 | Thảo Nails | 253 Nguyễn Chí Thanh: 4,9 / 1.910, đóng 20:00; 137 Phạm Cự Lượng: 4,9 / 61 | 5.8K; 100% (38) | ? | "Reservation number ... (sms/zalo/wechat/What's app) - English + Vietnamese". | Bài FB: "20-days-guarantee for manicure", "Keep your luggages until 8 PM", "30% discount for children under 7 6 years old" (nguyên văn). |
| 31 | DzonDzon Nails | 4,9 / 756, đóng 18:00 | 1.9K; 100% (69); 2 bậc; có "Online booking" | ? | Booking qua SĐT. | "Open: 9:00am-6:00pm từ Thứ 3- Chủ nhật". Hashtag đa ngôn ngữ (Nhật, Đức, Thái, Hàn). |
| 32 | IU Nails | Có 2 kết quả: "IU NAILS Lounge" 4,7 / 44 (96 Nguyễn Việt Hồng) và "Iu nails boutique" 4,5 / 33 | ? | ? | ? | Chưa xác định cái nào là tiệm trong part 2. |
| 33 | Merci NailArt | "Merci Nail" 4,2 / 11, đóng 19:30 (Ninh Kiều) - có thể là tiệm này | ? | ? | ? | Cần xác minh. |
| 34 | COCO Nails Studio | 4,5 / 16, đóng 20:00 | ? | ? | ? | 55 Trần Bình Trọng, Ninh Kiều. |
| 35 | Nail Johnny Nam Kiệt | "Học viện đào tạo Nail-Mi JOHNNY NAM KIỆT" 5,0 / 175, đóng 17:00 | 16K; 100% (458) | ? | Web johnnynamkiet.vn chết. | Bài FB: "lớp học thử #Nail và #Nối_mi hoàn toàn #MIỄNPHÍ". |
| 36 | Thanh Xuân Korean Nail & Lash | "Thanh Xuân nail & lash" 5,0 / 3, đóng 20:00 | 1.9K | ? | Hotline. | Bài FB ghi "1 cơ sở duy nhất: 01 Cát Cụt" nhưng Intro và Maps ghi 165 Hoàng Minh Thảo (thông tin mâu thuẫn). |
| 37 | Hachi Nails & Beauty | 4,9 / 130, đóng 19:00 | ? | ? | ? | 84 Trần Bình Trọng, Nha Trang. |
| 38 | Jenny's Nails & Spa | Có thể là "Jenny's Spa & Nail" 4,9 / 2.408, đóng 22:00 (danh mục "Bác sĩ trị liệu xoa bóp", web kakao.com) | ? | ? | ? | Nhắm khách Hàn; chưa chắc trùng tiệm. |
| 39 | The Nail Lab | 4,8 / 60, đóng 19:00 | ? | ? | ? | 66 Văn Tiến Dũng. |
| 40 | Miso Nails Room | **5,0 / 2.705**, đóng 22:00 | ? | ? | IG. | Mô tả chủ tiệm (EN): "Simultaneous manicure & pedicure available", "Book in advance for the best experience!" |
| 41 | Seoul Academy | ? | ? | Khóa nail chuyên nghiệp "15 – 25 triệu đồng cho 70 buổi" (đoạn khác ghi "15 – 20 triệu đồng/khóa cho 70 buổi"); nail đi nước ngoài "20 – 25 triệu đồng, học trong thời gian từ 3 – 4 tháng"; "dự trù thêm 2–5 triệu đồng cho dụng cụ" | Bài viết, không có bảng. Mobile: thanh dưới Hotline / Tư vấn / Messenger / Zalo + nút WhatsApp nổi. | Trang chủ không còn bộ đếm chỗ "11/20" như part 2 ghi; có 14 cam kết (cơm trưa, tea break, hỗ trợ nơi ở, giảng viên 1-1...). |

Không mở thêm được: VietBeauty Academy, Học viện Nail Cali, Be You Nail Academy (không có trong vòng này).

### Phụ lục (a): bảng giá chi tiết đọc từ ảnh/trang

**Silis Nail Studio** (ảnh menu, đơn vị nghìn đồng; tiệm đã đóng theo Maps)
- NAIL CARE: Phá Gel 30-50/set; Cắt Da, Sửa Móng Tay 40/set; Cắt Da, Sửa Móng Chân 45/set; Cắt Da, Sửa Móng Nam 65/set; Lấy Khoé Móng 20-50/set.
- NAIL ENHANCEMENT: Sơn Cứng Móng 60/set; Sơn Gel Hàn Quốc 120-140/set; Sơn Gel Cao Cấp 140-200/set; Sơn Flash Gel 180/set; Úp Móng / X-Gel Canni 170/set; Đắp Gel 250/set; Fill Móng 90-150/set; Đắp Gel - Nối Móng 40-290/set; Mix Trên Hai Màu 30.
- NAIL DESIGN: Vẽ Gel 5-50/ngón; Tráng Gương/Ombre 15/ngón; Marble/Loang/Galaxy 10-25/ngón; Ẩn xà cừ/Hoa khô/Nhũ 10-30/ngón; Flash/Hiệu ứng 10-15/ngón; Sơn mắt mèo/Flash/Nhũ hàn 15-25/ngón (250-270/set); Đính Đá Nhỏ/Phụ Kiện 5-20/ngón; Đính Đá Khối/Charm Nails 10-50/ngón.
- HAND & FOOT CARE: Tẩy TBC, Đắp Mặt Nạ Tay/Chân 150/set; Tẩy TBC, Chà Gót Chân 190/set; COMBO 260/set.
- Gội đầu dưỡng sinh: Gội thư giãn (30') 110K/buổi; An nhiên (45') 190K; Chuyên sâu (60') 290K; gội dầu cặp 80K; gội dầu thường 60K; combo Nourishing 90 phút 380.

**Lisa Nail & Spa** (ảnh "NAIL SERVICE"; trái = An Đông/Tân Hưng/Chánh Hưng, phải = Tân Định)
- NAIL EXTENSION: Gel X 200K / 200K; Đắp Gel/Gel Gôm 350k/bộ; Đắp Bột 350k/bộ.
- NAIL SERVICE: Sơn Gel Hàn/Sơn Thạch 200K / 250K; Sơn Mắt Mèo 250K / 300K; Combo Sơn Gel + Cắt Da 250K / 300K; Combo Mắt Mèo + Cắt Da 300K / 350K; Sơn Cứng Móng 50K/lớp; Phá Sơn 30K; Phá Móng Up/Đắp Bột/Đắp Gel 80K.
- DESIGNS: Vẽ đơn giản 15K-50K/ngón; Ombre/French/Nhũ/Sticker/Tráng Gương 15K/ngón; Nặn Gel Nổi 2D,3D 30K-80K/ngón; Hoa khô/Xà Cừ 25K-50K/ngón; Đính Đá Nhỏ 5K-20K/cái; Đính Đá Lớn 20K-50K/cái; Charm Nhựa 25K/cái; Charm Cao Cấp 50K-70K/cái.
- COMBO CHÀ GÓT 250K; COMBO CHĂM SÓC TAY 150K; Chà gót + cắt da chân 300k; Combo tay & chân 450k.

**Mina Nails & Beauty** (ảnh "BẢNG GIÁ / PRICE LIST", VNĐ + USD)
- NAILS: Cắt da 80.000đ; Sơn thường 200.000đ; Sơn Gel Hàn 280.000đ; Sơn Gel 260.000đ; Sơn thạch 300.000đ; Sơn gel nhũ 380.000đ; Sơn tráng gương 400.000đ; Sơn mắt mèo 400.000đ; Sơn gel CND 380.000đ; Sơn Hermes 450.000đ; Chà gót 300.000đ.
- NEW SET: Đắp Bột Clear 350.000đ; Refill Bột Clear 300.000đ; Đắp Bột Màu 450.000đ; Refill Bột Màu 400.000đ; Đắp Gel 350.000đ; Refill Gel Đắp 300.000đ; Móng Úp 300.000đ; Móng Dài 100.000đ; Đắp Ombre 90.000đ/ngón; Cắt French Bột 80.000đ/ngón; Ẩn Bột 60.000đ.
- DESIGN: Mắt Mèo, Flash, Tráng Gương, Ombre 25.000đ/ngón; Ẩn Xà Cừ, Nhũ 45.000đ; Vẽ Đơn Giản 20.000đ; Vẽ Nhiều 50.000đ; Vẽ Đầu Móng 25.000đ; Vẽ Nổi 60.000đ; Gắn Đá Nhỏ 10.000đ; Vừa 20.000đ; Lớn 30.000đ; Charm Nhỏ 40.000đ; Charm Lớn 70.000đ; Dán Sticker 20.000đ; Sơn Cứng Móng 80.000đ; Phá Gel 30.000đ; Phá Móng Giả 70.000đ; Kềm 200.000đ.
- HAIR WASH: Gội sạch & sấy (dầu thường) 150.000đ; (Keratine) 250.000đ.

**PLUSH Nail & Beauty** (ảnh menu, VNĐ)
- Manicure: with gel polish (Nhặt da, sơn gel) 200.000; Nails Extension with gel polish (Nối móng đắp gel và sơn gel) 450.000; Infill/Overlay builder gel with gel polish 350.000; cat eyes gel polish (Nhặt da, sơn mắt mèo) 250.000; normal polish 180.000; without color (Nhặt da, sơn dưỡng) 80.000; Gel remover/Fake nails remover 30.000 - 100.000; Hard gel (Cứng móng) 30.000 - 80.000.
- Pedicure: gel polish 200.000; normal polish 180.000; without color 80.000; Deluxe Spa Pedicure 300.000; Foot Care 250.000; Callus remover and basic Foot scrub (Chà gót chân) 100.000.
- Add-ons: French tips 150.000; Extra 3-5 gel colors 30.000; Nail art On Request; Ombre (10 fingers) 150.000 - 200.000; Chrome (10 fingers) (Tráng gương) 100.000.
- Hairwash: Basic 30 mins 100.000; Deluxe Spa Hairwash 80 mins (Gội đầu dưỡng sinh) 350.000.

**Tropicana Nail Lab** (ảnh "price list", đơn vị nghìn đồng)
- NAIL CARE: Tháo móng (sơn thường/gel/nối/bột) 10/30/50/100; Chăm sóc móng kiểu Hàn 50; Đánh bóng móng và dưỡng CND Solar oil 79; Chăm sóc móng em bé dưới 10 tuổi 30.
- POLISHING: Base top Rouni China 50; Base top Topclou Malaysia 100; Base top Non-toxic Dgel Korea 120; Sơn gel màu NON-TOXIC Korea, Malaysia 99; Cứng móng Rouni China 50; Cứng móng Topclou Malaysia (KHÔNG NÓNG) 80; BIAB by The Gel Bottle 450; Mix từ 3 màu sơn 20.
- SPA: Tẩy da chết tay/chân 50; Ủ mềm và chà gót chân sản phẩm Mỹ 150.
- EXTENSION & OVERLAYS: Vá móng thật 30/ngón; Nối móng úp keo 10/ngón; Nối móng úp Xgel by Canni 25/ngón - 200/bộ; Đắp gel tạo cầu/fill Topclou 20/ngón; Nối tip đắp gel Topclou 30/ngón; Đắp gel tạo cầu Dgel 30/ngón; Nối tips đắp gel Dgel 40/ngón.
- NAIL ART: Sơn mắt mèo 15/ngón - 120/bộ; Sticker/Foil 5/ngón; Kẻ đầu móng 10-20/ngón; Ombre 10-30; Tráng gương 15-30; Trang trí phụ kiện ẩn 10k-50/ngón; Charm/đá 5-60; Vẽ đơn giản 10-30; Vẽ hoạt hình/Loang vân đá 40-150/ngón.

**Euphorea**: xem dòng 2 ở bảng trên (đầy đủ phần nail của 2 chi nhánh).

---

## (b) Bảng tiệm mới (có website riêng, đã mở thật)

| # | Tiệm | Thành phố | Website | GM 07/10/2026 | Định vị, khách chính | Giá nail đã thấy | Trình bày giá | Kênh đặt lịch | Chính sách / ưu đãi | Màu, font (computed) | Ảnh |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Uni Nails | TP.HCM (49 Đặng Dung, Tân Định) | uninailsvn.com (Shopify) | 5,0 / 1.605, đóng 20:00 | Khách Việt và nước ngoài; "You can use English to make phone calls or send messages" | ? (khối "DỊCH VỤ NAIL" không hiện nội dung khi xem) | ? | Nút "ĐẶT LỊCH" và "Booking" đều mở **Instagram**; Messenger; 2 hotline | "Cam kết bảo hành miễn phí 7 ngày trong mọi trường hợp, sẵn sàng đổi 1 dịch vụ tương đương nếu khách hàng không hài lòng." Chọn mẫu trên iPad theo bộ sưu tập. Link chính sách ở footer trỏ về trang chủ. | Poppins; cam đất + trắng; nút đen chữ trắng | uninails-desktop/mobile |
| 2 | 22Nail / 22Spa | TP.HCM (100 Đề Thám, Q1) | 22spa.com | "22Nail" 4,9 / 2.143 (web tự ghi "Google Maps 4.6 (3,184 Customers)" cho spa) | Khách du lịch: gửi hành lý miễn phí 12 giờ, tắm nước nóng, đặt xe sân bay | Classic Manicure/Pedicure (Women) 45' 80.000 VND; (Men) 100.000; Nutrition Mani/Pedi (Women) 60' 120.000, (Men) 140.000; Premium Korean Gel Polish 60' 240.000; Callus Removal (Women) 50' 300.000, (Men) 350.000; Nutrition Mani/Pedi + Gel Polish 75' 350.000; Mani/Pedi + Callus Combo 60' 470.000 | **Thẻ dịch vụ HTML có thời lượng, mô tả, giá VND và quy đổi USD** | BOOK NOW; hotline; bottom bar "BOOK / MENU / FIND US / BOOK CAR" | "Easy Online Booking: No pre-payment required. Pay inside the spa!" Nail mở 9:30-21:00, "Last Order 7:30 PM". | Hanken Grotesk + EB Garamond (h1 67px); xanh rêu rgb(38,71,45) trên nền kem rgb(250,248,245); nút bo tròn tối đa | 22spa-desktop; 22spa-mobile (màn đầu) |
| 3 | Samélie Nails & Spa | TP.HCM (399 Hai Bà Trưng, Xuân Hòa) | bestnailsalon.samelie.vn | 4,9 / 843 (web ghi 4.9 (782)) | Khách nước ngoài; trang tiếng Anh | ? (không có bảng giá) | Không có | Form: tên, SĐT, ngày, giờ, dịch vụ (Hair Washing Ritual / Nail Extension / Lash Extensions / Massage & Care / Other), số khách; "Your request will open in WhatsApp so our team can confirm the appointment." Bottom nav Book / Call / Map | Mở 09:00-21:00 hằng ngày; "WhatsApp / Zalo: 0868 726 221 - Message to book quickly". Nhúng 3 đánh giá Google mới nhất. | Be Vietnam Pro; nâu đất rgb(75,64,56) trên nền be rgb(244,238,232); nút rgb(143,118,98) bo tròn | samelie-desktop/mobile |
| 4 | Taho Nail Spa | TP.HCM (5/6 Nguyễn Trung Ngạn, Sài Gòn) | tahonailspa.com | 4,9 / 75 | Khách nước ngoài | ? | Không có | "Book now" nhưng trang Services ghi "Walk-ins are welcome but you can't book an appointment with us so you don't have to wait" (nguyên văn); hotline; Instagram | Gói 5 đến 10 bước chăm sóc | Inter + Gowun Batang; nút vàng rgb(240,172,0) bo 8px | taho-desktop/mobile |
| 5 | Colynn Nail Studio | TP.HCM (Q1, gần chợ Bến Thành) | colynn.carrd.co (Carrd 1 trang) | 4,9 / 331 (tên Maps: "...Last Appt 9PM") | Khách nước ngoài; đoạn giới thiệu Anh + Nhật + Hàn | COMBO: Cắt Da Khô + Sơn Thường (không hơ đèn) 150K; + Sơn Gel Trơn 190K; + Sơn Set Mắt Mèo 260K; + Set French/Loang/Chrome 300K; (+50K nền Premium Gel). Cắt Da Khô Tay/Chân 70K/100K; Tháo Gel Ủ Dưỡng 40K; Tháo Móng Úp 70K; Tháo Móng Bột 120K; Phủ Cứng Móng 40K; Phủ Cứng Móng Dưỡng 80K; Sơn Thường OPI/Cre8tion 100K; Sơn Gel Tiêu Chuẩn 140K; Sơn Gel Premium 190K; Sơn BIAB/CND Shellac 350K; Úp Móng Bằng Base 190K; Đắp Móng 250K; Gel-X/Gel Extensions 190K/250K; Designed Press-on Nails From 150K; Mix Từ 3 Màu 20K/Set; Mắt Mèo/Tráng Gương/Ombre/French 10K-15K/Ngón; Xà Cừ/Hoa Khô/Đá/Charm 20K-80K/Ngón | **PDF 2 trang trên Google Drive** (trang 1 tiếng Việt, trang 2 tiếng Anh) | SimplyBook (colynnnail.simplybook.asia); WhatsApp; hotline | "FREE Tháo Gel/Móng Úp Của Tiệm khi làm lại cùng dịch vụ"; "BẢO HÀNH: 5 ngày Sơn Gel ~ 7 ngày Gel Premium, Móng Úp/Đắp & Design" | Playfair Display nâu rgb(103,45,25) trên nền hồng đất rgb(237,216,206) | colynn-desktop/mobile |
| 6 | Nét Đẹp Thẩm Mỹ | TP.HCM (làm **tận nơi**; địa chỉ 276 Bình Trị Đông) | netdepthammy.com | ? | Làm nail, nối mi, phun xăm, trang điểm tại nhà khách | Bảng "GIÁ THAM KHẢO (VNĐ)": Cắt da, sửa móng (Tay/Chân) Từ 50.000; Sơn gel Từ 100.000; Đắp bột/Đắp gel Từ 300.000; Thiết kế (Vẽ, đính đá, charm) Từ 15.000/ngón; Gói Chăm Sóc Toàn Diện (Cắt da, sơn gel) Từ 310.000 | **Bảng HTML, toàn giá "Từ"** | Gọi, Zalo, nút "Đặt lịch" | FAQ: "bảo hành bong tróc, gãy móng trong vòng 3-5 ngày (tùy dịch vụ) do lỗi kỹ thuật... sắp xếp kỹ thuật viên đến sửa lại miễn phí". Phí di chuyển: ?. Trang chủ ghi số liệu "15+ chuyên viên, 5.000+ khách hàng, 13 giải thưởng, 9.248+ đánh giá tốt" và footer "9000+ khách tin tưởng" (số không khớp nhau, không có nguồn). | Roboto + Plus Jakarta Sans 800; tím nâu rgb(90,63,72); nút bo tròn | netdepthammy-desktop; mobile (màn đầu) |
| 7 | Nail Kitchen | Hà Nội (4 cơ sở: 62 Từ Hoa, 57 Trịnh Công Sơn, 37 Đường Thành, 5 Trần Phú) | nailkitchen.vn | CS3 Đường Thành: 4,8 / 1.544 | Khách nước ngoài Tây Hồ, phố cổ; "100% CND products" | Manicure Shellac/Madam Glam + cứng móng VND 330.000; Gel + cứng móng 295.000; sơn thường 180.000; tháo gel & làm sạch 150.000; tháo móng nối & làm sạch 180.000; nối móng + gel/shellac 680.000-730.000; Gel X 550.000; Layer gel/poly gel/acrylic 420.000-490.000; Refill 440.000-520.000; BIAB 410.000 / 450.000-490.000; Press on 450.000; Nail art "start from 15k/ finger"; Pedicure Shellac 310.000, gel 275.000; Full Pedicure package 635.000-680.000 | **Bảng HTML 2 cột giá (giá thường / giá cao)** | Picktime (picktime.com/nailkitchen); Zalo, WhatsApp, Messenger; "CALL US" | "All prices above are excluded to 5% service chareg" (nguyên văn); "save 3% on what you use for your next visit"; "50% off for children under 12 (only apply for color service...)"; "If you bring your own colors, we will charge full price" | Muli + Rochester (chữ viết tay) vàng rgb(188,155,93) | nailkitchen-desktop; mobile (màn đầu) |
| 8 | Healing Spa and Nail | Hà Nội (22 Hàng Bạc, phố cổ) | healingspahanoi.vn | 4,8 / 1.157 | Khách du lịch, có Hàn (menu song ngữ Anh-Hàn) | Manicure/Pedicure (Colors not included) 180.000 / 7$; Hand/Foot Scrub 220.000; Pedicure + Salt Scrub 330.000; Foot Scrub 45' 390.000; Pedicure + Scrub + Mask 65' 550.000; Remove (Gel polish, fake nail) 70.000-170.000; Gel Polish 300.000 / 12$; Regular Nail Polish 200.000; Extension 330.000; Acrylic 440.000; Fake Nail 280.000; French Tip 170.000-300.000; Custom Handmade Nail Art 300.000 and Up | **Ảnh menu ngang (VNĐ + USD)** | BOOK NOW; WhatsApp, Zalo, KakaoTalk, gọi | "No service charge"; "Signature welcome drinks & snacks". Giờ ghi 2 kiểu trên cùng trang: "8h30 until 23h00 / Last order 21h30" và "09:00AM - 10:00PM". | Work Sans + Playfair Display; xám nâu | healingspa-desktop/mobile |
| 9 | Ocean Spa Nail | Đà Nẵng (26 An Thượng 1) | oceanspanail.com | 4,8 / 538 (web Maps trỏ oceanspadanang.com) | Khách du lịch Hàn ("한국어합니다"); 6 ngôn ngữ | Manucure/Móng tay 70.000 vnđ / 3$; Pedicure 70.000; Nail Design 170.000-360.000; Hard Nails/Móng cứng 50.000; Nail Stickers 170.000; Extension/Nối móng 200.000; Extension + Sticker 290.000; Shellac/Sơn gel 220.000; Shellac French 310.000; Take Off Old Shellac 70.000-120.000-150.000; Tẩy da chết chân 240.000; Deluxe Manicure 220.000; Deluxe Pedicure 340.000 | **1 ảnh menu chung** spa + nail + wax (VNĐ + USD) | "Book Now!"; Zalo, WhatsApp, LINE, Messenger, KakaoTalk ID | "NOTE INCLUDING FREE FRUIT (MANGO, ORANGE, SOFT DRINK BEER)". Mở 9AM-11PM. | Epilogue + Bellota Text xanh lá rgba(29,89,29,.83) | oceanspanail-desktop/mobile |
| 10 | Posh Nails & Spa (Posh Nail Lab) | Đà Nẵng (3 cơ sở gần biển Mỹ Khê) | poshnailsdanang.com | "Posh Nail Lab" 2 An Thượng 32: 5,0 / 993 (web ghi "5.0 ★ 1,790+ Google reviews") | Khách du lịch; "walk-ins welcome" | Posh Manicure 120.000 VND; Deluxe Manicure 250.000; add-on Gel remove 50.000, Gel color 120.000, Regular color 100.000; Basic Pedicure 200.000; Posh Signature Pedicure 350.000; Posh Luxury Pedicure 550.000; BIAB 250.000; Acrylic tips / Dual form / Builder gel tip 400.000; Gel X 300.000; French tips, Ombre, Chrome, Cat eye 150.000 mỗi loại; Nail art (from) 50.000; Long nail 100.000; Nail repair 30.000; Acrylic refill / Builder gel refill 250.000; Acrylic/Gel X removal 100.000 | **Menu HTML theo tab** (Manicure / Pedicure / Hair Wash / Artificial Nails), giá VND + USD, 3 "pedicure box" có danh sách "What's included" | WhatsApp có sẵn câu nhắn; gọi | "Sterilized before every use", "Walk-ins welcome", "Easy WhatsApp booking". Mở 9:00-20:00. | Inter + Playfair Display; nâu rgb(92,58,33) trên kem rgb(247,242,234); nút bo tròn | poshnails-desktop; mobile (màn đầu) |

Tiệm nổi bật trên Google Maps 07/10/2026 nhưng không thấy website riêng (để tham khảo, chưa mở web): Thuỳ Thỏ Nail Q1 4,9 / 4.593 (đặt qua Fresha); Thuỳ Thỏ Nail Đà Nẵng 4,9 / 1.994; Hà Nội Nail 4,9 / 2.507; The Garden Nail Spa 4,9 / 1.720; Ha Noi Nail Pro 4,9 / 1.700; The Nails 4,9 / 1.120; Nail Districts & Spa Q1 5,0 / 1.083; PEA Nail Room 4,9 / 961; Maria Nail House 4,9 / 880; Rosemary Nail Art Q1 4,9 / 833; Olyv Nail & Lashes 4,9 / 645; RI-O Nail&More 4,9 / 638; SuNam Nail & Spa Đà Nẵng 4,9 / 631.

---

## (c) Bảng giá tham chiếu theo nhóm dịch vụ

Đơn vị: **nghìn đồng**. Nguồn là bảng giá niêm yết đã đọc ở trên (07/10/2026). "Phổ biến" là khoảng mà đa số tiệm rơi vào. HN = Hà Nội, HCM = TP.HCM, ĐN = Đà Nẵng. Cần Thơ, Hải Phòng, Nha Trang: không tìm được bảng giá niêm yết (?).

| Nhóm dịch vụ | Min | Phổ biến | Max | HN | HCM | ĐN |
|---|---|---|---|---|---|---|
| Cắt da / làm sạch móng tay (không sơn) | 40 (Silis) | 70-100 | 180 (Healing, mani/pedi không màu) | 50 Tropicana; 80 Plush; 100 Nail Kitchen; 150 Euphorea; 180 Healing | 40 Silis; từ 50 Nét Đẹp (tại nhà); 70 Colynn; 80 Mina, 22Spa; 100 Euphorea TĐ | 70 Ocean; 120 Posh |
| Sơn thường | 75 (Euphorea, Vinylux) | 100-200 | 200 | 95 Euphorea; 180 Plush (gồm nhặt da), Nail Kitchen; 200 Healing | 75 Euphorea TĐ; 100 Colynn; 200 Mina | 100 Posh (add-on) |
| Sơn gel trơn (tay) | từ 100 (Nét Đẹp, tại nhà) | 200-260 | 380 (Mina gel CND) | 200 Plush (gồm nhặt da); 240 Euphorea (CPG); 295 Nail Kitchen (gel + cứng); 300 Healing, Euphorea Shellac; 330 Nail Kitchen Shellac. Tropicana tính tách: màu 99 + base top 50/100/120 | 120-140 Silis gel Hàn; 140 Colynn tiêu chuẩn / 190 premium; 200 Lisa (Q5/7/8) / 250 (Tân Định); 200-250 Euphorea TĐ; 240 22Spa; 260-280 Mina | 120 Posh (add-on, chưa gồm manicure 120); 220 Ocean Shellac |
| Combo cắt da + sơn gel | 190 (Colynn) | 250-300 | 350 (22Spa) | 200 Plush | 190 Colynn; 250/300 Lisa; 350 22Spa; từ 310 Nét Đẹp | 240 Posh (cộng manicure + gel color) |
| Sơn mắt mèo (cả bộ) | 120 (Tropicana, phần mắt mèo) | 250-300 | 400 (Mina) | 120/bộ Tropicana; 250 Plush | 250-270 Silis; 250/300 Lisa; 260 Colynn combo; 400 Mina | 150 Posh (design) |
| Tháo gel | 30 | 30-50 | 170 (Healing, gồm móng giả) | 30 Tropicana; 30-100 Plush; 50 Nail Kitchen (add-on); 70-170 Healing | 30-50 Silis; 30 Lisa, Mina; 40 Colynn, Euphorea TĐ (miễn phí nếu làm tại tiệm) | 50 Posh; 70-150 Ocean |
| Tháo móng úp / bột / nối | 50 | 70-100 | 120 | 50-100 Tropicana; 80 Nail Kitchen | 50-100 Euphorea TĐ; 70 Mina, Colynn (úp); 80 Lisa; 120 Colynn (bột) | 100 Posh |
| Cứng móng | 40 (Colynn) | 50-80 | 80 | 30-80 Plush; 50/80 Tropicana | 40/80 Colynn; 50/lớp Lisa; 60 Silis; 80 Mina | 50 Ocean |
| BIAB | 250 (Posh) | 350-450 | 490 (Nail Kitchen) | 450 Tropicana; 410-490 Nail Kitchen | 350 Colynn | 250 Posh |
| Úp móng / Gel X (bộ) | 170 (Silis) | 190-300 | 550 (Nail Kitchen Gel X) | 200 Tropicana Xgel; 280 Healing fake nail; 450 Nail Kitchen press-on; 550 Gel X | 170 Silis; 190 Colynn; 200 Lisa Gel X; 300 Mina móng úp | 300 Posh Gel X |
| Đắp gel / đắp bột / nối móng (bộ) | 200 (Ocean) | 250-450 | 730 (Nail Kitchen) | 330 Healing; 440 Healing acrylic; 450 Plush; 680-730 Nail Kitchen | 250 Silis, Colynn; 350 Lisa, Mina (gel/bột clear); 450 Mina bột màu; từ 300 Nét Đẹp | 200 Ocean; 400 Posh |
| Refill / fill | 90 (Silis) | 250-350 | 520 (Nail Kitchen) | 350 Plush; 440-520 Nail Kitchen | 90-150 Silis; 300-400 Mina | 250 Posh |
| French (cả bộ) | 60 (Euphorea, sơn thường) | 150 | 300 (Healing) | 150 Plush; 170-300 Healing | 120 Euphorea TĐ (gel); 25/ngón Mina | 150 Posh |
| Vẽ / nail art (mỗi ngón) | 5 (Silis) | 15-50 | 150 (Tropicana vẽ hoạt hình) | 10-30 đơn giản, 40-150 hoạt hình Tropicana; từ 15 Nail Kitchen | 5-50 Silis; 15-50 Lisa; 20-60 Mina; 10-15 hiệu ứng, 20-80 xà cừ/charm Colynn; từ 20 Euphorea; từ 15 Nét Đẹp | từ 50 Posh (không ghi đơn vị ngón) |
| Ombre / tráng gương / hiệu ứng (mỗi ngón) | 10 | 15-25 | 30 | 10-30 Tropicana; Plush 100-200/10 ngón | 15 Silis, Lisa; 25 Mina; 10-15 Colynn | 150/bộ Posh |
| Đính đá nhỏ (mỗi hạt/ngón) | 5 | 5-20 | 20 | 5-60 charm/đá Tropicana | 5-20 Silis, Lisa; 10 Mina; từ 5/hạt Euphorea | ? |
| Charm | 25 (Lisa charm nhựa) | 40-70 | 80 (Colynn) | ? | 25-70 Lisa; 40/70 Mina; 20-80 Colynn | ? |
| Chà gót / spa chân | 100 (Plush chà gót cơ bản) | 190-300 | 550 (Posh Luxury) | 100/250/300 Plush; 150 Tropicana; 190-250, 270-340 Nail Kitchen; 330-550 Healing; 380 Euphorea LC | 190 Silis; 250 Lisa combo; 300 Mina, 22Spa (nữ); 300 Euphorea TĐ | 200/350/550 Posh |
| Gội đầu dưỡng sinh | 60 (Silis, gội thường) | 110-300 | 650 (Healing 75') | 100 / 350 Plush; 300 / 500 / 650 Healing | 110 / 190 / 290 / 380 Silis; 150 / 250 Mina | ? |

Nhận xét giá:
- Cùng một thương hiệu giá chênh theo chi nhánh: Lisa sơn gel Hàn 200K ở Q5/7/8 và 250K ở Tân Định; Euphorea Creative Play Gel 200.000 ở Thảo Điền và 240.000 ở La Chapelle (HN).
- Khu du lịch (Q1 gần chợ Bến Thành, phố cổ Hà Nội, An Thượng Đà Nẵng) giá cao hơn và ghi thêm USD: Mina, Healing, 22Spa, Ocean, Posh.
- Hai cách tính sơn gel: trọn bộ (Plush 200 gồm nhặt da) và tính tách (Posh: manicure 120 + gel color 120; Tropicana: màu 99 + base top theo hãng 50/100/120).
- Phụ phí thấy được: 5% phí dịch vụ (Nail Kitchen); +50K nền premium gel (Colynn); +30.000 khi dùng 3-5 màu (Plush); 20 cho mix từ 3 màu (Tropicana, Colynn); BYO sơn vẫn tính đủ giá (Nail Kitchen).

---

## (d) Tên dịch vụ tiếng Việt hay dùng (đúng chữ trên menu)

**Chăm sóc móng**: Cắt da; Nhặt da; Cắt da, sửa móng tay / chân; Cắt da khô; Cắt tỉa, vệ sinh móng tay; Chăm sóc móng kiểu Hàn; Lấy khoé móng; Đánh bóng móng; Dưỡng móng; Chăm sóc móng em bé; Cắt da sửa móng nam.

**Tháo**: Phá gel; Phá sơn; Tháo gel; Tháo sơn gel; Tháo gel ủ dưỡng; Tháo móng giả; Tháo móng úp; Tháo móng bột; Phá móng úp / đắp bột / đắp gel; Phá móng giả.

**Sơn**: Sơn thường; Sơn dưỡng; Sơn gel; Sơn gel trơn; Sơn gel Hàn (Hàn Quốc); Sơn gel cao cấp; Sơn gel premium; Sơn thạch; Sơn gel nhũ; Sơn mắt mèo; Sơn tráng gương; Sơn flash gel; Sơn cứng móng / Cứng móng / Phủ cứng móng; Mix màu (từ 3 màu); Base top.

**Nối và đắp**: Úp móng; Móng úp; Nối móng úp keo; Nối móng úp Xgel; Gel X; Đắp gel; Đắp gel tạo cầu; Đắp bột (clear / màu); Đắp ombre; Nối móng; Nối tip đắp gel; Fill móng; Refill bột / gel; Vá móng; Móng dài; BIAB.

**Trang trí**: Vẽ gel; Vẽ đơn giản; Vẽ nhiều; Vẽ nổi; Nặn gel nổi 2D, 3D; Vẽ đầu móng / Kẻ đầu móng / French; Ombre; Tráng gương; Loang / vân đá / Marble / Galaxy; Ẩn xà cừ; Ẩn nhũ; Hoa khô; Nhũ kim tuyến; Dán sticker; Đính đá nhỏ / vừa / lớn; Đính đá khối; Gắn charm (nhỏ / lớn, nhựa / cao cấp); Trang trí phụ kiện ẩn.

**Tay chân, spa**: Spa tay; Spa chân; Tẩy tế bào chết (TBC) tay / chân; Đắp mặt nạ tay / chân; Chà gót (chân); Ủ mềm và chà gót; Mát-xa chân; Ngâm chân thảo dược.

**Kèm theo**: Gội đầu dưỡng sinh; Gội thư giãn; Nối mi; Uốn mi; Wax / triệt lông.

Cách ghi đơn vị: "/set", "/bộ", "/ngón", "/cái", "/hạt", "/lớp"; giá "từ ..."; khoảng "20-50"; dạng tắt "250K", "15K/ngón"; menu song ngữ thường ghi tên Việt dưới tên Anh (Plush, Mina, Healing).

---

## (e) Mẫu chính sách thường gặp (câu chữ thực tế)

**Bảo hành**
- "Các dịch vụ gel, nối móng, nail art được bảo hành trong 7 ngày." (Tropicana)
- "BẢO HÀNH: 5 ngày Sơn Gel ~ 7 ngày Gel Premium, Móng Úp/Đắp & Design" (Colynn)
- "Cam kết bảo hành miễn phí 7 ngày trong mọi trường hợp, sẵn sàng đổi 1 dịch vụ tương đương nếu khách hàng không hài lòng." (Uni Nails)
- "bảo hành bong tróc, gãy móng trong vòng 3-5 ngày (tùy dịch vụ) do lỗi kỹ thuật. Nếu gặp bất kỳ vấn đề gì, bạn chỉ cần liên hệ hotline, chúng tôi sẽ sắp xếp kỹ thuật viên đến sửa lại miễn phí cho bạn." (Nét Đẹp Thẩm Mỹ, làm tại nhà)
- "20-days-guarantee for manicure" (Thảo Nails, bài FB)

**Tháo gel miễn phí**
- "(*) Miễn phí đối với móng đã làm tại Euphorea" (Euphorea)
- "*Free tháo móng cho khách cũ làm từ 3 dịch vụ." (Tropicana)
- "FREE Tháo Gel/Móng Úp Của Tiệm khi làm lại cùng dịch vụ" (Colynn)

**Giá tham khảo, giá theo chi nhánh**
- "Bảng giá dưới đây chỉ mang tính chất tham khảo. Để được tư vấn chi tiết dịch vụ và chương trình ưu đãi, quý khách hàng vui lòng liên hệ theo hotline 1800-9467" (Euphorea)
- "Các chi nhánh Lisa Tân Định và Premium – Lê Thánh Tôn & Premium – Sài Gòn sẽ có mức giá cao hơn. Giá chính xác sẽ được hiển thị tự động trong form Booking theo từng chi nhánh bạn chọn!" (Lisa)
- "Giá : 600k đã bao gồm nhặt da sửa móng và làm trên móng thật" (Oăn, bài FB theo mẫu)

**Phụ phí và điều kiện**
- "All prices above are excluded to 5% service chareg" (Nail Kitchen, nguyên văn)
- "If you bring your own colors, we will charge full price applicable to that service." (Nail Kitchen)
- "(+50K nền Premium Gel)" (Colynn)
- "No service charge" (Healing Spa, ghi như điểm bán)

**Thanh toán, đặt cọc, hủy lịch**
- "Easy Online Booking: No pre-payment required. Pay inside the spa!" (22Spa)
- Đặt cọc, phí hủy lịch, phí đến trễ: **không thấy tiệm nào ghi** trên các trang đã mở (?).

**Walk-in và đặt trước**
- "No appointment needed to receive guests." (Mina)
- "Walk-ins are always welcome, and booking over WhatsApp takes less than a minute." (Posh)
- "Your request will open in WhatsApp so our team can confirm the appointment." (Samélie)
- "Book in advance for the best experience!" (Miso, mô tả Maps)
- "Last Order 7:30 PM" (22Spa); "Last order: 21h30" (Healing)

**Ưu đãi, thành viên, trẻ em**
- "Our Loyalty Program: Everytime you are using services at Nail Kitchen, save 3% on what you use for your next visit (Does not combine with any other promotion)"
- "Note: 50% off for children under 12 (only apply for color service, not applying for design, extension, fake nail set or any other add on service and spa service." (Nail Kitchen)
- "30% discount for children under 7 6 years old" (Thảo Nails, nguyên văn)
- "Mua combo 5 buổi - Giảm 10% / 10 buổi - Giảm 20% / 20 buổi - Giảm 25%" (Silis, gói gội đầu)
- "Trải Nghiệm Spa Tay Chỉ 150K ... Miễn Phí dịch vụ khi hóa đơn từ 500K trở lên." (Diory, bài FB)
- "TẢI APP NGAY – SAY VOUCHER" (Nailroom)
- Nhãn "20% OFF" ngay trên dòng giá (Tropicana)
- "CHỈ ÁP DỤNG CHO KHÁCH MEMBERS TẠI LISA AN ĐÔNG, TÂN HƯNG, CHÁNH HƯNG" (Lisa)

**Tiện ích cho khách du lịch**
- "Keep your luggages until 8 PM" (Thảo Nails); "Free Secure Luggage Storage ... up to 12 hours" (22Spa)
- "NOTE INCLUDING FREE FRUIT (MANGO, ORANGE, SOFT DRINK BEER)" (Ocean)
- "You can use English to make phone calls or send messages" (Uni Nails); "The staff speaks English." (Mina)

---

## (f) Nhận xét bố cục trang chủ và mobile

### Thứ tự section thường gặp

1. **Thanh trên cùng**: giờ mở cửa, hotline, chọn ngôn ngữ (cờ), đôi khi link app (Nailroom, Euphorea, Lisa, Uni, Healing, Nét Đẹp).
2. **Menu**: Giới thiệu / Dịch vụ / Bảng giá / Gallery / Hệ thống salon / Tin tức / Liên hệ / Đặt lịch. Chuỗi lớn thêm Học viện, Nhượng quyền (Nailroom, Lisa).
3. **Hero**: ảnh không gian tiệm (Lisa, Posh) hoặc slider banner khuyến mãi (Euphorea, Nailroom). Site nhắm khách du lịch đặt điểm Google ngay trong hero ("5.0 ★ 1,790+ Google reviews" Posh; "Google Certified Favorite 4.6" 22Spa).
4. **Dịch vụ**: thẻ dịch vụ có giá "từ" (Nailroom), thẻ có thời lượng + VND + USD (22Spa, Posh), hoặc khối dịch vụ kèm nút ĐẶT LỊCH (Lisa, Mina).
5. **Lý do chọn**: 4 ô cam kết (Uni: Bảo hành / Nails design trên iPad / Pro-team / Clean space; Tropicana: hàng chính hãng, 500+ màu, 300+ phụ kiện, ghế Gold Class; Posh: dụng cụ tiệt trùng, walk-in, WhatsApp).
6. **Bảng giá**: đa số là **ảnh menu** (Lisa, Mina, Plush, Tropicana, Silis, Healing, Ocean); ít tiệm làm bảng HTML (Euphorea, Nail Kitchen, Nét Đẹp) hoặc menu tab (Posh). Colynn dùng PDF Google Drive.
7. **Gallery / Instagram**, **đánh giá** (Google, FB, nhiều ngôn ngữ), **hệ thống chi nhánh** (địa chỉ, SĐT, giờ, chỉ đường, đặt lịch từng chi nhánh), **blog** SEO.
8. **Footer**: chính sách (bảo hành, thành viên, bảo mật), mạng xã hội.

### Bố cục từng site đã chụp

- **Nailroom**: slider → Blog chương trình → Khách hàng người nổi tiếng → Cảm nhận → Giới thiệu → Dịch vụ (Mi / Nail / Lông mày, giá "từ") → Học viện → "Đặt lịch liền tay" → chi nhánh theo thành phố. Nền hồng nhạt rgb(250,239,237), tiêu đề vàng đồng rgb(183,117,43), Open Sans 300. Mobile tràn ngang, không có nút cố định.
- **Euphorea**: slider 4 banner (H3 Source Serif Pro 34px + nút "CHI TIẾT" đen bo 4px) → Dịch vụ nổi bật → Đẹp cùng Euphorea (blog xu hướng nail 2026) → Khách hàng nói → đăng ký nhận ưu đãi. Mobile: thanh dưới IG / FB / Messenger.
- **Lisa**: hero ảnh salon + "Hệ thống Nail & Spa hàng đầu Việt Nam" + Xem địa chỉ → các khối dịch vụ, mỗi khối một nút ĐẶT LỊCH (SVN-Megante 30px, nâu rgb(147,100,58) trên nền kem rgb(255,238,221), bo 99px) → bài SEO rất dài. Mobile: **thanh dưới 5 nút gọi theo chi nhánh** (Quận 1 / Q1 HTK / Quận 5 / Quận 7 / Quận 8) + 3 nút tròn nổi bên phải (Booking, Messenger, Social Media).
- **Mina**: form đặt lịch nằm ngay đầu trang → giờ, "No appointment needed" → Featured services (thời lượng 30-60 phút) → ảnh bảng giá → Các mẫu nails → Đánh giá "4.9 Dựa trên 3000+ đánh giá" → Chi nhánh → About → Album → Blog. Mobile: thanh dưới 3 số điện thoại + cụm nổi Call / Cabinet / Chat / Social.
- **Tropicana, Plush** (LadiPage, cùng đơn vị làm "X3Sales"): trang dài một cột, ảnh menu, lý do chọn, review, footer hashtag. Mobile tràn ngang 420px. Tropicana có popup giả lập thông báo đặt lịch và nút Zalo/gọi nổi góc trái.
- **Seoul Academy**: menu khóa học dày → Về Seoul → Khóa học đang tuyển sinh → 14 cam kết → câu chuyện thành công → hợp tác. Mobile: thanh dưới Hotline / Tư vấn / Messenger / Zalo.
- **22Spa**: header cố định → hero lớn → giải thưởng → thẻ dịch vụ có giá → tiện ích du khách → testimonial. Mobile: thanh dưới BOOK / MENU / FIND US / BOOK CAR.
- **Samélie**: một trang ngắn: H1 + chip dịch vụ → form đặt lịch → giờ mở và nút gọi/chỉ đường → album → 3 review Google mới nhất. Mobile: thanh dưới Book / Call / Map.
- **Posh**: hero toàn màn hình, 3 "pedicure box" có giá, menu tab, 3 cơ sở mỗi cơ sở có Call / WhatsApp / Get directions. Mobile: header cố định + nút WhatsApp nổi.
- **Uni Nails**: banner ảnh "Uni Family" → giới thiệu + Đặt lịch → (dịch vụ) → Top reviews nhiều ngôn ngữ → 4 ô lý do → Hình ảnh. Mobile: thanh dưới Facebook / Messenger / Instagram / G-Map / Booking + nút chọn ngôn ngữ.
- **Nail Kitchen**: About → 4 nhóm dịch vụ (Book Now sang Picktime) → combo có giá → đồ uống → testimonial → 4 cơ sở. Mobile: dải "CALL US" cố định đáy + 3 icon nổi.
- **Healing, Ocean, Nét Đẹp**: nút liên hệ dọc nổi bên phải (WhatsApp, Zalo, KakaoTalk, LINE, gọi).
- **Colynn** (Carrd): một cột, 3 nút Hotline / Booking / WhatsApp, link PDF menu; không có nút cố định.

### Điều rút ra cho mẫu web tiệm nail Việt Nam

- Kênh đặt lịch thật sự là **chat**: Zalo cho khách Việt; WhatsApp, Instagram, KakaoTalk, LINE cho khách nước ngoài. Form web thường chỉ chuyển tiếp sang WhatsApp (Samélie) hoặc là trang của bên thứ ba (SalonHero, Picktime, SimplyBook, Fresha).
- Mobile luôn có **ít nhất một nút liên hệ cố định**; mẫu tốt nhất là thanh dưới có nút theo từng chi nhánh (Lisa) hoặc Book / Call / Map (Samélie).
- Bảng giá dạng ảnh dễ cập nhật nhưng không tìm kiếm được và khó đọc trên điện thoại; site có giá dạng HTML (Euphorea, Nail Kitchen, 22Spa, Posh) dễ so sánh và hiển thị tốt hơn. Mẫu nên có bảng giá HTML theo nhóm, đơn vị rõ (/bộ, /ngón), cột giá chi nhánh nếu có.
- Thông tin bảo hành, tháo gel miễn phí đặt ngay dưới bảng giá (Tropicana, Colynn) thay vì giấu trong trang chính sách.
- Nhiều tiệm có điểm Maps rất cao (4,8-5,0 với hàng nghìn đánh giá) nhưng website chết hoặc không có; Facebook và Google Maps mới là kênh chính. Một website gọn, có giá và nút chat sẽ nổi bật trong nhóm này.
- Điểm cần tránh thấy trong thực tế: tên miền hết hạn, link chính sách trỏ về trang chủ, chữ mẫu template còn sót, giờ mở cửa ghi hai kiểu, số liệu tự công bố không khớp nhau, tràn ngang trên mobile, popup đặt lịch giả lập.
