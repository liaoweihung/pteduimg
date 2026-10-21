# Search Console 與公開網址觀測（2026-10-21）

觀測：2026-10-21 台灣時間約 11:00。資源為 `https://liaoweihung.github.io/`。登入後 Search Console 畫面逐頁查核；公開網址另以 HTTP/HTML/XML 讀取。以下是觀測，不是 Search Console 匯出檔；未查得的數值保留 null。網址審查的「上次檢索」不等於首次收錄日。

## 新增兒科感冒藥水三頁

| 頁面 | 10/19 提交前 | 10/21 網址審查 | 畫面所示上次檢索 |
|---|---|---|---|
| [鼻福糖漿](https://liaoweihung.github.io/pteduimg/cards/ped_cold_peace_syrup.html) | Google 無法辨識 | [已編入索引](https://search.google.com/search-console/inspect?resource_id=https%3A%2F%2Fliaoweihung.github.io%2F&id=7JL86mqyVBw9s8l4k9KwaA) | 10/19 00:38:55 |
| [咳酚糖漿](https://liaoweihung.github.io/pteduimg/cards/ped_cold_guaphen_syrup.html) | Google 無法辨識 | [已編入索引](https://search.google.com/search-console/inspect?resource_id=https%3A%2F%2Fliaoweihung.github.io%2F&id=MKUadFCX9y1YD4gJXhF2fw) | 10/19 01:07:21 |
| [喘解液](https://liaoweihung.github.io/pteduimg/cards/ped_cold_exdila_liquid.html) | Google 無法辨識 | [已編入索引](https://search.google.com/search-console/inspect?resource_id=https%3A%2F%2Fliaoweihung.github.io%2F&id=TroPgUyAehdejVQW7m4CCw) | 10/19 01:08:49 |

三頁審查皆顯示 Googlebot 智慧型手機、成功擷取、允許檢索與建立索引、Google 選用受檢測網址為標準網址。首次**觀察到**已收錄為 10/21；實際首次收錄時點未知。10/19 精確提交時刻未記錄，不能將收錄歸因於手動要求。10/20–10/26 固定七日預測尚在期間中，且成效報表只到 10/18，三頁曝光、點擊、查詢皆未取得；10/29 起且報表完整涵蓋 10/26 後再核對。

## 原 26 頁：手動提交組與自然等待組

10/21 對 26 頁逐一使用網址審查；另確認 26/26 公開 HTTP 200、自我 canonical、主 sitemap 收錄。

**手動提交組（8/29 的 5 頁）**：`Ped_abx_susp_8`、`oral_hygiene_08`、`over_one_oint_01`、`ped_cold_cetirizine`、`ped_cold_secorine` 均顯示已編入索引。這是持續已收錄，不是 10/21 新增。28 天成效表分別顯示 2、1、13、7、27 次曝光；僅 `ped_cold_secorine` 有 2 次點擊。

**未手動提交組（21 頁）**：已索引 6 頁：`wound_cover`、`Ped_abx_susp_1`、`antiphen`、`ibuprofen_sol`、`oral_hygiene_01`、`adult_diaper_2`。其餘 15 頁顯示「Google 無法辨識的網址」：`Ped_abx_susp_2` 至 `Ped_abx_susp_7`（6 頁）、`oral_hygiene_02` 至 `oral_hygiene_07`（6 頁）、`over_one_oint_02`、`over_one_oint_03`、`ped_cold_cypromin`。成效表可見 `wound_cover` 1、`antiphen` 3、`ibuprofen_sol` 3、`adult_diaper_2` 4 次曝光，均 0 點擊；另外兩頁未出現在可見頁面列，不填零。手動組在這個非隨機小樣本表現較好，但頁面主題、內容、歷史可見度不同，無法推定提交造成差異。

## 網站資訊頁

[關於本站](https://liaoweihung.github.io/pteduimg/about.html)、[作者資訊](https://liaoweihung.github.io/pteduimg/author.html)、[編輯與資料來源政策](https://liaoweihung.github.io/pteduimg/editorial-policy.html) 均 HTTP 200、自我 canonical、在 sitemap，卻都於 10/21 網址審查顯示「Google 無法辨識的網址」；公開頁間有靜態互連。三頁未出現在截至 10/18 的可見成效列，不能寫成零曝光。此組與 JSON-LD 批次分開追蹤。

## 搜尋與 AI 成效

- [Google 搜尋成效（網路，全部國家／裝置，28 天）](https://search.google.com/search-console/performance/search-analytics?resource_id=https%3A%2F%2Fliaoweihung.github.io%2F&num_of_days=28&metrics=CLICKS%2CIMPRESSIONS%2CCTR%2CPOSITION&breakdown=page)：9/21–10/18，159 曝光、5 點擊、UI CTR 3.1%、平均排名 20.5。可見網頁表共 21 列，逐列數值保存在 JSON。10/19 前次窗口 9/19–10/16 是 147 曝光、5 點擊；窗口高度重疊，不稱為獨立成長比較。
- [Google 搜尋生成式 AI 功能 Beta 報表](https://search.google.com/search-console/performance/search-analytics/ai?resource_id=https%3A%2F%2Fliaoweihung.github.io%2F&num_of_days=28)：同一窗口 15 曝光，頁面列為混擦 01 六次、息咳寧五次、首頁／痘痘貼使用／青春痘嚴重度／勝克敏各一次。10/16 舊窗口為 13 曝光，但日期重疊。這不等於已在 AI 回答中明確引用；ChatGPT 搜尋及逐問題 AI 引用未驗證。
- JSON-LD 第二批 25 頁：本次公開唯讀檢查 25/25 HTTP 200、在 sitemap、head 內 JSON 可解析，Article headline、description、image、url 與相應 HTML metadata/canonical 配對。成效表可見 `acne_stage` 5 曝光、`acne_dailycare` 1 曝光；其餘頁面不在可見表中，不能填零，也未逐頁查 GSC 索引。第二批 10/1 部署後完整 28 天窗口尚未結束，不能作 JSON-LD 因果結論。

## Sitemap、404 與技術

- 根首頁、根 `robots.txt`、根 `sitemap.xml`、專案 `sitemap-main.xml` 均 HTTP 200。首頁 canonical 與 meta refresh 指向 `/pteduimg/`。robots 允許 `/` 並指向根 sitemap。根 sitemap 是只有一個子項的 sitemap index，指向專案主 sitemap；後者為含 396 URL 的 urlset（10/19 曾見 393）。
- 另查原 26、JSON-LD 第二批 25、新藥水 3、網站資訊 3，共 57 頁全為 HTTP 200、自我 canonical、列於主 sitemap。新藥水 3/3 JSON-LD 有效且在 head。舊感冒藥頁 `ped_cold_cypromin`、`ped_cold_cetirizine`、`ped_cold_secorine` 的 Article headline 為「兒科感冒藥水」，與各頁 title 的個別藥名不一致；僅記錄，不在本監控修改網站。
- [GSC Sitemap 報表](https://search.google.com/search-console/sitemaps?resource_id=https%3A%2F%2Fliaoweihung.github.io%2F) 仍將根 `/sitemap.xml`、`/pteduimg/sitemap-main.xml`、`/pteduimg/sitemap.xml` 列為「無法擷取」與 0 已發現；不能因公開 200 或 10/16 即時網址測試成功便宣稱報表修復。這項仍需追蹤。
- [GSC 網頁索引報表](https://search.google.com/search-console/index?resource_id=https%3A%2F%2Fliaoweihung.github.io%2F) 仍顯示 24 已索引、1 未索引、404 修正驗證「通過」，**報表更新日仍是 10/12**。這個舊彙總不能取代 10/21 新藥水逐 URL 審查結果。

本次只有觀測與本機管理紀錄；未重新要求索引、修改網站、建置、Commit 或 Push。
