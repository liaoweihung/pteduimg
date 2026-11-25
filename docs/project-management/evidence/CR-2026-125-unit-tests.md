# CR-2026-125 Evidence

- 範圍：`tests/test_build_dates.py`、`tests/test_rule_fingerprints.py`（修復架構審計報告所述 2 個既有失敗單元測試，不改動醫療內容與產出頁面）。
- 基準檔：`outputs/mgmt-before-20261126-0032.json`
- 依據：`docs/architecture_health_audit_2026-11-24.md` 最後一段與藥師 2026-11-26 確認方案。
- 結果：`python -B -m unittest discover -s tests` 50/50 通過（59.018s）；JSON OK；`check_site.py` 通過；基準比對 `new=0, worsened=0`。
