# 作業卡 6：發布（commit／push）

適用：藥師明確要求 commit、push 時。只讀這一份。沒有明確要求就不能 commit 或 push。

## 步驟

### 1. 同步遠端
```powershell
git pull --ff-only
```
失敗時（例如遠端和本機都有新提交，或遠端改到本機正在修改的檔案）停下回報，不要強制合併、覆蓋或暫存（stash）本機變更。

### 2. 核對變更
```powershell
git status --short
```
把每個變更的檔案對照本次任務的回報清單：
- 清單內的檔案：要提交。
- 清單外的檔案：**先列出來問藥師**，不要自行決定。
- 一律不提交：`outputs/`、`__pycache__/`、`output/hub`、原始 PNG 素材。

### 3. 更新 CR 並確認同步後仍然正確
- **本次工作有 CR 時**：確認 CR 的 `git_commit` 是 `same_commit`（作業卡在建立 CR 時已填；若仍是 `unknown`，**在加入檔案前**改好）。不需要 CR 的工作（例如計算器、主題頁）跳過這一項。
- 第 1 步同步下來的遠端提交，如果改到 `cards.json`、`cards.manual.json`、`data/`、`build.py`、`templates/`、`scripts/`（自動更新的 `dashboard/` 不算），先依原本那張作業卡重新建置、重跑它的檢查步驟（含基準比對），並更新 CR 的 `validation_result`，通過後再繼續。

### 4. 只加入指定的檔案
```powershell
git add <檔案1> <檔案2> ...
```
不要使用 `git add .` 或 `git add -A`。檔案很多時（例如完整建置更新了大量 `cards/*.html`），可以用 `git add cards/`，但先確認 `cards/` 裡沒有清單外的改動。刪除的檔案用 `git rm` 或 `git add <刪除的路徑>`。

加入後執行 `git diff --cached --stat`，確認暫存的檔案跟清單一致；有 CR 時，確認 CR 檔案已在其中，而且本次 CR 的 `validation_result` 已是實際檢查結果，**不是**「建置與檢查進行中」。還是暫時文字就停下來回報：代表檢查沒做完，不能發布。

### 5. 提交
- commit 訊息：一句話說明做了什麼，有 CR 時結尾加上 CR 編號。例如：`新增失眠與失眠藥物雙系列（9 張）CR-2026-086`
- 同一批變更包含兩件以上互不相關的事時，盡量分開 commit；但 CR 的 `same_commit` 必須跟它記錄的變更在同一個 commit。無法乾淨拆開時，合併成一次，訊息寫明每一件事。

### 6. 推送
```powershell
git push
```
推送被拒絕時，停下回報，**不要強制推送**（`--force`）。

### 7. 回報
- commit 編號與訊息
- 提交的檔案數量
- `git status` 是否乾淨

推送成功不代表網站已經更新。GitHub Pages 通常需要幾分鐘部署，上線後由藥師用手機檢查。
