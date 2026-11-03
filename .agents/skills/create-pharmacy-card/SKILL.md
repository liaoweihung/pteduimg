---
name: create-pharmacy-card
description: 根據使用者提供的圖卡定稿文字、網頁版文字重點及 SEO/AEO 建議，製作符合藥局衛教助手品牌規範的繁體中文衛教圖卡，加入正式 Logo 並檢查成品。適用於製作圖卡、修改圖卡、放大文字及加入 Logo。
---

# 製作藥局衛教助手圖卡（create-pharmacy-card）

本技能用於根據使用者提供的定稿內容製作、修改繁體中文衛教圖卡、放大文字、合成正式品牌 Logo 並執行成品檢查。

## 規範引用與路徑基準

執行前須先讀取並遵循專案共同規範，不在此複製整份品牌規範或網站 SOP：

- 專案共同入口與醫療／簽核底線：[AGENTS.md](../../../AGENTS.md)、[GEMINI.md](../../../GEMINI.md)、[編輯與來源政策](../../../editorial-policy.html)
- 品牌規範共同入口：[docs/brand/README.md](../../../docs/brand/README.md)
- 圖卡視覺布局規範：[docs/brand/CARD_DESIGN_GUIDE_v1.0.md](../../../docs/brand/CARD_DESIGN_GUIDE_v1.0.md)
- 正式品牌識別與母版規範：[docs/brand/BRAND_GUIDE_v2.3.md](../../../docs/brand/BRAND_GUIDE_v2.3.md)
- AI 品牌硬性約束：[docs/brand/BRAND_GUIDE_AI.md](../../../docs/brand/BRAND_GUIDE_AI.md)
- 網站圖卡上架與建置管理（僅在使用者要求加入網站時使用）：[skills/pteduimg-card-manager/SKILL.md](../../../skills/pteduimg-card-manager/SKILL.md)

**路徑解析基準：**
- 本技能位於 `.agents/skills/create-pharmacy-card/SKILL.md`，本檔內的 Markdown 相對連結以 `../../../` 解析至專案根目錄。
- 專案命令與一般檔案路徑以**專案根目錄**為準；品牌素材包的 `assets/`、`data/` 路徑以 **[docs/brand/](../../../docs/brand/)** 為根目錄（即專案根目錄下的 `docs/brand/assets/...` 與 `docs/brand/data/...`）。

---

## 工作流程

### 1. 輸入與內容

使用者通常提供以下三類資料：
- **A. 圖卡文字內容**：作為圖片上的主要定稿。
- **B. 網頁版文字重點**：作為內容脈絡與圖文一致性檢查依據。
- **C. SEO/AEO 建議**：作為檔名、`alt`、網頁標題與問答結構的參考。

**處理原則：**
- 三份資料用途不同，**不把所有網頁文字、關鍵字和 FAQ 塞進圖片**。
- 資料已足夠時直接製作，不重複要求確認。
- 未提供非必要欄位時，先完成可做部分，不為了填滿欄位編造資料。

### 2. 醫療內容

- 完整保留定稿中的**藥名、成分、濃度、劑量、單位、年齡、頻次、步驟與警語**。
- **不得**為了排版擅自刪減醫療資訊、改寫數值或新增療效。
- 發現圖卡文字與網頁文字矛盾時，具體指出差異；涉及用藥安全的部分先釐清，不自行猜測。
- 需要查證時使用官方核准仿單、官方衛教或專業指引等直接來源（依 [editorial-policy.html](../../../editorial-policy.html) 與 [AGENTS.md](../../../AGENTS.md)）；未實際查核不得宣稱已查核。
- AI 校對不等於藥師簽核，**不自行標記已完成醫療審閱**（例如不得自行標記 `pharmacist_reviewed` 或將 `needsMedicalReview` 設為 `false`）。

### 3. 視覺規範

依循 [docs/brand/CARD_DESIGN_GUIDE_v1.0.md](../../../docs/brand/CARD_DESIGN_GUIDE_v1.0.md)：
- **比例與解析度**：預設 **9:16 直式**，目標解析度 **1080×1920**（若使用者當次指定其他比例或尺寸，依指定辦理）。
- **版面配置**：標題區約占上方 **7%–10%**，靠左對齊（未使用的上方空間可安排人物、產品或插圖）；中段依內容彈性排版（漫畫、比較圖、操作步驟、Q&A、人物或產品示意）。
- **視覺風格與字體**：白色或淺色醫療風格，使用**台灣繁體中文**與台灣讀者習慣用語，大字、清楚層級、確保手機直立閱讀清晰。
- **內容過多之處理**：內容多時先調整布局、減少裝飾；仍放不下才提出拆卡建議，**不偷偷刪字或縮成密集小字**。
- **仿單表格**：使用者指定仿單表格時，完整保留表格欄位、數值與對應關係，可做視覺美化但**不可自行改成其他劑量表**。
- **產品外觀示意**：使用者提供產品照片時可卡通化／插畫化，保留辨識特徵，**不虛構包裝文字**；示意外觀應適當註明。
- **資料來源**：資料來源須清楚列出，不捏造來源或日期。
- **條碼限制**：**不生成假的 QR code**。

### 4. 正式 Logo

品牌識別與限制以 [docs/brand/README.md](../../../docs/brand/README.md)、[docs/brand/BRAND_GUIDE_v2.3.md](../../../docs/brand/BRAND_GUIDE_v2.3.md) 及 [docs/brand/BRAND_GUIDE_AI.md](../../../docs/brand/BRAND_GUIDE_AI.md) 為準：

- **位置與外觀保護**：
  - 圖卡右下角放置**正式單色 Logo**，保持完整比例、原方向與手寫「助手」原筆跡。
  - **禁止** AI 重畫、描摹、以字型重打「助手」、額外旋轉或覆寫原始母版。
- **兩階段疊加流程**：
  - 先製作圖卡主畫面並**預留右下角空間**，再使用影像合成工具（如 Python Pillow）疊加原始 Logo 素材。
  - **不要僅靠圖像生成提示詞要求「畫出相同 Logo」**。
- **素材路徑**（以 [docs/brand/](../../../docs/brand/) 為根目錄）：
  - [assets/logo_primary_color_original.png](../../../docs/brand/assets/logo_primary_color_original.png)：正式彩色母版（2048×684）。
  - [assets/logo_monochrome_black_light_background.png](../../../docs/brand/assets/logo_monochrome_black_light_background.png)：淺底黑色單色參考（含淺色背景）。
  - [assets/logo_monochrome_white_dark_background.png](../../../docs/brand/assets/logo_monochrome_white_dark_background.png)：深底白色單色參考（含深色背景）。
- **素材選用與驗收狀態判定**：
  - 透明衍生素材（[assets/logo_primary_transparent.png](../../../docs/brand/assets/logo_primary_transparent.png)、[assets/logo_black_transparent.png](../../../docs/brand/assets/logo_black_transparent.png)、[assets/logo_white_transparent.png](../../../docs/brand/assets/logo_white_transparent.png)）是否可用，依最新品牌文件與 [data/transparent_asset_manifest_v2.3.json](../../../docs/brand/data/transparent_asset_manifest_v2.3.json) 人工驗收紀錄判定；**不要把待驗收當成已核准**。
  - 可使用已核准且背景相容的單色原圖合成。
  - 使用者本次指定特定 Logo 檔案時，優先使用指定檔。
  - 若沒有可用的正式素材，清楚指出缺少哪個檔案，**禁止自行補畫**。
- **尺寸、對齊與浮水印限制**：
  - Logo 不得遮擋文字、來源或插圖；依當次要求調整尺寸。
  - 若使用者要求與頁尾文字等高、不受固定 5%（或 3%）高度限制，依該次要求執行。
  - **漸層浮水印不是預設**（參見 [data/watermark_status.json](../../../docs/brand/data/watermark_status.json)），只在明確要求時使用。

### 5. 生成能力與費用

- 動手前先確認目前環境實際可用的圖片生成與影像合成工具（例如：環境內建之圖像生成工具／subagent、本機 Python Pillow 影像合成工具等）。
- **費用與帳號限制**：僅使用現有帳號可用功能，**不自行設定需另外計費的 API、不索取 API key、不購買額度**。
- 本技能僅定義工作流程與檢核標準，技能本身不會新增圖片生成能力。
- **無法生成圖片時的處理**：若目前環境無法生成圖片，必須明確說明限制，並提供**可貼到 Gemini 圖像生成介面的完整提示詞（含預留右下角 Logo 空間之要求）與素材清單**，**不把提示詞當作已完成圖卡**。

### 6. 輸出與驗證

- **檔案輸出與保存**：
  - 交付實際圖卡，並保留可修改的工作檔（如未疊加 Logo 的底圖、合成腳本或中間素材）。
  - 需要網站使用時另輸出 WebP（如以 Pillow `quality=90, method=6` 轉換，**嚴禁覆寫品牌 PNG 母版**），並保留原始高品質圖片。
- **逐項成品檢查**：
  1. **圖片尺寸與比例**：確認為 9:16 比例（預設 1080×1920）或當次指定尺寸。
  2. **文字與醫療數值**：確認台灣繁體中文字、藥名、成分、濃度、數值、單位、年齡、頻次、步驟與警語與定稿完全一致。
  3. **表格配對**：確認表格列欄配對正確，未擅改劑量對應。
  4. **版面完整性**：確認沒有截字、重疊、過小文字或遺漏警語。
  5. **手機可讀性**：縮至手機顯示寬度檢視仍可清晰閱讀。
  6. **Logo 合成品質**：確認正式 Logo 原檔已合成且維持原比例與原方向、未變形、未遮擋文字／來源／插圖。
  7. **圖文一致性**：確認圖片內容與網頁版文字重點一致。
- **修正與回報底線**：
  - 發現錯字或版面問題先修正；未解決項目明列，**不宣稱全部通過**。
- **網站修改界線與流程銜接**：
  - **只要求製作圖卡時，不自動修改網站**（不變更 `cards.json`、`cards.manual.json`、`data/card_content.json`，不執行 `build.py`，不執行 Commit、Push 或部署）。
  - 使用者另要求將圖卡加入網站時，銜接既有 [skills/pteduimg-card-manager/SKILL.md](../../../skills/pteduimg-card-manager/SKILL.md)，沿用現行建置、逐頁文字／日期／直接來源與專案管理流程，不另創一套。
