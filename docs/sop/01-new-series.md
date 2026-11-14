# 作業卡 1：新增圖卡系列

適用：把一個**全新系列**放上網站。只讀這一份，照步驟做；其他文件只在本卡沒寫到的狀況才查。

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
- 食藥署仿單（品名＋許可證字號）→ 寫入 `data/label_links.json` 的 `pages` 物件內，以 `img/<頁ID>.webp` 為鍵：`[{"name": "品名", "license": "許可證字號", "url": "https://mcp.fda.gov.tw/im_detail_1/<許可證字號>"}]`
- 推薦閱讀（標題＋網址，可放外部連結或 YouTube）→ card_content 該頁加 `"related_links": [{"title": "", "url": ""}]`
- 工具按鈕（例如連到計算器）→ 系列資料加 `"tool_link": {"title": "直接計算", "url": "../xxx.html"}`

## 1. 確認工作區並存下檢查基準

> 指令以 PowerShell 為例。用 bash 執行時：`> $null` 改成 `> /dev/null`，`| Select-String "…"` 改成 `| grep "…"`。
```powershell
git status --short
python -c "import os;os.makedirs('outputs',exist_ok=True)"
python -B scripts/check_project_management.py --summary --report-file <基準檔> > $null
python -c "import json;json.load(open('<基準檔>',encoding='utf-8'));print('BASELINE OK')"
```
**基準檔**：`<基準檔>` 用這次開工的日期時間命名，例如 `outputs/mgmt-before-20261114-1240.json`，**不可是已存在的檔名**，並在本次的 evidence 檔記下這個檔名。
**續作同一筆 CR**（例如上次失敗、這次接著做）：**跳過本步的存基準**，改用 evidence 記錄的原始基準檔；不可重新存基準，否則上次已經引入的錯誤會被當成原本就有的錯誤。原始基準檔遺失時停下回報。


記下已存在的改動，本次不碰、不提交。存基準的指令會因為網站原有的管理錯誤回報失敗，這是正常的；但最後一行必須印出 `BASELINE OK`，沒有就代表基準沒存到，停下來回報，不要開始修改。這份基準是「改之前」的狀態，第 9 步用來比對。

## 2. 登記需求單（CR）

先查有沒有已涵蓋本次工作、尚未完成的 CR：`git grep -n "<系列ID>" docs/project-management/change-requests.csv`。有就沿用並補上受影響的 ID；沒有才在末尾新增一列，編號接續最後一筆：

| 欄位 | 填法 |
|---|---|
| request_id | `CR-YYYY-NNN`（接續編號） |
| proposed_at | 今天 |
| name／description | 一句話說明新增什麼系列、幾張 |
| request_type | `新增系列` |
| scope、related_ids | `series:<系列ID>\|page:<頁ID>\|…`，**只列新系列與它的新頁**。同時被修改的既有系列（例如互設 `related_series`）不要列進來，否則首頁「最近新增」會把它們算成新卡；它們會在第 9 步的清冊合併中處理，並在 evidence 檔寫明「連帶變更的既有頁」 |
| priority／status／approval | `P1`／`in_progress`／`approved` |
| needs_pharmacist／author_permission／commercial_disclosure | `yes`／`unknown`／`unknown`（藥師確認沒有商業關係才填 `no`） |
| completed_at／validation_result | `unknown`（第 6、9 步再填） |
| git_commit | `same_commit`（本次變更會和 CR 一起提交；先填好，變更追蹤檢查才會通過） |
| evidence | `docs/project-management/evidence/<CR編號>-<系列ID>.md`（沿用既有 CR 時，更新該 CR 原本的 evidence 檔，不另建） |

同時建立這個 evidence 檔，10 行以內：範圍（系列、頁數）、素材來源（圖片檔名、對應文字的版本或日期、藥師定稿確認）。第 9 步再補上檢查結果。

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
- `needsMedicalReview` 一律為 `true`，只有藥師提供具名複核紀錄才可以改。

## 6. 標記 CR 完成（必須在建置前）

把該 CR 的 `status` 改成 `completed`，`completed_at` 填今天，`validation_result` 先填「建置與檢查進行中」（不可留 `unknown`，否則管理檢查會報錯；檢查步驟會改成實際結果）。順序不能顛倒，否則首頁「最近新增」不會出現本系列。

之後的建置或檢查失敗、本次無法完成時，把 `status` 改回 `in_progress`、`completed_at` 改回 `unknown`，並在 `validation_result` 寫明失敗原因。然後**停下來回報**，不要自行重新建置或還原檔案（完整建置會刪掉並重產整個 `cards/`，可能毀掉不屬於本次的工作）。回報時說明：失敗在哪一步、已產生哪些檔案（`git status --short`），以及首頁「最近新增」（`data/recent-changes.json`）是否已出現這筆 CR。由藥師決定修好後繼續，或用 git 還原本次變更。

## 7. 建置

```powershell
python -B build.py --incremental <頁ID1> <頁ID2> ...
```

列出全部新頁 ID。若同時修改了既有系列（例如兩邊互設 `related_series`），再加上該既有系列任一頁 ID，否則建置會拒絕。如果增量建置拒絕執行，**停下回報原因**，不要自行改跑完整建置。

## 8. 管理紀錄

1. 取得清冊提案：
   ```powershell
   python -B scripts/check_project_management.py --propose --page <頁ID1> --page <頁ID2>
   ```
   把輸出的機械欄位依 `page_id` 新增到 `page-inventory.csv`。新頁的人工欄位照下表填（跟其他欄位不同，這幾欄填 `unknown` 會被檢查判為錯誤）：

   | 欄位 | 填法 |
   |---|---|
   | `known_issue_ids` | 本 CR 編號 |
   | `review_required` | `yes` |
   | `review_reason` | `新頁尚待藥師複核` |
   | `audit_ids` | 空白（不可填 `unknown`） |
   | `history_note` | 空白 |
   | 其餘人工欄位（`medical_review_status`、`medical_review_evidence`、`reviewer`、`review_date`、`reviewed_content_sha256`、`documented_status`、`seo_aeo_status`、`last_human_confirmed_at`） | `unknown` |
   `added_at`、`added_cr`、`last_updated_at`、`last_updated_cr` 由程式依 CR 自動推算，**不要手填**；不要用提案內容整份覆蓋 CSV。
2. 在 `content-relations.csv` 為每頁加一列：
   `REL-<雜湊>,series:<系列ID>,has_card,page:<頁ID>,source_observed,series_membership,cards.json,<CR 編號>`
   `<雜湊>` 是 `series:<系列ID>|has_card|page:<頁ID>` 的 SHA-256 前 16 碼。

## 9. 檢查

**清冊要涵蓋的頁**：不只本次直接修改的頁。建置後用 `git status --short cards/` 列出所有 HTML 有變動的頁，再加上「系列設定（`steps`、標題、`showFooter`、`favorite_keys`、`related_series`、`tool_link` 等）有改動的系列」的**每一頁**；這些頁的機械欄位都會跟著變。以下 `<受影響頁ID>` 指的就是這整份清單。

```powershell
python -B scripts/check_project_management.py --propose --page <受影響頁ID> ...
python -c "import json;[json.load(open(f,encoding='utf-8')) for f in ('cards.json','cards.manual.json','data/card_content.json')];print('JSON OK')"
python -B scripts/check_site.py
python -B scripts/project_change_tracker.py --check --page <本次任一頁ID>
python -B scripts/check_project_management.py --summary --baseline-file <基準檔> --report-file outputs/mgmt-after.json | Select-String "Baseline difference"
```

- 三份 JSON 都要能解析。
- 逐張看疊上 Logo 的圖，確認 Logo 清楚可見，而且沒有蓋到文字或重要圖案。有問題時**不要自行移動、縮小 Logo 或修圖**，停下來回報下列內容，由藥師決定：
  - **哪幾張、蓋到什麼**：附上右下角的裁切圖（右側 25%、底部 10%）。
  - **可能原因**（逐一核對後寫出是哪一種）：
    1. 素材在右下角 Logo 區（右邊寬 20%、底部高 6%）放了文字或圖案。
    2. 圖片不是 9:16，Logo 的大小或位置因此偏掉。
    3. 依底色選的 Logo 顏色與背景對比不足，看不清楚。
  - **可行的處理方式**：
    - 原因 1、2：退回素材階段，請製圖 AI 依素材規範避開 Logo 區或重產正確比例（建議做法）。
    - 原因 3：改用另一色的 Logo 重新轉檔（例如淺底改深色）。
    - 只蓋到不重要的裝飾：可由藥師決定直接接受。
- `check_site.py` 必須通過。
- `--propose` 必須零差異。
- 基準比對：只看輸出的 `Baseline difference` 那一行，`new` 與 `worsened` 都必須是 0。原本就有的錯誤（`persistent`）不處理，也不必閱讀完整報告；不是 0 時才打開 `outputs/mgmt-after.json` 找出是哪幾筆。
- 變更追蹤：只需執行一次、填本次任一頁 ID。程式對「尚未提交的變更」本來就整體檢查；`--page` 只是排除與本次無關的舊提交紀錄。結果不可有「目前未提交網站變更：缺少管理連結」。
- 開啟一頁生成的 HTML，確認有摘要、分段重點、兩個日期、來源連結，以及「內容更新」那一行。
- 介面：首頁列表有出現本系列、同系列翻頁與「第幾張／共幾張」正確、返回入口可用、分享網址指向正確頁面。
- 用 `git diff --stat` 確認變更只有本次相關的檔案，沒有動到 `build.py`、`templates/`、`scripts/`、`index.html`、`public.html`。
- 一般圖卡作業不執行 `scripts/test_*.py`，改到檢查程式本身才需要。

**執行順序**：
1. 先用 `--propose`（涵蓋上述全部受影響頁）把機械欄位合併進 `page-inventory.csv`，再跑一次 `--propose` 確認零差異。既有頁只合併機械欄位，人工欄位不動（本作業卡明確要求修改的人工欄位除外）；新頁的人工欄位照作業卡 1 第 8 步的表格填。
2. 再執行其餘檢查（JSON、`check_site.py`、變更追蹤、頁面確認），把結果寫入 CR 的 `validation_result` 和 evidence 檔。
3. 最後才執行基準比對，並在 `validation_result` 補上「基準比對 new=0、worsened=0」。

## 10. 回報（不要 commit 或 push）

- 新增的系列、頁數、CR 編號。
- 第 9 步各項檢查的結果。
- 要提交的檔案清單：圖片、兩份 cards JSON、`data/card_content.json`、`cards/*.html`、建置產生的全站檔案、`docs/project-management/` 的變更。
- 待藥師做：手機實際操作、Logo 目視檢查、醫療複核。
