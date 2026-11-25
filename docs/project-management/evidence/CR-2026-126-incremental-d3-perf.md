# CR-2026-126：補齊增量建置跨系列推薦依賴（D3）與提速

- 範圍：`scripts/incremental_build.py`、`build.py`（`build_card_text_integration_report` 選用 `source_root`）、`tests/test_incremental_build.py`（不改動正式站 `cards/*.html` 與醫療資料）。
- 基準檔：`outputs/mgmt-before-20261126-0101.json`
- 核准：藥師於 2026-11-26 確認方案並同意修改 `scripts/incremental_build.py`、`build.py` 與測試套件。
- 單元測試：`python -B -m unittest discover -s tests` 58/58 通過（含新增 8 項 D3 跨系列推薦、`cards.manual.json` 邊界、CR-only 邊界、快取重用／失效與併發修改攔截測項）。
- 隔離實庫對照：單段文字修改（`09_australia_usa_china`）由 `47.54s` 降至 `2.43s`（僅寫 1 頁＋`sw.js`）；D3 改 `compression_stockings.title` 由 `45.80s` 降至 `3.75s` 且精準更新 `cards/knee_brace_safety.html` 等 8 張跨系列末頁；D3（`3.69s` vs 全建 `58.96s`）、manual-only（`3.84s` vs `50.06s`）、CR-only（`2.04s` vs `50.38s`，0 頁改寫）與完整建置逐檔比對均 0 差異。
- 網站與管理檢查：JSON OK、`check_site.py` 通過、`project_change_tracker.py --check` 確認未提交網站檔案（`build.py`）連結 `CR-2026-126`、基準比對 `new=0, worsened=0`。另記既有 `tests/verify_incremental_repository.py` 因 `pediatric_gi_syrup` 新增 `favorite_keys` 後腳本未同步清空該鍵而報錯，屬既有測試腳本待修項，本案未動。
