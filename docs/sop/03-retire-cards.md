# 作業卡 3：刪除圖卡（淘汰）

適用：讓一張圖卡、或整個系列下架。只讀這一份。

網站**不真的刪除頁面**，而是「淘汰」：舊網址保留，打開會看到退出日期與**淘汰原因**，並列入「退出圖卡紀錄」（`retired-cards.html`）；同時從搜尋引擎、首頁、索引中移除。這樣民眾的收藏和外部連結才不會變成錯誤頁。

## 素材

- 要淘汰的頁（或整個系列）
- 淘汰原因（必填，一兩句話；會顯示在舊網址頁面上給民眾看）
- 替代頁（選填）：現有的圖卡。藥師沒有指定就不填，不要自己挑一頁湊數。

## 步驟

### 1. 確認工作區並存下檢查基準
```powershell
git status --short
python -B scripts/check_project_management.py --summary --report-file outputs/mgmt-before.json > $null
```
記下已存在的改動，本次不碰。第二個指令會因為網站原有的管理錯誤回報失敗，這是正常的：它只是存下「改之前」的狀態，檢查時用來比對。

### 2. 登記 CR
先查有沒有已涵蓋本次工作、尚未完成的 CR：`git grep -n "<系列ID>" docs/project-management/change-requests.csv`。有就沿用並補上受影響的 ID；沒有才在 `docs/project-management/change-requests.csv` 末尾新增一列，編號接續最後一筆：
`request_type` 填 `修改既有圖卡`；`related_ids` 列出系列與每一個淘汰的頁；`status` 填 `in_progress`、`approval` 填 `approved`；`completed_at`、`git_commit`、`validation_result` 先填 `unknown`。其餘欄位照前一筆同類 CR 的寫法。

### 3. 從系列移除
- **淘汰單張**：從 cards.json 與 cards.manual.json 該系列的 `steps` 移除。
- **整個系列下架**：從兩份 cards JSON 刪除整個系列。
- 圖檔和 `data/card_content.json` 的紀錄都**保留，不要刪除**。

### 4. 保護收藏編號（淘汰單張且不是最後一張時）
系列中剩下的卡要保留原本的收藏編號，否則民眾收藏的會變成另一張卡。在該系列設定 `favorite_keys`，跟 `steps` 一一對應：

```
原本 steps：[A, B, C]，編號 [x-0, x-1, x-2]
淘汰 B：steps [A, C]
favorite_keys：["x-0", "x-2"]
```

系列已經有 `favorite_keys` 時，刪掉被淘汰那張的編號即可。

### 5. 登記淘汰紀錄
在 `cards.retired.json` 每淘汰一頁新增一筆，格式照檔案內現有紀錄：

```json
{
  "image": "img/<頁ID>.webp",
  "title": "原頁標題",
  "reason": "淘汰原因",
  "page": "cards/<頁ID>.html",
  "retired_at": "YYYY-MM-DD",
  "original_series": "原系列標題",
  "replacements": [{"page": "cards/<替代頁ID>.html", "title": "替代頁標題"}],
  "tags": ["原系列標籤"]
}
```

沒有替代頁時，`replacements` 填 `[]`。

### 6. 處理指向它的連結
搜尋其他地方有沒有連到被淘汰的頁，有的話改連到替代頁；沒有替代頁就移除該連結：
```powershell
git grep -n "<頁ID>.html" -- topics/ data/card_content.json data/label_links.json cards.json
```
- `topics/` 主題頁裡的連結 → 改成替代頁網址。
- 其他圖卡的 `related_links` → 改成替代頁。
- 其他系列的 `related_series` 指向被下架的系列 → 移除。

改了哪些地方要列在回報裡。

### 7. 標記 CR 完成（必須在建置前）
`status` 改為 `completed`，`completed_at` 填今天。

### 8. 完整建置
```powershell
python -B build.py
```

### 9. 檢查
```powershell
python -m json.tool cards.json > $null
python -m json.tool cards.manual.json > $null
python -m json.tool data/card_content.json > $null
python -B scripts/check_site.py
python -B scripts/check_project_management.py --propose --page <淘汰頁ID> --page <受影響頁ID> ...
python -B scripts/check_project_management.py --summary --baseline-file outputs/mgmt-before.json --report-file outputs/mgmt-after.json | Select-String "Baseline difference"
python -B scripts/project_change_tracker.py --check --page <淘汰頁ID> --page <受影響頁ID> ...
```
- `check_site.py` 必須通過。
- 三份 JSON 都要能解析。
- 基準比對：只看輸出的 `Baseline difference` 那一行，`new` 與 `worsened` 都必須是 0。原本就有的錯誤（`persistent`）不處理，也不必閱讀完整報告；不是 0 時才打開 `outputs/mgmt-after.json` 找出是哪幾筆。
- 變更追蹤：受影響的頁都要對應到本次 CR。
- 清冊的 `added_at`、`added_cr`、`last_updated_at`、`last_updated_cr` 由程式依 CR 推算，不要手填。
- 一般圖卡作業不執行 `scripts/test_*.py`。
- `--propose` 有差異時，只把機械欄位依 `page_id` 合併進 `page-inventory.csv`，人工欄位不動；合併後必須零差異。
- 開啟 `cards/<淘汰頁ID>.html`，確認顯示退出日期與原因；有替代頁時確認連結可以點開。
- 確認 `retired-cards.html` 有這一筆，`sitemap.xml` 和 `all-cards.html` 已經沒有它。
- 用 `git diff --stat` 確認只改到本次相關的檔案，有不明的改動要列出來。

結果填入 CR 的 `validation_result`。

### 10. 回報（不要 commit 或 push）
淘汰了哪些頁、替代頁、改了哪些連結、收藏編號怎麼處理、檢查結果、要提交的檔案清單。
