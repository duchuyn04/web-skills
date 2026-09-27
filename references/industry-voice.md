# Industry voice

People who buy or sell outsourcing read vendor homepages every week. They can tell AI-written copy because it breaks the conventions of the industry, even when every sentence is grammatical and every fact is plausible. This file lists those conventions. It comes from the homepages of 106 English-language and 14 Vietnamese-language BPO, staffing and IT outsourcing companies, collected in September 2026. Only counts and patterns were kept; no company's wording is reused here.

Read this file before writing copy. `build.py` enforces part of it (see "What the build checks" at the end).

## What gives AI copy away

The table compares the first version of this skill's example pages (written by an LLM that followed the old rules) with the real sites.

| Signal | AI-written examples | Real sites |
|:---|---:|---:|
| Hero title addresses the reader (you, your) | 100% | 14% |
| Hero title uses "[people] who/that [verb] your [thing]" | 67% | 8% |
| Hero title length, median words | 9 | 6 |
| Section headings that address the reader | 36% | 12% |
| Section headings that are short labels ("Case studies") | 6% | 34% |
| ", with ..." add-on clauses per 100 sentences | 4.9 | 0.7 |

Three habits cause most of the damage:

1. Every heading is a crafted benefit line aimed at "you". Real pages mix plain labels ("Our services", "Industries we serve", "How it works") with a few claims.
2. Invented process detail everywhere. The AI examples used words like week, hours, within, first call, pilot and monthly five to eight times more often than real sites ("reports to you every Friday", "daily report by 07:00", "replies within two business days"). One such detail makes a page concrete; ten make it read like a model trying to sound specific.
3. The category words are missing. Real sites repeat services, outsourcing, global, delivery, partner, talent, expertise, customer experience and solutions. The AI examples avoided them almost entirely, which makes the company sound unlike any real vendor. Repeating the category vocabulary is normal; do not hunt for synonyms.

## Hero

Title: 3-8 words, about the company or its category, rarely about the reader. Pick one pattern and fill it with the client's facts:

| Pattern | Shape | Fits |
|:---|:---|:---|
| Category and place | "[Service] company in [country]", "Offshore [role] teams in [city]", "[Service] outsourcing in Vietnam" | Staffing, Vietnam and Philippines vendors, IT outsourcing |
| Category and buyer | "Customer operations for [industries]", "Outbound SDR teams for B2B sales", "Human data for AI training and evaluation" | Enterprise CX, sales development, AI data |
| Short positioning line | A plain claim the brief supports, may end with a period: "[Human-led / Managed] [service], [qualifier]." | Brands with a clear position |
| Recognition | "[Ranking or award] [category] company" | Only when the client holds that ranking |

Mark 1-3 words as `*accent*`. Real hero titles often end with a period (31%); that is allowed.

Lead: the first sentence has the company name as its subject and says what it does, for whom and since when. The second gives scale or place (headcount, delivery centers, languages, certifications). Example shape: "[Brand] has run [services] for [buyers] since [year]. Our [number] [people] work from [cities] in [number] languages."

Proof chips and badges: founding year, headcount, certifications, languages, coverage hours, savings percentage. These are the facts real sites put near the top.

## Section headings

About a third should be plain labels, a few can be claims, and at most one in four should address the reader. Put the accent markup on the hero and two or three headings, not on every one.

| Section | Common English labels | Common Vietnamese labels |
|:---|:---|:---|
| About | About [Brand], Who we are | Về chúng tôi, Giới thiệu |
| Services | Our services, What we do, [Category] services | Dịch vụ, Dịch vụ của chúng tôi |
| Industries | Industries we serve, Industries | Lĩnh vực, Ngành nghề |
| Process | How it works, How we work | Quy trình làm việc |
| Why us | Why [Brand], Why choose us | Vì sao chọn [Tên] |
| Numbers | [Brand] at a glance, [Brand] in numbers | Thành tựu, [Tên] qua những con số |
| Case studies | Case studies, Our work, Client results | Dự án tiêu biểu, Khách hàng tiêu biểu |
| Testimonials | What our clients say | Khách hàng nói về chúng tôi |
| Security | Security and compliance, Certifications | Chứng nhận và giải thưởng, Bảo mật |
| Locations | Our delivery centers, Our locations | Văn phòng, Trung tâm vận hành |
| Insights | Latest insights, Resources, Blog | Tin tức, Tin tức và sự kiện |
| FAQ | Frequently asked questions | Câu hỏi thường gặp |
| Contact | Contact us, Talk to our team, Get in touch | Liên hệ, Liên hệ tư vấn |

When the heading is a label, the eyebrow above it should add information ("Since 2009", "Four countries") or be left out; do not repeat the label.

## Body copy

- Say what the company is in category words buyers search for: outsourcing, BPO, offshore, nearshore, customer support, back office, delivery center, dedicated team, managed service, talent.
- Keep one operational detail per card. Put a single response-time promise near the form instead of timetables in every section.
- Use the proof real sites use. Share of the 106 sites showing each:

| Proof | Share |
|:---|---:|
| Industries named (healthcare, fintech, retail...) | 74% |
| Careers link in the menu or footer | 59% |
| Big number with a plus sign (10,000+ agents, 160+ clients) | 58% |
| Percentage claim (save up to 60%, 98% accuracy) | 47% |
| Founding year or years in business | 45% |
| People plus AI or technology positioning | 45% |
| Countries or cities of delivery | 32% |
| Analyst ranking or award | 31% |
| Named certification (ISO 27001, SOC 2, PCI DSS, HIPAA) | 21% |
| A named method or platform with a trademark sign | 13% |

  All of these must come from the client. When the brief has none, leave that proof out; never make up an award, ranking or founding year.
- Do not tack an extra benefit onto a fact with ", so ..." or ", with ...". Two short sentences read better.
- Testimonials sound like people talking: one concrete change, at most one number, name, role and company.
- Industry abbreviations (AHT, CSAT, FCR, SLA, QA, KYC, RLHF) belong in cards, FAQ and case results. Real homepages rarely use them in hero titles.

## Buttons and links

Real sites use a small set of labels. The most common first words are explore, see, view, book, get, read, learn and start. Use labels such as:

- Primary: Contact us, Talk to an expert, Get a quote, Book a call, Book a demo, Get started, Request a proposal
- Secondary: Learn more, See case studies, Our services, View all, Read more, How it works
- Vietnamese: Liên hệ, Nhận báo giá, Đặt lịch tư vấn, Xem thêm, Tìm hiểu thêm, Xem dự án

Avoid invented labels ("Ask about fit", "Plan a care program", "Hear our callers").

## Vietnamese pages

- The company is "chúng tôi" or its name. The reader is "khách hàng", "doanh nghiệp" or "Quý khách". "Bạn" appears on real sites but far less often than "chúng tôi" (33 against 95 uses in the study).
- The first sentence names the company and its category: "[Tên] là [loại hình dịch vụ] tại [nơi], thành lập năm [năm]."
- Keep the English terms the industry uses: BPO, outsourcing, offshore, KPI, SLA, QA, CSAT.
- Use the terms Vietnamese vendors use, not word-for-word translations. The right column shows what models tend to write when they translate:

| English term | Common Vietnamese industry term | Avoid (literal translation) |
|:---|:---|:---|
| dedicated team | đội ngũ riêng, nhân sự chuyên trách | nhóm nhân sự tận tâm |
| back office | back-office, nghiệp vụ hỗ trợ, vận hành nội bộ | hoạt động hành chính |
| contact center | tổng đài, trung tâm chăm sóc khách hàng | trung tâm liên hệ |
| account manager | quản lý dự án, phụ trách khách hàng | trưởng phòng ban |
| delivery center | trung tâm vận hành, văn phòng | trung tâm giao hàng |
| go live | vận hành chính thức, bắt đầu triển khai | đi vào sống |
| shared dashboard | báo cáo trực tuyến, hệ thống báo cáo | bảng điều khiển chia sẻ |
| calibration | thống nhất tiêu chí chấm điểm | hiệp chỉnh |
| service credits (SLA) | cam kết chất lượng dịch vụ (SLA), điều khoản phạt | tín dụng dịch vụ |
| Talk to an expert | Liên hệ tư vấn, Nhận tư vấn | Nói chuyện với chuyên gia |

- Headings are short labels in sentence case (see the table above). Many Vietnamese sites use ALL CAPS headings; the house style keeps sentence case.
- Do not translate English marketing lines word for word. The build rejects these phrases, which none of the Vietnamese sites use: "hãy để chúng tôi", "trong khi bạn", "để bạn tập trung", "nâng tầm", "giải phóng/khai phá/mở khóa tiềm năng", "trong bối cảnh", "hơn bao giờ hết", "kiến tạo tương lai", "bứt phá", "chinh phục mọi", "không chỉ ... mà còn".

## By archetype

| Archetype | Hero pattern | What real sites in this group lead with |
|:---|:---|:---|
| `enterprise-cx` | Category and buyer | Scale (agents, countries, languages), certifications, people plus AI, industries |
| `offshore-staffing` | Category and place | Savings percentage, time to hire, roles, employer of record, "an extension of your team" |
| `ai-data-ops` | Category and buyer | Data types, quality metrics, vetted experts, security controls |
| `cx-voice-sales` | Category and buyer | Meetings, pipeline and call numbers (half of hero titles in this group contain a number), CRM names, call recordings |
| `it-bpo-partner` | Category and place | "[Service] company in Vietnam", years in business, headcount, ISO certifications, markets served (US, Japan, Australia) |

## Before and after

| Field | AI-style | Industry voice |
|:---|:---|:---|
| Hero title | Support teams that protect your CSAT while you scale | Customer operations for banks, telcos and retail |
| Hero lead | We recruit, train and run dedicated customer care teams, with live reporting from day one. | Northbridge CX has run voice, chat and back-office programs since 2009. Our 2,400 agents work from Manila, Ho Chi Minh City, Bogota and Krakow in 12 languages. |
| Services heading | Pick the programs you need and add more later | Customer care and back-office services |
| Why-us row | Agents who already speak your customers' language. Your team approves the shortlist, so nobody joins the floor as a stranger to your brand. | Hiring with client sign-off. Recruiters screen for language level, product knowledge and tone. Your team interviews the shortlist and approves each hire. |
| Metrics heading | Numbers our clients check every week | Northbridge at a glance |
| Contact heading | Get a staffing plan in two business days | Talk to our solutions team |

## What the build checks

- Error: a sentence copied from an example page, or a figure, time frame or contract term that appears in an example but not in `"brief"`. The examples describe fictional companies; their numbers are sample data.
- Warning: a figure that is not in `"brief"` (years in business derived from the founding year are accepted).

- Error: any phrase from the English or Vietnamese "llm-tell" lists in `scripts/rules.py` (for example "while you scale", "so nobody", "peace of mind", "every step of the way", "hãy để chúng tôi").
- Error: more than 40% of section headings address the reader. Warning above 25%.
- Warning: no section heading is a short label.
- Warning: hero title longer than 10 words, or built on the "[people] who/that [verb] your [thing]" formula.
- Warning: "every call", "each agent" and similar phrases more than twice on a page.
