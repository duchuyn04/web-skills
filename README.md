# bpo-landing-builder

Skill giúp coding agent dựng landing page cho công ty BPO, outsourcing, contact center, offshore staffing, xử lý dữ liệu AI hoặc bán hàng outbound.

Nếu bạn từng nhờ AI làm giao diện kiểu này, chắc bạn biết vấn đề: model mạnh làm ra trang đẹp, model yếu làm ra trang xấu, còn bố cục thì mỗi lần một kiểu. Skill này giải quyết bằng cách lấy quyết định thiết kế ra khỏi tay model. Agent chỉ điền một file `page.json` với nội dung công ty. Một script Python ghép file đó thành trang hoàn chỉnh từ 24 section đã làm sẵn, đã chỉnh spacing, responsive và animation. Mình đã thử với Haiku và Opus trên cùng một brief: hai trang ra cùng bố cục và cùng độ chỉn chu, khác nhau ở phần chữ.

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

Agent sẽ chọn một trong 4 kiểu trang, chọn bộ màu, copy file `page.json` mẫu rồi sửa nội dung, sau đó chạy build, lint và chụp ảnh kiểm tra. Trang xong nằm ở `sites/<tên-công-ty>/dist/index.html`, mở thẳng bằng trình duyệt là xem được.

Thiếu thông tin thì skill không bịa. Một con số thiếu sẽ thành `[KPI]`. Cả một khối bằng chứng thiếu (logo khách hàng, lời chứng thực, file ghi âm cuộc gọi, bảng lương để tính tiết kiệm) thì section đó bị bỏ, và agent báo lại cho bạn những gì còn thiếu.

## Chạy tay, không cần agent

Trong thư mục của skill:

```bash
python scripts/build.py examples/enterprise-cx.page.json --out dist
python scripts/lint_output.py dist
python scripts/qa_screenshot.py dist --sections
```

Bốn file mẫu trong `examples/` build được ngay. Bạn có thể copy một file ra ngoài, đổi chữ và build lại để xem nó hoạt động thế nào.

## Bên trong có gì

Bốn kiểu trang, mỗi kiểu có thứ tự section cố định:

| Kiểu | Dùng cho | Bộ màu mặc định |
|:---|:---|:---|
| `enterprise-cx` | Tập đoàn CX nhiều dịch vụ, nhiều trung tâm, khách là ngân hàng, viễn thông | `enterprise-navy` |
| `offshore-staffing` | Thuê đội ngũ riêng ở Việt Nam hoặc Philippines, điểm bán hàng là tiết kiệm chi phí | `human-warm` |
| `ai-data-ops` | Gán nhãn dữ liệu, RLHF, kiểm duyệt nội dung | `dark-ai` |
| `cx-voice-sales` | Đội gọi điện, telesales, tổng đài, chất lượng cuộc gọi là bằng chứng chính | `clean-minimal` |

24 section gồm header có megamenu, ba kiểu hero (ảnh chia đôi, chữ đổi từ, mạng lưới điểm 3D), băng chuyền logo, bộ đếm số, bento có đèn rọi theo chuột, tab dịch vụ, máy tính tiết kiệm chi phí, trình phát cuộc gọi mẫu, timeline quy trình, bảng giá có công tắc, bản đồ hub có ghim radar, slider case study, FAQ, form báo giá 3 bước, footer và các nút nổi. Toàn bộ chạy bằng HTML, CSS và JavaScript thuần, không cần build frontend.

Ba lớp kiểm tra chạy trước khi giao:

1. `build.py` kiểm tra `page.json` theo schema từng section: giới hạn độ dài chữ, số item, tên icon, link nội bộ, thứ tự section. Mỗi lỗi ghi rõ đường dẫn JSON và cách sửa.
2. `lint_output.py` quét trang đã dựng: emoji, mũi tên bằng chữ, gạch ngang dài, dấu ngoặc cong, từ ngữ kiểu AI, thiếu `alt`, nhiều hơn một `h1`, inline style.
3. `qa_screenshot.py` chụp ở 1440, 768 và 390 px, tìm phần tử tràn ngang, chữ bị cắt, ảnh hỏng và lỗi JavaScript.

## Cấu trúc thư mục

```
SKILL.md          quy trình cho agent, đọc file này trước
references/       tài liệu tra cứu (một số file do script sinh ra)
templates/        base.css, base.js, 24 section, bộ màu, icon, cờ, ảnh mẫu
examples/         4 file page.json mẫu
previews/         ảnh chụp từng section
scripts/          build, lint, QA, sinh tài liệu
agents/           metadata cho Codex
```

## Thêm section mới

1. Tạo `templates/sections/<tên>/` gồm `schema.json`, `section.html`, `section.css` và `section.js` nếu cần. Copy một section có sẵn để làm mẫu.
2. Thêm tên vào slot phù hợp trong `templates/archetypes.json`.
3. Dùng nó trong ít nhất một file ở `examples/`, rồi build, lint và QA.
4. Chạy `python scripts/make_catalog.py` để cập nhật tài liệu tra cứu. Thêm `--previews <thư mục dist>` nếu muốn làm mới ảnh preview.

Khách cần một khối mà thư viện chưa có thì xem `references/custom-section-spec.md`, cách viết section riêng nằm ngoài thư viện.

## Giới hạn hiện tại

- Form báo giá chưa gửi dữ liệu đi đâu. Điền URL endpoint vào `form.action` trong `page.json` khi có.
- Ảnh trong `templates/assets/images` là ảnh stock để xem thử. Trang thật nên dùng ảnh của khách. Kiểm tra giấy phép của các ảnh này trước khi dùng cho dự án thương mại.
- Hero video nền chưa có, vì cần video thật của khách.
- Skill chặn được lỗi bố cục và lỗi câu chữ, nhưng vẫn không ngăn hẳn model yếu thêm chi tiết nhỏ không có trong brief, ví dụ chia số nhân sự cho từng văn phòng. Nên đọc lại nội dung trước khi giao cho khách.
- Bản đồ và cờ vẽ bằng SVG, phủ 44 quốc gia và 73 thành phố hub phổ biến. Thành phố chưa có thì truyền tọa độ trực tiếp trong `page.json`.
