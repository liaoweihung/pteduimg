# 2026-11-12 公眾衛教圖卡返回與推薦閱讀：管理連結補登

- 對應提交：`9afb5fcbc2da04e159c697d6372973d2cbe3ffa3`（2026-11-12）。
- 該提交修改 `public.html` 的篩選狀態及返回時捲動還原、`build.py` 的公眾／藥師圖卡返回行為與公眾系列末頁推薦閱讀；並重新產生圖卡 HTML、`seo.json`、`sw.js`。同一提交另含 Search Console noindex 觀測證據與總控台更新，分別由既有搜尋追蹤紀錄管理。
- GitHub Actions run `43184770137` 的 `project-management-links` 工作失敗：唯讀追蹤器指出此提交「有管理檔但未連結需求」。本檔及 CR-2026-075 是事後補登該提交的管理連結，不代表原始變更已經人工核准。
- 本機重現：`python -B scripts/project_change_tracker.py --check --range f6166c43148186289da5408a35009efd378a152e..9afb5fcbc2da04e159c697d6372973d2cbe3ffa3 --no-working-tree` 回傳缺少管理連結（exit 1）。`python -B scripts/check_site.py` 通過。
- 原始授權及桌機／手機操作驗收證據未在本次核對的提交與管理紀錄中找到；保留待確認。此補登不改醫療內容或人工醫療審閱狀態。
