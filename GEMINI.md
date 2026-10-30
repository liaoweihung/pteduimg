# pteduimg Gemini／Antigravity 專案入口

操作前確認已讀取根目錄 [AGENTS.md](AGENTS.md) 全文，再依其任務表以檔案工具讀取適用的 SOP／Skill；若客戶端未提供全文，先開檔閱讀。根入口已精簡，詳細規範按需載入，不用 inline include 展開整套文件。

涉及品牌、Logo、配色或品牌素材時，必須讀取共同入口 [docs/brand/README.md](docs/brand/README.md)、[Brand Guide v2.3](docs/brand/BRAND_GUIDE_v2.3.md) 與 [AI 品牌約束](docs/brand/BRAND_GUIDE_AI.md)，不要另維護一份規範。素材包相對路徑以 `docs/brand/` 為根目錄。

涉及圖卡與網頁文字產稿、接收 `handoff.json`、製圖或整合網站時，讀取 [圖卡與網頁文字交接規範 v1.1](docs/card-content-handoff-v1.md)、[圖卡製作 Skill](.agents/skills/create-pharmacy-card/SKILL.md) 及 [專案 Card Manager Skill](skills/pteduimg-card-manager/SKILL.md)；產稿使用此規範的 JSON 內容包，接收時保留定稿文字並依欄位整合現有網站資料。

醫療來源、人工簽核、Git 授權與品牌不可重繪等底線依 AGENTS 及相應 SOP。找不到或無法讀取所需規範時，回報缺項，不能猜測，也不能把靜態連結有效當成模型已載入。

這些是專案工作指引，不是工具或內容隔離的技術保證。既有 `skills/gemini-review/` 仍限明確呼叫，Live 維持 `BLOCKED / ISOLATION_UNVERIFIED`；不得繞過執行器或把 AI 品牌檢查稱為藥師複核。未經使用者明確授權，不 Commit、Push 或部署。
