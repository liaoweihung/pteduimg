# 必爾生口服液單張圖卡入庫紀錄

- 範圍：新增 `series:kidsolone_oral_solution`、`page:kidsolone_oral_solution` 到 `index.html` 的特定產品衛教資料來源；單張圖卡與靜態文字頁。
- 使用者先提供 `D:\Downloads\兒童口服類固醇用藥指南.png` 與已人工確認的文字，後續明確同意依仿單將兒童分次由「1～2 次」改為「3～4 次，實際依醫師處方」，並提供修正版 `D:\Downloads\必爾生兒童用藥指引.png`。本次正式圖片只採修正版，圖卡第 3 區已顯示「分 3～4 次」。
- 產品直接來源：晟德必爾生口服液核准仿單（衛署藥製字第046614號）：https://www.tai-an.com.tw/upload/DrugInfo/Drug/Instructions/PREDS.pdf；光田綜合醫院藥品資料：https://www.ktgh.com.tw/ktgh/Home/WesternMedDetail?CatID=65&NewsID=821&Ordid=26013。2026-10-23 定點核對兒童起始日劑量、分次、成分、適應症與使用警語。沒有對舊圖卡執行醫療盤點。
- 來源修正界線：仿單與光田頁的兒童起始劑量為 0.14～2 mg/kg/day、分 3～4 次；實際個人劑量仍依醫師處方，網頁不提供家長可自行套用的每次毫升表。
- 使用者的「已人工確認」不等於有具名、日期、版本及範圍的藥師簽核證據。`needsMedicalReview` 保持 `true`，清冊 `medical_review_status` 保持 `unknown`。
- 本機增量建置只寫入新頁與全域索引／SEO／PWA必要輸出；`check_site.py` 通過。新頁清冊 `--propose` 零差異。完整管理驗證與測試中的既有歷史問題另以命令結果記錄，不因入庫批次修復。
- 管理驗證 `--summary` 為 419 筆錯誤、19 筆警告；類別為歷史欄位漂移 392、證據路徑缺失 14、舊報告變更 13。沒有經確認的基準報告，不宣稱本次新增問題為零；完整診斷在忽略的 `outputs/kidsolone-management-2026-10-24.json`。18 項管理測試中 2 項因現行快照錯誤而失敗；10 項追蹤測試中 1 項因歷史提交 `7c201523` 缺管理連結而失敗。追蹤器辨識本次未提交檔案連到 CR-2026-042，但同一歷史缺漏使全量 `--check` 失敗。
- 靜態檢查確認頁面有文字區、標題、修正後分次、雙日期、直接來源連結，且兩份系列 JSON 一致；兩份 sitemap、全站索引、SEO 與 worker 均有新頁條目。桌機／手機瀏覽器操作未測試：本機 `file:` URL 被瀏覽器安全政策拒絕，不繞過限制。
