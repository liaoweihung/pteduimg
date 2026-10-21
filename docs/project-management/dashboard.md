# 衛教助手網站狀態

入口 dashboard/index.html。執行 python -B scripts/build_dashboard.py 可重建；只寫 dashboard/，不改人工清冊。技術檢查沿用既有 machine_snapshot，不進行醫療內容重審。公開來源以 current 去重計數；hidden、retired另列。領域是 topics 分類，不是疾病數。專頁與工具尚未全面涵蓋其他資料庫。

main push、手動執行及既有PWA工作完成後，dashboard-publish 工作流程讀取最新 main，產生並只提交 dashboard/index.html、status.json，再以 Pages API 明確要求既有 main根目錄的Pages建置。沒有改變既有快取策略。產生失敗不提交，競爭推送最多重試三次，不強推；GitHub Actions失敗紀錄可查。頁面顯示台灣時間與來源SHA。更新不依賴筆電，手機重新整理讀取最近發布快照。未推送工作不會出現。

輸出只有技術摘要，noindex不是權限控制，不含私人審核者、證據全文或Google流量。清冊機械差異不等於醫療錯誤；dashboard使用本次技術檢測，不覆寫人工狀態。未註冊service worker。

2026-10-21 正式啟用：實作 e0d5dfb；Actions 39621013450 成功，自動輸出提交 5f469ee。Pages 回報 built；https://liaoweihung.github.io/pteduimg/dashboard/ 與 status.json 均 HTTP200，頁面標題為衛教助手網站狀態，來源版本 e0d5dfb。
