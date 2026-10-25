# 舊 workflow 退役與 Dashboard 精簡

日期：2026-10-25（Asia/Taipei）。沿用 CR-2026-022；使用者明確核准退役「自動更新 PWA 快取與版本號」及「Scheduled card publish」，保留並精簡 Dashboard。只完成本機設定；尚未 Commit／Push，線上尚未套用。

## 原因與範圍

- PWA [run 40154287508](https://github.com/liaoweihung/pteduimg/actions/runs/40154287508) 的建置成功，但推送被拒；Dashboard [run 40154287472](https://github.com/liaoweihung/pteduimg/actions/runs/40154287472) 先推入 b227d3c。舊流程重複整站建置且只提交 sw.js。
- 移除 `.github/workflows/auto-build.yml` 與 `.github/workflows/scheduled-card-publish.yml`。舊檔保存在 Git 歷史（本次工作起點 9e364f693ec4a610230a20dab3f87078e0c55265）；不刪本機 `scripts/publish_scheduled_cards.py`、發布資料或既有 workflow 執行紀錄。
- Dashboard 改為相關網站輸入、管理 CSV/指定 JSON 與相關程式觸發；保留手動執行、抓最新 main、安全重試、只提交兩個輸出與 Pages 請求。移除舊 workflow_run 依賴。
- 同步 AGENTS、網站建置發布規範、專案 Card Manager 排程段落、Dashboard 說明與管理進度。CR-2026-022 的 pending 高信心文字檢查器限制尚未處理，保持 in_progress；這次 approval 僅限上述授權範圍。
- 沒有執行 build.py、publisher 或 Dashboard 產生器；沒有修改衛教頁、圖片、清冊、人工簽核或既有稽核報告。管理連結驗證 workflow 未修改。

## 驗證

- PyYAML BaseLoader：剩餘兩個 workflow YAML 可解析；Dashboard 只保留 main Push 與 workflow_dispatch。
- 31 個路徑案例通過：相關圖卡／來源／管理資料／程式會觸發；dashboard 輸出、一般文件、技能說明及純測試不觸發。
- 與 HEAD 的 YAML 結構比對：permissions、concurrency 與所有 job steps 一致，只移除舊 workflow_run 專用條件。兩個退役檔案已不存在。
- CSV 比對：保留 UTF-8 BOM 與全部 request_id；只有 CR-2026-022 一列更新。
- `git diff --check` 通過。Git 差異確認沒有衛教頁、圖片、清冊、產生器或 PWA 產物變更；既有 `.codex-remote-attachments/` 未動。
- `python -B scripts/check_project_management.py --summary --report-file outputs/workflow-retirement-after.json`：仍為 424 errors、19 warnings。與改前 JSON 逐欄比較，只有 checked_at 不同，errors、warnings、diagnostics 完全一致；驗證仍以 exit 1 如實回報。
- `python -B scripts/project_change_tracker.py --check --limit 2`：exit 1，唯一歷史缺項仍為 7c201523。`--range HEAD..HEAD` 回報零筆本機網站變更，但另查明既存 normalize 使用 lstrip 導致 `.github/workflows/...` 變成 `github/workflows/...`，因此不能將零筆視為 workflow 已受檢；本次以實際 Git 檔案差異、CR-2026-022 的 same_commit 與定點證據人工核對。未擴大修改追蹤器。
- 未執行 build.py、publisher、Dashboard 產生器或 Actions；沒有以本機檢查宣稱線上退役已生效。

修改前完整管理檢查：424 errors、19 warnings（evidence_path_missing=14、machine_field_drift=397、report_changed=13）。僅作本次改前／改後診斷比對，不將這份快照當成已核准的正式基準。

## 同日追加：修正追蹤器的點目錄漏判

使用者另明確授權一併修正 `.github` 路徑漏判。`scripts/project_change_tracker.py` 改為只移除完整的 `./` 前綴，保留 `.github` 等目錄名稱的點；管理專用 workflow 與 `.codex`／`.agents` 的既有排除規則保持不變。

- `python -B scripts/test_project_change_tracker.py`：16 項測試通過，包含點目錄、重複相對前綴、Windows 路徑、一般／合併提交及無 CR 的 workflow 變更攔截。
- `python -B scripts/project_change_tracker.py --check --range HEAD..HEAD --limit 0`：exit 0，正確列出本次兩個刪除與一個修改的 workflow，全部連結 CR-2026-022。
- 完整歷史 `--check --limit 2`：exit 1，仍只有 7c201523 的既有歷史缺連結；本機三個 workflow 變更已正確受檢。
- `git diff --check` 通過。未執行 build.py、未修改衛教網頁、未 Commit／Push。上方初次診斷的 `.github` 漏判已由這次補修解除。
