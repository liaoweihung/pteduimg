# CR-2026-118 兒科用藥總整理主題頁與兒科圖卡頂部按鈕（2026-11-23）

- 範圍：新增 `topics/pediatric-medicine.html`；`build.py` 新增通用 `topic_hub` 欄位並收錄 sitemap；12 個純兒科系列（61 頁）＋ `diarrhea_care_3..6`（4 頁）共 65 頁加入頂部「兒科用藥總整理」按鈕（`Ped_abx_susp`、`Ped_susp` 同步啟用 `showFooter`）；`public.html`、`topics/mom.html`、`scripts/site_footer.py` 串接。
- 基準檔：`outputs/mgmt-before-20261123-0106.json`（總錯誤 1047）。
- 醫療正文未改動；肛門塞劑（`rectal`）與成人腹瀉（`diarrhea_care_1..2`）依藥師指示不加按鈕。
- 檢查結果：`JSON OK`、`scripts/site_footer.py` 通過、`scripts/check_site.py` 通過、65 頁 `--propose` 合併後零差異（5 頁既已複核頁 `content_sha256` 未變）、`project_change_tracker.py --check` 確認未提交變更連結 `CR-2026-118`。
- 基準比對：總錯誤 1047→1004（`worsened=0`、`resolved=80`；`new=37` 均為 `build.py` 與 `scripts/site_footer.py` 改動所致的他頁 `rules_sha256` 機械指紋落差，無實質新增錯誤）。
- 視覺與互動實測：本機 417px 手機寬度驗證 `public.html` 新入口、`ped_cold_secorine.html` 頂部「兒科用藥總整理」按鈕點擊導向與 `topics/pediatric-medicine.html` 全部連結正常、0 console/network 錯誤。
