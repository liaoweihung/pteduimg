# 增量建置驗證 — CR-2026-040

日期：2026-10-23。範圍是建置程式、直接相關測試與技術文件；沒有在正式工作樹執行建置、修改衛教來源／圖片／生成頁、調整醫療審核狀態，在該開發驗證階段亦未 Commit／Push。

## 根因及實作

原完整建置刪除所有 `cards/*.html` 後套用目前模板，因而將既有模板／SEO差異一次帶入舊頁。worker 又每次採當下分鐘作版本；全域產物直接寫入，索引匯出日期也可能造成差異。

新增 `--incremental` 以最後成功本機建置或 Git HEAD 的來源為比較基準，推導同系列、同系列SEO與反向相關系列依賴。僅受影響頁面進行舊／新render及三方合併；無關頁保持原始bytes。人工衝突與不支援結構變更在寫入前拒絕。所有有效圖卡共同計算全域索引；暫存準備完成並重查來源後才寫回。相同內容不寫入，匯出日期單獨變化不重寫索引；醫療日期不變。

worker 版本使用公開資源與worker邏輯的內容指紋；快取策略、runtime cache、更新提示與點擊後重整的程式碼不變。完整建置保留清除重建行為；`--only`保留不更新全域產物的行為。

## 可重現驗證

- `python -B -m unittest discover -s tests`：35項全數通過，包含原有醫療日期／sitemap回歸與新增增量測試。另定點驗證完整建置在Git不可用時仍可執行，重跑內容及worker不變。
- `python -B tests/verify_incremental_repository.py`：複製實際repository到可回復的隔離目錄，保留原始舊HTML，再使用既有圖文的複本作合成測試資料；不建立正式新衛教卡。
- `python -B scripts/check_site.py`：原工作樹及增量後隔離副本皆通過。
- `git diff --check`：檢查程式／文件差異。

管理檢查未通過，與網站建置結果分開：`check_project_management.py`回報419筆錯誤。以唯讀方式將產生器雜湊替換為`HEAD:build.py`重算得到402筆；本次增加17筆`rules_sha256`過期提示，沒有新增圖文來源或人工醫療欄位錯誤。保留清冊，不批次刷新既有機械或人工欄位。比較明細在`outputs/incremental-management-comparison.json`。

`project_change_tracker.py --check`確認本次未提交建置修改已連結CR-2026-040，但既有提交`7c201523`缺少管理連結；同一問題使`test_project_change_tracker.py`的10項測試中1項live-history測試失敗、9項通過。本次不修改無關提交的管理紀錄，亦不把這兩項檢查宣稱為通過。

| 情境 | 實測 |
|---|---|
| 小型六張系列追加第七張 | 寫入7頁；無關頁SHA-256與mtime不變；上一張／下一張循環、1/7至7/7、收藏鍵及全域索引正確 |
| 指定頁文字段落修改 | 僅寫入1頁；同系列其餘頁及無關頁不變；原雙日期與needsMedicalReview保留 |
| 真實資料新增獨立系列 | 新增1頁；原有387個HTML（382有效＋4退出＋404）SHA-256與mtime全數一致 |
| 真實單張系列追加 | 寫入2頁；原有其餘386個HTML SHA-256與mtime全數一致；1/2、2/2及雙向翻頁正確 |
| 全域完整性 | seo.json、all-cards.html、兩份sitemap、sw.js均包含測試後384個有效頁 |
| 重跑無資料變更 | 0公開檔案bytes或mtime改變；worker版本不變 |
| 圖片內容變動 | worker版本改變；移除版本字串後worker程式與變動前一致 |
| 人工修改 | 不衝突內容保留；與頁碼更新重疊時拒絕且所有公開輸出不變 |
| Git初次基準／寫入失敗 | 無先行完整重建即可增量；單獨worker程式變更也會更新版本；注入寫入錯誤後回復所有公開檔案bytes |
| 不支援異動 | 刪除、排序、hidden、publish_at、退休、共用模板、缺頁、未知ID及漏列系列均拒絕；不自動完整建置 |

測試程式會自動刪除隔離目錄。當次命令輸出保留於忽略路徑 `outputs/incremental-unittest.log`、`outputs/incremental-repository-check-site.log`、`outputs/incremental-working-tree-check-site.log`；這些log與本機baseline不是預計提交產物。

## 證據界線及限制

沒有實際瀏覽器安裝／更新PWA的端到端操作驗證；版本變化及原有更新程式以自動化、靜態回歸驗證。沒有改版或醫療內容變更，不把測試通過當醫療簽核。人工合併衝突須人工釐清；刪除／退休／可見性／重組／共用規則變更使用審閱後的完整建置。一般寫入錯誤可回復；斷電或程序強制終止不具檔案系統交易保證。完整建置本身仍可能覆寫人工HTML，不能拿它當成消除衝突的捷徑。

開發驗證當時功能尚未提交；當時工作樹的產生器與Git HEAD不同，所以正式增量呼叫會要求可靠基準。測試只在隔離副本建立基準，不在正式工作樹繞過安全檢查。之後經授權提交此實作後，可直接以含新產生器的HEAD作初次增量基準，不必先重寫所有舊卡。

## 後續提交授權

使用者於開發驗證完成後明確授權：僅提交已回報的10個檔案，Commit訊息為`feat: add safe incremental card builds`，正常Push至`origin/main`。沿用既有測試結果，不重建舊圖卡、不修復管理歷史問題、不force push。CR-2026-040的`same_commit`連結本次提交；實際Commit SHA、Push結果與遠端一致性另由執行結果回報，不將Push視為Pages部署證據。
