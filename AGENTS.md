# pteduimg AI 專案指令

本 repository 是藥局衛教圖卡的靜態 GitHub Pages 網站。**只讀本檔和對應的作業卡，照步驟做。**其他文件是參考資料，作業卡沒寫到的狀況才查。

## 工作分派

| 工作 | 讀這張作業卡 |
|---|---|
| 新增圖卡系列（就算只有一張） | [docs/sop/01-new-series.md](docs/sop/01-new-series.md) |
| 既有系列插入新卡、調整順序、搬移、共用、拆分或合併系列 | [docs/sop/02-add-or-move-cards.md](docs/sop/02-add-or-move-cards.md) |
| 刪除圖卡、整個系列下架 | [docs/sop/03-retire-cards.md](docs/sop/03-retire-cards.md) |
| 修改圖卡頁面（換圖、改文字、仿單、推薦閱讀） | [docs/sop/04-edit-card-page.md](docs/sop/04-edit-card-page.md) |
| 修改系列設定（標題、icon、標籤、分類、排序、工具按鈕、隱藏） | [docs/sop/05-series-settings.md](docs/sop/05-series-settings.md) |
| commit、push | [docs/sop/06-publish.md](docs/sop/06-publish.md) |
| 登記藥師複核（藥師提供複核結果後） | [docs/sop/07-record-review.md](docs/sop/07-record-review.md) |
| 撰寫或查核圖卡文字（素材階段，不改網站） | [docs/material/README.md](docs/material/README.md) 的 A 節 |
| 製作圖卡圖片（素材階段，不改網站） | [docs/material/README.md](docs/material/README.md) 的 B 節 |

同時有多種工作時，讀對應的每一張。**不在上表的圖卡工作**（例如批次修正多張卡的同一欄位），先說明打算怎麼做、會改哪些檔案，經藥師同意再做。

**不在流程中**：計算器、主題頁（`topics/`）、查詢工具等圖卡以外的頁面，可以自由進行，不需登記 CR，但仍須遵守下方的「共同底線」第 3～7 條。

## 共同底線

1. **素材與網站分開**：圖片與文字由藥師在網站外定稿。網站作業不查核、不改寫醫療內容，也不自行找來源。缺素材就停下來問，不補寫、不猜測，不捏造日期、來源、作者或審閱者。
2. **醫療狀態不得假冒**：新內容的 `needsMedicalReview` 一律為 `true`；沒有藥師具名的複核紀錄，不得標記為已複核。技術檢查通過不等於醫療簽核。
3. **改程式和規則要先經同意**：
   - 程式：`build.py`、`scripts/`、`templates/`、共用樣式（`css/base.css` 等）、`sw.js` 的快取邏輯、`index.html`、`public.html` 的程式部分。建置時由 `build.py` 自動更新的 `sw.js` 屬正常產物，不需另外同意。
   - 規則：本檔、各 AI 入口檔（`CLAUDE.md`、`GEMINI.md`、`.github/copilot-instructions.md`）、`docs/sop/`、`docs/material/`。
   修改前必須先停下來，說明原因、要改的檔案與改法，經藥師同意才能動。即使是為了完成任務、或發現規則有誤，也不可自行修改，改為回報。
4. **新功能做成資料欄位**：新增頁面功能時，build.py 只能寫通用能力，不可用系列 ID 或頁面 ID 寫死特例；哪些系列或頁面要使用，一律以資料欄位指定（cards.json、cards.manual.json 或 `data/` 下的資料檔）。提案時須說明欄位名稱、放在哪個檔案、填寫範例。
5. **不擅自 commit／push**：藥師明確要求才做，並照作業卡 6。開工先執行 `git status --short`，已存在的其他改動不碰、不提交。
6. **網頁不直接改**：`cards/*.html`、`all-cards.html`、`seo.json`、sitemap 都由 `build.py` 依資料產生。要改內容就改資料，再重新建置；直接改網頁，下次建置就會被覆蓋。
7. **Logo 不可重畫**：只用 `docs/brand/assets/` 裡的正式 Logo 檔，不讓 AI 生成或重畫 Logo。

## 參考資料（平常不必讀）

- 建置細節：[docs/site-build-and-release.md](docs/site-build-and-release.md)
- 管理系統：[docs/project-management/README.md](docs/project-management/README.md)
- 分類代碼對照表：[docs/sop/card-data.md](docs/sop/card-data.md)
- 品牌：[docs/brand/README.md](docs/brand/README.md)
- 素材規範（文字定稿與製圖，素材階段用）：[docs/material/README.md](docs/material/README.md)
- 計算器：[docs/medical-calculator-guide-v1.md](docs/medical-calculator-guide-v1.md)
- 藥局工具與 Hub：[docs/pharmacy-tools-maintenance.md](docs/pharmacy-tools-maintenance.md)
- 青春痘主題頁（Pilot）：[docs/acne-pilot-spec.md](docs/acne-pilot-spec.md)
- 搜尋成效追蹤：[docs/project-management/search-tracking.md](docs/project-management/search-tracking.md)
