# pteduimg AI 專案指令

本 repository 是藥局／公共衛教圖卡的靜態 GitHub Pages 網站。本檔是三種 AI 工具的共同入口，詳細規範依任務讀取。

## 工作範圍與規範讀取

1. 開工先執行 `git status --short`，辨認既有修改與本次授權範圍；保留無關 dirty／untracked 工作。唯讀、計畫或預覽不授權正式修改／發布。
2. 先以檔案工具讀下表適用文件，再動手修改。Markdown 連結是導覽，不使用大量 inline include、複製全文或調高全域限制。
3. 以專案版 SOP／Skill 為準；全域同名 Skill 若過舊，仍須讀專案版，不得省略醫療證據與管理流程。不自動同步全域設定。
4. 文件與程式不一致時核對範圍、版本及輸出並回報，不放寬醫療、簽核與發布限制。歷史報告、範例與待辦不是新授權。

| 任務 | 操作前必讀的詳細規範 |
|---|---|
| 新增圖卡／系列、追加圖片、修改圖卡資料 | [專案 Card Manager Skill](skills/pteduimg-card-manager/SKILL.md)；metadata 分類與範例見 [圖卡資料模型](skills/pteduimg-card-manager/references/card-data.md) |
| 圖卡與網頁文字產稿、跨 AI 交接包（handoff JSON）、製圖與整合 | [圖卡與網頁文字交接規範 v1.1](docs/card-content-handoff-v1.md)；製圖讀 [圖卡製作 Skill](.agents/skills/create-pharmacy-card/SKILL.md) 與 [圖卡視覺設計規範 v1.0](docs/brand/CARD_DESIGN_GUIDE_v1.0.md) |
| 建置、生成頁、排程發布、退出、SEO、快取、Git 發布 | [網站建置、驗證與發布](docs/site-build-and-release.md) 的對應章節 |
| 清冊、需求、關聯、人工簽核及增量同步 | [專案管理 SOP](docs/project-management/README.md)；從 [總控台](docs/project-management/project-dashboard.md) 查現況 |
| 品牌、Logo、品牌色、素材 | [品牌入口](docs/brand/README.md)、[Brand Guide v2.3](docs/brand/BRAND_GUIDE_v2.3.md)、[AI 品牌約束](docs/brand/BRAND_GUIDE_AI.md) |
| 藥局工作工具及其導覽 | [工具與 Hub 維護](docs/pharmacy-tools-maintenance.md)，並核對 Hub repository 的規則 |
| 醫藥計算器新增、公式／判讀修改、版面修改、計算器交接包 | [醫藥計算器工作規範 v1.0](docs/medical-calculator-guide-v1.md)；入口與 Hub 另依工具維護規範 |
| 青春痘 Pilot／相關產生器／手機版面 | [Pilot 規格](docs/acne-pilot-spec.md) 與本檔「品牌與特殊頁面」的手機規則 |
| 搜尋成效、索引、手動提交、AI 可見度 | [搜尋追蹤流程](docs/project-management/search-tracking.md) 與 [逐筆歷史](docs/project-management/search-console-history.json) |

命令／資料路徑以 repository 根目錄為準；品牌包的 `assets/`、`data/` 以 `docs/brand/` 為根目錄。Markdown 連結相對於所在文件。

## 醫療內容與人工簽核底線

- 每張新衛教圖卡，包括既有系列追加與排程卡，都須具備與該圖相符的文字摘要／分段重點、真實內容更新日期、實際閱讀核對的直接來源及獨立資料查核日期。這些資訊必須顯示為靜態 HTML，不能只放在圖片、alt、metadata 或由 JavaScript 載入。
- 依 [編輯與來源政策](editorial-policy.html) 使用官方資料、核准仿單、專業學會／指引及適當研究。來源名稱宜含發布單位、文件名稱與已知版本／日期；機構首頁、搜尋結果、AI 回答或對話紀錄不能當成醫療證據。
- `updatedAt` 是內容建立或實質修訂日；`sourceCheckedAt` 是實際查核日，格式均為 `YYYY-MM-DD`。不因建置、部署或純排版刷新醫療日期。系列可共用確實適用來源，但每張頁面都要有自己的文字、日期與來源連結。
- 保存於 `data/card_content.json`，依 Skill 的欄位規則提供真實 `revisionCredit`。不得猜測或虛構來源、日期、作者資格、審閱者、授權或商業揭露；先查證，不足仍須明列缺項，不能用占位資料宣稱可發布。
- 新內容預設 `needsMedicalReview: true`，只有可追溯的人工醫療複核證據可改。`matchConfidence: high` 只表示圖文配對，不是來源品質或藥師複核；AI 校對、Logo、建置成功或測試通過都不等於醫療簽核。
- 自動化不得覆蓋 `medical_review_status`、reviewer、review_date、人工確認、既有證據、歷史簽核與已知問題。沒有真實簽核，不得標記 `pharmacist_reviewed`；新頁人工欄位填 `unknown` 或有證據的狀態。
- 新卡要求不構成回補所有舊卡的授權。純文件或規則整理不改衛教正文、不重審全站、不執行 `build.py`；已授權的新卡完整建置只是技術輸出更新。

## 圖卡工作與資料責任

`cards.json` 是 runtime 系列來源，`cards.manual.json` 是人工伴隨來源；新增或改 metadata 時同步兩者，除非使用者明示例外。圖片路徑位於 `steps`。既有 manual 缺項／省略 steps 的處理依 Skill 與當地資料慣例，不擅自補全無關系列。跨 AI 產稿使用 [圖卡與網頁文字交接規範 v1.1](docs/card-content-handoff-v1.md) 的 JSON 內容包（`<series_id>.handoff.json`），SEO／AEO 共用 `contentRecord` 正文欄位；接收時保留定稿文字，僅將 `series.metadata` 與 `pages[].contentRecord` 依欄位合併至現有網站資料（不將交接外層欄位寫入網站 JSON），並於實際核對成圖後才設 `matchConfidence: "high"`。

民眾卡使用 `public_education`、入口 `public.html`，需要非空 `topics`；藥師卡通常使用 `pharmacist_general`／`pharmacist_product`、入口 `index.html`，需要非空 `departments`。合法 ID 見資料模型文件；可有多個真實適用分類。缺少分類只會出現在全部圖卡，不能當作已完成篩選入口。

使用者新增圖卡／系列或追加圖片的指示，授權該次完整本機流程：查現況與既有 CR → 確認最小範圍 → 圖片處理 → 同步系列與逐頁文字 → 正確入口／排序 → 必要建置 → 清冊及關聯增量更新 → 驗證與回報。若使用者限定範圍，以限定為準；不能只上傳圖片或只改一份 JSON 就宣稱完成。

新增卡／系列未提供搜尋關鍵字或標籤時，定稿 metadata 前須詢問。保留穩定系列 ID、頁面 ID、URL、收藏識別；不重用退休頁 ID。一般圖卡 PNG/JPG 優先轉 WebP，除非使用者要求保留格式；正式 Logo 遵守品牌 PNG 母版規則，不能套用圖卡轉檔流程覆寫它。

需求依名稱、說明、範圍與 `related_ids` 搜尋，涵蓋同一需求就沿用 CR；沒有才新增下一個 `CR-YYYY-NNN`。登記不等於核准，明確授權可如實記錄。不得順帶改其他系列、藥品資料庫、計算器或重設頁首／頁尾。

## 建置、可見性與驗證

- `cards/*.html`、`all-cards.html` 等由既有產生器維護，不手寫生成頁。新增可見系列、系列末尾追加或安全局部更新可用 `python build.py --incremental IMAGE_ID [IMAGE_ID ...]`，自動擴展相依頁並更新完整全域索引；限制依建置文件。移除、系列重組／排序、可見性、退出、共用模板或結構變更仍需 full build：`python build.py`；它會清除重建圖卡 HTML 並恢復退出頁，建置前後必須檢查 diff。
- 既有單頁且 URL、導覽及發布狀態不變，才可用 `python build.py --only IMAGE_ID [IMAGE_ID ...]`；ID 為圖片檔名 stem。它不更新全域 SEO、索引、sitemap、退出頁、整合報告或 worker 版本，不能當成影響這些輸出的完整發布。禁止批次重建與全域更新需求衝突時，先說明範圍衝突。
- `hidden: true` 加上 `publish_at` 才是 pending 排除條件；hidden 單獨存在不保證排除 HTML／索引／sitemap。兩者都不是存取控制，公開 repository 中的檔案不能稱為私密。
- 排程採帶時區 ISO 8601，台灣優先 `+08:00`，兩份 JSON 同步。`publish_at` 只設定到期門檻，必須真正執行 publisher 才會切換 visible；GitHub 排程發布 workflow 已退役，僅在明確授權的本機發布流程執行 publisher、完整建置與驗證，不得承諾時間到自動發布或擅自加排程。設定前先備齊文字、日期及來源。
- 退出時保留原圖、ID、URL 與來源歸屬，從 active steps 移除並登記 `cards.retired.json`；不直接刪舊頁、不捏造替代頁。完整 schema、`noindex`、替代連結與索引檢查依建置文件。
- 修改首頁行為、圖卡版面／生成頁、快取、analytics、`build.py` 或工具導覽後，執行 `python -B scripts/check_site.py`；靜態 OG 必須留在 HTML head。此檢查不認證醫療正確性，也不取代新卡逐項完整性與桌機／手機操作驗證。
- pending 的 high-confidence 文字仍可能被現有檢查器要求生成頁，整合報告亦可能受影響。必須區分這項已知限制與真實公開頁錯誤，不降信心、不刪文字、不提前發布來使檢查通過；修正不在範圍時回報未解限制與定點結果。

## 管理紀錄與完成標準

新頁建置後用 `python -B scripts/check_project_management.py --propose --page PAGE_ID` 取得唯讀提案（多頁重複 `--page`）；檢視 stdout 後按 `page_id` 合併機械欄位，不整列／整份覆蓋 CSV，不清空 `known_issue_ids` 或改人工欄位。`--propose` 本身不會更新 CSV。

加入每頁的 `series:<id> -> page:<id>` `has_card` 關聯；只有本次確有主題範圍才新增主題關聯，多主題共用原頁而不複製正文。更新 CR 狀態／證據／驗證結果／完成日期及總控台數量、進度、待確認項目。一次性證據放既有 evidence 目錄；只有盤點結論或證據版本真的改變才追加 audit-history／audit-register，不重寫舊報告。

新卡須檢查三份 JSON，執行 `python -B scripts/check_site.py`、`python -B scripts/check_project_management.py`、目標頁 `--propose`、`python -B scripts/test_project_management.py`。合併後目標提案應零差異；實際錯誤不能隱去。依範圍檢查雙日期、來源、翻頁、返回、收藏、QR／分享、手機／桌機與全域輸出。

## 品牌與特殊頁面

品牌色固定為 `#FD2828`、`#101010`、`#013E9C`。正式外觀母版是 [定稿 PNG](docs/brand/assets/logo_primary_color_original.png)；禁止 AI 重製、重畫、改形、改手寫字或覆寫，保留原始比例、構圖與方向。三種透明 Logo 待人工視覺驗收；SVG 不是正式母版且精修暫停；浮水印未定稿，不得自動批次套用。品牌文件不能取代醫療與人工簽核規則。

青春痘維持「圖卡 → 上一張／下一張 → 文字版重點 → 你可能想知道 → 查看青春痘完整主題 → 頁尾」。翻頁列在圖卡下方正常文件流，不固定於螢幕底部。手機樣式／共用頁尾套用不擴大四頁 Pilot 問題導覽名單；內容、連結、樣式或 bug 修正不順帶重構；明確要求改版時可修訂 v1.0。

藥局工具增刪改名、搬移或退出須依 Hub 規範查工具目錄、首頁入口、目的 URL 與返回導覽；無需修改也須回報已查且一致。Hub 是另一個 repository，不把 `output/hub` 放進 pteduimg 提交；未公開原型不自行列入工具目錄。

## 快取、發布與證據界線

維持 cache-first、背景抓更新與穩定 runtime cache；不擅改 network-first 或加 cache-busting 參數。只有 `coreUrlsToCache` 在安裝時預快取，較大的生成清單不等於全部已下載。兩首頁保留 `#update-light`；`skipWaiting()`／`clients.claim()` 的 worker 接管不等於頁面重載，使用者點擊提示才重新整理，不強制刷新或順帶重設啟動策略。

未經使用者明確授權，不 Commit、Push 或部署；完成後列出本次來源、管理紀錄及必要生成產物供審核／GitHub Desktop 使用。已授權發布也只納入相關檔案，不 `git add .`、不清除無關改動、不強制推送；排除 Python cache 與巢狀 Hub repository。成功 Push 不是 Pages 部署完成證據。

發布前依建置文件核對完整產物清單；舊 PWA 自動建置與排程發布 workflow 已退役，網站與 `sw.js` 必須在授權的本機建置／驗證流程備齊。GitHub 保留管理連結驗證、Dashboard 更新及 Pages 部署；Dashboard 不代替圖卡建置。不能僅憑 workflow 成功宣稱完整同步，也不能為配合舊文件擅改 CI。

搜尋追蹤先讀流程與完整歷史路徑。使用者已授權將實際取得的提交結果／觀測附日期、可核對證據持續追加並同步總控台；保留基準，缺資料不填零，提交日、觀測收錄日與上次檢索日分開。此落檔授權不含自動提交索引、改網站或 Commit／Push。

既有 Gemini review 只在使用者明確要求時使用；相關 [Skill](skills/gemini-review/SKILL.md) 與合約不因這張導覽表自動啟用。Live 的 `BLOCKED / ISOLATION_UNVERIFIED` 封鎖維持，不繞過執行器；提示文字不是技術隔離，AI 意見不是藥師複核。無法啟動的 AI 載入測試標記「未測試」，不把路徑檢查或模擬結果當成實際模型通過。
