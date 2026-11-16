# 作業卡 3：刪除圖卡（淘汰）

適用：讓一張圖卡**從全站下架**，或整個系列下架。先讀作業卡 0（共同步驟），再照本卡做。

**圖片路徑**：既有頁的圖片不一定是 `.webp`（網站有不少 `.png`）。先在 cards.json 該頁所屬系列的 `steps` 找到**實際圖片路徑**，以下所有寫 `img/<頁ID>.webp` 的地方（搜尋、仿單的鍵、淘汰紀錄、換圖）都改用這個實際路徑。

**先確認這張卡是否還在其他系列**：`git grep -n "<實際圖片路徑>" -- cards.json`。如果只是要從某個系列拿掉、其他系列仍保留，**不要用本卡**，改用作業卡 2 的「從其中一個系列移除共用卡」。

網站**不真的刪除頁面**，而是「淘汰」：舊網址保留，打開會看到退出日期與**淘汰原因**，並列入「退出圖卡紀錄」（`retired-cards.html`）；同時從搜尋引擎、首頁、索引中移除。這樣民眾的收藏和外部連結才不會變成錯誤頁。

## 素材

- 要淘汰的頁（或整個系列）
- 淘汰原因（必填，一兩句話；會顯示在舊網址頁面上給民眾看）
- 替代頁（選填）：現有的圖卡。藥師沒有指定就不填，不要自己挑一頁湊數。

## 步驟

### 1. 開工
照作業卡 0 第 1 步。

### 2. 登記 CR
照作業卡 0 第 2 步，本卡的欄位：`request_type` 填 `修改既有圖卡`；`related_ids` 列出系列與每一個淘汰的頁。

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
  "image": "<實際圖片路徑>",
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
git grep -n "<實際圖片路徑>" -- data/ cards.json cards.manual.json
git grep -n "<系列ID>" -- cards.json cards.manual.json
```
（第三行只在整個系列下架時需要。搜尋結果中，被淘汰頁**自己的**逐頁文字紀錄不用改。）
- `topics/` 主題頁、其他圖卡的 `related_links` 指向被淘汰的頁：有替代頁就改連過去，沒有就移除。
- `cards.retired.json` 裡**其他舊淘汰卡**的 `replacements` 指向本次淘汰的頁：藥師有指定新的替代頁就改過去；沒有就從該筆的 `replacements` 移除這一項，其他有效的替代頁保留（清單可以變成空的）。
- `data/label_links.json` 以被淘汰圖片為鍵的紀錄：保留不動（淘汰頁仍保留歷史）。
- 其他系列的 `related_series` 指向被下架的系列：移除。

改了哪些地方要列在回報裡。

### 7. 標記完成與建置
照作業卡 0 第 3 步。建置指令：`python -B build.py`（完整建置，先做作業卡 0 第 3 步的 `cards/` 檢查）。

### 8. 草稿（視藥師要求）
藥師要先看草稿：照作業卡 0 第 4 步（預覽網址開被淘汰的頁）；修改後用第 7 步的指令重新建置。淘汰不涉及複核。

### 9. 檢查
照作業卡 0 第 6 步。本卡的**頁面確認**：
- 開啟 `cards/<淘汰頁ID>.html`，確認顯示退出日期與原因；有替代頁時確認連結可以點開。
- 確認 `retired-cards.html` 有這一筆，`sitemap.xml` 和 `all-cards.html` 已經沒有它。

### 10. 回報
照作業卡 0 第 8 步，另外列出：淘汰了哪些頁、替代頁、改了哪些連結、收藏編號怎麼處理、檢查結果、要提交的檔案清單。
