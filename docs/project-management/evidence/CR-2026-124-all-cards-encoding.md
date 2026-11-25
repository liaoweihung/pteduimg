# CR-2026-124：修復 all-cards.html 字面問號與日期比對（D2）

- 範圍：修復 `build.py`（`render_all_cards_page`）字面問號、`scripts/incremental_build.py`（`preserve_index_date`）正規表示式，僅重產 `all-cards.html`。
- 基準檔：`outputs/mgmt-before-20261126-0020.json`
- 核准：藥師於 2026-11-26 同意修改 `build.py`、`scripts/incremental_build.py` 與目錄文案。
- 檢查結果：僅重產 `all-cards.html`（零張 `cards/*.html` 異動）；`preserve_index_date` 同日與跨日（`2026-11-27`）重跑皆回傳 `False`；JSON OK、`check_site.py` 通過、`project_change_tracker.py --check` 顯示未提交網站檔案有需求紀錄、`tests/test_incremental_build.py` 18/18 通過；基準比對 `new=0`、`worsened=0`。另檢出 `otc_eye_drops` 系列原有資料 `tags` 含問號（1880、1885、1890、1895、1900 行），屬資料層問題未動。
