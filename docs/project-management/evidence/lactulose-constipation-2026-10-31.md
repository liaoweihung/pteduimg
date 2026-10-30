# CR-2026-051 乳果糖藥水新增證據（2026-10-31）

- 使用者提供乳果糖藥水（含杜化液 667 mg/mL、樂多 666 mg/mL 比較）衛教圖卡定稿圖檔與人工審核文字，授權追加於 `pediatric_gi_syrup`（兒科腸胃藥水）系列第 2 張。
- 審核者姓名、資格及簽核版本證據未提供；依規範保留 `needsMedicalReview: true`，管理清冊人工醫療欄位維持 `unknown`。
- 圖卡尺寸 `576×1024`，轉換輸出為 `img/lactulose_constipation.webp`（WebP `quality=90, method=6`），原圖保留。新頁 ID `lactulose_constipation`；既有第 1 張（`wempty_suspension`）URL 與收藏鍵不變，新收藏鍵 `pediatric_gi_syrup-1`。
- 今日建立網站文字版，`updatedAt: "2026-10-31"`；核對 TFDA 核准電子仿單直接來源（亞培杜化液，衛署藥輸字第025302號；杏輝樂多糖漿，衛署藥製字第039701號）及秀傳醫療體系衛教須知，`sourceCheckedAt: "2026-10-31"`。
- 執行安全增量建置 `python -B build.py --incremental lactulose_constipation`，更新同系列 2 張圖卡導覽與全域索引（`seo.json`、`all-cards.html`、`sitemap.xml`、`sitemap-main.xml`、`sw.js`、`data/card_text_web_integration_report.md`）；整合文字 240 成功、0 失敗。
- `check_site.py` 通過；同系列 2 頁 `--propose` 零差異、零移除、零來源錯誤。
- 未執行 Commit、Push 或部署。

## 本次變更檔案清單（供 GitHub Desktop 審核）

- `img/lactulose_constipation.webp`
- `cards/lactulose_constipation.html`
- `cards/wempty_suspension.html`
- `cards.json`
- `cards.manual.json`
- `data/card_content.json`
- `data/card_text_web_integration_report.md`
- `seo.json`
- `all-cards.html`
- `sitemap.xml`
- `sitemap-main.xml`
- `sw.js`
- `docs/project-management/page-inventory.csv`
- `docs/project-management/content-relations.csv`
- `docs/project-management/change-requests.csv`
- `docs/project-management/project-dashboard.md`
- `docs/project-management/evidence/lactulose-constipation-2026-10-31.md`
