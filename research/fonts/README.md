# Font cho website tiếng Việt và website song ngữ

Ngày đo: 2026-10-07. Nguồn: metadata của Google Fonts (`fonts.google.com/metadata/fonts`, 1.950 họ font), render thật trong Edge (Playwright) và đo bằng canvas. Bảng mẫu nằm ở `sheets/`, số đo ở `metrics.json`. Áp dụng cho mọi skill trong repo, đặc biệt `nail-salon-builder`.

## 1. Hỗ trợ ngôn ngữ trên Google Fonts

| Bộ chữ | Số họ font | Ghi chú |
|---|---|---|
| Tiếng Việt (`vietnamese`) | 520 | 225 sans, 86 serif, 88 display, 99 viết tay |
| Hàn (`korean`) | 38 | Noto Sans KR, Nanum Gothic, Gothic A1, Gowun Dodum... |
| Nhật (`japanese`) | 68 | Noto Sans JP, M PLUS Rounded 1c, Zen Kaku Gothic New... |
| Trung giản thể / phồn thể | 10 / 16 | Noto Sans SC / TC là lựa chọn chính |
| Thái (`thai`) | 34 | Kanit, Prompt, Sarabun, Noto Sans Thai |

Font có **cả tiếng Việt và chữ châu Á** (một font cho menu song ngữ): Noto Sans KR, Noto Serif KR, Gothic A1, Gowun Batang, Gowun Dodum (Hàn); Noto Sans JP, Noto Serif JP, M PLUS Rounded 1c (Nhật); Noto Sans SC, Noto Sans TC (Trung); Kanit, Prompt, Mitr, Sarabun, Mali, Itim, Charm, Chonburi (Thái).

## 2. Font phổ biến nhưng KHÔNG có tiếng Việt

Các font này xuất hiện trên website salon thật trong nghiên cứu (part 1, 3, 4) nhưng Google Fonts không có bộ chữ tiếng Việt. Khi dùng cho tiếng Việt, trình duyệt lấy chữ có dấu từ font khác, nên trong một từ có hai kiểu chữ ("Đ", "ặ", "ố" khác nét).

Poppins, DM Sans, Jost, Outfit, Figtree, Urbanist, Sora, Albert Sans, Red Hat Display, Fredoka, Lato, Libre Baskerville, Italiana, Cinzel, Marcellus, Bodoni Moda, Gilda Display, DM Serif Display, Instrument Serif, Young Serif, Tenor Sans, Forum, Bellefair, Lustria, Lilita One, Chewy, Sniglet, Caveat, Parisienne, Sacramento, Cookie, Zen Kaku Gothic New, Zen Maru Gothic, LINE Seed JP, Shippori Mincho, Nanum Gothic, Nanum Myeongjo.

Thay thế gần nhất: Poppins thì dùng Montserrat hoặc Be Vietnam Pro; DM Sans, Jost, Outfit thì dùng Manrope, Plus Jakarta Sans hoặc Lexend; Libre Baskerville thì dùng Lora hoặc Newsreader; Italiana, Cinzel, Marcellus thì dùng Cormorant Garamond; Bodoni Moda, DM Serif Display thì dùng Playfair Display hoặc Libre Bodoni; Caveat, Sacramento, Parisienne thì dùng Dancing Script, Birthstone hoặc Allura; Fredoka thì dùng Baloo 2 hoặc Quicksand.

## 3. Dấu chồng và chiều cao dòng

Tiếng Việt có dấu chồng hai tầng (ầ ẫ ậ ẳ ể ỗ ữ) nên phần chữ cao hơn tiếng Anh. Đo trên chữ cỡ 100 px:

- `stack_low`: độ cao của "ẫ" (chữ thường có dấu chồng)
- `stack_cap`: độ cao của "Ẫ" (chữ hoa có dấu chồng)
- `desc`: độ sâu đuôi chữ "g", "ỵ"

Hai dòng chạm nhau khi phần cao của dòng dưới cộng phần đuôi của dòng trên lớn hơn khoảng cách hai dòng. Từ đó:

- giãn dòng tối thiểu cho tiêu đề chữ thường: `(stack_low + desc) / 100 + 0,05`
- giãn dòng tối thiểu cho tiêu đề VIẾT HOA: `(stack_cap + desc) / 100 + 0,05`

Đoạn văn (giãn dòng 1,5 đến 1,7) an toàn với mọi font đã đo. Rủi ro nằm ở tiêu đề (thường đặt 1,1 đến 1,2) và chữ viết hoa.

| Font | Tiêu đề thường | VIẾT HOA | Nhận xét khi xem |
|---|---|---|---|
| Cormorant Garamond | 1,15 | 1,20 | Dấu gọn nhất trong nhóm serif sang |
| EB Garamond, Newsreader, Fraunces | 1,15 | 1,30 đến 1,35 | Tốt |
| Lora, Libre Bodoni, Noto Serif Display | 1,20 | 1,35 đến 1,50 | Tốt, Bodoni đậm |
| Playfair Display | 1,25 | 1,40 | Đẹp nhưng sát dòng ở 1,2 |
| Prata | 1,30 | 1,50 | Chạm dòng trên ở 1,2 (thấy rõ trong `sheets/serif.jpg`) |
| Be Vietnam Pro, Inter, Open Sans | 1,20 | 1,35 đến 1,45 | Thiết kế kỹ cho tiếng Việt, dấu cao |
| Montserrat, Quicksand, Source Sans 3, Kanit | 1,15 | 1,20 đến 1,25 | Dấu thấp, hợp tiêu đề viết hoa |
| Plus Jakarta Sans, Manrope, Lexend | 1,25 | 1,35 đến 1,45 | |
| Bricolage Grotesque | 1,35 | 1,50 | Đuôi chữ dài |
| Baloo 2, Itim | 1,15 | 1,20 đến 1,25 | Tốt nhất cho phong cách vui tươi |
| Mali, Calistoga, Grandstander | 1,20 đến 1,30 | 1,40 đến 1,45 | |
| Lemonada, Playpen Sans, Shantell Sans, Coiny, Paytone One | 1,35 đến 1,55 | 1,50 đến 1,70 | Dấu quá cao, tránh cho tiêu đề nhiều dòng |

## 4. Chữ viết tay (script)

Tiệm nail, spa hay dùng chữ viết tay cho điểm nhấn. Kết quả xem bằng mắt (`sheets/script.jpg`):

- Đọc tốt với tiếng Việt: **Dancing Script, Birthstone, Moon Dance, Oooh Baby, Allura, Charm** (Charm đuôi chữ rất dài, giãn dòng từ 1,5).
- Chỉ dùng cho chữ thường ngắn, không viết hoa: Great Vibes, Alex Brush, Pinyon Script, Ms Madi, Meow Script, Style Script, Italianno, Corinthia (chữ hoa trang trí cộng dấu chồng thành khó đọc).
- Tránh: **Ephesis** (chữ hoa có dấu bị vỡ), **Pacifico** (chữ hoa lẫn dấu dính nhau, giãn dòng phải 1,45), **Bad Script** (dấu chạm dòng trên).

Quy tắc: chữ viết tay chỉ cho tối đa 4 đến 5 từ (tagline, nhãn nhỏ), không cho đoạn văn, nút bấm, giá, menu.

## 5. Cặp font gợi ý theo phong cách

| Phong cách | Tiêu đề | Nội dung | Điểm nhấn | Giãn dòng tiêu đề |
|---|---|---|---|---|
| Sang trọng ấm | Cormorant Garamond 500 đến 600 | Be Vietnam Pro hoặc Manrope | Allura hoặc Birthstone | 1,15 đến 1,2 |
| Sang trọng (thay thế) | EB Garamond, Newsreader, Fraunces | Mulish, Nunito Sans | | 1,2 |
| Tối giản Hàn Nhật | Be Vietnam Pro 600 đến 700 | Be Vietnam Pro | | 1,2 đến 1,25 |
| Tối giản (thay thế) | Plus Jakarta Sans, Lexend, Manrope | Inter, Be Vietnam Pro | | 1,25 |
| Quyến rũ tối | Playfair Display | Be Vietnam Pro | Dancing Script | 1,25 (VIẾT HOA 1,4) |
| Quyến rũ tối (thay thế) | Libre Bodoni, Noto Serif Display | Montserrat | | 1,2 |
| Vui tươi | Baloo 2 700 đến 800 | Be Vietnam Pro hoặc Nunito | Itim | 1,15 đến 1,2 |
| Vui tươi (thay thế) | Calistoga, Mali, Grandstander | Quicksand, Nunito | | 1,25 đến 1,3 |

Font nội dung tiếng Việt an toàn: Be Vietnam Pro, Inter, Manrope, Mulish, Nunito Sans, Montserrat, Open Sans, Roboto, Source Sans 3, Lexend.

## 6. Menu song ngữ và khách nước ngoài

Phần 6 nghiên cứu cho thấy tiệm ở khu du lịch có menu tiếng Anh, Hàn, đôi khi Nhật, Trung, và kênh KakaoTalk, LINE, WhatsApp.

- **Tiếng Anh**: mọi font tiếng Việt ở trên đều đủ.
- **Hàn, Nhật, Trung, Thái** trong cùng trang tiếng Việt: kiểm tra ngày 2026-10-07 cho thấy:
  - nếu khai báo một chuỗi font chung, chữ Nhật và chữ Trung bị vẽ bằng font Hàn (Malgun Gothic, Noto Sans KR) vì font Hàn cũng chứa chữ Hán và kana, nên chữ Hán sai kiểu theo từng nước;
  - cách đúng: bọc chữ nước ngoài trong `<span lang="ko|ja|zh|th">` và khai báo font theo `:lang()`:

```css
:lang(ko){font-family:var(--font),'Noto Sans KR','Apple SD Gothic Neo','Malgun Gothic',sans-serif}
:lang(ja){font-family:var(--font),'Noto Sans JP','Hiragino Sans','Yu Gothic',sans-serif}
:lang(zh){font-family:var(--font),'Noto Sans SC','PingFang SC','Microsoft YaHei',sans-serif}
:lang(th){font-family:var(--font),'Noto Sans Thai','Thonburi','Leelawadee UI',sans-serif}
```

  - font Latin đứng đầu nên số, giá và chữ Việt trong cùng dòng vẫn giữ một kiểu; chữ ngoại dùng font của nước đó.
  - chiều cao dòng không đổi khi trộn chữ (đo 31 px ở 20 px, giãn dòng 1,5 cho cả 5 trường hợp).
- **Tải font châu Á**: Noto Sans KR, JP, SC rất nặng; Google Fonts chia nhỏ theo `unicode-range` nên trình duyệt chỉ tải phần chữ cần. Khi chỉ có vài từ (tên dịch vụ, khẩu hiệu), thêm `&text=<các ký tự>` vào link css2 để chỉ tải đúng những ký tự đó. Có thể bỏ hẳn font web và dựa vào font hệ thống (Apple SD Gothic Neo, Malgun Gothic, Hiragino, Yu Gothic, PingFang, Microsoft YaHei, Thonburi, Leelawadee).
- **Thái**: Kanit, Prompt, Sarabun có cả tiếng Việt và chữ Thái, nên một font dùng được cho cả trang.

## 7. Lỗi hay gặp cần chặn khi build

1. Chọn font không có bộ chữ tiếng Việt (danh sách mục 2).
2. Tin rằng thêm `&subset=vietnamese` sẽ có dấu: API css2 tự trả phần `vietnamese` khi font có (kiểm tra 2026-10-07: Prata trả cyrillic-ext, cyrillic, vietnamese, latin), còn font không có tiếng Việt (Poppins chỉ có devanagari, latin-ext, latin) thì tham số đó không thêm được gì. Cách kiểm tra đúng là danh sách `subsets` trong metadata.
3. Tiêu đề giãn dòng 1,0 đến 1,1 với font dấu cao (mục 3), nhất là tiêu đề VIẾT HOA và `letter-spacing` lớn.
4. Chữ viết tay cho câu dài, nút bấm hoặc giá.
5. Font chữ Hàn đứng trước trong chuỗi font cho trang có chữ Nhật hoặc Trung.
6. Yêu cầu một độ đậm font không có (ví dụ Prata chỉ có 400). Kiểm tra 2026-10-07: link chỉ có `family=Prata:wght@500` trả HTTP 400; link ghép `family=Prata:wght@500&family=Inter` trả 200 nhưng **Prata bị bỏ qua không báo lỗi**, trang hiện font dự phòng. Build phải lấy độ đậm từ danh sách độ đậm có thật của font.
