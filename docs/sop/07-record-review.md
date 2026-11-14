# 作業卡 7：登記藥師複核

適用：藥師已完成某些圖卡的醫療複核，要把頁面標記為「已複核」。只讀這一份。

**AI 不能自己判斷複核是否完成**。只有藥師明確提供下列資料時才做，缺一項就停下來問：
- 複核了哪些頁（頁 ID）
- 複核者（要記錄的名稱）
- 複核日期
- 複核依據（例如複核紀錄文件的名稱或位置）
- 頁面上要不要顯示「審閱狀態」（預設不顯示）

## 步驟

### 1. 確認工作區並存下檢查基準
> 指令以 PowerShell 為例。用 bash 執行時：`> $null` 改成 `> /dev/null`，`| Select-String "…"` 改成 `| grep "…"`。
```powershell
git status --short
python -B scripts/check_project_management.py --summary --report-file outputs/mgmt-before.json > $null
```
記下已存在的改動，本次不碰。第二個指令會因為網站原有的管理錯誤回報失敗，這是正常的。

### 2. 登記 CR
先查有沒有已涵蓋本次工作、尚未完成的 CR：`git grep -n "<系列ID>" docs/project-management/change-requests.csv`。有就沿用；沒有才在末尾新增一列，編號接續最後一筆：`request_type` 填 `修改既有圖卡`，名稱寫「登記藥師複核：<系列或頁>」，`related_ids` 列出系列與每一個複核的頁；`status` 填 `in_progress`、`approval` 填 `approved`；`completed_at`、`git_commit`、`validation_result` 先填 `unknown`。

### 3. 建立 evidence 檔
在 `docs/project-management/evidence/` 建立一份，10 行以內：複核的頁、複核者、日期、複核依據，以及藥師的原話（如「已複核通過」）。

### 4. 更新逐頁文字
在 `data/card_content.json` 用搜尋找到每一頁的紀錄：
- `needsMedicalReview` 改為 `false`。
- 藥師要在頁面顯示審閱狀態時，才加上 `"reviewStatus": "藥師提供的文字"`；預設不加。
- 其他欄位（文字、日期、來源）一律不動。複核不等於內容更新，`updatedAt` 不改。

### 5. 標記 CR 完成（必須在建置前）
`status` 改為 `completed`，`completed_at` 填今天。

之後的建置或檢查失敗、本次無法完成時，把 `status` 改回 `in_progress`、`completed_at` 改回 `unknown`，並在 `validation_result` 寫明失敗原因。

### 6. 建置
```powershell
python -B build.py --incremental <複核頁ID> ...
```
增量建置被拒絕時，停下回報原因。

### 7. 更新清冊的人工欄位
先取得最新的機械欄位：
```powershell
python -B scripts/check_project_management.py --propose --page <複核頁ID>
```
把提案的機械欄位依 `page_id` 合併進 `docs/project-management/page-inventory.csv`，再填這幾個人工欄位：

| 欄位 | 填法 |
|---|---|
| `medical_review_status` | `pharmacist_reviewed` |
| `medical_review_evidence` | 第 3 步的 evidence 檔路徑 |
| `reviewer` | 藥師提供的名稱 |
| `review_date` | 複核日期 |
| `reviewed_content_sha256` | 合併後該列的 `content_sha256`（代表複核的是這個版本的內容） |
| `review_required` | `no` |
| `last_human_confirmed_at` | 複核日期 |

其他人工欄位不動。

### 8. 檢查
```powershell
python -c "import json;[json.load(open(f,encoding='utf-8')) for f in ('cards.json','cards.manual.json','data/card_content.json')];print('JSON OK')"
python -B scripts/check_site.py
python -B scripts/check_project_management.py --propose --page <複核頁ID>
python -B scripts/check_project_management.py --summary --baseline-file outputs/mgmt-before.json --report-file outputs/mgmt-after.json | Select-String "Baseline difference"
python -B scripts/project_change_tracker.py --check --page <本次任一頁ID>
```
- JSON 都要能解析，`check_site.py` 必須通過，`--propose` 必須零差異。
- 基準比對：`new` 與 `worsened` 都必須是 0；有複核相關的錯誤時，打開 `outputs/mgmt-after.json` 找出原因並回報，不要為了通過而改人工欄位。
- 變更追蹤：結果不可有「目前未提交網站變更：缺少管理連結」。
- 用 `git diff --stat` 確認只改到本次相關的檔案。

結果填入 CR 的 `validation_result`。

### 9. 回報（不要 commit 或 push）
登記了哪些頁、複核者與日期、頁面是否顯示審閱狀態、檢查結果、要提交的檔案清單。
