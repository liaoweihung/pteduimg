# 作業卡 7：登記藥師複核

適用：藥師已完成某些圖卡的醫療複核，要把頁面標記為「已複核」。只讀這一份。

**AI 不能自己判斷複核是否完成**。只有藥師明確提供下列資料時才做，缺一項就停下來問：
- 複核了哪些頁（頁 ID）
- 複核者（要記錄的名稱）
- 複核日期
- 複核依據（例如複核紀錄文件的名稱或位置），以及**複核的是哪個版本**（素材定稿的圖片檔名、文字版本或日期）
- （選填）頁面上要不要顯示「審閱狀態」。沒提到就照預設：不顯示，不必為此停下來問。

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

記下已存在的改動，本次不碰。存基準的指令會因為網站原有的管理錯誤回報失敗，這是正常的；但最後一行必須印出 `BASELINE OK`，沒有就代表基準沒存到，停下來回報，不要開始修改。

### 2. 確認複核的是目前網站上的版本（登記 CR 之前做）
藥師複核的版本，必須就是現在網站上的版本，才能登記。對每一頁檢查：
1. **找出實際圖片**：在 cards.json 該頁所屬系列的 `steps` 找到它的圖片路徑（可能是 `.webp`，也可能是 `.png` 等其他格式），不要自己假設副檔名。
2. **找出最近一次改到這頁圖文的紀錄**：從清冊 `page-inventory.csv` 該頁的 `last_updated_cr` 開始找；那張 CR 若只改系列設定（排序、標題等）、沒有記錄素材版本，就用 `git grep -n "page:<頁ID>" docs/project-management/change-requests.csv` 往前找更早的 CR，直到找到記錄了素材版本（圖片檔名、文字版本或日期）的那一張。
3. **比對**：藥師複核的版本（定稿檔名、文字版本，或藥師實際看過的網站版本）跟第 2 項找到的版本一致，就算相符，直接登記。
   - **只憑日期不算相符**：同一天也可能改過版本。
   - 找不到任何素材紀錄（例如很舊的頁），或無法分辨是否一致時：列出這頁圖片與文字最近一次被修改的提交（`git log -1 --format="%h %ad" --date=iso -- <實際圖片路徑>`），請藥師確認他看的是不是這個版本；確認後才登記。
4. **確認沒有未提交的修改**：`git status --short` 中，這頁的圖片或 `data/card_content.json` 不可有尚未提交、又不屬於本次的改動。

版本一致、也沒有未提交修改的頁，才列入本次登記。版本不一致、對不到 evidence，或無法判斷的頁，**不登記**，回報藥師：「這頁目前版本與複核版本無法確認相同，需要重新複核或提供版本資料」。**一頁都不符合就停止，不建立 CR。**

### 3. 登記 CR
先查有沒有已涵蓋本次工作、尚未完成的 CR：`git grep -n "<系列ID>" docs/project-management/change-requests.csv`。有就沿用；沒有才在末尾新增一列，編號接續最後一筆：`request_type` 填 `修改既有圖卡`，名稱寫「登記藥師複核：<系列或頁>」，`related_ids` 只列第 2 步確認相符的頁與其系列；`status` 填 `in_progress`、`approval` 填 `approved`；`git_commit` 填 `same_commit`；`completed_at`、`validation_result` 先填 `unknown`；`evidence` 填第 4 步的 evidence 檔路徑。

### 4. 建立 evidence 檔
在 `docs/project-management/evidence/` 建立一份（檔名 `<CR編號>-review-<系列ID>.md`），10 行以內：確認相符的頁（以及排除的頁與原因）、複核者、日期、複核依據與版本，以及藥師的原話（如「已複核通過」）。

### 5. 更新逐頁文字（只改第 2 步確認相符的頁）
在 `data/card_content.json` 用搜尋找到每一頁的紀錄：
- `needsMedicalReview` 改為 `false`。
- 藥師要在頁面顯示審閱狀態時，才加上 `"reviewStatus": "藥師提供的文字"`。選擇不顯示（或沒提到）時，該頁若已有舊的 `reviewStatus`，一併移除。
  - 頁面只有在 `updatedAt` 和 `revisionCredit` 都有值時才會顯示這一行；該頁若設了 `"showEditorialDetails": false`，`reviewStatus` 也不會顯示。遇到這兩種情況，先回報藥師，不要自行改其他欄位。
- 其他欄位（文字、日期、來源）一律不動。複核不等於內容更新，`updatedAt` 不改。

### 6. 標記 CR 完成（必須在建置前）
`status` 改為 `completed`，`completed_at` 填今天，`validation_result` 先填「建置與檢查進行中」（不可留 `unknown`，否則管理檢查會報錯；檢查步驟會改成實際結果）。

之後的建置或檢查失敗、本次無法完成時，把 `status` 改回 `in_progress`、`completed_at` 改回 `unknown`，並在 `validation_result` 寫明失敗原因。然後**停下來回報**，不要自行重新建置或還原檔案（完整建置會刪掉並重產整個 `cards/`，可能毀掉不屬於本次的工作）。回報時說明：失敗在哪一步、已產生哪些檔案（`git status --short`），以及首頁「最近新增」（`data/recent-changes.json`）是否已出現這筆 CR。由藥師決定修好後繼續，或用 git 還原本次變更。

### 7. 建置
```powershell
python -B build.py --incremental <複核頁ID> ...
```
增量建置被拒絕時，停下回報原因。

### 8. 更新清冊的人工欄位
先取得最新的機械欄位：
```powershell
python -B scripts/check_project_management.py --propose --page <複核頁ID>
```
把提案的機械欄位依 `page_id` 合併進 `docs/project-management/page-inventory.csv`，再填這幾個人工欄位：

| 欄位 | 填法 |
|---|---|
| `medical_review_status` | `pharmacist_reviewed` |
| `medical_review_evidence` | 第 4 步的 evidence 檔路徑 |
| `reviewer` | 藥師提供的名稱 |
| `review_date` | 複核日期 |
| `reviewed_content_sha256` | 合併後該列的 `content_sha256`（代表複核的是這個版本的內容） |
| `review_required` | `no` |
| `last_human_confirmed_at` | 複核日期 |

其他人工欄位不動。

### 9. 檢查

**清冊要涵蓋的頁**：不只本次直接修改的頁。建置後用 `git status --short cards/` 列出所有 HTML 有變動的頁，再加上「系列設定（`steps`、標題、`showFooter`、`favorite_keys`、`related_series`、`tool_link` 等）有改動的系列」的**每一頁**；這些頁的機械欄位都會跟著變。以下 `<受影響頁ID>` 指的就是這整份清單。

```powershell
python -B scripts/check_project_management.py --propose --page <受影響頁ID> ...
python -c "import json;[json.load(open(f,encoding='utf-8')) for f in ('cards.json','cards.manual.json','data/card_content.json')];print('JSON OK')"
python -B scripts/check_site.py
python -B scripts/project_change_tracker.py --check --page <本次任一頁ID>
python -B scripts/check_project_management.py --summary --baseline-file <基準檔> --report-file outputs/mgmt-after.json | Select-String "Baseline difference"
```
- JSON 都要能解析，`check_site.py` 必須通過，`--propose` 必須零差異。
- 基準比對：`new` 與 `worsened` 都必須是 0；有複核相關的錯誤時，打開 `outputs/mgmt-after.json` 找出原因並回報，不要為了通過而改人工欄位。
- 變更追蹤：結果不可有「目前未提交網站變更：缺少管理連結」。
- 開啟複核的頁面，確認「審閱狀態」有或沒有顯示，符合藥師的選擇。
- 用 `git diff --stat` 確認只改到本次相關的檔案。

**執行順序**：
1. 先用 `--propose`（涵蓋上述全部受影響頁）把機械欄位合併進 `page-inventory.csv`，再跑一次 `--propose` 確認零差異。既有頁只合併機械欄位，人工欄位不動（本作業卡明確要求修改的人工欄位除外）；新頁的人工欄位照作業卡 1 第 8 步的表格填。
2. 再執行其餘檢查（JSON、`check_site.py`、變更追蹤、頁面確認），把結果寫入 CR 的 `validation_result` 和 evidence 檔。
3. 最後才執行基準比對，並在 `validation_result` 補上「基準比對 new=0、worsened=0」。

### 10. 回報（不要 commit 或 push）
登記了哪些頁、複核者與日期、頁面是否顯示審閱狀態、檢查結果、要提交的檔案清單。
