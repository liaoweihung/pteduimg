# CR-2026-023：保留定稿原句與警告提醒

- 範圍：`build.py`、`cards/09_australia_usa_china.html`、`data/card_text_web_integration_report.md`、`docs/project-management/page-inventory.csv`
- 基準檔：`outputs/mgmt-before-20261126-0010.json`
- 素材來源：既有 `data/card_content.json` 定稿原句（不改醫療內容，僅修正 `build.py` 不再靜默刪除 `FORBIDDEN_SEO_WORDS`）
- 建置與整合比對：`python -B build.py --only 09_australia_usa_china` 僅更新該頁並印出 `[WARN]` 提醒「保證」；原句比對整合報告 388 頁通過、0 失敗
- 檢查結果：`--propose` 零差異；`JSON OK`、`check_site.py` 通過、`project_change_tracker.py` 未提交檔案有管理連結；基準比對 `new=0, worsened=0, resolved=2`
