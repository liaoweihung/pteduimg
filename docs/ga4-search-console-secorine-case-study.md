# 息咳寧頁面流量查核成果 / GA4 vs. Search Console for the Secorine Syrup page

[中文](#中文) · [English](#english) · [數據 / Data](#data) · [官方資料 / References](#references)

## 中文

### 背景與問題

2026 年 11 月 12 日至 18 日，藥局衛教助手的「息咳寧糖漿」頁面在 GA4「網頁和畫面」報表以 **98 次瀏覽**居首，占報表中 587 次瀏覽的 16.7%，有 48 位活躍使用者。最初想知道讀者如何抵達這一頁，以及接著去了哪裡。進一步查入口時，GA4 顯示 **48 個工作階段**以息咳寧為入口並歸因給 `google / organic`，Search Console 的網頁文字搜尋則記錄 **16 次點擊**。本報告記錄查核過程、全站對照，以及現有報表能支持的結論。 [息咳寧糖漿頁面][page]

### 查核方式

1. **固定日期與網站範圍。** 兩套報表都選 2026/11/12–11/18。GA4 資源使用台灣時間（UTC+8），Search Console 每日資料使用太平洋時間，本期間為 PST（UTC−8）。相同日期標籤的邊界相差 16 小時。全站比較限定在 `liaoweihung.github.io` 的 `/pteduimg/` 路徑，同網域的其他工具另計。 [Google 的報表差異說明][comparison]
2. **用 GA4 查瀏覽、站內路徑和入口。** 在「網頁和畫面」讀取瀏覽量，在「路徑探索」以頁面標題分別設定起點與終點。在「任意形式」篩選 `到達網頁` 完全符合 `/pteduimg/cards/ped_cold_secorine.html`，以及 `工作階段來源／媒介` 完全符合 `google / organic`。全站改用入口路徑規則運算式 `^/pteduimg/.*$`，並限定正式主機。另以 `事件名稱 = session_start` 分組查看工作階段開始時的網頁參照網址。 [GA4 路徑探索][path] · [GA4 工作階段與歸因][sessions]
3. **用 Search Console 查點擊、搜尋類型與標準網址。** 在「搜尋結果」成效報表，單頁用完整網址完全比對，全站用 `https://liaoweihung.github.io/pteduimg/` 作網址前綴。分別查網頁文字、圖片、網頁多模態、影片與新聞搜尋。查看逐日、裝置、國家分組，另用網址審查工具核對 Google 選定的標準網址。 [Search Console 搜尋成效與搜尋類型][performance]
4. **用站內其他頁作對照，再抽查兩天。** 分別從全站工作階段數與各搜尋類型點擊數扣除息咳寧，得出其他頁合計。針對 11/12、11/14 的 7 個工作階段，查看地區、城市、作業系統、瀏覽器、參與時間與「新／舊使用者」，並用「首次造訪」指標 (`first_visit`) 交叉核對。 [GA4 使用者指標][users]

### 嘗試過的查核與結果

| 核對項目 | 結果與判讀 |
| --- | --- |
| 前一頁與下一頁 | 前一頁的主要節點為勝克敏液 9 次、滅喘淨液 8 次。下一頁主要是滅喘淨液 14 次、勝克敏液 8 次、衛教助手首頁 2 次。這些是路徑探索的事件次數。 |
| 圖片、Lens、影片與新聞 | 息咳寧有圖片搜尋 2 次點擊，含 Lens、畫圈搜尋的網頁多模態合計 2 次，影片與新聞搜尋各 0 次。多模態報表未單獨列出 Lens。 |
| Discover、引薦與來源歸因 | 此資源未顯示 Discover 報表，無法量化。48 個自然工作階段的 `session_start` 中，46 個的引薦為 `https://www.google.com/`，2 個為站內滅喘淨液頁。`google.com` 可出現在多種 Google 入口。站內引薦的兩筆顯示，引薦欄位與歸因可以不同，無法據此還原造訪經過。 |
| 時區與資料回補 | GSC 的 11/11（太平洋時間）整天只有 1 次文字搜尋點擊，換成台灣時間的日期範圍，原先 16 次最多增到 17 次。重讀時 11/17 與 11/18 仍是 6 次與 4 次，後續是否更新尚未查證。 |
| 正式主機與標準網址 | 48 個工作階段均在正式主機。Google 選定 `.html` 版為標準網址，無副檔名的版本也可開啟，並宣告 `.html` 版為標準網址。將 GSC 篩選放寬為包含 `ped_cold_secorine`，仍只有同一列及 16 次文字搜尋點擊。 |
| 地區、裝置與互動 | 48 個工作階段中，台灣 41 個、行動裝置 38 個、互動工作階段 34 個。兩天抽查的 7 個工作階段中，6 個來自台灣，6 個符合互動條件，平均參與 25 秒。7 個全為 GA4 新訪，有 7 次 `first_visit`。這批樣本沒有呈現大量海外、低互動的型態，也削弱了同一 GA4 身分重開舊分頁的解釋。 |
| Search Console 裝置和國家明細 | 息咳寧文字搜尋總計 16 次。裝置明細合計 8 次（手機 5、桌面 3、平板 0），國家明細也只有 8 次（台灣 5、美國 3）。明細不足以與 GA4 比較完整占比，也無法知道兩個明細是否少了同一批點擊。 |

引薦與 Discover 的限制可參考 [Google 引薦網址說明][referrer]、[Discover 報表門檻][discover]。圖表與明細可能因彙總方式而不同。 [Search Console 資料差異說明][gsc-discrepancies]

### 結論

**息咳寧的 GA4 工作階段與 GSC 點擊落差比其他頁大，且 GA4 互動率也較高。** 息咳寧為 48 個工作階段對 20 次點擊（2.40 倍），其他頁為 24 對 17（1.41 倍）。互動率分別為 71% 和 33%。這些比值用於比較報表落差，沒有通用的正常門檻。互動率反映工作階段是否符合 GA4 條件，無法證明讀者身分、閱讀意圖或衛教效果。 [GA4 互動率定義][engagement]

差距的來源尚未確認。現有報表無法逐筆配對點擊與工作階段、量化 Discover，也不足以排除追蹤設定問題或確認 Search Console 漏計。兩天的 7 次 `first_visit` 只確認 GA4 辨識為新訪，並未逐筆核對這 7 次的引薦網址或確認有 7 位不同的真人。平常用 Search Console 看曝光、點擊、查詢字詞和排名，用 GA4 看進站後的參與和站內瀏覽。這次查核只使用既有報表，公開紀錄採彙總數字。 [Google 對兩份報表的使用建議][comparison] · [GA4 報表識別方式][identity]

## English

### Background and question

From November 12 to 18, 2026, the Secorine Syrup page on the Pharmacy Education Assistant ranked first in the GA4 Pages and screens report. It received **98 views**, or 16.7% of the 587 views in the report, with 48 active users. The original question was how readers arrived and where they went next. GA4 showed **48 landing sessions** attributed to `google / organic`, while Search Console recorded **16 text-based web search clicks**. This report documents the investigation, the sitewide comparison, and what the available data support. [Secorine Syrup page][page]

### How we checked

1. **Fix the date range and site scope.** Both reports used November 12–18, 2026. The GA4 property uses Taiwan time (UTC+8). Search Console daily data use Pacific time, which was PST (UTC−8) in this period. The matching date labels therefore have boundaries 16 hours apart. The sitewide comparison covered `/pteduimg/` on `liaoweihung.github.io` and excluded other tools on that host. [Google's guide to reporting discrepancies][comparison]
2. **Use GA4 to examine views, paths, and landing sessions.** We read page views in Pages and screens and set the page title as a starting or ending point in Path exploration. In Free form, `Landing page` exactly matched `/pteduimg/cards/ped_cold_secorine.html` and `Session source / medium` exactly matched `google / organic`. For the sitewide comparison, the landing page matched `^/pteduimg/.*$` on the production hostname. A separate view grouped page referrers with `Event name = session_start`. [GA4 path exploration][path] · [GA4 sessions and attribution][sessions]
3. **Check clicks, search types, and the canonical URL in Search Console.** The Search results performance report used an exact full-URL filter for the page and the `https://liaoweihung.github.io/pteduimg/` prefix for the site. We checked text-based web, image, web multimodal, video, and news search separately, reviewed daily, device, and country breakdowns, and confirmed the Google-selected canonical in URL Inspection. [Search Console performance report and search types][performance]
4. **Compare with other pages and spot-check two days.** We subtracted the Secorine page's counts from the corresponding sitewide sessions and click totals. For the seven sessions on November 12 and 14, we examined geography, city, operating system, browser, engagement time, and the New / returning dimension. We cross-checked the classification with the First visits metric (`first_visit`). [GA4 user metrics][users]

### What we tried and found

| Check | Finding and interpretation |
| --- | --- |
| Previous and next pages | The leading previous-page nodes were 勝克敏液 with 9 events and Meptin Liquid with 8. The leading next-page nodes were Meptin Liquid with 14, 勝克敏液 with 8, and the homepage with 2. Path exploration reports event counts. |
| Images, Lens, video, and news | Search Console recorded 2 image clicks and 2 web multimodal clicks, a category that includes Lens and Circle to Search. Video and news search each showed 0 clicks. The multimodal report provides no separate Lens count. |
| Discover, referrers, and attribution | This property did not display a Discover report, so Discover traffic could not be quantified. Of the 48 organic-attributed `session_start` records, 46 had `https://www.google.com/` as the referrer and 2 had the on-site Meptin Liquid page. Multiple Google surfaces can send the Google referrer. The internal referrers show that the recorded referrer and session attribution can differ, without establishing the session history. |
| Time zone and reporting updates | Search Console showed 1 text-based web click for all of November 11 in Pacific time. Using the reported data, alignment to Taiwan dates could increase the original 16 clicks to at most 17. A reread still showed 6 clicks on November 17 and 4 on November 18. Later revisions were not checked. |
| Production hostname and canonical URL | All 48 sessions were on the production hostname. Google selected the `.html` canonical. The extensionless URL also loaded and declared the `.html` URL canonical. A broader GSC filter for URLs containing `ped_cold_secorine` still showed one row and 16 text-based web clicks. |
| Geography, devices, and engagement | Of 48 sessions, 41 were from Taiwan, 38 were on mobile devices, and 34 were engaged. In the seven-session spot check, six were from Taiwan and six were engaged, with 25 seconds of average engagement time. All seven were new in GA4, with seven `first_visit` events. The sample showed no large cluster of low-engagement overseas traffic and weakens the old-tab explanation for the same GA4 identity. |
| Search Console device and country breakdowns | The page's text-based web total was 16. The device breakdown showed 8 clicks (5 mobile, 3 desktop, 0 tablet), and the country breakdown also showed 8 (5 Taiwan, 3 United States). Neither breakdown provides a complete distribution. Equal subtotals do not establish that the same clicks were omitted. |

See [Google's referrer documentation][referrer], the [Discover report eligibility criteria][discover], and [Search Console guidance on differences between chart and table totals][gsc-discrepancies].

### Conclusion

**The difference between GA4 sessions and Search Console clicks was larger for the Secorine page, which also had a higher GA4 engagement rate.** The page had 48 sessions and 20 clicks (2.40 times), compared with 24 and 17 (1.41 times) for the rest of the site. Engagement rates were 71% and 33%, respectively. The ratios compare report counts and have no universal benchmark. Engagement indicates that a session met GA4's criteria and cannot establish reader identity, intent, or educational benefit. [GA4 engagement rate definition][engagement]

The cause remains unresolved. These reports cannot match clicks and sessions one to one, quantify Discover traffic, rule out tracking issues, or establish that Search Console undercounted clicks. The seven `first_visit` events establish new visits as recognized by GA4. The referrer was not cross-checked for those exact seven visits, and the count does not establish seven distinct individuals. For routine monitoring, use Search Console for impressions, clicks, queries, and position, and GA4 for engagement and on-site browsing. The investigation used existing reports, and this public record presents aggregate findings. [Google's guidance on using both reports][comparison] · [GA4 reporting identity][identity]

## Data

**2026-11-12–2026-11-18 · `liaoweihung.github.io/pteduimg/`**

**搜尋類型核對。** 在單頁的同一日期範圍，從「圖片」切回「網路」父選項時，介面預選「文字型」，套用後標示「網頁（文字）」並顯示 16 次點擊（`search_type=WEB`）。另選「多模態」才會顯示「網頁（多模態）」和 2 次點擊（`search_type=WEB-MULTIMODAL`）。加上圖片的 2 次，下表三類合計為 20 次。 [Search Console 搜尋類型][performance]

**Search type cross-check.** For the same URL and dates, switching from Image to the Web parent option selected Text-based by default. After applying the filter, the report showed Web (text-based) and 16 clicks (`search_type=WEB`). Selecting Multimodal separately showed Web (multimodal) and 2 clicks (`search_type=WEB-MULTIMODAL`). With 2 Image clicks, the three selected types sum to 20. [Search Console search types][performance]

| 指標 / Metric | 全站 / Site total | 息咳寧 / Secorine | 其他頁 / Other pages |
| --- | ---: | ---: | ---: |
| GA4 `google / organic` 入口工作階段 / Landing sessions | 72 | 48 | 24 |
| GSC 網頁文字搜尋點擊 / Text-based web clicks | 31 | 16 | 15 |
| GSC 圖片搜尋點擊 / Image clicks | 4 | 2 | 2 |
| GSC 網頁多模態點擊 / Web multimodal clicks | 2 | 2 | 0 |
| GSC 三類點擊合計 / Clicks across those three types | 37 | 20 | 17 |
| GA4 工作階段 ÷ 上述 GSC 點擊 / Sessions per click across those three types | 1.95 | 2.40 | 1.41 |
| GA4 互動工作階段 / Engaged sessions | 42 | 34 | 8 |
| GA4 互動率 / Engagement rate | 58% | 71% | 33% |

息咳寧有 52 個全來源入口工作階段，含 48 個 `google / organic` 和 4 個 `(direct) / (none)`。48 個自然工作階段對應 43 個 GA4 辨識的使用者身分，無法據此推算跨瀏覽器的真人回訪次數。 / The page had 52 landing sessions across all sources, with 48 attributed to `google / organic` and 4 to `(direct) / (none)`. The 48 organic-attributed sessions corresponded to 43 GA4 user identities, which cannot establish how often the same person returned across browsers.

### 逐日對照 / Daily comparison

下表沿用各報表的日期標籤，GA4 用台灣日界，GSC 用太平洋日界。 / The figures retain each report's date labels, using Taiwan dates for GA4 and Pacific dates for GSC.

| 日期 / Date | 全站 GA4 自然工作階段 / Site sessions | 息咳寧 GA4 自然工作階段 / Secorine sessions | 全站 GSC 文字搜尋點擊 / Site text-based web clicks | 息咳寧 GSC 文字搜尋點擊 / Secorine text-based web clicks |
| --- | ---: | ---: | ---: | ---: |
| 11/12 | 4 | 3 | 0 | 0 |
| 11/13 | 4 | 2 | 2 | 1 |
| 11/14 | 9 | 4 | 3 | 0 |
| 11/15 | 14 | 12 | 3 | 3 |
| 11/16 | 10 | 7 | 7 | 2 |
| 11/17 | 20 | 12 | 7 | 6 |
| 11/18 | 11 | 8 | 9 | 4 |

## References

- [GA4 和 Search Console 比較 / Using Search Console and Google Analytics data for SEO][comparison]
- [Google 引薦網址 / Identify Google Search traffic in analytics and logs][referrer]
- [搜尋成效報表與搜尋類型 / Search results performance report and search types][performance]
- [Search Console 圖表與明細差異 / Troubleshooting Search Console data discrepancies][gsc-discrepancies]
- [Discover 報表顯示門檻 / Discover performance report eligibility][discover]
- [GA4 路徑探索 / GA4 path exploration][path]
- [GA4 工作階段與來源歸因 / GA4 sessions and attribution][sessions]
- [GA4 使用者指標 / GA4 user metrics][users]
- [GA4 互動率 / GA4 engagement rate][engagement]
- [GA4 報表識別方式 / GA4 reporting identity][identity]

[page]: https://liaoweihung.github.io/pteduimg/cards/ped_cold_secorine.html
[comparison]: https://developers.google.com/search/docs/monitor-debug/google-analytics-search-console
[referrer]: https://developers.google.com/search/docs/monitor-debug/identify-google-search-traffic
[performance]: https://support.google.com/webmasters/answer/7576553
[gsc-discrepancies]: https://support.google.com/webmasters/answer/17010575
[discover]: https://support.google.com/webmasters/answer/9216516
[path]: https://support.google.com/analytics/answer/9317498
[sessions]: https://support.google.com/analytics/answer/9191807
[users]: https://support.google.com/analytics/answer/12253918
[engagement]: https://support.google.com/analytics/answer/12195621
[identity]: https://support.google.com/analytics/answer/10976610
