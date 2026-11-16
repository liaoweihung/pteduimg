# CR-2026-104 作業卡 0 新增開工遠端同步步驟

- 範圍：更新 `docs/sop/00-common.md` 的流程總覽，並在「開工存基準」前新增第 0 步；保留原第 1～8 步編號。
- 基準檔：`outputs/mgmt-before-20261117-sop-pull-rule.json`（於 CR 登記前產生；原有管理錯誤 1127 筆）。
- 授權：藥師於 2026-11-17 同意提案，並補充新任務遇已追蹤檔案未提交改動時，不 pull、不開始任務；後續明確要求 commit、push 並照前次作業卡變更登記 CR。
- 內容：新任務使用 `git pull --ff-only`；續作同一筆 CR 不 pull，使用 `git fetch` 與遠端差異檢查；失敗或遠端有新 commit 時停下回報。
- 不涉及圖卡、圖片或醫療內容；本次不建置網站。
- 既有未追蹤的 `Claude outputs/` 不碰、不提交。
- 檢查結果：`git diff --check` 與 `check_site.py` 通過；變更追蹤顯示目前未提交網站檔案 0，僅有 2 筆既有提交缺管理連結；基準比對 new=0、resolved=0、worsened=0（persistent=1127）。
