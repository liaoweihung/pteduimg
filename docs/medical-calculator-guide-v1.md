# 藥局衛教助手｜醫藥計算器工作規範 v1.0

制定日期：2026-10-31。適用：所有參與醫藥計算器規格、實作、版面修改、驗證或網站整合的 AI 與人員，不限品牌、模型與工具。

本規範補足 [AGENTS.md](../AGENTS.md) 對計算器的細節；醫療證據、人工簽核、Git 授權與品牌底線仍以 AGENTS 及 [編輯與來源政策](../editorial-policy.html) 為準。藥局工作用工具的導覽與 Hub 同步另依 [工具與 Hub 維護](pharmacy-tools-maintenance.md)。

## 0. 適用範圍與核心原則

適用於 `calc.html` 列出的醫藥計算器，目前為：健檢數值解讀助手、癌症相關檢驗值解讀助手、台灣小朋友生長狀況百分位計算器、經期／排卵／預產期計算器、10 年心血管風險評估。藥局工作用工具（例如 `rx-refillable-date.html`）若含計算或判讀邏輯，第 2～5 節同樣適用。藥品資料庫的資料匯入流程不在本規範範圍。

核心原則：

- **醫療邏輯與版面分開。** 公式、常數、門檻、對照表、判讀分類與判讀文字是醫療內容；排版、顏色、互動與文案位置是技術內容。兩者分開修改、分開驗證、分開記錄。
- **版面修改不得改變任何計算結果。** 只改版面時，新舊版必須用同一組輸入比對並全部一致（第 4 節）。
- **前瞻適用。** 本規範不構成回補舊計算器的授權；修改舊計算器時，只對本次涉及的部分套用。舊計算器的驗證證據缺口持續由 CR-2026-024 追蹤。
- **不猜測。** 不得自行推導、記憶或改寫公式與門檻；來源、日期、測試預期值不足時列為缺項，不以占位資料宣稱完成。
- **AI 驗算不等於藥師簽核。** 測試通過、建置成功或 AI 校對都不代表醫療複核。

## 1. 分工與狀態

- 規格 AI：整理用途、輸入、公式、門檻、判讀文字、來源與測試案例，產出第 3 節的交接包；未知資料明列缺項。
- 實作 AI：依交接包實作或修改頁面，保留定稿公式與文字，執行第 4～7 節的驗證與整合。
- 使用者：決定工具範圍、判讀文字、醫療簽核、上架入口與發布。

交接包 `workflowStatus` 僅允許：

| 值 | 意義 |
|---|---|
| `draft` | 仍有缺項、公式或判讀文字待確認，或來源尚未實際查核 |
| `spec_ready` | 使用者已確認輸入、公式、判讀文字與測試案例，來源與查核日期齊備，可實作 |
| `implemented` | 已實作，尚未完成第 4 節全部驗證 |
| `verified` | 測試案例、回歸比對與手機／桌機檢查已通過並留證 |

上述狀態都不代表藥師複核或發布核准。`operation` 使用 `new_tool`、`update_logic`、`update_text`、`update_layout` 或 `retire_tool`；同時涉及邏輯與版面時列為 `update_logic`，並在交接包分開描述。

## 2. 醫療內容與來源

- 每個公式、常數、門檻、對照表與判讀分類，都要有實際閱讀的直接來源：發布單位、文件名稱、版本或年份及完整網址。另記 `sourceCheckedAt`（實際查核日，`YYYY-MM-DD`）。
- 來源優先順序依編輯政策：官方資料、核准仿單、專業學會指引，再到研究。公式以原始發表或官方指引為準；台灣參考值優先使用台灣官方或在地研究。線上計算器、搜尋摘要與 AI 回答都不是醫療證據。
- 常數、係數與門檻逐字照抄，記錄單位、換算、四捨五入方式，以及邊界的歸屬（例如 `≤`、`<`）。來源與常見網路計算器不一致時，以來源為準，並在交接包說明差異。
- 註明適用族群（年齡、性別、族群、單位制）。超出來源適用範圍的輸入應拒絕或明確警示，不自行外推。生長計算器的「超過資料庫的數據，無法提供資料」即屬此類處理。
- 判讀文字定位為衛教或初步篩檢，不寫成診斷；必要時提供就醫時機。涉及產品、營養品或 OTC 建議時，屬醫療內容，必須有來源；涉及品牌或購買連結時，依專案管理 SOP 的「賣場連結」規則處理。
- 頁面須以靜態 HTML 顯示以下內容，不能只放在 JavaScript 字串、圖片或註解：用途與適用對象、計算依據摘要、可點擊的來源連結、資料查核日期、限制與免責說明。站內現有範例是 `menstrual-calculator.html` 的「計算依據與參考來源」區塊。
- 新增或修改醫療邏輯、判讀文字時，CR 的 `needs_pharmacist` 填 `yes`。沒有具名、有日期、有證據的簽核，不得宣稱已經藥師複核。

## 3. 計算器交接包（JSON）

跨 AI 交接使用一份 UTF-8、合法 JSON 的內容包，建議檔名 `<toolId>.calculator.json`，`schemaVersion` 為 `"pteduimg-calculator/1.0"`。固定英文欄位、繁體中文內容，不使用註解、尾端逗號或省略號；來源使用完整網址。交接包是工作文件，不放進網站、不被頁面載入。

| 欄位 | 用途 |
|---|---|
| `toolId`、`operation`、`workflowStatus` | 工具識別碼（同頁面檔名 stem，例如 `growth-calculator`）、操作類型、狀態 |
| `page` | `file`、`url`、`title`、`audience`（`public` 或 `pharmacist`）、`entry`（`calc.html`、`hub` 或 `index.html`） |
| `inputs[]` | `id`、`label`、`unit`、`type`、`required`、`min`、`max`、`step`、驗證錯誤訊息 |
| `computations[]` | `id`、`description`、`formula`（純文字公式）、`constants`、`units`、`rounding`、`boundaryRule`、`referenceIds` |
| `dataTables[]` | 對照表檔案路徑、內容說明、來源、版本或年份、`referenceIds` |
| `outputs[]` | 結果項目與 `categories[]`（`label`、`condition`、`tone`：`green`／`yellow`／`red`、`text`） |
| `outOfRange[]` | 超出適用範圍或資料範圍時的處理與顯示文字 |
| `staticText` | `intro`、`method`、`limitations`、`disclaimer`：頁面靜態文字定稿 |
| `references[]`、`sourceCheckedAt` | `id`、`title`、`url`；實際查核日期 |
| `testCases[]` | `id`、`inputs`、`expected`、`basis`（預期值依據）、`note` |
| `openIssues[]` | 缺項、矛盾或待確認事項；不顯示於網頁 |

可複製的空白範本：

```json
{
  "schemaVersion": "pteduimg-calculator/1.0",
  "toolId": "",
  "operation": null,
  "workflowStatus": "draft",
  "page": { "file": "", "url": "", "title": "", "audience": "public", "entry": "calc.html" },
  "inputs": [],
  "computations": [],
  "dataTables": [],
  "outputs": [],
  "outOfRange": [],
  "staticText": { "intro": "", "method": "", "limitations": "", "disclaimer": "" },
  "references": [],
  "sourceCheckedAt": null,
  "testCases": [],
  "openIssues": []
}
```

接收規則：

- 先檢查 `schemaVersion` 與必要欄位；缺項集中列一次，不逐欄反覆詢問。
- 公式、常數、判讀文字與 `staticText` 逐字保留，不潤飾、不摘要、不增加醫療建議。發現公式與來源不符、測試預期值彼此矛盾或有用藥安全疑慮時，具體指出並停止實作該部分。
- `operation: "update_layout"` 的交接包不得包含公式或判讀文字的修改。
- 預備交接包不等於授權修改網站、建置、Commit 或 Push。

## 4. 驗證

**測試案例（`new_tool`、`update_logic`、`update_text`）**

- 每個判讀分類至少一筆典型值；每個門檻至少測邊界上、邊界下各一筆，確認 `≤`／`<` 歸屬與來源一致。
- 必測：缺少選填欄位、超出合理範圍、超出資料或適用範圍、單位換算、四捨五入位數。
- 涉及日期與年齡時加測：月底、閏年 2 月 29 日、當天、未來日期。
- 涉及性別或族群分表時，每個分表至少各一筆。
- 預期值依據來源提供的範例，或獨立的人工／試算表計算；不得用同一段程式碼的輸出當預期值。
- 案例與結果記錄於 `docs/project-management/evidence/<toolId>-<YYYY-MM-DD>.md`；邏輯有修改時，案例須能重跑。

**版面回歸（`update_layout`）**

- 新舊版用同一組輸入比對所有結果文字與顯示狀態，必須全部一致。輸入包含隨機值與上述邊界案例，並記錄案例數。CR-2026-052 以 152 組輸入比對為範例。
- 若回歸比對出現差異，表示動到了邏輯，須改走 `update_logic` 流程。

**瀏覽器檢查（所有操作）**

- 在 320、375 與 1024 以上寬度實際操作：沒有水平捲動、沒有 JavaScript 錯誤，輸入、計算、錯誤訊息與重新計算流程正常。
- 手機實機操作由使用者驗收；未驗收時在 CR 與回報中如實寫明。

## 5. 頁面與手機版面規範

以手機直立使用為主要情境，桌機為次要。

- **縮放**：新增或修改的計算器不得使用 `maximum-scale=1` 或 `user-scalable=no`，讓使用者可以放大。
- **頁首與返回**：保留既有頁首（網站圖示＋工具名稱）與「‹ 回前頁」按鈕及其目的地；不重設網站頁首。
- **分析碼**：保留既有 GA 本機／私有網路保護片段（`isPrivateNetworkHost`、`window.isAnalyticsDisabled`）。
- **輸入**：標籤含單位，數字欄位使用 `inputmode="decimal"`、合理 `min`／`max`／`step` 與範例 placeholder，欄位字級不小於 16px。短欄位在手機可兩欄並排（例如身高／體重），日期等長欄位獨占一行。錯誤訊息以文字顯示在 `role="alert"` 區域。
- **結果**：計算後自動捲到結果區（尊重 `prefers-reduced-motion`）。主要判讀以大字呈現，顏色同時搭配文字，不能只靠顏色表達。結果旁說明查表依據或使用的輸入。
- **說明與來源**：第 2 節要求的靜態說明、來源與查核日期放在結果附近或頁面下方，字級不小於 0.85rem。
- **共用頁尾**：使用 `templates/site-footer.html`，以 `scripts/site_footer.py` 的 `render_footer(ROOT, '<頁面檔名>')` 產生後放在 `</main>` 之後。目前計算器頁尚未列入 `site_footer.py` 的自動同步清單，屬靜態副本；範本修改時需另外更新，並在 CR 記錄。
- **隱私**：計算只在瀏覽器內進行；不得把使用者輸入的健康數值送到分析工具或任何伺服器。非經使用者要求，不把健康數值存進 localStorage；需要時以 try/catch 包住讀寫。
- **檔案**：頁面放在根目錄；樣式放 `css/<toolId>.css`，較長的腳本放 `js/<toolId>.js`，資料表放根目錄或 `data/`。資產留在本站，不新增外部 CDN。
- **品牌**：配色與 Logo 依品牌規範；不重繪 Logo。

## 6. 網站整合

**新增計算器**

1. 在 `calc.html` 加入工具卡（民眾健康計算器）。藥師工作用工具改依 [工具與 Hub 維護](pharmacy-tools-maintenance.md) 加入 Hub 工具目錄；需要時另加 `index.html` 入口。
2. 修改 `build.py`：把頁面與其 CSS／JS／資料檔加入 `update_service_worker` 的 `cache_items`，把頁面加入 `update_sitemap` 的靜態頁清單；需要時把頁面加入 `scripts/check_site.py` 的 GA 保護檢查清單。這屬於 `build.py` 與檢查腳本變更，依 AGENTS 執行 `python -B scripts/check_site.py` 與相關測試。
3. 依 [網站建置與發布](site-build-and-release.md) 執行建置，並確認 `sw.js`、兩份 sitemap 有新頁面且沒有非預期的變更。

**修改既有計算器**

1. 網址、檔名與工具名稱維持不變；更名、搬移或退出依 Hub 規範，並同步 `calc.html`、sitemap 與快取清單。
2. 修改了計算器自己的 CSS／JS 時，把頁面引用中既有的 `?v=` 數字加一；原本沒有版本參數的引用不新增。
3. 更新 `sw.js` 內容指紋：目前做法是 `python -B build.py --incremental <任一未變更且可見的圖片 ID>`。在圖卡來源都沒有變更時，應只更新 `sw.js` 的 `CACHE_NAME`。執行後檢查 `git diff`，若出現圖卡頁或其他非預期檔案的寫入，停止並回報。
4. 執行 `python -B scripts/check_site.py`。

**Hub 核對**：工具名稱、網址或入口有任何變動時，依 Hub 規範核對工具目錄與返回導覽；沒有變動時，回報「已查且一致」。

## 7. 管理紀錄

- 依 [專案管理 SOP](project-management/README.md) 先找既有 CR；沒有才新增，`request_type` 填 `計算器`。
- `related_ids` 只能填 `content-topics.json` 中已存在的節點（目前只有 `tool:menstrual-calculator`、`tool:ingredient-explorer`）；其他工具留空，把修改的檔案寫進 `evidence`，`scope` 寫明工具與修改範圍。
- `validation_result` 寫可重現的命令與數字，例如回歸比對案例數、測試寬度、`check_site` 結果、手機實機是否已驗收、是否已 Commit／Push。不得只寫「OK」。
- 涉及醫療邏輯的 CR，`needs_pharmacist` 填 `yes`；只改版面填 `no`。
- 在總控台加入一筆日期紀錄；測試案例與結果放在 `evidence/`。只有真的補齊某個舊計算器的驗證證據時，才在 CR-2026-024 追加進度。
- 收尾執行 `python -B scripts/project_change_tracker.py --check`，確認網站變更都已連結 CR。

## 8. 完成回報

回報時列出：

- 修改的工具、操作類型，以及計算結果是否改變。
- 公式、門檻或判讀文字的來源與查核日期；未解缺項。
- 測試案例數、回歸比對數、瀏覽器檢查寬度與結果，以及手機實機驗收狀態。
- 執行的建置與檢查命令及結果；`sw.js` 版本是否已更新；Hub 核對結果。
- CR 編號與醫療複核狀態。
- 需要 Commit 的完整檔案清單。未經使用者明確授權，不 Commit、Push 或部署。

## 9. 修訂紀錄

- v1.0（2026-10-31）：依 CR-2026-052 生長計算器手機版面修改的實際流程，以及 CR-2026-024 記錄的計算器驗證缺口制定。
