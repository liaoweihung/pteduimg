# CR-2026-039｜生達鎮咳袪痰液圖卡本機驗證

- 日期：2026-10-23（Asia/Taipei）。範圍：`series:pediatric_cold_syrup` 新增 `page:ped_cold_cough_mixture` 為第 10 張；使用者提供圖片與文字，並確認本次搜尋關鍵字及「本站依使用者提供內容整理」署名。
- 圖片：`D:\Downloads\生達鎮咳祛痰液用藥指南.png`，1024 × 1536，轉為 `img/ped_cold_cough_mixture.webp`。目視核對圖片顯示桔梗流浸膏 0.2 mL/mL、成人每次 5～15 mL 每日 3 次、兒童體重÷4 的參考算法及醫囑提醒；文字版另明確區分此算法與仿單的「兒童酌減」。
- 本次直接核對：[生達產品頁](https://www.standard.com.tw/product-info.php?c1=1&c2=4&c3=37&i=123)、[生達仿單（耕莘醫院收錄）](https://www.cth.org.tw/public/medi_news/01832855f81982955529d0a68ed0e9bd.pdf)、[耕莘醫院藥品資訊](https://www.cth.org.tw/?aid=606&iid=1181&page_name=detail&pid=0)、[Dr. Jaden Health 文章](https://www.drjadenhealth.com/l/cough-mixture/)。仿單沒有明確的兒童體重公式、最低適用年齡或兒童最高日劑量；0.25 mL/kg 與體重÷4 來自後兩個參考來源。
- `updatedAt` 與 `sourceCheckedAt` 均為 2026-10-23。新頁 `needsMedicalReview=true`；尚無具名人工醫療複核者、日期及版本證據，正式狀態維持 `unknown`。
- `python build.py`：382 張現行／hidden 靜態圖卡頁；220 張文字整合成功、0 失敗。完整建置產生的新頁、同系列 9 張導覽、`all-cards.html`、兩份 sitemap、`seo.json`、`sw.js` 與文字整合報告已核對；334 張與本次無關的舊生成頁差異已從原本乾淨的工作樹復原。
- `python -m json.tool` 三份 JSON、`python -B scripts/check_site.py`、`python -B scripts/project_change_tracker.py --check`、`python -B scripts/test_project_change_tracker.py`（10/10）及 `git diff --check` 通過。新頁和同系列受影響頁的 `--propose` 均為零差異、零移除、零來源錯誤。靜態核對 10 張翻頁、新頁圖片、文字、雙日期、來源、返回入口、分享網址、收藏格式及全域索引通過。
- `python -B scripts/check_project_management.py` 仍有 401 筆歷史指紋或缺證據錯誤；沒有本次兒科感冒藥水頁、CR-2026-039 或 AUD-007 錯誤。`python -B scripts/test_project_management.py` 18 項中 16 項通過，兩項當前快照測試受上述舊錯誤影響而失敗。
- 嘗試以本機 HTTP 預覽在 Codex 瀏覽器檢查桌機／手機畫面，瀏覽器對 `127.0.0.1` 回傳 `net::ERR_FAILED`；實際視覺與點擊操作未測試。沒有 Commit、Push 或部署。

## 本次 GitHub Desktop 檔案清單

- 來源：`cards.json`、`cards.manual.json`、`data/card_content.json`、`img/ped_cold_cough_mixture.webp`。
- 生成頁：`cards/ped_cold_cough_mixture.html`；同系列既有頁 `cards/ped_cold_cypromin.html`、`cards/ped_cold_cetirizine.html`、`cards/ped_cold_secorine.html`、`cards/ped_cold_peace_syrup.html`、`cards/ped_cold_guaphen_syrup.html`、`cards/ped_cold_exdila_liquid.html`、`cards/ped_cold_mintapp_syrup.html`、`cards/ped_cold_musco_solution.html`、`cards/ped_cold_koko_sou_syrup.html`。
- 全域生成產物：`all-cards.html`、`seo.json`、`sitemap.xml`、`sitemap-main.xml`、`sw.js`、`data/card_text_web_integration_report.md`。
- 管理紀錄：`docs/project-management/page-inventory.csv`、`docs/project-management/content-relations.csv`、`docs/project-management/change-requests.csv`、`docs/project-management/project-dashboard.md`、`docs/project-management/audit-register.json`、`docs/project-management/audit-history.md`、`docs/project-management/evidence/cough-mixture-2026-10-23.md`。
