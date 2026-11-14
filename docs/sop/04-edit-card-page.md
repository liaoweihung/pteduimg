# 作業卡 4：修改圖卡頁面

適用：修改已上線圖卡的**單頁內容**，例如換圖、改文字、刪掉某段文字、加減仿單連結、推薦閱讀、工具按鈕。只讀這一份。改系列標題、icon、分類等系列層級的設定，改用作業卡 5。

網站作業從「素材已定稿」開始，**不查核、不改寫醫療內容**。新的圖片或文字必須是藥師提供的定稿，缺素材就停下來問。

## 步驟

### 1. 確認工作區並存下檢查基準
```powershell
git status --short
python -B scripts/check_project_management.py --summary --report-file outputs/mgmt-before.json > $null
```
記下已存在的改動，本次不碰。第二個指令會因為網站原有的管理錯誤回報失敗，這是正常的：它只是存下「改之前」的狀態，檢查時用來比對。

### 2. 登記 CR
先查有沒有已涵蓋本次工作、尚未完成的 CR：`git grep -n "<系列ID>" docs/project-management/change-requests.csv`。有就沿用並補上受影響的 ID；沒有才在 `docs/project-management/change-requests.csv` 末尾新增一列，編號接續最後一筆：
`request_type` 填 `修改既有圖卡`；`related_ids` 列出系列與每一個受影響的頁；`status` 填 `in_progress`、`approval` 填 `approved`；`completed_at`、`git_commit`、`validation_result` 先填 `unknown`。其餘欄位照前一筆同類 CR 的寫法。

### 3. 依改動類型修改
可以同時做好幾項。`data/card_content.json` 很大，用搜尋找到該頁的紀錄直接修改，不要整份讀取。

| 改動 | 改哪裡 | 注意 |
|---|---|---|
| 換圖片 | 新圖（不含 Logo 的 PNG）轉檔加 Logo（做法同作業卡 1 第 3 步），**沿用原檔名**覆蓋 `img/<頁ID>.webp` | 該頁紀錄加上或更新 `"imageUpdatedAt": "今天"`，否則民眾手機會繼續顯示快取的舊圖。新圖上的文字與該頁文字必須仍然對得上；對不上就停下來問，不要維持 `matchConfidence: "high"` |
| 改文字 | 該頁的 `title`、`summary`、`sections` | **醫療內容有改**：更新 `updatedAt`、`sourceCheckedAt`、`references`、`revisionCredit`（依素材填寫，`updatedAt` 和 `revisionCredit` 缺一個，「內容更新」那行就不會顯示），`needsMedicalReview` 設為 `true`。**只改錯字或標點**：日期都不動 |
| 刪掉某段文字 | 該頁 `sections` 刪掉那一段 | `title`、`summary` 和至少一段 `sections` 必須保留 |
| 食藥署仿單連結 | `data/label_links.json`，以 `img/<頁ID>.webp` 為鍵：`[{"name": "品名", "license": "許可證字號", "url": "https://mcp.fda.gov.tw/im_detail_1/<許可證字號>"}]` | 網址只能用食藥署仿單平台；刪除連結就移除該鍵 |
| 推薦閱讀 | 該頁 `related_links`：`[{"title": "", "url": ""}]` | 外部連結、YouTube 都放這裡；站內連結用 `../cards/<頁ID>.html` |
| 工具按鈕 | 屬於系列設定，改用作業卡 5 | 會套用到整個系列 |
| 頁面上加入**以上都沒有**的東西 | 需要改 build.py | **停下來**，依 AGENTS.md 先提出改法，經藥師同意才能做 |

另外：該系列在兩份 cards JSON 若還沒有 `"showFooter": true`，一併加上（修改既有系列的圖片、文字或 SEO 時都要開啟共用頁尾）。只開本次修改的系列，不要動其他系列。

### 4. 標記 CR 完成（必須在建置前）
`status` 改為 `completed`，`completed_at` 填今天。

### 5. 建置
```powershell
python -B build.py --incremental <受影響頁ID> ...
```
增量建置被拒絕時，停下回報原因，不要自行改跑完整建置。

### 6. 檢查
```powershell
python -m json.tool cards.json > $null
python -m json.tool cards.manual.json > $null
python -m json.tool data/card_content.json > $null
python -B scripts/check_site.py
python -B scripts/check_project_management.py --propose --page <受影響頁ID> ...
python -B scripts/check_project_management.py --summary --baseline-file outputs/mgmt-before.json --report-file outputs/mgmt-after.json | Select-String "Baseline difference"
python -B scripts/project_change_tracker.py --check --page <受影響頁ID> ...
```
- `check_site.py` 必須通過。
- 三份 JSON 都要能解析。
- 換圖時，逐張檢查疊上 Logo 的新圖；有問題時照作業卡 1 第 9 步「Logo 檢查」的方式回報原因與處理方式，不自行移動、縮小 Logo 或修圖。
- 基準比對：只看輸出的 `Baseline difference` 那一行，`new` 與 `worsened` 都必須是 0。原本就有的錯誤（`persistent`）不處理，也不必閱讀完整報告；不是 0 時才打開 `outputs/mgmt-after.json` 找出是哪幾筆。
- 變更追蹤：受影響的頁都要對應到本次 CR。
- 清冊的 `added_at`、`added_cr`、`last_updated_at`、`last_updated_cr` 由程式依 CR 推算，不要手填。
- 一般圖卡作業不執行 `scripts/test_*.py`。
- `--propose` 有差異時，只把機械欄位依 `page_id` 合併進 `page-inventory.csv`，人工欄位不動；合併後必須零差異。
- 開啟修改的頁面，確認改動有出現在 HTML 裡。
- 換圖時，確認 `sw.js` 的 `revisedImageUrls` 有這張圖。
- 用 `git diff --stat` 確認只改到本次相關的檔案。

結果填入 CR 的 `validation_result`。

### 7. 回報（不要 commit 或 push）
改了哪些頁、改了什麼、日期有沒有更新（說明理由）、檢查結果、要提交的檔案清單。
