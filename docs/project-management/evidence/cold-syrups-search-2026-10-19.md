# 三張兒童藥水頁：提交、搜尋需求與七天預測

觀測／預測建立日：2026-10-19（台灣日期）。使用者明確選擇「手動要求建立索引，並加入追蹤」。本次只操作這三個 URL 的 Search Console 要求與追蹤紀錄；沒有重建、修改或發布網站。

## 提交與收錄基準

資源：`https://liaoweihung.github.io/`。三頁提交前均為「網址不在 Google 服務中」「網頁未編入索引：Google 無法辨識的網址」，上次檢索時間不適用，未偵測到參照 Sitemap／網頁。逐頁點選要求建立索引後，均看到「已要求建立索引」「已將網址加入優先檢索佇列」。這是要求被接受，不代表已收錄。精確點擊時間未另外抄錄，JSON 的 submitted_at 留 null，已知提交日期保留。

| 證據 ID | URL | 審查頁 id | 提交確認截圖 |
|---|---|---|---|
| S1019-peace | https://liaoweihung.github.io/pteduimg/cards/ped_cold_peace_syrup.html | vDom_WazhMKft67nBAFGNw | `output/search-tracking-2026-10-19/peace-submitted.png` |
| S1019-guaphen | https://liaoweihung.github.io/pteduimg/cards/ped_cold_guaphen_syrup.html | YSQhJvqD2VqFnwuQtjxb4g | `output/search-tracking-2026-10-19/guaphen-submitted.png` |
| S1019-exdila | https://liaoweihung.github.io/pteduimg/cards/ped_cold_exdila_liquid.html | Q-HvZG26OFO0vHcszYm7Bg | `output/search-tracking-2026-10-19/exdila-submitted.png` |

審查網址格式為 `https://search.google.com/search-console/inspect?resource_id=https%3A%2F%2Fliaoweihung.github.io%2F&id=<上表id>`，需要有權限的登入狀態；當前網址審查資料會變化，截圖與本段才是這次歷史快照。對話 `019ea607-498c-7ee1-a659-bab67e92a923` 本輪 `mcp__cua_repl.js` 的頁面狀態也記錄三個完整 URL、提交前狀態及逐頁成功對話框。沒有另行取得 Google 伺服器端要求編號。

獨立 cohort：`manual-cold-syrups-2026-10-19`，不併入原本 26 頁、青春痘六頁或 JSON-LD 第一至第三批。

## 技術核對：O1019-technical

- 三個公開頁面可在瀏覽器載入，標題分別為「鼻福糖漿怎麼吃？兒童劑量、成分與注意事項」「咳酚糖漿是什麼？兒童化痰藥水劑量與用法」「喘解液兒童劑量：依年齡、體重換算與副作用」。
- 三頁均有文字版重點、同系列靜態連結、自我指向的 canonical，以及 head 中可成功 JSON.parse 的 Article；headline、description、url/mainEntityOfPage 與該頁 metadata 對應，author 指向 `author.html#person`。
- 三頁可見內容日期與 Article.dateModified 為 2026-10-18；這不證明首次成功部署時間，部署日仍未核實。
- 根 robots 顯示 `User-agent: *`、`Allow: /` 及根 sitemap 位置。未取得 X-Robots-Tag HTTP 標頭；不把 DOM 中沒有 robots meta 說成所有伺服器限制均通過。
- `sitemap-main.xml` 初次瀏覽顯示舊的 377 URL 且缺三頁；主動 reload 後為 **393 URL、三頁皆包含**。以重新載入結果記錄，初次差異可能與快取有關，不宣稱伺服器漏頁或自行改 sitemap。
- 終端 curl 因 DNS 解析失敗，沒有取得獨立 HTTP status code；瀏覽器可載入與 Google 接受索引要求分別記錄，不把工具失敗說成網站故障。
- 本機 cards.json、card_content.json 與 sitemap 尚未找到三個檔名；線上頁面為此次核對依據，沒有用舊本機檔案覆蓋線上內容。
- 技術擷取存於 `output/search-tracking-2026-10-19/public-metadata.json`。未測 ChatGPT / AI Overview 的逐回答引用，AI found/cited 均為未驗證；JSON 可解析不等於已證明 AI 成效。

## 成效參照：O1019-performance

實際開啟根資源「搜尋結果成效」的 28 天／網路搜尋／全部國家與裝置；資料期間 **2026-09-19 至 2026-10-16**，UI 當時上次更新 4.5 小時前。報表時區未獨立核實。

全站 147 次曝光、5 次點擊、UI CTR 3.4%、平均排序 20.7。21 個可見頁面列中未出現這三個新頁；報表截止早於頁面顯示的 10/18 內容日期，三頁成效 baseline 記「未取得」，不填 0。

| 同站參照頁 | 28 天曝光 | 點擊 | 曝光除以 4 的每週尺度 |
|---|---:|---:|---:|
| 息咳寧 `ped_cold_secorine.html` | 28 | 2 | 7 |
| 勝克敏 `ped_cold_cetirizine.html` | 7 | 0 | 1.75 |
| 安佳熱 `antiphen.html` | 3 | 0 | 0.75 |
| 依普芬 `ibuprofen_sol.html` | 3 | 0 | 0.75 |

參照頁已有較長收錄歷史，不能當新頁的保證值或隨機對照。與 10/16 保存的 9/16–10/13 視窗有重疊，不能把兩者當獨立前後實驗。原始可見頁面 DOM 存於 `output/search-tracking-2026-10-19/gsc-28d-pages-dom.txt`；沒有宣稱這是 GSC CSV 匯出。

## 關鍵字需求：O1019-trends

實際使用 Google Trends：台灣、所有類別、Google 網頁搜尋、搜尋字詞（非主題）。

| 比較組 | UI 期間 | 字詞順序 | 顯示平均相對指數 |
|---|---|---|---|
| 完整藥名 | 過去 12 個月 | 鼻福糖漿／咳酚糖漿／喘解液 | 0／2／2 |
| 完整藥名 | 過去 90 天 | 鼻福糖漿／咳酚糖漿／喘解液 | 0／1／1 |
| 短名稱與較廣詞 | 過去 90 天 | 鼻福／咳酚糖漿／喘解液／化痰藥 | 3／1／1／4 |

90 天畫面實際日序列標籤為 7/18–10/18；保存 UI 期間與實際標籤兩者，不自行補出缺失日期。完整藥名資料大量為 0，咳酚有孤立尖峰；鼻福糖漿、喘解液相關搜尋多處顯示資料不足。短詞「鼻福」近段出現較連續訊號，但可包含其他劑型；「化痰藥」用途比兒童單一糖漿廣。

這些是同一次比較內、四捨五入後的相對指數，**不是月搜尋次數、百分比或可靠的需求倍數**。不跨查詢組直接相除，不把低量 0 當沒人搜尋，也不把孤立尖峰當確定需求暴增。[Google 官方說明](https://support.google.com/trends/answer/4365533?hl=zh-Hant)指出低量門檻、抽樣、標準化及低量統計雜訊的限制。未取得 Keyword Planner 或其他可核實的月搜尋量資料。

- [完整藥名 12 個月比較](https://trends.google.com/trends/explore?geo=TW&date=today%2012-m&q=%E9%BC%BB%E7%A6%8F%E7%B3%96%E6%BC%BF,%E5%92%B3%E9%85%9A%E7%B3%96%E6%BC%BF,%E5%96%98%E8%A7%A3%E6%B6%B2&hl=zh-TW)
- [短名稱／化痰藥 90 天比較](https://trends.google.com/trends/explore?date=today%203-m&geo=TW&q=%E9%BC%BB%E7%A6%8F,%E5%92%B3%E9%85%9A%E7%B3%96%E6%BC%BF,%E5%96%98%E8%A7%A3%E6%B6%B2,%E5%8C%96%E7%97%B0%E8%97%A5&hl=zh-TW)
- 下載的 Trends CSV（完整藥名 12 月）與 90 天 DOM 表格存於 `output/search-tracking-2026-10-19/trends-full-drug-names-12m.csv`、`trends-dom-snapshots.json`；截圖為 `trends-comparison.png`。相對期間連結重開會變動，保留這次本機摘錄。

## 搜尋結果供給與候選字詞

使用公開網頁搜尋，實際查「鼻福糖漿 兒童 劑量」「咳酚糖漿 兒童 化痰」「喘解液 兒童 劑量」並開啟結果摘要；查到醫院的直接用藥資料。這是競爭內容的抽樣，沒有量測固定地區 Google SERP 名次，也不以結果筆數推算搜尋熱度。

| 新頁 | 建議固定追蹤的候選 query（非已證實熱門） | 已有可核對的專業結果 |
|---|---|---|
| 鼻福 | 鼻福、鼻福糖漿、鼻福糖漿劑量、鼻福糖漿副作用、鼻福兒童劑量 | [南門醫院](https://www.nanmen.com.tw/DrugInformationDetail/515)、[秀傳使用須知](https://www.show.org.tw/PharmaCare/EduOverview/ArticleDetail/cdac5796-8201-4c62-abd6-f69d7d3267ad) |
| 咳酚 | 咳酚糖漿、咳酚糖漿劑量、咳酚糖漿副作用、兒童化痰藥水、Guaifenesin | [中國醫用藥指導](https://www.cmuh.cmu.edu.tw/HealthEdus/Detail?no=5958)、[中山醫藥品手冊](https://www.csh.org.tw/into/pharm/HEALTH/GUAPS1.pdf) |
| 喘解 | 喘解液、喘解液劑量、喘解液體重換算、喘解液副作用、Procaterol | [中國醫用藥指導](https://www.cmuh.cmu.edu.tw/HealthEdus/Detail?no=5961)、[輔大醫院藥品資料](https://pharmacy.fjuh.fju.edu.tw/Key_Search/P4?query=EXD02) |

判讀：三個品牌都已有醫院資料，不能稱為「網路沒有好答案」。完整藥名是窄需求；更有意圖的劑量／注意事項問題適合持續觀察，但目前沒有各長尾詞的可靠搜尋量。三頁的標題已各自對準品牌和兒童使用問題，第一週宜保持內容穩定，先觀察哪些真實 query 出現。JSON-LD keywords 目前共用系列廣泛字詞，不能當作頁面已對每個詞排名；本次沒有調整它們。

## 七天預測：FORECAST-2026-10-19-cold-7d

固定評估日期：**2026-10-20 至 2026-10-26**，排除 10/19 提交當日；用 GSC 日報日期比較，報表時區與台灣時區可能不同。本預測現在保存，後續不得用實際結果回改原數字。

| 頁面 | 預測曝光範圍 | 預測點擊範圍 |
|---|---:|---:|
| 鼻福糖漿 | 0–8 | 0–1 |
| 咳酚糖漿 | 0–5 | 0–1 |
| 喘解液 | 0–8 | 0–1 |

三頁合計曝光規劃範圍 0–21；點擊較可能合計 0–2，最可能仍是 0。各頁點擊上緣不代表三頁同時達到上緣。收錄以「七天內觀察到 1–3 頁」為低信心工作假設，0 頁仍可能；不是收錄期限承諾。

這是低信心的人工情境估計，**不是統計信賴區間或正式訓練模型**。尺度來自同站既有藥水／藥品頁每週約 0.75–7 次曝光，以及新頁的收錄等待；鼻福／喘解較寬上緣只是近期短詞訊號及頁面意圖的弱假設，三頁需求高低沒有得到精確證明。沒有用 Trends 指數換算月流量。

若整週未收錄，接近零曝光／零點擊符合延遲情境。若很快收錄且出現新 query，少量曝光是第一個正向訊號；點擊不足不能單獨判定標題或內容失敗。CTR、平均排名在少量／零曝光時不做數值預測。若七天曝光明顯超過上緣，記為預測低估，再檢查搜尋需求、外部分享、內容變動與收錄時間，不能直接歸功於手動提交或 JSON-LD。

後續每次追蹤都讀本 cohort，追加實際索引／檢索／成效與 evidence。**10/29 起且 GSC 完整包含 10/26 後**才做七天核對；未齊則延後，不拿不完整期間比較。記錄這段期間其他內容、標題、導覽或推廣變動。三頁自身已含 JSON-LD，但與新上線／手動提交重疊，沒有獨立的 JSON-LD 對照效果；作者／政策三頁本次未重測。

## 範圍與驗證

提交成功畫面、三頁公開 metadata、主 sitemap 包含情況、Trends 摘錄與 GSC 參照均已保存。修改僅限搜尋管理紀錄與原追蹤工作的新增觀察範圍；維持原頻率及重要改變才通知，不新增自動索引提交、不修改網站、不 Commit/Push。紀錄驗證結果以本輪完成檢查為準。
