# CR-2026-120 補齊 7 頁全站防護版 GA4 追蹤碼（2026-11-23）

- 範圍：
  - 獨立靜態頁（5 頁）：`topics/mom.html`、`topics/acne.html`、`about.html`、`author.html`、`editorial-policy.html`。
  - 建置產生頁（2 頁）：`build.py`（`render_all_cards_page` → `all-cards.html`）與 `scripts/card_archive.py`（僅 `retired-cards.html`，4 張 `noindex` 歷史圖卡頁維持不加）。
- 基準檔：`outputs/mgmt-before-20261123-0933.json`（總錯誤 1004）。
- 規則核准：藥師於 2026-11-23 同意修改 `build.py` 與 `scripts/card_archive.py`；不修改醫療內容與既有圖卡正文。
- 檢查結果：完整建置並還原 10 張無關既有漂移圖卡、重算 `sw.js` 快取版本；7 頁目標 HTML 皆通過 `G-T5R33JYTC0`／本機與內網排除／開發者隱形開關／非無條件載入檢查，4 張歷史頁未加入；`JSON OK`、`site_footer.py` 通過、`check_site.py` 通過、`project_change_tracker.py` 確認未提交網站檔案均連結 `CR-2026-120`。
- 基準比對：`outputs/mgmt-after-20261123-0936.json` 與基準檔比對結果 `new=0`、`worsened=0`、`resolved=0`（總錯誤維持 1004）。
