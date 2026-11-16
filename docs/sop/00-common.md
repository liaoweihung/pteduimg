# 作業卡 0：共同步驟

作業卡 1～5、7 的共同流程。先讀本卡，再讀對應的作業卡；作業卡寫「照作業卡 0 第 N 步」時就照本卡做，作業卡另有規定時以作業卡為準。

> 指令以 PowerShell 為例。用 bash 執行時：`> $null` 改成 `> /dev/null`，`| Select-String "…"` 改成 `| grep "…"`。

**流程總覽**：確認工作區並同步遠端（第 0 步）→ 開工存基準（第 1 步）→ 登記 CR（第 2 步）→ 依作業卡修改資料 → 標記完成並建置（第 3 步）→（藥師要先看時）草稿預覽（第 4 步）→（藥師複核時）登記複核（第 5 步）→ 檢查（第 6 步）→ 回報（第 8 步）。失敗或續作照第 7 步。

## 0. 開工：確認工作區並同步遠端

先執行 `git status --short`，既有改動不碰、不提交。

- **開新任務**：若有已追蹤檔案的未提交改動（包括已暫存的改動），停下回報，不要 pull，也不要開始新任務。未追蹤的 `Claude outputs/` 不屬於這項停工條件。確認後執行 `git pull --ff-only`；失敗就停下回報，不要開始新任務。
- **續作同一筆 CR**：不要 pull。執行 `git fetch`，再用 `git rev-list --count 'HEAD..@{upstream}'` 檢查遠端追蹤分支；結果大於 0，表示遠端有新 commit，停下回報。`git fetch` 或差異檢查失敗時也停下回報。

## 1. 開工：確認工作區並存下檢查基準

```powershell
git status --short
python -c "import os;os.makedirs('outputs',exist_ok=True)"
python -B scripts/check_project_management.py --summary --report-file <基準檔> > $null
python -c "import json;json.load(open('<基準檔>',encoding='utf-8'));print('BASELINE OK')"
```

- **基準檔**：用這次開工的日期時間命名，例如 `outputs/mgmt-before-20261116-1240.json`，**不可是已存在的檔名**，並記在本次的 evidence 檔。
- 第三行會因為網站原有的管理錯誤回報失敗，這是正常的，不要重試；但最後一行必須印出 `BASELINE OK`，沒有就停下來回報，不要開始修改。
- `git status` 列出的既有改動，本次不碰、不提交。
- **續作同一筆 CR**：跳過本步，沿用 evidence 記錄的原始基準檔（見第 7 步）。

## 2. 登記 CR 與 evidence

先查有沒有已涵蓋本次工作、尚未完成的 CR：`git grep -n "<系列ID>" docs/project-management/change-requests.csv`。有就沿用並補上受影響的 ID；沒有才在末尾新增一列，編號接續最後一筆。

| 欄位 | 填法 |
|---|---|
| request_id | `CR-YYYY-NNN`（接續編號） |
| proposed_at | 今天 |
| name／description | 一句話說明做什麼 |
| request_type、scope、related_ids | 照作業卡規定（`related_ids` 格式：`series:<ID>\|page:<ID>\|…`） |
| priority／status／approval | 照前一筆同類 CR／`in_progress`／`approved` |
| needs_pharmacist／author_permission／commercial_disclosure | `yes`／`unknown`／`unknown`（藥師確認沒有商業關係才填 `no`） |
| completed_at／validation_result | `unknown`（第 3、6 步再填） |
| git_commit | `same_commit`（本次變更會和 CR 一起提交；先填好，變更追蹤檢查才會通過） |
| evidence | `docs/project-management/evidence/<CR編號>-<系列ID>.md` |

同時建立 evidence 檔（沿用既有 CR 時更新原本那份，不另建），10 行以內：範圍、基準檔名、素材來源（有新素材時：圖片檔名、對應文字的版本或日期、藥師定稿確認）。檢查完成後補上結果。

## 3. 標記完成並建置

1. **標記 CR 完成（第一次建置前做，整個工作只做一次）**：`status` 改為 `completed`，`completed_at` 填今天，`validation_result` 填「建置與檢查進行中」（不可留 `unknown`）。順序不可顛倒：增量建置只在資料有變時才更新首頁「最近新增」，建置後才標記完成，就會漏掉本次；清冊推算也會算錯。
2. **建置**：用作業卡指定的指令。
   - 完整建置（`python -B build.py`）前先執行 `git status --short cards/`：有不屬於本次工作的未提交 HTML 就停下回報（完整建置會刪除並重產整個 `cards/`）。
   - 增量建置被拒絕時，停下回報原因，不要自行改跑完整建置。
3. CR 標記完成、但檢查還沒做完時，`validation_result` 維持「建置與檢查進行中」，作業卡 6 會擋下發布。

## 4. 草稿預覽（藥師要求先看時才做）

藥師沒要求先看，就跳過本步。

1. 在 repo 根目錄開啟本機預覽，用固定指令，不要另外摸索：
   ```powershell
   Start-Process python -ArgumentList "-m","http.server","8765","--bind","127.0.0.1" -WorkingDirectory (Get-Location) -WindowStyle Hidden
   Start-Process "http://127.0.0.1:8765/cards/<頁ID>.html"
   ```
   之前已開過預覽（8765 已被占用）時，只執行第二行。
2. 停下來回報：預覽網址、改了什麼，並提醒藥師「確認定稿時如果也已複核，請一起說，可以在這筆 CR 一併登記」。等藥師回覆。
3. 藥師要修改：只改資料、用同一個建置指令重新建置，請藥師重新整理預覽，再停下來等回覆。**草稿階段不跑檢查**，也不重新標記 CR。
4. 藥師確認定稿後，進入第 5 步（藥師同時表示已複核時）或第 6 步。
5. 藥師決定不做了：照第 7 步的「失敗」處理，把 CR 改回 `in_progress` 並寫明原因，由藥師決定保留或用 git 還原。

## 5. 當場複核（藥師表示已複核時）

適用情況（都在**同一筆 CR** 登記，不另開 CR、不再跑作業卡 7）：
- 藥師看過**最後定稿的版本**（之後沒有再改）並表示已複核；或開工時就表示本次素材已複核。
- 藥師在第 6 步檢查完成後、**發布之前**才表示已複核：照本步修改，再重新建置、重跑第 6 步檢查。已經發布才複核的，改用作業卡 7。

表示複核之後又改了內容，要請藥師重新確認。

- **預設值**：複核者「藥局衛教助手製作者」、複核日期為今天、依據為「本 CR 的預覽版本」（素材已複核時寫素材的檔名與版本）。藥師沒有另外指定就照預設，**不再反問**。
- `data/card_content.json` 這些頁：`needsMedicalReview` 改為 `false`。藥師要求在頁面顯示審閱狀態時，才加 `"reviewStatus": "藥師提供的文字"`；沒提到就不顯示，已有的舊 `reviewStatus` 一併移除。其他欄位不動。改完用作業卡的建置指令重新建置。
- 頁面原本已登記複核、作業卡已先改成待複核時：照本步改回已複核即可；`history_note` 保留舊複核的那一句（沒寫過就補「YYYY-MM-DD 前的版本曾由（複核者）於（日期）複核」）。
- 頁面沒有逐頁文字紀錄（`data/card_content.json` 找不到）時無法登記，回報藥師。
- 清冊的複核欄位在第 6 步清冊合併**之後**填（見下表）。新頁先照作業卡 1 的新頁人工欄位填，再用下表的值覆蓋。
- evidence 加一行：複核的頁、複核者、日期、依據，以及藥師的原話。

| 清冊欄位 | 填法 |
|---|---|
| `medical_review_status` | `pharmacist_reviewed` |
| `medical_review_evidence` | 本 CR 的 evidence 檔路徑 |
| `reviewer` | 複核者 |
| `review_date` | 複核日期 |
| `reviewed_content_sha256` | 合併機械欄位後，該列的 `content_sha256` |
| `review_required` | `no` |
| `last_human_confirmed_at` | 複核日期 |

## 6. 檢查（每筆 CR 只在定稿後跑一次）

先做作業卡的**建置後管理紀錄**（作業卡有寫才做，例如新頁的清冊列與關聯）。

**清冊要涵蓋的頁（`<受影響頁ID>`）**：本次直接修改的頁（包括 HTML 沒變的，例如只登記複核），加上建置後 `git status --short cards/` 列出的所有 HTML 有變動的頁，再加上「系列設定（`steps`、標題、`showFooter`、`favorite_keys`、`related_series`、`tool_link` 等）有改動的系列」的每一頁。

依序執行：

1. **清冊合併**：
   ```powershell
   python -B scripts/check_project_management.py --propose --page <受影響頁ID> ...
   ```
   有差異時，只把機械欄位依 `page_id` 合併進 `page-inventory.csv`，人工欄位不動（作業卡或第 5 步要求修改的除外）；不要用提案整份覆蓋。`added_at`、`added_cr`、`last_updated_at`、`last_updated_cr` 由程式依 CR 推算，不要手填。有第 5 步的複核時，此時填複核欄位。再跑一次 `--propose`，必須零差異。
2. **其餘檢查**：
   ```powershell
   python -c "import json;[json.load(open(f,encoding='utf-8')) for f in ('cards.json','cards.manual.json','data/card_content.json')];print('JSON OK')"
   python -B scripts/check_site.py
   python -B scripts/project_change_tracker.py --check --page <本次任一頁ID>
   git diff --stat
   ```
   - JSON 都要能解析，`check_site.py` 必須通過。
   - 變更追蹤只跑一次、填任一頁 ID 即可；結果不可有「目前未提交網站變更：缺少管理連結」。
   - `git diff --stat` 只能有本次相關的檔案，有不明的改動要列出來。
   - 再做作業卡列出的**頁面確認**。
   - 把結果寫入 CR 的 `validation_result` 和 evidence 檔。
3. **最後才做基準比對**：
   ```powershell
   python -B scripts/check_project_management.py --summary --baseline-file <基準檔> --report-file outputs/mgmt-after.json | Select-String "Baseline difference"
   ```
   這個指令也會回報失敗，屬正常；只看 `Baseline difference` 那一行，`new` 與 `worsened` 都必須是 0。不是 0 時才打開 `outputs/mgmt-after.json` 找出是哪幾筆。通過後在 `validation_result` 補上「基準比對 new=0、worsened=0」。

一般圖卡作業不執行 `scripts/test_*.py`。

## 7. 失敗與續作

**失敗**：建置或檢查失敗、本次無法完成時，把 CR 的 `status` 改回 `in_progress`、`completed_at` 改回 `unknown`，在 `validation_result` 寫明失敗原因，然後**停下來回報**：失敗在哪一步、已產生哪些檔案（`git status --short`），以及首頁「最近新增」（`data/recent-changes.json`）是否已出現這筆 CR。不要自行重新建置或還原檔案，由藥師決定修好後繼續，或用 git 還原。

**續作同一筆 CR**：
1. 不重新存基準，沿用 evidence 記錄的原始基準檔（否則上次引入的錯誤會被當成原本就有）；原始基準檔遺失時停下回報。
2. CR 已改回 `in_progress` 時，**先重新標記完成（第 3 步第 1 項）**，再從失敗的那一步接著做。CR 停在 `in_progress` 時跑清冊合併，算出的 `last_updated_cr` 會是舊 CR，基準比對就會出現新錯誤。
3. 建置已成功、之後也沒改資料，就不必重新建置。

## 8. 回報（不要 commit 或 push）

作業卡列出的回報項目、檢查結果、要提交的檔案清單。有當場複核時寫明複核的頁與複核者。最後提醒藥師：發布照作業卡 6；下一件工作建議開新對話。
