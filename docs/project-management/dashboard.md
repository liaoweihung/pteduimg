# 衛教助手網站狀態

入口 dashboard/index.html。執行 python -B scripts/build_dashboard.py 可重建；只寫 dashboard/，不改人工清冊。技術檢查沿用既有 machine_snapshot，不進行醫療內容重審。公開來源以 current 去重計數；hidden、retired另列。領域是 topics 分類，不是疾病數。專頁與工具尚未全面涵蓋其他資料庫。

main 上相關網站輸入或機械可讀管理資料變更時，或手動執行時，dashboard-publish 工作流程讀取最新 main，產生並只提交 dashboard/index.html、status.json，再以 Pages API 明確要求既有 main根目錄的Pages建置。沒有改變既有快取策略。產生失敗不提交，競爭推送最多重試三次，不強推；GitHub Actions失敗紀錄可查。頁面顯示台灣時間與來源SHA。更新不依賴筆電，手機重新整理讀取最近發布快照。未推送工作不會出現。

2026-10-25 精簡：移除已退役的 PWA／Scheduled card publish 完成事件監聽。Push 採明確路徑清單，涵蓋根目錄 HTML/JSON、圖卡、圖片、網站資產／資料／工具、模板、相關建置／檢測程式，以及管理 CSV、主題與稽核索引 JSON。一般說明文件、純測試及 dashboard 輸出不觸發；完整清單以 `.github/workflows/dashboard-publish.yml` 為準。來源時間與 SHA 表示最近一次相關輸入快照，不保證等於每一筆純文件提交；必要時可手動更新。保留原有 main 最新版本讀取、重試、只提交兩個輸出與 Pages 請求，不新增部署閘門。

輸出只有技術摘要，noindex不是權限控制，不含私人審核者、證據全文或Google流量。清冊機械差異不等於醫療錯誤；dashboard使用本次技術檢測，不覆寫人工狀態。未註冊service worker。

2026-10-21 正式啟用：實作 e0d5dfb；Actions 39621013450 成功，自動輸出提交 5f469ee。Pages 回報 built；https://liaoweihung.github.io/pteduimg/dashboard/ 與 status.json 均 HTTP200，頁面標題為衛教助手網站狀態，來源版本 e0d5dfb。
