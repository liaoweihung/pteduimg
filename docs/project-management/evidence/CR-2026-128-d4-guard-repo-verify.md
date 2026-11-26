# CR-2026-128：D4 空 SEO 防呆保護與整庫驗證腳本修復

- **範圍**：`build.py`（完整建置 `--allow-empty-seo` 與空索引中止防呆）、`tests/test_incremental_build.py`（歷史標題保護與空索引中止／放行測試）、`tests/verify_incremental_repository.py`（清除 `incremental_test` 合成系列 `favorite_keys`）。
- **基準檔**：`outputs/mgmt-before-20261126-1033.json`
- **素材來源**：工程維護與測試修復（不修改圖卡醫療正文或正式站台資料）。
- **驗證結果**：`python -B -m unittest discover -s tests` 60/60 通過；`python -B tests/verify_incremental_repository.py` 通過（`Isolated check_site exit=0`）；`check_site.py` 通過；`project_change_tracker.py --check --range HEAD..HEAD` 通過；管理基準比對 `new=0`、`worsened=0`。
