# 瘀青藥膏系列圖卡重繪與網頁文字（CR-2026-067）

日期：2026-11-04（審查自 2026-11-03 起）
範圍：`bruising_care` 系列 4 頁（`bruising_care_1`～`bruising_care_4`），不改其他系列。

## 授權與來源

- 使用者（藥師、網站作者）於對話中要求審查本系列並提出修改建議，2026-11-04 表示「我同意這些內容」，並要求「上線」。
- 使用者以圖像 AI 依確認文字重新生成四張圖卡（含卡3 同文字重生），由 Claude 逐字核對圖上文字與確認文案一致、無錯字或亂碼後轉 WebP，以原檔名替換。
- 原卡問題：卡1「撞傷前 48 小時」語意相反、AI 字跡錯亂，且「前 48 小時不可擦藥膏」與卡3「依產品指示輕塗」矛盾；卡2 寫死「3–5 公分」並畫轉圈按摩箭頭；卡4 編號跳號、就醫時機不足；卡1、2、4 頁面沒有靜態文字。

## 直接查核來源（2026-11-04 實際閱讀）

| 來源 | 支持內容 |
|---|---|
| Gloucestershire Hospitals NHS：Ice and heat treatment（GHPI0659_02_25，review due 2028-02） | 冰袋隔濕布、小範圍 10–15 分鐘、前 24–48 小時反覆冰敷、受傷 2 天後才熱敷、新傷不熱敷、不冰敷開放傷口 |
| TVBS 健康2.0（2023-09-07）轉述食藥署「藥博士 正藥說」 | 外力瘀青先冰敷後再上藥膏、3 天後熱敷；MPS 主要用於鈍物創傷後血腫 |
| MedlinePlus：Bruise（review 2025-04-01） | 冰敷包毛巾不直接貼皮膚；服抗凝血／抗血小板藥較易瘀青；無故瘀青、劇烈壓力或疼痛需就醫；顏色由紅轉藍、黃綠再恢復 |
| NHS：Head injury and concussion | 撞到頭後嘔吐、無法保持清醒、服用抗凝血藥等需就醫 |
| Hirudoid Gel SmPC（emc，2023-11-28） | 薄層塗抹、最多一天 4 次；不用於破皮、黏膜；5 歲以下不用；症狀持續或惡化就醫 |
| 食藥署西藥許可證查詢：喜療瘀凝膠（衛署藥輸字第025606號） | 指示藥，適應症「鈍物創傷後之血腫，淺層性靜脈炎之局部治療」 |

食藥署許可證另查（2026-11-03）：喜療瘀乳膏（衛署藥輸字第025607號）已於 114-02-05 自請註銷，不寫入；外用七葉素（腫可癒軟膏、愛新凝膠）台灣核准適應症為慢性靜脈功能不全之局部腫脹，不列為瘀青藥。

## 變更

- `img/bruising_care_1～4.webp`：替換為重繪圖卡（卡3、卡4 為 941×1672，卡1、卡2 為 1024×1536）。
- `data/card_content.json`：新增卡1、2、4 三筆紀錄（`updatedAt`／`sourceCheckedAt` 2026-11-04、`revisionCredit`、3 筆來源、`needsMedicalReview: true`）；四筆都加 `imageUpdatedAt: 2026-11-04`，讓 PWA 重新抓取換過的圖；卡3 文字與原日期不變，只更新 alt。
- `cards.json`／`cards.manual.json`：同步四張標題（texts），標籤新增 淤青、黑青、瘀青藥膏、瘀青藥膏怎麼擦、瘀青多久會好、喜療瘀。
- 生成輸出：`cards/bruising_care_1～4.html`、`all-cards.html`、`seo.json`、`sitemap.xml`、`sitemap-main.xml`、`data/card_text_web_integration_report.md`、`sw.js`。

## 建置方法

`build.py --incremental` 因卡1 舊頁缺 JSON-LD（舊產生器版本）回報 Manual/legacy HTML conflict，未寫入任何輸出。改用隔離 worktree：HEAD 完整建置為基準 A，套用變更後完整建置為 B；A→B 僅本系列 4 頁與上述全域檔不同。全域檔 HEAD 與 A 相同，直接採 B；四頁 HEAD 與 A 只差 JSON-LD，採 B（補上 JSON-LD）。`sw.js` 採 B 清單，以 `scripts/incremental_build.worker_version` 依正式工作樹重算 CACHE_NAME。

## 驗證

- `python -B scripts/check_site.py`：通過。
- `--propose --page bruising_care_1..4`：合併機械欄位後 0 提案、0 移除、0 來源錯誤；人工欄位未改。
- `check_project_management.py --summary`：25 錯誤、19 警告，與 HEAD 基準相同（AUD-007 已登記新版報告）。
- 四頁 title／H1／meta description／JSON-LD（含 dateModified）、文字版重點、雙日期與 3 筆來源已核對。

## 未完成

- 具名醫療簽核證據未提供；`needsMedicalReview: true`，清冊人工欄位維持 unknown。
- FAQ 結構化資料（FAQPage）不在現行產生器支援範圍，本次未加入，未改 `build.py`。
- 「約 2 週沒變淡就醫」為藥師確認的實務門檻，來源僅間接支持（SmPC：症狀持續或惡化就醫）。
- 手機實機驗收待使用者確認。
