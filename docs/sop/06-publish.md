# 作業卡 6：發布（commit／push）

適用：藥師明確要求 commit、push 時。只讀這一份。沒有明確要求就不能 commit 或 push。

## 步驟

### 1. 同步遠端
```powershell
git pull --ff-only
```
無法快轉合併（遠端和本機都有新提交）時，停下回報，不要強制合併或覆蓋。

### 2. 核對變更
```powershell
git status --short
```
把每個變更的檔案對照本次任務的回報清單：
- 清單內的檔案：要提交。
- 清單外的檔案：**先列出來問藥師**，不要自行決定。
- 一律不提交：`outputs/`、`__pycache__/`、`output/hub`、原始 PNG 素材。

### 3. 只加入指定的檔案
```powershell
git add <檔案1> <檔案2> ...
```
不要使用 `git add .` 或 `git add -A`。檔案很多時（例如完整建置更新了大量 `cards/*.html`），可以用 `git add cards/`，但先確認 `cards/` 裡沒有清單外的改動。

### 4. 提交
- commit 訊息：一句話說明做了什麼，結尾加上 CR 編號。例如：`新增失眠與失眠藥物雙系列（9 張）CR-2026-086`
- 同一批變更包含兩件以上互不相關的事時，盡量分開 commit；共用同一批檔案無法拆開時，合併成一次，訊息寫明每一件事。
- 本次 CR 的 `git_commit` 欄位若為 `unknown`，提交前改成 `same_commit`。

### 5. 推送
```powershell
git push
```
推送被拒絕時，停下回報，**不要強制推送**（`--force`）。

### 6. 回報
- commit 編號與訊息
- 提交的檔案數量
- `git status` 是否乾淨

推送成功不代表網站已經更新。GitHub Pages 通常需要幾分鐘部署，上線後由藥師用手機檢查。
