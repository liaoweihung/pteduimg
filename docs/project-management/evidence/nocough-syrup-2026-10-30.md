# CR-2026-050 「杏輝」安咳糖漿新增證據（2026-10-30）

- 使用者提供「杏輝」安咳糖漿（NOCOUGH SYRUP "SINPHAR"，衛署藥製字第029634號）藥品基本資料、手機直式圖卡定稿文字、完整網頁文字重點與實品照片，授權製作 9:16 衛教圖卡（含卡通化藥瓶與右下角正式黑色單色品牌 Logo）並建立專屬網頁，追加於 `pediatric_cold_syrup`（兒科感冒藥水）系列末尾（第 12 張）。
- 審核者姓名、資格及簽核版本證據未提供；依規範保留 `needsMedicalReview: true`，管理清冊人工醫療欄位維持 `unknown`。
- 圖卡尺寸 `1080×1920`，輸出 `img/ped_cold_nocough_syrup.webp`（WebP `quality=90, method=6`），未覆寫品牌 PNG 母版。新頁 ID `ped_cold_nocough_syrup`；既有 11 張 URL 與收藏鍵不變，新收藏鍵 `pediatric_cold_syrup-11`。
- 今日建立網站文字版，`updatedAt: "2026-10-30"`；核對 TFDA 核准電子仿單直接來源（https://mcp.fda.gov.tw/exportpdf/%E8%A1%9B%E7%BD%B2%E8%97%A5%E8%A3%BD%E5%AD%97%E7%AC%AC029634%E8%99%9F ，衛署藥製字第029634號），`sourceCheckedAt: "2026-10-30"`。
- 執行安全增量建置 `python -B build.py --incremental ped_cold_nocough_syrup`，更新同系列 12 張圖卡導覽與全域索引（`seo.json`、`all-cards.html`、`sitemap.xml`、`sitemap-main.xml`、`sw.js`、`data/card_text_web_integration_report.md`）；整合文字 236 成功、0 失敗。
- `check_site.py` 通過；同系列 12 頁 `--propose` 零差異、零移除、零來源錯誤；`project_change_tracker.py --request CR-2026-050` 確認本次變更檔案均已連結 `CR-2026-050`。
- 未執行 Commit、Push 或部署。

## 本次變更檔案清單（供 GitHub Desktop 審核）

- `img/ped_cold_nocough_syrup.webp`
- `cards/ped_cold_nocough_syrup.html`
- `cards/ped_cold_cypromin.html`
- `cards/ped_cold_cetirizine.html`
- `cards/ped_cold_secorine.html`
- `cards/ped_asthma_meptin_liquid.html`
- `cards/ped_cold_peace_syrup.html`
- `cards/ped_cold_guaphen_syrup.html`
- `cards/ped_cold_exdila_liquid.html`
- `cards/ped_cold_mintapp_syrup.html`
- `cards/ped_cold_musco_solution.html`
- `cards/ped_cold_koko_sou_syrup.html`
- `cards/ped_cold_cough_mixture.html`
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
- `docs/project-management/audit-register.json`
- `docs/project-management/audit-history.md`
- `docs/project-management/project-dashboard.md`
- `docs/project-management/evidence/nocough-syrup-2026-10-30.md`
