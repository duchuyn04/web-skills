# bpo-landing-builder

Skill giúp coding agent dựng landing page cho công ty BPO, outsourcing, contact center, offshore staffing, xử lý dữ liệu AI hoặc bán hàng outbound.

Nếu bạn từng nhờ AI làm giao diện kiểu này, chắc bạn biết vấn đề: model mạnh làm ra trang đẹp, model yếu làm ra trang xấu, còn bố cục thì mỗi lần một kiểu. Skill này giải quyết bằng cách lấy quyết định thiết kế ra khỏi tay model. Agent chỉ điền một file `page.json` với nội dung công ty. Một script Python ghép file đó thành trang hoàn chỉnh từ 49 section đã làm sẵn, đã chỉnh spacing, responsive và animation. Mình đã thử với Haiku và Opus trên cùng một brief: hai trang ra cùng bố cục và cùng độ chỉn chu, khác nhau ở phần chữ.

## Cài đặt

Bạn cần Node.js (để chạy `npx`). Trong thư mục project, chạy:

```bash
npx skills@latest add duchuyn04/bpo-landing-builder
```

CLI sẽ hỏi bạn muốn cài cho agent nào, rồi tự đặt skill vào đúng thư mục của từng agent. Mình đã xác nhận CLI nhận ra skill này, nhưng chưa thử hết từng agent một.

Vài tùy chọn hay dùng:

```bash
# Xem skill có gì trước khi cài
npx skills@latest add duchuyn04/bpo-landing-builder --list

# Cài cho mọi project trên máy thay vì chỉ project hiện tại
npx skills@latest add duchuyn04/bpo-landing-builder -g

# Chọn sẵn agent, khỏi bị hỏi
npx skills@latest add duchuyn04/bpo-landing-builder -a claude-code -a codex -a cursor

# Chép file thật thay vì tạo symlink (hữu ích trên Windows hoặc khi đưa project lên git)
npx skills@latest add duchuyn04/bpo-landing-builder --copy

# Cập nhật và gỡ
npx skills@latest update
npx skills@latest remove bpo-landing-builder
```

### Cài thủ công

Không muốn dùng `npx` thì clone repo rồi chép vào thư mục skills của agent:

```bash
git clone https://github.com/duchuyn04/bpo-landing-builder.git
cp -r bpo-landing-builder <thư-mục-skills>/bpo-landing-builder
```

Thư mục skills của từng agent (theo bảng của CLI `skills`):

| Agent | Thư mục trong project |
|:---|:---|
| Codex, Cursor, Gemini CLI, GitHub Copilot, OpenCode, Droid, Cline, Amp, Kilo Code | `.agents/skills/` |
| Claude Code | `.claude/skills/` |
| Qwen Code | `.qwen/skills/` |
| Roo Code | `.roo/skills/` |
| Kiro | `.kiro/skills/` |
| Continue | `.continue/skills/` |
| Windsurf | `.windsurf/skills/` |
| Oh My Pi | `.agents/skills/` (đọc được ngay, xem ghi chú bên dưới) |

Oh My Pi không có trong danh sách agent của CLI `skills`, nên lệnh `npx` không tạo thư mục `.omp/skills`. Điều này không ảnh hưởng gì: Oh My Pi tự đọc cả `.agents/skills` và `.claude/skills`, ở cấp project lẫn cấp người dùng. Chỉ cần skill nằm trong một trong hai thư mục đó là Oh My Pi thấy, nên cài cho Codex (dùng `.agents/skills`) hoặc Claude Code (dùng `.claude/skills`) đều được. Thư mục file của Oh My Pi hoặc IDE có thể ẩn các thư mục bắt đầu bằng dấu chấm, nên nếu không thấy `.agents` thì dùng `dir /a` (Windows) hoặc `ls -a` để kiểm tra. Muốn dùng đúng thư mục riêng của Oh My Pi thì chép skill vào `.omp/skills/` trong project, hoặc `~/.omp/agent/skills/` để dùng cho mọi project.

Agent không tự nạp skill thì bảo nó đọc `SKILL.md` trong thư mục vừa chép và làm theo từng bước. Nếu project có `AGENTS.md`, thêm một dòng trỏ tới đường dẫn đó là đủ.

### Yêu cầu máy

- Python 3.9 trở lên để chạy `build.py` và `lint_output.py`. Hai script chỉ dùng thư viện chuẩn, không cần `pip install`.
- Bước chụp ảnh kiểm tra cần Python Playwright (`pip install playwright`) và Edge hoặc Chrome trên máy. Không có trình duyệt thì chạy `python -m playwright install chromium`.
- Agent phải chạy được lệnh shell. Agent chỉ chat mà không chạy lệnh thì không dùng được skill này.

## Cách dùng

Mở agent trong project rồi đưa brief của khách, ví dụ:

> Dùng bpo-landing-builder làm landing page cho Saigon Bridge Outsourcing. Công ty ở TP.HCM, khoảng 300 nhân sự, bán dịch vụ chăm sóc khách hàng tiếng Anh và kế toán cho doanh nghiệp Mỹ và Úc. Khách nói tiết kiệm khoảng 60% so với thuê tại chỗ, có chứng chỉ ISO 27001.

Claude Code gọi bằng `/bpo-landing-builder`, Codex gọi bằng `$bpo-landing-builder`. Các agent khác chỉ cần nhắc tên skill.

Agent sẽ chọn một trong 5 kiểu trang, chọn bộ màu, copy file `page.json` mẫu rồi sửa nội dung, sau đó chạy build, lint và chụp ảnh kiểm tra. Trang xong nằm ở `sites/<tên-công-ty>/dist/index.html`, mở thẳng bằng trình duyệt là xem được.

Thiếu thông tin thì skill không bịa. Một con số thiếu sẽ thành `[KPI]`. Cả một khối bằng chứng thiếu (logo khách hàng, lời chứng thực, file ghi âm cuộc gọi, bảng lương để tính tiết kiệm) thì section đó bị bỏ, và agent báo lại cho bạn những gì còn thiếu.

Nên dán nguyên brief của khách vào trường `"brief"` trong `page.json`. Build dựa vào đó để phân biệt số liệu thật với số liệu mẫu: một câu chép gần nguyên văn từ trang mẫu, hoặc mang con số của công ty mẫu (kiểu "báo trước 30 ngày", "phản hồi trong 48 giờ") mà brief không có, sẽ làm build dừng.

## Giọng văn ngành

Văn phong được đo trên trang chủ của 106 công ty BPO viết bằng tiếng Anh và 14 trang tiếng Việt. Người trong ngành nhận ra copy do AI viết qua cấu trúc nhiều hơn qua từ ngữ, và bảng dưới là các khác biệt đo được:

| Dấu hiệu | Copy AI cũ của skill | Site thật |
|:---|---:|---:|
| Tiêu đề hero nói với người đọc ("your") | 100% | 14% |
| Tiêu đề hero theo công thức "[người] who/that [làm gì] your [cái gì]" | 67% | 8% |
| Tiêu đề section là nhãn ngắn ("Case studies", "Dịch vụ") | 6% | 34% |
| Mệnh đề nối đuôi ", with ..." trên 100 câu | 4,9 | 0,7 |

Skill xử lý bằng ba cách. `references/industry-voice.md` hướng dẫn cách viết theo từng kiểu trang, kèm nhãn tiêu đề và nút bấm mà site thật dùng. Build chặn các cụm mà gần như không site BPO nào dùng ("while you scale", "peace of mind", "hãy để chúng tôi", "nâng tầm"...) và cảnh báo khi quá nhiều tiêu đề nói với người đọc. Trang mẫu tiếng Việt `examples/vi/enterprise-cx.page.json` được viết thẳng bằng tiếng Việt, nên model không phải dịch từ tiếng Anh.

## Chạy tay, không cần agent

Trong thư mục của skill:

```bash
python scripts/build.py examples/enterprise-cx.page.json --out dist
python scripts/lint_output.py dist
python scripts/qa_screenshot.py dist --sections
```

Năm file mẫu trong `examples/` và ba trang biến thể trong `examples/variations/` build được ngay. Bạn có thể copy một file ra ngoài, đổi chữ và build lại để xem nó hoạt động thế nào.

## Bên trong có gì

Năm kiểu trang, mỗi kiểu có thứ tự section cố định:

| Kiểu | Dùng cho | Bộ màu mặc định |
|:---|:---|:---|
| `enterprise-cx` | Tập đoàn CX nhiều dịch vụ, nhiều trung tâm, khách là ngân hàng, viễn thông | `enterprise-navy` |
| `offshore-staffing` | Thuê đội ngũ riêng ở Việt Nam hoặc Philippines, điểm bán hàng là tiết kiệm chi phí | `human-warm` |
| `ai-data-ops` | Gán nhãn dữ liệu, RLHF, kiểm duyệt nội dung | `dark-ai` |
| `cx-voice-sales` | Đội gọi điện, telesales, tổng đài, chất lượng cuộc gọi là bằng chứng chính | `clean-minimal` |
| `it-bpo-partner` | Công ty vừa làm phần mềm (ITO) vừa làm back-office (BPO), nhiều dịch vụ, thường giao hàng từ Việt Nam | `orange-charcoal` |

49 section gồm header có megamenu, bảy kiểu hero (ảnh chia đôi, chữ đổi từ, mạng lưới điểm 3D, nền ảnh hoặc video toàn khung, nền gradient màu thương hiệu có quả cầu chấm xoay, hero có thẻ chọn nhanh nhu cầu, hero ghép ảnh tròn với hình khối màu), dải chữ chạy ngang, câu tuyên bố lớn hiện dần từng chữ, dải ảnh giữa trang, trích dẫn khách hàng cỡ lớn có chuyển qua lại, phần giới thiệu kèm lưới ảnh đội ngũ, khung số liệu 2x2, danh sách dịch vụ dạng hàng link, khối giải pháp hai thẻ trên nền tối, thẻ đối tượng khách hàng, khối liên hệ chia đôi có địa chỉ từng văn phòng, băng chuyền logo, bộ đếm số, bento có đèn rọi theo chuột, tab dịch vụ, hàng ảnh và chữ xen kẽ, thẻ ảnh cho tin tức hoặc ngành (dạng lưới hoặc slider kéo được), khối video mở trong modal, dải kêu gọi hành động, máy tính tiết kiệm chi phí, trình phát cuộc gọi mẫu, timeline quy trình, bảng giá có công tắc, bản đồ hub có ghim radar, slider case study, FAQ, form báo giá 3 bước, footer và các nút nổi. Thêm bảy section lấy bố cục từ các sản phẩm sát ngành trên Mobbin (Deel, Upwork, Intercom, Airtable...): bảng so sánh với tự tuyển, dải giải thưởng và điểm đánh giá, lưới ban lãnh đạo, khối tuyển dụng, lưới công cụ đang dùng, quy trình dạng hàng ngang và thẻ quốc gia có cờ. Toàn bộ chạy bằng HTML, CSS và JavaScript thuần, không cần build frontend.

Có 8 bộ màu. Ngoài 5 bộ mặc định theo kiểu trang còn có `corporate-blue`, `crimson-trust` và `teal-fresh`, dành cho thương hiệu có logo xanh dương, đỏ hoặc xanh ngọc (ba nhóm màu này chiếm khoảng 55% trong 113 site đã phân tích). Ba bộ này bật thêm các tùy chọn thiết kế: mép section cắt chéo hoặc cong, khung ảnh cắt góc hoặc hình vòm, chữ nhấn dạng gradient hoặc gạch chân, ảnh hiện ra bằng hiệu ứng quét từ dưới lên. Bộ màu nào cũng dùng được các tùy chọn này qua khóa `theme` trong `page.json`, chi tiết ở `references/style-presets.md`.

Ba lớp kiểm tra chạy trước khi giao:

1. `build.py` kiểm tra `page.json` theo schema từng section: giới hạn độ dài chữ, số item, tên icon, link nội bộ, thứ tự section, giọng văn và câu chép từ trang mẫu. Mỗi lỗi ghi rõ đường dẫn JSON và cách sửa.
2. `lint_output.py` quét trang đã dựng: emoji, mũi tên bằng chữ, gạch ngang dài, dấu ngoặc cong, từ ngữ kiểu AI, thiếu `alt`, nhiều hơn một `h1`, inline style.
3. `qa_screenshot.py` chụp ở 1440, 768 và 390 px, tìm phần tử tràn ngang, chữ bị cắt, ảnh hỏng và lỗi JavaScript.

## Cấu trúc thư mục

```
SKILL.md          quy trình cho agent, đọc file này trước
references/       tài liệu tra cứu (một số file do script sinh ra)
templates/        base.css, base.js, 49 section, 8 bộ màu, icon, cờ, ảnh và video mẫu
examples/         5 file page.json mẫu, mỗi kiểu trang một file; variations/ có 3 trang, mỗi bộ màu mới một trang; vi/ có trang mẫu tiếng Việt
previews/         ảnh chụp từng section
scripts/          build, lint, QA, sinh tài liệu
agents/           metadata cho Codex
```

## Thêm section mới

Mobbin không có trang của công ty BPO, nhưng có nhiều sản phẩm sát ngành với thiết kế tốt. Nếu máy bạn đã kết nối Mobbin MCP, agent có thể tra mẫu tham khảo trước khi làm section mới; quy trình và danh sách tham chiếu nằm trong `references/mobbin-references.md`. Việc tạo trang không cần Mobbin.

1. Tạo `templates/sections/<tên>/` gồm `schema.json`, `section.html`, `section.css` và `section.js` nếu cần. Copy một section có sẵn để làm mẫu.
2. Thêm tên vào slot phù hợp trong `templates/archetypes.json`.
3. Dùng nó trong ít nhất một file ở `examples/`, rồi build, lint và QA.
4. Chạy `python scripts/make_catalog.py` để cập nhật tài liệu tra cứu. Thêm `--previews <thư mục dist>` nếu muốn làm mới ảnh preview.

Khách cần một khối mà thư viện chưa có thì xem `references/custom-section-spec.md`, cách viết section riêng nằm ngoài thư viện.

## Giới hạn hiện tại

- Form báo giá chưa gửi dữ liệu đi đâu. Điền URL endpoint vào `form.action` trong `page.json` khi có.
- Ảnh trong `templates/assets/images` là ảnh stock để xem thử. Trang thật nên dùng ảnh của khách. Kiểm tra giấy phép của các ảnh này trước khi dùng cho dự án thương mại.
- Video mẫu `sample-ambient-loop` là một đoạn nền trừu tượng do `scripts/make_sample_video.py` tự vẽ, chỉ để xem thử. Hero nền video và khối video nên dùng video thật của khách; khối video còn nhận link YouTube hoặc Vimeo và chỉ tải trình phát khi người xem bấm play.
- Skill chặn được lỗi bố cục và lỗi câu chữ, nhưng vẫn không ngăn hẳn model yếu thêm chi tiết nhỏ không có trong brief, ví dụ chia số nhân sự cho từng văn phòng. Nên đọc lại nội dung trước khi giao cho khách.
- Bản đồ và cờ vẽ bằng SVG, phủ 44 quốc gia và 73 thành phố hub phổ biến. Thành phố chưa có thì truyền tọa độ trực tiếp trong `page.json`.
