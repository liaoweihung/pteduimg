# 作業卡 5：修改系列設定

適用：修改系列層級的設定，例如系列標題、icon、搜尋標籤、分類、首頁排序、工具按鈕、相關系列，或暫時隱藏系列。只讀這一份。單頁內容改用作業卡 4；要永久下架改用作業卡 3。

## 步驟

### 1. 確認工作區並存下檢查基準
> 指令以 PowerShell 為例。用 bash 執行時：`> $null` 改成 `> /dev/null`，`| Select-String "…"` 改成 `| grep "…"`。
```powershell
git status --short
python -B scripts/check_project_management.py --summary --report-file outputs/mgmt-before.json > $null
```
記下已存在的改動，本次不碰。第二個指令會因為網站原有的管理錯誤回報失敗，這是正常的：它只是存下「改之前」的狀態，檢查時用來比對。

### 2. 登記 CR
先查有沒有已涵蓋本次工作、尚未完成的 CR：`git grep -n "<系列ID>" docs/project-management/change-requests.csv`。有就沿用並補上受影響的 ID；沒有才在 `docs/project-management/change-requests.csv` 末尾新增一列，編號接續最後一筆：
`request_type` 填 `修改既有圖卡`；`related_ids` 列出系列與該系列每一頁；`status` 填 `in_progress`、`approval` 填 `approved`；`completed_at`、`git_commit`、`validation_result` 先填 `unknown`。其餘欄位照前一筆同類 CR 的寫法。

### 3. 修改設定（cards.json 與 cards.manual.json 寫入相同內容）

| 設定 | 欄位 | 注意 |
|---|---|---|
| 系列標題 | `title` | |
| icon | `icon` | 一個 emoji |
| 搜尋標籤 | `tags` | |
| 分類 | 民眾：`topics`；藥師：`departments`（可填多個，讓系列同時出現在多個分類） | 代碼只能用 `docs/sop/card-data.md` 列出的 ID |
| 首頁排序 | `order` | 數字越小越前面 |
| 工具按鈕 | `tool_link`：`{"title": "直接計算", "url": "../xxx.html"}` | 刪除按鈕就移除這個欄位 |
| 相關系列 | `related_series`：`["<另一系列ID>"]` | 兩個系列都要互相加 |
| 暫時隱藏 | `hidden: true` | 見下方說明 |
| 共用頁尾 | `showFooter: true` | 有改到的系列若還沒開啟，一併開啟 |

**暫時隱藏的限制**：`hidden: true` 只會讓系列從首頁列表消失，圖卡頁面仍然存在，知道網址的人還是看得到，搜尋引擎也可能還在收錄。要真正下架，請改用作業卡 3。

### 4. 標記 CR 完成（必須在建置前）
`status` 改為 `completed`，`completed_at` 填今天。

之後的建置或檢查失敗、本次無法完成時，把 `status` 改回 `in_progress`、`completed_at` 改回 `unknown`，並在 `validation_result` 寫明失敗原因。

### 5. 建置
- **改 `order` 或 `hidden`**：`python -B build.py`（完整建置）
- **其他設定**：`python -B build.py --incremental <該系列任一頁ID>`

增量建置被拒絕時，停下回報原因。

### 6. 檢查
```powershell
python -c "import json;[json.load(open(f,encoding='utf-8')) for f in ('cards.json','cards.manual.json','data/card_content.json')];print('JSON OK')"
python -B scripts/check_site.py
python -B scripts/check_project_management.py --propose --page <該系列頁ID> ...
python -B scripts/check_project_management.py --summary --baseline-file outputs/mgmt-before.json --report-file outputs/mgmt-after.json | Select-String "Baseline difference"
python -B scripts/project_change_tracker.py --check --page <本次任一頁ID>
```
- `check_site.py` 必須通過。
- 三份 JSON 都要能解析。
- 基準比對：只看輸出的 `Baseline difference` 那一行，`new` 與 `worsened` 都必須是 0。原本就有的錯誤（`persistent`）不處理，也不必閱讀完整報告；不是 0 時才打開 `outputs/mgmt-after.json` 找出是哪幾筆。
- 變更追蹤：只需執行一次、填本次任一頁 ID。程式對「尚未提交的變更」本來就整體檢查；`--page` 只是排除與本次無關的舊提交紀錄。結果不可有「目前未提交網站變更：缺少管理連結」。
- 清冊的 `added_at`、`added_cr`、`last_updated_at`、`last_updated_cr` 由程式依 CR 推算，不要手填。
- 一般圖卡作業不執行 `scripts/test_*.py`。
- `--propose` 有差異時，只把機械欄位依 `page_id` 合併進 `page-inventory.csv`，人工欄位不動；合併後必須零差異。
- 開啟該系列的一頁，確認改動有出現。
- 用 `git diff --stat` 確認只改到本次相關的檔案。

結果填入 CR 的 `validation_result`。

### 7. 回報（不要 commit 或 push）
改了哪些設定、檢查結果、要提交的檔案清單。隱藏系列時，要提醒藥師頁面仍可經由網址開啟。
