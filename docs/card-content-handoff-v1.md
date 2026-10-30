# 藥局衛教助手｜圖卡與網頁文字交接規範 v1.1

制定／修訂日期：2026-10-30。適用：所有執行內容準備、製圖、校對或 pteduimg 網頁整合的 AI，不限品牌、模型與工具。

文件路徑保留 `docs/card-content-handoff-v1.md`，避免既有引用失效；本次修訂為 v1.1。

本文件定義專案交接格式，v1.1 已整合至本機專案及既有入口；沒有新增自動匯入器。它不取代專案的醫療、品牌、建置與發布規則。

## 0. 預設用途與執行原則

使用者製作衛教圖卡，預設用於「藥局衛教助手」網站。除非當次另有指定，產稿 AI 應一次準備圖卡與網站所需內容，不必再詢問是否需要網頁文字。

核心規則：**直接使用已確認的內容與順序；保留圖文、來源及建置檢查，只修正具體問題，不重新策劃整份內容。**

流程：準備完整內容包與易讀文字預覽 → 使用者確認文字 → 製圖並合成正式 Logo → 實際核對最終圖片與文字 → 依當次授權整合網頁與驗證。

- 文字確認前即決定內容、段落順序、圖卡布局與插圖指示；不要把編排工作留給接收 AI。
- 預覽與 JSON 必須來自同一份內容。使用者閱讀正常文字，不必閱讀程式碼；修改時同步更新兩者。
- 使用者只要求文字時，不提前製圖；已提供核准成圖時直接使用，不重新生成。
- 預備上網內容不等於授權修改網站、建置、Commit、Push 或部署；這些依當次指示與既有流程執行。
- 本規範提供一致依據，不保證所有模型自動載入或確實執行；須由入口明確引用並以實際結果留證。

## 1. 核心決定

每次交付一份 UTF-8、合法 JSON 的內容包，建議檔名 `<series_id>.handoff.json`。同一系列可包含多張卡，每張卡獨立一筆 `pages`。JSON 是文字的唯一交接主稿；需要人讀的預覽時，由同一份資料呈現，不另外維護不同文案。

採固定英文欄位名、繁體中文內容。不得使用註解、尾端逗號、省略號或對話中的引用代碼。來源使用完整可點擊網址。段落欄位是純文字，不嵌入 HTML 或 Markdown 語法。

正文欄位直接沿用 `data/card_content.json` 的現有格式；外層的 `schemaVersion`、`workflowStatus`、`operation`、`series`、`pages`、`cardCopy`、`openIssues` 是本規範的交接欄位，不可把整份內容包直接貼入網站 JSON。

## 2. 分工與狀態

- 產稿 AI（例如 ChatGPT、Codex）：產出完整正文、圖卡定稿、真實來源與日期；已知 ID 沿用，未知資料明列缺項；檢查 JSON 與內容一致性。
- 接收 AI（例如 Antigravity、Codex 或其他工具）：讀取內容包，沿用原文製圖與整合資料；確認圖片、識別碼、來源、必要欄位及建置結果；只做必要的格式與路徑處理。
- 使用者：決定內容及醫療簽核、指定修改與發布範圍。文字定稿不等於已簽核或已授權發布。

`workflowStatus` 僅允許：

| 值 | 意義 |
|---|---|
| `draft` | 仍有缺項、文字待確認或尚未完成必要來源查核 |
| `text_ready` | 使用者已確認文字、提示詞與段落順序，必要來源及日期已備齊，可製圖；尚未核對成圖 |
| `integration_ready` | 成圖與文字已核對、路徑及分類等資料齊備，可依授權整合網站 |

上述狀態都不代表藥師複核或發布核准。`operation` 使用 `new_series`、`append_cards` 或 `update_cards`。未知操作留 `null` 並列缺項；不以猜測建立重複頁。

## 3. 固定欄位與用途

| 交接欄位 | 用途／寫入位置 |
|---|---|
| `series.id` | 系列識別碼；對應兩份系列 JSON 的頂層 key，以及每張的 `contentRecord.cardId` |
| `series.metadata` | 系列標題、分類、標籤、篩選、排序等；依現行慣例同步 `cards.json` 與 `cards.manual.json` |
| `pages[].pageId` | 圖片檔名 stem；對應 `cards/<pageId>.html`，不得隨標題變更 |
| `pages[].cardCopy` | 圖片上的精確文案與製圖資訊；不直接當成網頁正文 |
| `pages[].contentRecord` | 逐張網頁文字；以 `image` 比對合併至現有 `data/card_content.json` 陣列 |
| `openIssues` | 缺少資料、文案矛盾或尚待確認項目；不顯示於正式網頁 |

`series.metadata` 沿用專案既有鍵名：`title`、`category`、`order`、`icon`、`hidden`、`tags`，及適用的 `topics` 或 `departments`。排程才使用 `publish_at`；不得為了填滿格式猜測發布設定。

民眾卡 `category: public_education`，須填合法 `topics`；藥師卡為 `pharmacist_general` 或 `pharmacist_product`，須填合法 `departments`。合法分類以專案 `card-data.md` 為準。新系列未提供標籤時，依現行專案規則取得確認。

系列 `steps` 由已確認的圖片與順序整合產生。追加／更新時保留所有既有 steps，不用本次 pages 覆蓋整個系列，也不得依未經確認的順序重新排序。

## 4. 網頁正文規範

每張 `contentRecord` 必須包含下列欄位。未知值在交接草稿中填 `null` 或空陣列，列入 `openIssues`；不得將未完成草稿當成可發布紀錄。

| 欄位 | 規則 |
|---|---|
| `cardId` | 正確系列 ID |
| `image` | 真實對應的 `img/<pageId>.webp` 路徑；草稿可先提案，整合前須確認檔案存在 |
| `url` | 對應正式網域與穩定頁面路徑；保留既有 canonical URL |
| `title` | 完整、自然的網頁主標題，不附站名；可比圖片標題詳細 |
| `summary` | 開頭直接回答主要問題，1–3 句為原則；同時作搜尋摘要，不另寫矛盾版本 |
| `sections` | 非空陣列，每筆都有 `heading` 與 `text`；一段回答一個問題 |
| `altText` | 描述圖卡實際主題與內容，不堆關鍵字，不取代正文 |
| `updatedAt` | 實際建立或實質修訂日，YYYY-MM-DD；純排版不刷新 |
| `sourceCheckedAt` | 實際閱讀核對來源的日期，YYYY-MM-DD；不得用產稿或建置日期代填 |
| `revisionCredit` | 真實編修歸屬，例如確實由 AI 編寫時可記「AI 整理，待藥師複核」；不得冒稱藥師審閱 |
| `references` | 非空 `{title, url}` 陣列；名稱含單位／文件名稱與已知版本，網址直達支持內容的來源 |
| `matchConfidence` | 成圖尚未檢視時留 null；核對精確成圖後才能設為 high。它只表示圖文配對，不是醫療簽核 |
| `needsMedicalReview` | 新內容預設 true；只有可追溯人工複核證據才能改動 |

既有紀錄的作者、審閱狀態、sourceType、expandText 等額外欄位應依事實及本次範圍保留，不因交接稿未列出就刪除。合併以 image 精確定位，另核對 cardId、pageId、url；發現重複或衝突先處理，不以最後一筆覆蓋掩蓋。

### 正文排列

依主題選擇必要段落，不要求每張都有全部章節：

1. 重點摘要：放在 `summary`，直接回答本卡主要問題，不在 sections 重複一段相同摘要。
2. 基本說明：產品、成分、用途、適用對象或情境。
3. 主要衛教內容：用法、劑量、操作步驟或比較。
4. 注意事項：副作用、禁忌、常見錯誤或就醫警訊。
5. 保存與日常照護：適用才列。
6. 常見問答 Q&A：放在正文後段，每個問題為獨立 heading，答案為 text。
7. 資料來源與查核日期：使用 references 與 sourceCheckedAt 等既有欄位，依模板置於正文後。

上述為預設，不硬湊章節；專門 Q&A 卡可直接呈現問答，操作卡可省略不必要的產品介紹。內容經確認後，接收 AI 必須保留既定順序。

產品口味、包裝、濃度、許可證與適應症僅在適用且有可核對資料時提供，不把未知資料補成常見規格。

## 5. SEO／AEO 使用同一份正文

目前 `build.py` 的 `apply_card_content_seo()` 會以正文覆寫相關 SEO 欄位，因此不再另交一份與正文不同的標題或摘要。

| 網頁／SEO 輸出 | 唯一來源 |
|---|---|
| 頁面 title、OG title | `contentRecord.title` 加「｜藥局衛教助手」 |
| 頁面主標題 | 原則上 `contentRecord.title`；整合時檢查既有 `display_title` 或特殊頁覆寫 |
| meta description、OG description | `contentRecord.summary` |
| 圖片 alt | `contentRecord.altText` |
| 搜尋標籤 | 已確認的 `series.metadata.tags`；另檢查既有 SEO keywords 是否需依現行流程同步 |
| AEO 簡答 | `summary` 的直接回答 |
| AEO 問答 | `sections` 中問題式 heading 與完整 text |

問答必須顯示在靜態 HTML，不能只藏在 JSON-LD 或 metadata。不要自創 `faq`／`aeo` 欄位期待現有建置器自動呈現；本規範不要求新增 FAQPage schema，也不保證搜尋排名或 AI 引用。

## 6. 圖卡文字與表格

`cardCopy` 採 `title`、`blocks`、`footer`，並以 `generationPrompt` 保存完整可直接執行的圖卡提示詞。此為交接欄位，不寫入網站正文 schema。

`generationPrompt` 必須包含：預設 9:16（當次另有指定則依指定）與手機可讀要求、標題位置、區塊順序、布局、插圖或產品參考指示、以 blocks 為準的精確文案、來源呈現及右下角正式 Logo 預留要求。提示詞與 blocks 不得有不同版本的文案。正式 Logo 使用核准原檔合成，不要求生成模型重畫；無可用素材時列缺項，不補畫。

首次交稿即統一圖卡與網頁的濃度、劑量與單位表示基準；需要不同基準時，先核對換算並明確標示，不留給接收 AI 臨時協調。

- blocks 可用 `type: text`，配合 `heading` 與 `text`。
- 需要劑量對照表時使用 `type: table`，配合 `heading`、`columns` 與 `rows`；每列儲存字串陣列，長度必須等於欄數。數值、單位與欄列關係不得修改。
- footer 可包含已核對的簡短來源文字；完整連結仍在 contentRecord.references。
- 圖卡步驟、劑量、禁忌與警語應在網頁文字有相應內容；網頁可有更多解釋，但不得矛盾。
- 圖卡遵循現行 9:16、大字、正式 Logo 與來源規範；品牌規則仍只引用共同文件。

現有網頁 renderer 只將 sections.heading 與 sections.text 輸出為標題和段落，並會轉義 HTML。因此網頁版的對照資料先由產稿者寫成「一個適用族群／條件一段」的完整句子，明列每個數值與單位；不要貼 Markdown 表格期待它變成 HTML 表格。如果使用者指定網頁也須呈現真正表格，另列建置器功能需求，不能聲稱本規範 v1.1 已讓現有建置器支援。

## 7. 可複製的草稿範本

以下是合法 JSON 的空白草稿，不是可發布資料。null 與空字串必須在各階段補齊；範本沒有虛構藥品、來源、查核日或簽核。

```json
{
  "schemaVersion": "pteduimg-handoff/1.1",
  "workflowStatus": "draft",
  "operation": null,
  "series": {
    "id": null,
    "metadata": {
      "title": "",
      "category": null,
      "order": null,
      "icon": null,
      "hidden": null,
      "tags": [],
      "topics": [],
      "departments": []
    }
  },
  "pages": [
    {
      "pageId": null,
      "cardCopy": {
        "generationPrompt": "",
        "title": "",
        "blocks": [
          {"type": "text", "heading": "", "text": ""}
        ],
        "footer": ""
      },
      "contentRecord": {
        "cardId": null,
        "image": null,
        "url": null,
        "title": "",
        "summary": "",
        "sections": [
          {"heading": "", "text": ""}
        ],
        "altText": "",
        "updatedAt": null,
        "sourceCheckedAt": null,
        "revisionCredit": null,
        "references": [],
        "matchConfidence": null,
        "needsMedicalReview": true
      }
    }
  ],
  "openIssues": [
    "空白範本：須補齊操作、內容、識別碼、分類、來源、真實日期與歸屬；成圖後核對圖文。"
  ]
}
```

可選表格 block 的形狀（僅作結構示範）：

```json
{
  "type": "table",
  "heading": "",
  "columns": ["適用條件", "用量與單位"],
  "rows": []
}
```

## 8. 接收方固定處理規則

1. 先讀 schemaVersion；未知版本不得默默套用。確認本次授權為製圖、整合網站或兩者。
2. 檢查 JSON、必要欄位、唯一 pageId、圖片路徑及來源資料；缺項集中列一次，不逐欄反覆問。
3. 已定稿提示詞、標題、正文、問答順序、關鍵字及來源逐欄保留，不再次摘要、潤飾、重排、補寫或重新產生 SEO 文案。發現矛盾或安全疑點，僅對問題做必要查核並提出修正。
4. 已有人審與直接來源的內容，核對支持關係、圖文一致性及整合完整度，不自動重啟全主題研究；缺來源或衝突時仍須定點查核。
5. 製圖完成後、整合網頁前，必須實際開啟最終圖片（含 Logo 合成及格式轉換後版本），必要時局部放大，逐項核對藥名、成分、濃度、劑量、數值、單位、年齡／體重、頻次、步驟、表格對應及重要警語；檢查錯字、漏字、截字、遮擋與手機閱讀。網頁可以更詳細，共同內容不得矛盾。圖片偏離正確定稿時優先修正圖片，不遷就錯圖修改正文；定稿本身有錯字、數值矛盾、來源不符或安全疑點時，定點查核、記錄修正，涉及醫療意義變更須交使用者確認。不得把錯誤同步到另一邊。無法讀圖時標示「圖文一致性未驗證」，不得僅憑提示詞、檔名、JSON 或腳本通過宣稱一致。只有完成實際核對後，才能將對應 matchConfidence 設為 high。現行 loader 只載入 high 紀錄；禁止為了讓網頁出現而無條件設 high。
6. 僅取 series.metadata 與 contentRecord 合併網站資料，不將交接外層欄位寫入現有 schema。不覆蓋無關頁面或人工審閱欄位。
7. 依專案 Card Manager 與 build SOP 執行必要建置、管理紀錄與驗證，不手寫生成頁。文稿交接本身不構成 Commit／Push／部署授權。
8. 沿用既有 evidence 紀錄，回報實際核對的圖片路徑／版本、文字依據、結果、已修正與未解決問題，以及適用的圖數、網頁數、改動檔案與驗證結果；不要另建一套重複檢查流程。明確區分腳本字串同步（machine_pass）、AI 圖文核對（matchConfidence）與人類醫療簽核。JSON 可解析或腳本通過不證明圖片或醫療內容正確；沒有可追溯的人類簽核證據不得改成人工已審閱。

## 9. 導入與日後使用

本規範保留於專案 `docs/card-content-handoff-v1.md`，既有 Card Manager、圖卡製作 Skill、GEMINI.md、AGENTS.md 與 `.github/copilot-instructions.md` 均沿用原路徑引用 v1.1。這是文件導入，不需建置全站，也不需改舊卡。

ChatGPT 專案指示及各 AI 入口可加入下列引用（檔案須實際可讀，不得只引用無法存取的本機路徑）：

> 製作衛教圖卡預設供網站使用。開始任務前閱讀「圖卡與網頁文字交接規範」最新版本（專案文件 docs/card-content-handoff-v1.md 或本專案附件），一次準備完整提示詞、圖卡文案、已編排網頁正文、搜尋資訊、來源與對應 JSON。先確認文字再製圖；定稿後直接套用，保留最終圖片、文字與來源核對。網站修改及發布依當次授權執行。

給產稿 AI 的固定指令：

> 請依「圖卡與網頁文字交接規範 v1.1」交付一份合法 JSON 內容包，包含完整圖卡提示詞、精確圖卡文案、排好順序且可直接映射的 contentRecord、已確認標籤及真實直接來源；SEO／AEO 沿用正文欄位。未知資料列 openIssues，不猜測、不輸出 HTML、不標記醫療簽核。提供人讀預覽時須由同一份 JSON 產生。

給接收 AI 的固定指令：

> 請讀取本規範與附件 handoff.json，依本次授權製圖／整合網站。保留定稿文字，將 contentRecord 精確合併至現行資料；沿用專案品牌、建置及管理流程。集中回報缺項，不重新改寫正文，不把未查核的圖文配對設為 high。

## 10. 原版核對依據與修訂驗證界線

- [Card Manager](https://github.com/liaoweihung/pteduimg/blob/main/skills/pteduimg-card-manager/SKILL.md)：來源、雙日期、人工簽核與整合要求。
- [資料模型](https://github.com/liaoweihung/pteduimg/blob/main/skills/pteduimg-card-manager/references/card-data.md)：系列 metadata 與分類。
- [現有逐張文字資料](https://github.com/liaoweihung/pteduimg/blob/main/data/card_content.json)：頂層陣列、逐張紀錄及現有欄位。
- [build.py](https://github.com/liaoweihung/pteduimg/blob/main/build.py)：high 載入條件、sections 純文字渲染、正文覆寫 SEO，以及日期顯示條件。

原 v1.0 記錄已核對上述程式行為；本次 v1.1 為交接規範修訂，未重新核閱遠端程式。修訂後範本完成 JSON 解析及欄位檢查。尚未實測由 Antigravity 讀取、製圖或匯入建置。後續建置器變更時，以實際程式與最新版專案規則重新核對，不假設新欄位已獲支援。


### v1.1 修訂紀錄

納入使用者確認的預設上網用途、跨 AI 通用分工、先確認後製圖、完整提示詞欄位、固定正文預設順序、定稿不重編、實際讀取最終圖卡與分層留證規則。保留既有網站欄位映射與來源規則。2026-10-31 已整合至 Windows 本機專案及上述入口；未修改 ChatGPT 專案指示，亦未完成任何工具的匯入實測。
