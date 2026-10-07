# Charts on an overview

Pick the chart from the data, not from the look. Sources: ecommerce-builder admin (grain rules, comparison), and on
Mobbin: QuickBooks Leads, Klaviyo, DoorDash Merchant, Calendly, Mintlify, Exa (range picker with comparison), Mixpanel.

## Which chart for which data

| Data | Chart | Notes |
|:---|:---|:---|
| A count over time (requests, orders, sites made) | Columns, one per hour, day, week or month | The comparison period is a dashed grey line over the same buckets. The bucket still running (today, this week) is the lighter `.c2` and says "tính đến 10:40" in the legend. |
| A rate or an average over time (conversion, response time) | Line | Columns suggest a total; a rate is not one. |
| Done and failed for the same thing | Stacked columns, failures `.cb` on top | Only two parts. |
| Steps one after another (sent, contacted, quoted, won) | Funnel: horizontal bars against the first step, with the share from the step before under each bar | Say when the later steps are not finished yet ("6 yêu cầu chưa gọi lần đầu"). |
| Groups compared (industry, source, staff) | Horizontal bars, largest first, at most 6 lines, the rest folded into "n nhóm khác" | Labels stay readable; a second figure (close rate) goes after the count. |
| One number now | A figure tile with the change against the comparison period | Colour the change by whether it is good: a shorter response time is green. |
| When things happen (weekday by hour) | Heat map | Only with 90 days or more of data; it is noise below that. |

Do not use pies or donuts with more than three parts, 3D, gauges, or a chart with no numbers on it. A chart needs an
axis or labels that give the values, a tooltip with the exact value and the comparison, and the same numbers in a
hidden table for screen readers.

## What an overview must have

1. The to-do list ("Cần làm ngay"), counted up to now and labelled so: it does not follow the date range.
2. Four figure tiles for the range, each with its change against the comparison period. Lead with the business
   (requests, close rate, response time), then the tool (sites made and success rate).
3. One main chart over time with a switch between the main counts (requests, won, sites made) and between the grains
   the range allows.
4. The funnel of the main flow.
5. One breakdown that answers a business question, such as source with close rate ("does the mockup tool bring
   customers?").

Everything else (industry, success of the tool, heat map) is optional and goes below.

## Date range

One range picker for the whole page, at the top right, never one per chart: two charts on different ranges side by
side are read as comparable and are not. Give presets (Hôm nay, Hôm qua, 7 ngày qua, 30 ngày qua, Tháng này, Tháng
trước, Quý này, Năm nay, Mọi lúc) and two typed dates, plus "So sánh với": Kỳ liền trước, Cùng kỳ năm trước, Không so
sánh. Tháng này, Quý này and Năm nay compare the same days of the period before. Keep the choice in the address. Write
the range and the comparison under the page title ("Từ 08/09 đến 07/10/2026, so với ..."). When the comparison reaches
before the first day with data, say so next to the chart.

Kit: `<div class="period" data-period="ov" data-default="30d" data-compare></div>`; listen for `ui:period` (from, to,
cmpFrom, cmpTo, range, cmpRange). `[data-period-note="ov"]` gets the sentence.

## Grain

| Range | Grains offered | Default |
|:---|:---|:---|
| 1 day | hour | hour |
| up to 31 days | day, week | day |
| up to 120 days | day, week, month | day up to 62 days, then week |
| longer | week, month | week up to 180 days, then month |

Counts keep whole numbers on the axis (gridlines every 1, 2, 5, 10, 20, 50...). Draw the SVG at the width of its box
so the text keeps its size on a phone, and redraw on resize. Show the last label (the bucket still running) and drop
the one just before it when they would touch.
