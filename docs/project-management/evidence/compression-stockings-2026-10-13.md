# CR-2026-026：彈性襪八張圖卡

## 授權與範圍

2026-10-13 使用者明確要求新增「彈性襪」八張圖卡，放在 public.html 最上方，授權依圖文建立標題、檔名、關鍵字、文字與來源，並試行管理系統 v1 增量流程。本次不得 Commit 或 Push。

這是網站製作授權，不是醫療簽核。新頁人工欄位維持 unknown；原有人工欄位逐頁保留。沒有新增作者、審閱者或商業連結。

## 圖片對應

來源目錄為使用者指定的 D:\Downloads；八張圖片已逐張查看，未修改圖片上的醫療文字。

| 次序 | 原圖 | 新頁 ID |
|---|---|---|
| 1 | 彈性襪作用與適用族群圖解.png | compression_stockings_benefits |
| 2 | 彈性襪壓力分級健康指南.png | compression_stockings_pressure |
| 3 | 彈性襪尺寸測量指南.png | compression_stockings_measurement |
| 4 | 彈性襪正確穿戴指南.png | compression_stockings_wear_1 |
| 5 | 彈性襪穿戴步驟圖解.png | compression_stockings_wear_2 |
| 6 | 彈性襪穿戴完整指南.png | compression_stockings_wear_3 |
| 7 | 彈性襪清洗保養指南.png | compression_stockings_care |
| 8 | 彈性襪安全穿戴指南.png | compression_stockings_safety |

## 來源與文字處理

2026-10-13 由 AI 查閱醫院、NHS、廠商技術資料及壓迫治療國際共識；逐頁引用保存在 data/card_content.json，不在管理清冊複製醫療正文。這不等於藥師複核。

- 壓力範圍是產品常見標示，不當作跨國統一分級或人人適用處方；圖中「初次使用」不等於可省略風險評估。
- 平整穿戴是避免局部壓力過大，並非消除原有由下而上的壓力梯度。
- 糖尿病或傷口不一概等於禁用；需先由醫療人員判斷循環、感覺及皮膚狀況。
- 單側突然腫痛應儘速評估；胸痛、呼吸困難另列立即急診警訊。
- 來源涉及廠商時僅用於壓力、量測及洗滌規格，不新增賣場或推薦品牌。

## 建置範圍與既有修改

任務開始已有 build.py、scripts/site_footer.py、三張示範頁及文件的未提交修改。本次新增系列需完整建置索引與 PWA；建置前保留既有 cards HTML 快照，建置後保留新八頁及全域輸出，既有圖卡維持任務開始時內容，不擴大尚未授權的全站頁尾套用。原有整合報告另留可追溯快照，並於 audit-history 登記新版本。

## 驗證結果（2026-10-14 完成）

- 開工前 --propose：0 頁差異、0 移除 ID、0 source errors。
- 完整建置新增八頁，並更新 SEO、兩份 sitemap、all-cards 及 PWA 資產清單；清單存在不代表所有圖片已預先離線下載。
- python -B scripts/check_site.py：通過；184 個高信心文字頁具有靜態文字與 SEO 欄位。
- python -B scripts/check_project_management.py：零管理錯誤；原有 18 份未知盤點日期及未完成臨床簽核提示保留。
- 最終 --propose：0 頁差異、0 移除 ID、0 source errors。
- python -B scripts/test_project_management.py：18 項通過。初次把新關聯插到檔案最前面，影響既有負向測試取第一列的假設；改為在原關聯後追加，再測通過，未修改測試工具。
- 1280×720 桌面及 390×844 手機各循環檢查八頁：圖片載入正常、無水平溢出、翻頁列位於圖片下方正常文件流，非浮動底部列。返回首頁到 public.html，彈性襪為一般系列列表第一個。
- 展開文字、來源與雙日期可閱讀；收藏操作後還原測試狀態；QR 視窗正常。八頁分享與收藏沿用既有 URL／favImages 格式，共用頁尾存在。
- 原 342 列人工管理欄位逐欄比對不變；原 343 個圖卡 HTML 與開工快照逐檔 bytes 相同；八頁 metadata 在兩份 cards JSON 一致，新頁人工醫療狀態仍 unknown、needsMedicalReview=true。
- 原 176 頁整合報告快照雜湊與歷史相符；CSV 的 UTF-8 BOM 保留。全域 sitemap 依目前既有產生器更新日期輸出，未將建置日改寫為舊頁醫療更新日。
- 內容建立與來源查核日仍為 2026-10-13；10 月 14 日僅為完成驗證日期。未 Commit、Push 或部署。
