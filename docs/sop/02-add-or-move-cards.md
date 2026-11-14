# 作業卡 2：新增或移動圖卡（既有系列）

適用：在已上線的系列**插入新卡**、**調整順序**、**把卡搬到另一個系列**、**讓一張卡同時出現在兩個系列**、**把共用卡從其中一個系列移除（卡仍留在其他系列）**，或**拆分、合併系列**。只讀這一份；同時還有其他調整時，再讀對應的作業卡。

網站作業從「素材已定稿」開始，**不查核、不改寫醫療內容**。缺素材就停下來問藥師。

## 素材

| 情況 | 需要 |
|---|---|
| 插入新卡 | 新圖 PNG、逐頁文字（同作業卡 1 第 0 步），以及插在哪個系列的第幾張之後 |
| 調整順序 | 系列的新順序 |
| 搬移或共用 | 哪張卡、從哪個系列、到哪個系列的第幾張；搬移（原系列移除）或共用（兩邊都保留） |
| 拆分或合併系列 | 新系列的系列資訊（同作業卡 1 第 0 步的「系列資訊」）、要放進哪些現有的卡與順序；原系列保留或移除 |

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
`request_type`：**插入新卡**填 `系列追加圖卡`；調整順序、搬移、共用、拆分、合併都沒有新增圖卡，填 `修改既有圖卡`（拆分或合併出來的新系列也不要填 `新增系列`，否則會被當成新內容出現在首頁「最近新增」）；`related_ids`：**插入新卡**時只列該系列與**新卡**的頁（其他順序有變的舊頁不要列，否則首頁「最近新增」和清冊會把它們算成新卡）；其他情況列出所有受影響的系列與頁（`series:<ID>|page:<ID>|…`）；`status` 填 `in_progress`、`approval` 填 `approved`；`git_commit` 填 `same_commit`（本次變更會和 CR 一起提交；先填好，變更追蹤檢查才會通過）；`completed_at`、`validation_result` 先填 `unknown`；`evidence` 填下面建立的 evidence 檔路徑。

同時建立 evidence 檔 `docs/project-management/evidence/<CR編號>-<系列ID>.md`（沿用既有 CR 時，更新該 CR 原本的 evidence 檔，不另建），10 行以內：本次範圍、素材來源（有新素材時：圖片檔名、對應文字的版本或日期、藥師定稿確認）。檢查完成後再補上結果。其餘欄位照前一筆同類 CR 的寫法。

### 3. 插入新卡時：處理新卡素材
- 圖片轉檔加 Logo、寫入 `data/card_content.json`：做法同作業卡 1 第 3、5 步，包括命名前的重複檢查，以及第 5 步下方 `updatedAt`／`revisionCredit`／`matchConfidence` 的規定。
- 在 `content-relations.csv` 為新頁加 `has_card` 關聯：格式同作業卡 1 第 8 步。

### 4. 修改 steps（cards.json 與 cards.manual.json 同步）
- **插入**：把新圖放到指定位置。
- **調整順序**：照新順序重排。
- **搬移**：從原系列 `steps` 移除，加入目標系列。頁 ID、網址、文字都不變。
- **共用**：原系列不動，在目標系列加入同一個圖片路徑。不要複製圖檔或文字。
  - **共用的限制**：同一張圖只會產生一個頁面，頁面上的翻頁、「第幾張／共幾張」和收藏按鈕，都以 cards.json 中**排在前面的系列**（主要系列）為準。民眾從另一個系列點進來，翻頁會跳到主要系列的其他卡。只在內容完全相同、可以接受這個限制時使用；回報時寫明主要系列是哪一個。
- **從其中一個系列移除共用卡**：卡仍留在其他系列，**不走淘汰流程**（不登記 `cards.retired.json`）。先依**移除前**的順序固定該系列的收藏編號（沒有 `favorite_keys` 就照預設 `<系列ID>-0, -1, …` 建立），再把這張卡從 `steps` 和 `favorite_keys` **同時**移除。這樣後面的卡仍保留原編號，舊收藏不會開到別張卡；其他系列不用改。

### 4-1. 拆分或合併時：建立新系列
- 在兩份 cards JSON 新增系列設定，欄位同作業卡 1 第 4 步；`steps` 填入搬過來的現有圖片路徑。
- 不需要轉檔、不新增 card_content 紀錄：頁面、網址、文字都沿用。
- 原系列被搬空時，從兩份 cards JSON 移除整個系列，並在 `docs/project-management/removed-series.json` 的 `series` 清單加一筆：`{"id": "<系列ID>", "title": "<系列標題>", "removed_at": "YYYY-MM-DD", "reason": "<原因>", "request_id": "<本次 CR>"}`。這樣過去引用這個系列的 CR 仍然有效，管理檢查不會報「missing related target」。系列沒有自己的頁面，不需要走淘汰流程；但要搜尋 `related_series` 有沒有指向它，有的話改指向新系列。
- 新系列在 `docs/project-management/content-relations.csv` 的 `has_card` 關聯照第 6 步處理。

### 4-2. 開啟共用頁尾
本次有變動的系列（插入新卡的系列、搬入卡片的目標系列、拆分或合併出來的新系列），在兩份 cards JSON 若還沒有 `"showFooter": true` 就加上。只開本次有變動的系列，不要動其他系列。

### 5. 保護收藏編號

網站用 `favorite_keys` 記住民眾收藏了哪張卡。系列沒有 `favorite_keys` 時，預設編號是「系列ID-順序」，例如 `demo-2`。**原則：一個編號只要曾經給過某張卡，就不能再給另一張卡**，否則舊收藏會打開別的衛教卡（例如淘汰了第 3 張，日後又在第 3 個位置加新卡，`demo-2` 就會指到新卡）。

**任何一張卡新加入既有系列**（插在尾端或中間的新卡，以及共用卡加入的目標系列；搬入的卡不算，見下方）：
1. 系列還沒有 `favorite_keys` 就先建立：照目前順序填預設編號 `["<系列ID>-0", "<系列ID>-1", …]`，舊卡編號不變。
2. 新卡的編號用 `"<系列ID>-<新卡頁ID>"`，例如 `"insomnia_public-insomnia_card10"`。頁 ID 永不重複使用，所以這個編號不會跟過去任何卡撞到。
3. 清單長度必須等於 `steps`，否則建置會拒絕。

```
原本 steps：[A, B, C]，沒有 favorite_keys（預設 x-0, x-1, x-2）
在 A 後插入 N：steps [A, N, B, C]
favorite_keys：["x-0", "x-N頁ID", "x-1", "x-2"]
```

**調整順序、搬移、拆分、合併、從其中一個系列移除共用卡**：舊卡一律**沿用原本的編號**，跟著卡走，即使編號前綴是舊系列名稱也沒關係（例如傷口系列拆分時，疤痕系列的卡仍使用 `fall_wound-2`）。原系列和目標系列都要處理。

所有系列的編號合起來不可重複。

### 6. 搬移或共用時：更新關聯
在 `content-relations.csv`：
- 共用：新增 `series:<目標系列>,has_card,page:<頁ID>`。
- 從其中一個系列移除共用卡：刪除該系列那一列，其他系列的列保留。
- 搬移：同上新增，並刪除原系列那一列。

關聯 ID 算法同作業卡 1 第 8 步。

### 7. 標記 CR 完成（必須在建置前）
`status` 改為 `completed`，`completed_at` 填今天，`validation_result` 先填「建置與檢查進行中」（不可留 `unknown`，否則管理檢查會報錯；檢查步驟會改成實際結果）。

之後的建置或檢查失敗、本次無法完成時，把 `status` 改回 `in_progress`、`completed_at` 改回 `unknown`，並在 `validation_result` 寫明失敗原因。然後**停下來回報**，不要自行重新建置或還原檔案（完整建置會刪掉並重產整個 `cards/`，可能毀掉不屬於本次的工作）。回報時說明：失敗在哪一步、已產生哪些檔案（`git status --short`），以及首頁「最近新增」（`data/recent-changes.json`）是否已出現這筆 CR。由藥師決定修好後繼續，或用 git 還原本次變更。

### 8. 建置
完整建置前先執行 `git status --short cards/`：如果有**不屬於本次工作**的未提交 HTML，停下回報（完整建置會刪除 `cards/` 下所有 HTML 再重新產生，那些檔案會消失）。

- **只是插在系列最後面**：`python -B build.py --incremental <新頁ID>`
- **其他情況**（插在中間、調整順序、搬移、共用、從其中一個系列移除共用卡、拆分、合併）：`python -B build.py`（完整建置）

增量建置被拒絕時，停下回報原因。

### 8-1. 插入新卡時：更新清冊（建置後）
照作業卡 1 第 8 步第 1 項：用 `--propose` 取得新頁的機械欄位，新增到 `page-inventory.csv`，人工欄位照該處的表格填。

### 9. 檢查

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
- 基準比對：只看輸出的 `Baseline difference` 那一行，`new` 與 `worsened` 都必須是 0。原本就有的錯誤（`persistent`）不處理，也不必閱讀完整報告；不是 0 時才打開 `outputs/mgmt-after.json` 找出是哪幾筆。
- 變更追蹤：只需執行一次、填本次任一頁 ID。程式對「尚未提交的變更」本來就整體檢查；`--page` 只是排除與本次無關的舊提交紀錄。結果不可有「目前未提交網站變更：缺少管理連結」。
- 清冊的 `added_at`、`added_cr`、`last_updated_at`、`last_updated_cr` 由程式依 CR 推算，不要手填。
- 一般圖卡作業不執行 `scripts/test_*.py`。
- `--propose` 有差異時，只把機械欄位依 `page_id` 合併進 `page-inventory.csv`，舊頁人工欄位不動；合併後必須零差異。
- 開啟受影響系列的一頁，確認「第幾張／共幾張」和上一張、下一張正確。
- 用 `git diff --stat` 確認只改到本次相關的檔案。完整建置會重寫很多頁，只要差異都是張數、翻頁之類的連帶變化就正常；有不明的改動要列出來。

**執行順序**：
1. 先用 `--propose`（涵蓋上述全部受影響頁）把機械欄位合併進 `page-inventory.csv`，再跑一次 `--propose` 確認零差異。既有頁只合併機械欄位，人工欄位不動（本作業卡明確要求修改的人工欄位除外）；新頁的人工欄位照作業卡 1 第 8 步的表格填。
2. 再執行其餘檢查（JSON、`check_site.py`、變更追蹤、頁面確認），把結果寫入 CR 的 `validation_result` 和 evidence 檔。
3. 最後才執行基準比對，並在 `validation_result` 補上「基準比對 new=0、worsened=0」。

### 10. 回報（不要 commit 或 push）
做了什麼、受影響的系列與頁、收藏編號怎麼處理、檢查結果、要提交的檔案清單。
