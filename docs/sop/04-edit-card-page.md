# 作業卡 4：修改圖卡頁面

適用：修改已上線圖卡的**單頁內容**，例如換圖、改文字、刪掉某段文字、加減仿單連結、推薦閱讀、工具按鈕。只讀這一份。改系列標題、icon、分類等系列層級的設定，改用作業卡 5。

網站作業從「素材已定稿」開始，**不查核、不改寫醫療內容**。新的圖片或文字必須是藥師提供的定稿，缺素材就停下來問。

## 步驟

### 1. 確認工作區並存下檢查基準
> 指令以 PowerShell 為例。用 bash 執行時：`> $null` 改成 `> /dev/null`，`| Select-String "…"` 改成 `| grep "…"`。
```powershell
git status --short
python -c "import os;os.makedirs('outputs',exist_ok=True)"
python -B scripts/check_project_management.py --summary --report-file <基準檔> > $null
python -c "import json;json.load(open('<基準檔>',encoding='utf-8'));print('BASELINE OK')"
```
**基準檔**：`<基準檔>` 用這次開工的日期時間命名，例如 `outputs/mgmt-before-20261114-1240.json`，**不可是已存在的檔名**，並在本次的 evidence 檔記下這個檔名。
**續作同一筆 CR**（例如上次失敗、這次接著做）：**跳過本步的存基準**，改用 evidence 記錄的原始基準檔；不可重新存基準，否則上次已經引入的錯誤會被當成原本就有的錯誤。原始基準檔遺失時停下回報。

記下已存在的改動，本次不碰。存基準的指令會因為網站原有的管理錯誤回報失敗，這是正常的；但最後一行必須印出 `BASELINE OK`，沒有就代表基準沒存到，停下來回報，不要開始修改。這份基準是「改之前」的狀態，檢查時用來比對。

### 2. 登記 CR
先查有沒有已涵蓋本次工作、尚未完成的 CR：`git grep -n "<系列ID>" docs/project-management/change-requests.csv`。有就沿用並補上受影響的 ID；沒有才在 `docs/project-management/change-requests.csv` 末尾新增一列，編號接續最後一筆：
`request_type` 填 `修改既有圖卡`；`related_ids` 列出系列與每一個受影響的頁；`status` 填 `in_progress`、`approval` 填 `approved`；`git_commit` 填 `same_commit`（本次變更會和 CR 一起提交；先填好，變更追蹤檢查才會通過）；`completed_at`、`validation_result` 先填 `unknown`；`evidence` 填下面建立的 evidence 檔路徑。

同時建立 evidence 檔 `docs/project-management/evidence/<CR編號>-<系列ID>.md`（沿用既有 CR 時，更新該 CR 原本的 evidence 檔，不另建），10 行以內：本次範圍、素材來源（有新素材時：圖片檔名、對應文字的版本或日期、藥師定稿確認）。檢查完成後再補上結果。其餘欄位照前一筆同類 CR 的寫法。

### 3. 依改動類型修改
**圖片路徑**：既有頁的圖片不一定是 `.webp`（網站有不少 `.png`）。先在 cards.json 該頁所屬系列的 `steps` 找到**實際圖片路徑**，以下所有寫 `img/<頁ID>.webp` 的地方（搜尋、仿單的鍵、淘汰紀錄、換圖）都改用這個實際路徑。

可以同時做好幾項。`data/card_content.json` 很大，用搜尋找到該頁的紀錄直接修改，不要整份讀取。

| 改動 | 改哪裡 | 注意 |
|---|---|---|
| 換圖片 | 新圖（不含 Logo 的 PNG）轉檔加 Logo（做法同作業卡 1 第 3 步），**沿用原路徑與副檔名**覆蓋實際圖片（原圖是 `.png` 就輸出 PNG：把轉檔程式最後一行改成 `im.convert("RGB").save(dst, "PNG")`） | 該頁紀錄加上或更新 `"imageUpdatedAt": "今天"`，否則民眾手機會繼續顯示快取的舊圖。新圖上的文字與該頁文字必須仍然對得上；對不上就停下來問，不要維持 `matchConfidence: "high"` |
| 改文字 | 該頁的 `title`、`summary`、`sections` | **醫療內容有改**：更新 `updatedAt`、`sourceCheckedAt`、`references`、`revisionCredit`（依素材填寫，`updatedAt` 和 `revisionCredit` 缺一個，「內容更新」那行就不會顯示），`needsMedicalReview` 設為 `true`。**只改不影響醫療意思的錯字或標點**：日期都不動。藥名、成分、劑量、單位、頻次、年齡或否定詞（不、勿、禁止）的錯字，視為醫療內容修改，須由素材端重新定稿後照「醫療內容有改」處理 |
| 刪掉某段文字 | 該頁 `sections` 刪掉那一段 | `title`、`summary` 和至少一段 `sections` 必須保留 |
| 食藥署仿單連結 | `data/label_links.json` 的 `pages` 物件內，以實際圖片路徑為鍵（例如 `img/<頁ID>.webp` 或 `img/<頁ID>.png`）：`[{"name": "品名", "license": "許可證字號", "url": "https://mcp.fda.gov.tw/im_detail_1/<許可證字號>"}]` | 網址只能用食藥署仿單平台；刪除連結就移除該鍵 |
| 推薦閱讀 | 該頁 `related_links`：`[{"title": "", "url": ""}]` | 外部連結、YouTube 都放這裡；站內連結用 `../cards/<頁ID>.html` |
| 工具按鈕 | 屬於系列設定，改用作業卡 5 | 會套用到整個系列 |
| 頁面上加入**以上都沒有**的東西 | 需要改 build.py | **停下來**，依 AGENTS.md 先提出改法，經藥師同意才能做 |

**已登記藥師複核的頁面**（清冊 `medical_review_status` 為 `pharmacist_reviewed`）：**任何改動都會讓舊簽核不適用新版本**，包括只換圖、只改錯字或標點、改推薦閱讀或仿單連結（清冊用該頁的逐頁文字紀錄加上圖片計算指紋，判斷複核的是哪個版本；仿單雖不在指紋內，但屬於醫療相關內容，一併重新複核）。只要改到這種頁面，兩處一起更新：
- `data/card_content.json`：`needsMedicalReview` 改為 `true`；有 `reviewStatus` 就移除（不讓讀者看到舊簽核）。
- `page-inventory.csv`：`medical_review_status` 改為 `pending_pharmacist`，`review_required` 改為 `yes`，`review_reason` 填「內容已修改，待藥師重新複核」；原有的 `reviewer`、`review_date`、`reviewed_content_sha256`、`medical_review_evidence` 保留不刪，並在 `history_note` 補一句「YYYY-MM-DD 前的版本曾由（複核者）於（日期）複核」。
- 醫療日期仍照上表規則處理（只改不影響醫療意思的錯字或標點時不動日期）。回報時提醒藥師：複核後用作業卡 7 重新登記。

另外：該系列在兩份 cards JSON 若還沒有 `"showFooter": true`，一併加上（修改既有系列的圖片、文字或 SEO 時都要開啟共用頁尾）。只開本次修改的系列，不要動其他系列。

### 4. 標記 CR 完成（必須在建置前）
`status` 改為 `completed`，`completed_at` 填今天，`validation_result` 先填「建置與檢查進行中」（不可留 `unknown`，否則管理檢查會報錯；檢查步驟會改成實際結果）。

之後的建置或檢查失敗、本次無法完成時，把 `status` 改回 `in_progress`、`completed_at` 改回 `unknown`，並在 `validation_result` 寫明失敗原因。然後**停下來回報**，不要自行重新建置或還原檔案（完整建置會刪掉並重產整個 `cards/`，可能毀掉不屬於本次的工作）。回報時說明：失敗在哪一步、已產生哪些檔案（`git status --short`），以及首頁「最近新增」（`data/recent-changes.json`）是否已出現這筆 CR。由藥師決定修好後繼續，或用 git 還原本次變更。

### 5. 建置
```powershell
python -B build.py --incremental <本次修改的頁ID> ...
```
有改到系列設定（例如補 `showFooter`）時，每個改到的系列至少列一頁。增量建置被拒絕時，停下回報原因，不要自行改跑完整建置。

### 6. 檢查

**清冊要涵蓋的頁**：不只本次直接修改的頁。建置後用 `git status --short cards/` 列出所有 HTML 有變動的頁，再加上「系列設定（`steps`、標題、`showFooter`、`favorite_keys`、`related_series`、`tool_link` 等）有改動的系列」的**每一頁**；這些頁的機械欄位都會跟著變。以下 `<受影響頁ID>` 指的就是這整份清單。

```powershell
python -B scripts/check_project_management.py --propose --page <受影響頁ID> ...
python -c "import json;[json.load(open(f,encoding='utf-8')) for f in ('cards.json','cards.manual.json','data/card_content.json')];print('JSON OK')"
python -B scripts/check_site.py
python -B scripts/project_change_tracker.py --check --page <本次任一頁ID>
python -B scripts/check_project_management.py --summary --baseline-file <基準檔> --report-file outputs/mgmt-after.json | Select-String "Baseline difference"
```
- `check_site.py` 必須通過。
- 三份 JSON 都要能解析。
- 換圖時，逐張檢查疊上 Logo 的新圖；有問題時照作業卡 1 第 9 步「Logo 檢查」的方式回報原因與處理方式，不自行移動、縮小 Logo 或修圖。
- 基準比對：只看輸出的 `Baseline difference` 那一行，`new` 與 `worsened` 都必須是 0。原本就有的錯誤（`persistent`）不處理，也不必閱讀完整報告；不是 0 時才打開 `outputs/mgmt-after.json` 找出是哪幾筆。
- 變更追蹤：只需執行一次、填本次任一頁 ID。程式對「尚未提交的變更」本來就整體檢查；`--page` 只是排除與本次無關的舊提交紀錄。結果不可有「目前未提交網站變更：缺少管理連結」。
- 清冊的 `added_at`、`added_cr`、`last_updated_at`、`last_updated_cr` 由程式依 CR 推算，不要手填。
- 一般圖卡作業不執行 `scripts/test_*.py`。
- `--propose` 有差異時，只把機械欄位依 `page_id` 合併進 `page-inventory.csv`，人工欄位不動；合併後必須零差異。
- 開啟修改的頁面，確認改動有出現在 HTML 裡。
- 換圖時，確認 `sw.js` 的 `revisedImageUrls` 有這張圖。
- 改仿單連結時，開啟該頁 HTML，確認新增的網址有出現、刪除的網址已消失。
- 用 `git diff --stat` 確認只改到本次相關的檔案。

**執行順序**：
1. 先用 `--propose`（涵蓋上述全部受影響頁）把機械欄位合併進 `page-inventory.csv`，再跑一次 `--propose` 確認零差異。既有頁只合併機械欄位，人工欄位不動（本作業卡明確要求修改的人工欄位除外）；新頁的人工欄位照作業卡 1 第 8 步的表格填。
2. 再執行其餘檢查（JSON、`check_site.py`、變更追蹤、頁面確認），把結果寫入 CR 的 `validation_result` 和 evidence 檔。
3. 最後才執行基準比對，並在 `validation_result` 補上「基準比對 new=0、worsened=0」。

### 7. 回報（不要 commit 或 push）
改了哪些頁、改了什麼、日期有沒有更新（說明理由）、檢查結果、要提交的檔案清單。
