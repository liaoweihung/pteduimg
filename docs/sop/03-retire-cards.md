# 作業卡 3：刪除圖卡（淘汰）

適用：讓一張圖卡**從全站下架**，或整個系列下架。只讀這一份。

**先確認這張卡是否還在其他系列**：`git grep -n "img/<頁ID>.webp" -- cards.json`。如果只是要從某個系列拿掉、其他系列仍保留，**不要用本卡**，改用作業卡 2 的「從其中一個系列移除共用卡」。

網站**不真的刪除頁面**，而是「淘汰」：舊網址保留，打開會看到退出日期與**淘汰原因**，並列入「退出圖卡紀錄」（`retired-cards.html`）；同時從搜尋引擎、首頁、索引中移除。這樣民眾的收藏和外部連結才不會變成錯誤頁。

## 素材

- 要淘汰的頁（或整個系列）
- 淘汰原因（必填，一兩句話；會顯示在舊網址頁面上給民眾看）
- 替代頁（選填）：現有的圖卡。藥師沒有指定就不填，不要自己挑一頁湊數。

## 步驟

### 1. 確認工作區並存下檢查基準
> 指令以 PowerShell 為例。用 bash 執行時：`> $null` 改成 `> /dev/null`，`| Select-String "…"` 改成 `| grep "…"`。
```powershell
git status --short
python -c "import os;os.makedirs('outputs',exist_ok=True);p='outputs/mgmt-before.json';os.path.exists(p) and os.remove(p)"
python -B scripts/check_project_management.py --summary --report-file outputs/mgmt-before.json > $null
python -c "import json;json.load(open('outputs/mgmt-before.json',encoding='utf-8'));print('BASELINE OK')"
```
記下已存在的改動，本次不碰。存基準的指令會因為網站原有的管理錯誤回報失敗，這是正常的；但最後一行必須印出 `BASELINE OK`，沒有就代表基準沒存到，停下來回報，不要開始修改。這份基準是「改之前」的狀態，檢查時用來比對。

### 2. 登記 CR
先查有沒有已涵蓋本次工作、尚未完成的 CR：`git grep -n "<系列ID>" docs/project-management/change-requests.csv`。有就沿用並補上受影響的 ID；沒有才在 `docs/project-management/change-requests.csv` 末尾新增一列，編號接續最後一筆：
`request_type` 填 `修改既有圖卡`；`related_ids` 列出系列與每一個淘汰的頁；`status` 填 `in_progress`、`approval` 填 `approved`；`git_commit` 填 `same_commit`（本次變更會和 CR 一起提交；先填好，變更追蹤檢查才會通過）；`completed_at`、`validation_result` 先填 `unknown`；`evidence` 填下面建立的 evidence 檔路徑。

同時建立 evidence 檔 `docs/project-management/evidence/<CR編號>-<系列ID>.md`（沿用既有 CR 時，更新該 CR 原本的 evidence 檔，不另建），10 行以內：本次範圍、素材來源（有新素材時：圖片檔名、對應文字的版本或日期、藥師定稿確認）。檢查完成後再補上結果。其餘欄位照前一筆同類 CR 的寫法。

### 3. 從系列移除
- **淘汰單張**：從 cards.json 與 cards.manual.json **所有**含這張圖的系列 `steps` 移除。
- **整個系列下架**：從兩份 cards JSON 刪除整個系列，並在 `docs/project-management/removed-series.json` 的 `series` 清單加一筆：`{"id": "<系列ID>", "title": "<系列標題>", "removed_at": "YYYY-MM-DD", "reason": "<原因>", "request_id": "<本次 CR>"}`。這樣過去引用這個系列的 CR 仍然有效，管理檢查不會報「missing related target」。
- 圖檔和 `data/card_content.json` 的紀錄都**保留，不要刪除**。

### 4. 保護收藏編號（淘汰單張時）
每個含這張圖的系列都要處理。系列中剩下的卡要保留原本的收藏編號，否則民眾收藏的會變成另一張卡。在該系列設定 `favorite_keys`，跟 `steps` 一一對應：

```
原本 steps：[A, B, C]，編號 [x-0, x-1, x-2]
淘汰 B：steps [A, C]
favorite_keys：["x-0", "x-2"]
```

系列已經有 `favorite_keys` 時，刪掉被淘汰那張的編號即可（清單長度必須等於 `steps`）。淘汰的是系列最後一張、且系列沒有 `favorite_keys` 時，不用處理：日後在這個系列加新卡時，作業卡 2 規定新卡用「系列ID-頁ID」當編號，不會重用被淘汰卡的編號。

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

### 6. 清理關聯表與指向它的連結

**關聯表**：在 `docs/project-management/content-relations.csv` 刪除所有 `source_id` 或 `target_id` 是 `page:<頁ID>` 的列；整個系列下架時，也刪除 `series:<系列ID>` 的列。不刪的話，管理檢查會出現「relation targets retired card」等新錯誤。

**其他連結**：分三種搜尋，兩份 cards JSON 都要搜：
```powershell
git grep -n "<頁ID>.html" -- topics/ data/ cards.json cards.manual.json cards.retired.json
git grep -n "img/<頁ID>.webp" -- data/ cards.json cards.manual.json
git grep -n "<系列ID>" -- cards.json cards.manual.json
```
（第三行只在整個系列下架時需要。搜尋結果中，被淘汰頁**自己的**逐頁文字紀錄不用改。）
- `topics/` 主題頁、其他圖卡的 `related_links` 指向被淘汰的頁：有替代頁就改連過去，沒有就移除。
- `cards.retired.json` 裡**其他舊淘汰卡**的 `replacements` 指向本次淘汰的頁：藥師有指定新的替代頁就改過去；沒有就從該筆的 `replacements` 移除這一項，其他有效的替代頁保留（清單可以變成空的）。
- `data/label_links.json` 以被淘汰圖片為鍵的紀錄：保留不動（淘汰頁仍保留歷史）。
- 其他系列的 `related_series` 指向被下架的系列：移除。

改了哪些地方要列在回報裡。

### 7. 標記 CR 完成（必須在建置前）
`status` 改為 `completed`，`completed_at` 填今天，`validation_result` 先填「建置與檢查進行中」（不可留 `unknown`，否則管理檢查會報錯；檢查步驟會改成實際結果）。

之後的建置或檢查失敗、本次無法完成時，把 `status` 改回 `in_progress`、`completed_at` 改回 `unknown`，並在 `validation_result` 寫明失敗原因。然後**停下來回報**，不要自行重新建置或還原檔案（完整建置會刪掉並重產整個 `cards/`，可能毀掉不屬於本次的工作）。回報時說明：失敗在哪一步、已產生哪些檔案（`git status --short`），以及首頁「最近新增」（`data/recent-changes.json`）是否已出現這筆 CR。由藥師決定修好後繼續，或用 git 還原本次變更。

### 8. 完整建置
完整建置前先執行 `git status --short cards/`：如果有**不屬於本次工作**的未提交 HTML，停下回報（完整建置會刪除 `cards/` 下所有 HTML 再重新產生，那些檔案會消失）。

```powershell
python -B build.py
```

### 9. 檢查

**清冊要涵蓋的頁**：不只本次直接修改的頁。建置後用 `git status --short cards/` 列出所有 HTML 有變動的頁，再加上「系列設定（`steps`、標題、`showFooter`、`favorite_keys`、`related_series`、`tool_link` 等）有改動的系列」的**每一頁**；這些頁的機械欄位都會跟著變。以下 `<受影響頁ID>` 指的就是這整份清單。

```powershell
python -B scripts/check_project_management.py --propose --page <受影響頁ID> ...
python -c "import json;[json.load(open(f,encoding='utf-8')) for f in ('cards.json','cards.manual.json','data/card_content.json')];print('JSON OK')"
python -B scripts/check_site.py
python -B scripts/project_change_tracker.py --check --page <本次任一頁ID>
python -B scripts/check_project_management.py --summary --baseline-file outputs/mgmt-before.json --report-file outputs/mgmt-after.json | Select-String "Baseline difference"
```
- `check_site.py` 必須通過。
- 三份 JSON 都要能解析。
- 基準比對：只看輸出的 `Baseline difference` 那一行，`new` 與 `worsened` 都必須是 0。原本就有的錯誤（`persistent`）不處理，也不必閱讀完整報告；不是 0 時才打開 `outputs/mgmt-after.json` 找出是哪幾筆。
- 變更追蹤：只需執行一次、填本次任一頁 ID。程式對「尚未提交的變更」本來就整體檢查；`--page` 只是排除與本次無關的舊提交紀錄。結果不可有「目前未提交網站變更：缺少管理連結」。
- 清冊的 `added_at`、`added_cr`、`last_updated_at`、`last_updated_cr` 由程式依 CR 推算，不要手填。
- 一般圖卡作業不執行 `scripts/test_*.py`。
- `--propose` 有差異時，只把機械欄位依 `page_id` 合併進 `page-inventory.csv`，人工欄位不動；合併後必須零差異。
- 開啟 `cards/<淘汰頁ID>.html`，確認顯示退出日期與原因；有替代頁時確認連結可以點開。
- 確認 `retired-cards.html` 有這一筆，`sitemap.xml` 和 `all-cards.html` 已經沒有它。
- 用 `git diff --stat` 確認只改到本次相關的檔案，有不明的改動要列出來。

**執行順序**：
1. 先用 `--propose`（涵蓋上述全部受影響頁）把機械欄位合併進 `page-inventory.csv`，再跑一次 `--propose` 確認零差異。既有頁只合併機械欄位，人工欄位不動（本作業卡明確要求修改的人工欄位除外）；新頁的人工欄位照作業卡 1 第 8 步的表格填。
2. 再執行其餘檢查（JSON、`check_site.py`、變更追蹤、頁面確認），把結果寫入 CR 的 `validation_result` 和 evidence 檔。
3. 最後才執行基準比對，並在 `validation_result` 補上「基準比對 new=0、worsened=0」。

### 10. 回報（不要 commit 或 push）
淘汰了哪些頁、替代頁、改了哪些連結、收藏編號怎麼處理、檢查結果、要提交的檔案清單。
