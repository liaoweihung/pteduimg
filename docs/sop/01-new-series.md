# 作業卡 1：新增圖卡系列

適用：把一個**全新系列**放上網站。先讀作業卡 0（共同步驟），再照本卡做；其他文件只在兩張卡都沒寫到的狀況才查。

## 0. 開工條件：素材必須齊全

網站作業從「素材已定稿」開始。**本階段不查核、不改寫醫療內容，也不找來源。**缺任何一項就停下來問藥師，不要自行補寫或猜測。

| 素材 | 內容 |
|---|---|
| 圖片 | 每張一個 PNG，已定稿（9:16 滿版，右下角留空、**不含 Logo**）。網站作業不修圖、不重產；Logo 只在第 3 步加 |
| 逐頁文字 | 每張：標題、摘要、分段重點（小標＋內文）、來源（名稱＋網址）、內容更新日期、資料查核日期、修訂歸屬 |
| 系列資訊 | 系列 ID（英文小寫）、系列標題、民眾或藥師、分類（民眾填 topics／藥師填 departments，可填多個）、icon、搜尋標籤；選填：排序、相關系列 |

分類代碼只能用 `docs/sop/card-data.md` 列出的 ID。

**同一內容要出現在多處時，不要複製圖片或文字**：系列要出現在多個分類，就在 topics／departments 填多個代碼；某張卡要同時放進另一個系列，照作業卡 2 的「共用」處理。

**選填素材**（有提供才做）：
- 食藥署仿單（品名＋許可證字號）→ 寫入 `data/label_links.json` 的 `pages` 物件內，以 `img/<頁ID>.webp` 為鍵：`[{"name": "品名", "license": "許可證字號", "url": "https://mcp.fda.gov.tw/im_detail_1/<許可證字號>"}]`。網址**直接用許可證字號組成**（URL 編碼方式照 `label_links.json` 現有紀錄），**不上網搜尋、不開瀏覽器查核**，由藥師在預覽頁點開確認。只有品名、沒有許可證字號時，停下來問。
- 推薦閱讀（標題＋網址，可放外部連結或 YouTube）→ card_content 該頁加 `"related_links": [{"title": "", "url": ""}]`
- 工具按鈕（例如連到計算器）→ 系列資料加 `"tool_link": {"title": "直接計算", "url": "../xxx.html"}`

## 1. 開工

照作業卡 0 第 1 步。

## 2. 登記 CR

照作業卡 0 第 2 步，本卡的欄位：
- `request_type`：`新增系列`；`priority`：`P1`。
- `scope`、`related_ids`：**只列新系列與它的新頁**。同時被修改的既有系列（例如互設 `related_series`）不要列進來，否則首頁「最近新增」會把它們算成新卡；它們會在檢查的清冊合併中處理，並在 evidence 檔寫明「連帶變更的既有頁」。

## 3. 圖片轉檔加 Logo

- 檔名：英文小寫加底線，例如 `img/<系列ID>_01.webp`。頁 ID＝檔名去掉副檔名。
- 命名前用一行指令確認沒被用過：`git ls-files "img/<頁ID>.*" "cards/<頁ID>.html"`。有輸出就換一個名稱；不需要讀其他檔案。
- 原始 PNG 不放進 repo。
- 依右下角底色選 Logo：淺底用 `logo_black_transparent.png`，深底用 `logo_white_transparent.png`（都在 `docs/brand/assets/`）。

用下列程式處理，不另寫新腳本：

```python
from PIL import Image, ImageStat
def convert(src, dst, color=None):  # color 可指定 "black" 或 "white"，預設依底色自動選
    im = Image.open(src).convert("RGBA")
    W, H = im.size
    corner = im.crop((int(W*.8), int(H*.94), W, H)).convert("L")
    name = color or ("black" if ImageStat.Stat(corner).mean[0] > 128 else "white")
    logo = Image.open(f"docs/brand/assets/logo_{name}_transparent.png")
    logo = logo.crop(logo.getbbox())
    h = round(H*0.03); w = round(logo.width*h/logo.height)
    logo = logo.resize((w, h), Image.Resampling.LANCZOS)
    im.paste(logo, (W-w-round(W*0.025), H-h-round(H*0.015)), logo)
    im.convert("RGB").save(dst, "WEBP", quality=90, method=6)
```

## 4. 系列資料（cards.json 與 cards.manual.json 寫入相同內容）

```json
"<系列ID>": {
  "title": "系列標題",
  "category": "public_education",
  "topics": ["sleep"],
  "order": 10,
  "hidden": false,
  "icon": "🌙",
  "tags": ["標籤1", "標籤2"],
  "showFooter": true,
  "steps": ["img/<系列ID>_01.webp", "img/<系列ID>_02.webp"]
}
```

- 藥師系列：`category` 用 `pharmacist_general` 或 `pharmacist_product`，用 `departments` 取代 `topics`。
- 有相關系列時加 `"related_series": ["<另一系列ID>"]`，兩邊都要加。
- 不設 `thumbnail`。
- `data/card_content.json` 很大，只能在尾端新增或搜尋特定頁，不要整份讀取。

## 5. 逐頁文字（data/card_content.json，每張圖一筆）

照素材**逐字填入，不改寫**：

```json
{
  "cardId": "<系列ID>",
  "image": "img/<頁ID>.webp",
  "url": "https://liaoweihung.github.io/pteduimg/cards/<頁ID>.html",
  "title": "", "summary": "",
  "sections": [{"heading": "", "text": ""}],
  "altText": "<系列標題>衛教圖卡第 N 張：<標題>",
  "updatedAt": "YYYY-MM-DD", "sourceCheckedAt": "YYYY-MM-DD",
  "revisionCredit": "",
  "references": [{"title": "", "url": "https://"}],
  "matchConfidence": "high",
  "needsMedicalReview": true
}
```

- `updatedAt` 和 `revisionCredit` **兩個都要填**，頁面上的「內容更新」那一行才會顯示。素材沒有修訂歸屬就停下來問，不要自己編。
- `matchConfidence` 填 `"high"` 前，確認這段文字確實屬於這張圖：圖上的標題與文字標題一致、張數順序沒有錯位。這只代表圖文配對正確，不代表醫療內容已複核。配對有疑問就停下來問，不要填 `high`（程式只收 `high` 的紀錄）。
- `altText` 是一句圖片描述，不要把整段內文塞進去。
- `needsMedicalReview` 一律為 `true`；只有藥師複核（作業卡 0 第 5 步或作業卡 7）才可以改。

## 6. 標記完成與建置

照作業卡 0 第 3 步。建置指令：

```powershell
python -B build.py --incremental <頁ID1> <頁ID2> ...
```

列出全部新頁 ID。若同時修改了既有系列（例如兩邊互設 `related_series`），再加上該既有系列任一頁 ID，否則建置會拒絕。

## 7. 草稿與複核（視藥師要求）

- 藥師要先看草稿：照作業卡 0 第 4 步；修改後用第 6 步的指令重新建置。
- 藥師看過定稿並表示已複核：照作業卡 0 第 5 步。

## 8. 建置後管理紀錄（定稿後、檢查前做一次）

1. **新頁清冊列**：
   ```powershell
   python -B scripts/check_project_management.py --propose --page <頁ID1> --page <頁ID2>
   ```
   把輸出的機械欄位依 `page_id` 新增到 `page-inventory.csv`。新頁的人工欄位照下表填（這幾欄填 `unknown` 會被檢查判為錯誤）；有當場複核時，再用作業卡 0 第 5 步的表格覆蓋：

   | 欄位 | 填法 |
   |---|---|
   | `known_issue_ids` | 本 CR 編號 |
   | `review_required` | `yes` |
   | `review_reason` | `新頁尚待藥師複核` |
   | `audit_ids` | 空白（不可填 `unknown`） |
   | `history_note` | 空白 |
   | 其餘人工欄位（`medical_review_status`、`medical_review_evidence`、`reviewer`、`review_date`、`reviewed_content_sha256`、`documented_status`、`seo_aeo_status`、`last_human_confirmed_at`） | `unknown` |
2. **關聯**：在 `content-relations.csv` 為每頁加一列：
   `REL-<雜湊>,series:<系列ID>,has_card,page:<頁ID>,source_observed,series_membership,cards.json,<CR 編號>`
   `<雜湊>` 是 `series:<系列ID>|has_card|page:<頁ID>` 的 SHA-256 前 16 碼。

## 9. 檢查

照作業卡 0 第 6 步。本卡的**頁面確認**：

- **Logo**：逐張看疊上 Logo 的圖，確認清楚可見，而且沒有蓋到文字或重要圖案。有問題時**不要自行移動、縮小 Logo 或修圖**，停下來回報，由藥師決定：
  - **哪幾張、蓋到什麼**：附上右下角的裁切圖（右側 25%、底部 10%）。
  - **可能原因**（逐一核對後寫出是哪一種）：
    1. 素材在右下角 Logo 區（右邊寬 20%、底部高 6%）放了文字或圖案。
    2. 圖片不是 9:16，Logo 的大小或位置因此偏掉。
    3. 依底色選的 Logo 顏色與背景對比不足，看不清楚。
  - **可行的處理方式**：原因 1、2 退回素材階段，請製圖 AI 避開 Logo 區或重產正確比例（建議做法）；原因 3 改用另一色的 Logo 重新轉檔；只蓋到不重要的裝飾，可由藥師決定直接接受。
- 開啟一頁生成的 HTML，確認有摘要、分段重點、兩個日期、來源連結，以及「內容更新」那一行；有仿單時確認連結出現。
- 介面：首頁列表有出現本系列、同系列翻頁與「第幾張／共幾張」正確、返回入口可用、分享網址指向正確頁面。
- `git diff --stat` 沒有動到 `build.py`、`templates/`、`scripts/`、`index.html`、`public.html`。

## 10. 回報

照作業卡 0 第 8 步，另外列出：新增的系列、頁數、CR 編號；要提交的檔案（圖片、兩份 cards JSON、`data/card_content.json`、`cards/*.html`、建置產生的全站檔案、`docs/project-management/` 的變更）；待藥師做的事（手機實際操作、Logo 目視檢查；沒有當場複核時，還有醫療複核）。
