# MDI 吸入器系列網頁文字與 SEO（CR-2026-069）

日期：2026-11-04
範圍：`MDI` 系列 7 頁（`MDI_1`～`MDI_7`），圖片不換，不改其他系列。

## 授權與來源

- 使用者（藥師、網站作者）觀察 MDI_1 流量穩定、會被反覆觀看，要求分析與優化。Claude 審查七張圖卡後提出問題（卡3 文字誤植、卡6 未提第二口再搖、全系列未提漱口、卡4 張口法括號），使用者判定「圖卡上的錯誤都屬於可以接受的程度」，不重繪，只要網頁文字與 SEO／AEO。
- 文字草稿見 Claude 專案文件 `mdi-seo-text-2026-11-04.md`；使用者確認「改成 5～10 秒，其他維持現狀」，並要求由 Claude 直接執行上線。
- MDI_1 作為入口頁（QR code、書籤、搜尋都從第 1 張進入）：7 步驟、常見錯誤、使用前須知、回診／就醫時機、8 題常見問題（以 sections 呈現）。MDI_2～7 為該步驟短文字並指回第 1 張。

## 直接查核來源（2026-11-04 實際閱讀）

| 來源 | 支持內容 |
|---|---|
| 臺北市立聯合醫院 用藥指導單張：備喘全定量噴霧液（TPE201709，流水號 167） | 新瓶先下壓 2 次、搖勻、轉頭吐完氣、含住按壓一下慢慢深吸、閉氣 5～10 秒、第二口間隔 30～60 秒、不可連續按壓兩次 |
| 中國醫藥大學新竹附設醫院：吸必擴氣化噴霧劑（Symbicort Rapihaler）操作（115.07） | 搖 5 秒、不對吸嘴吐氣、嘴唇含緊、吸氣同時按壓一下、第二口休息 30 秒並再搖、漱口吐掉、超過 7 天未用或摔落重新試噴、計數器、每週乾布擦吸嘴、勿放入水中 |
| Asthma Society of Ireland：How to use a metered dose inhaler（2025） | 輕輕吐氣、含住按壓深吸、閉氣約 10 秒或盡量久、間隔 30～60 秒 |
| Minnesota Department of Health：How to Use a Metered-Dose Inhaler | 吸氣 3～5 秒、閉氣數到 10、吸入型類固醇漱口吐掉、需要時試噴 |

閉氣時間依使用者指示採 5～10 秒（與圖卡及北市聯醫單張一致）。試噴次數、清潔方式寫「依仿單」。不列商品名（未做許可證查核）。

## 變更

- `data/card_content.json`：新增 MDI_1～7 七筆紀錄（`updatedAt`／`sourceCheckedAt` 2026-11-04、`revisionCredit`、4 筆來源、`needsMedicalReview: true`、`matchConfidence: high`）。
- `seo.json`：移除 7 頁舊的 `display_title`，讓 H1 與 title 一致（整合報告要求 H1＝title）；title、description、alt 由內容紀錄產生。
- 生成輸出：`cards/MDI_1～7.html`、`all-cards.html`、`sitemap.xml`、`sitemap-main.xml`、`data/card_text_web_integration_report.md`、`sw.js`。
- 管理：`page-inventory.csv` 7 列機械欄位依 `--propose` 合併（人工欄位未改）；既有 `series:MDI -> page:MDI_n` 關聯已存在，未新增；新增 CR-2026-069。

## 建置方法

`build.py --incremental MDI_1..7` 回報 `Manual/legacy HTML conflict in cards/MDI_1.html`，未寫入任何輸出（舊頁為舊產生器版本）。改用隔離 worktree：HEAD 完整建置為基準 A，套用變更後完整建置為 B；A→B 僅本系列 7 頁與上述全域檔不同。全域檔以 A→B 的 patch 套回正式工作樹；7 頁直接採 B。`sw.js` 以 `scripts/incremental_build.worker_version` 依正式工作樹重算 CACHE_NAME。

## 驗證

- 整合報告：274 頁 0 失敗。
- `python -B scripts/check_site.py`：通過。
- `--propose --page MDI_1..7`：合併後 0 提案、0 移除、0 來源錯誤。
- `check_project_management.py --summary --baseline-file`（HEAD 基準）：473 → 466 錯誤，7 項 MDI `rules_sha256` 落差解除，無新增或惡化；19 警告不變。

## 未完成

- `FAQPage`、`MedicalWebPage`、`BreadcrumbList` 結構化資料：產生器只輸出 `Article`，需改 `build.py`（影響全站），未做。
- 醫療複核紀錄、手機實機驗收、Search Console 提交。
