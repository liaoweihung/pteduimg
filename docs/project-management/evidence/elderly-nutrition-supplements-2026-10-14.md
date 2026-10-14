# CR-2026-027｜新增「營養品怎麼選」九張圖卡

## 授權與範圍

- 使用者於 2026-10-14 明確要求在 `public.html` 新增「營養品怎麼選」系列，共九張圖卡，並同步專案管理系統。
- 使用者提供完整文字內容，註明已人工確認；本次將該文字整理成逐頁靜態 HTML。
- 本次不重新盤點全站、不修改其他醫療內容、不 Commit、不 Push。
- 新內容保留 `needsMedicalReview: true`，清冊人工醫療狀態為 `unknown`；使用者確認文案不等同具名醫療人員簽核。

## 新增系列與頁面

- 系列 ID：`elderly_nutrition_supplements`
- 系列名稱：營養品怎麼選
- 公開分類：`public_education`
- 公開主題：`chronic_conditions`
- 圖卡頁：
  - `elderly_appetite_causes`
  - `elderly_appetite_meal_tips`
  - `elderly_protein_needs`
  - `elderly_nutrition_supplements_choose`
  - `balanced_nutrition_supplement`
  - `high_protein_supplement`
  - `diabetes_nutrition_formula`
  - `kidney_nutrition_formula`
  - `elderly_appetite_medical_alerts`

九張來源 PNG 由使用者指定的同批下載檔案提供，依內容順序轉為穩定英文檔名的 WebP。原始 PNG 未修改或刪除。每頁都建立標題、摘要、分段文字、替代文字、直接來源、內容更新日期及資料查核日期。

## 內容與來源

- 內容更新日期：2026-10-14
- 資料查核日期：2026-10-14
- 主要來源：國民健康署高齡營養與質地調整資料、ESPEN 2022 高齡臨床營養指引、NICE 成人營養支持指引、MedlinePlus 食慾下降與高齡營養資料、KDOQI 2020 慢性腎臟病營養指引、糖尿病專用營養配方專業共識及 ADA 營養照護標準。
- 疾病配方、吞嚥障礙、慢性腎臟病及再餵食風險均保留個別評估與就醫限制；未把產品或特殊配方描述成治療疾病。

## 管理增量

- 需求：`CR-2026-027`
- 新增九筆 `page-inventory.csv`，人工欄位皆維持 `unknown`。
- 新增 `topic:older-adult-nutrition` 與 `subtopic:older-adult-nutrition:oral-supplements` 管理集合；兩者皆為 `collection_only`，不是新疾病頁。
- 新增兩筆主題／系列關聯與九筆 `has_card` 關聯。
- 建置前保留 AUD-007 的 184 頁文字整合報告快照；完整建置後為 193 頁。
- `--propose` 原始結果保存在 `elderly-nutrition-supplements-proposals-2026-10-14.json`。

## 提交前定點查核

- 歷史盤點基準 HEAD 為 `333ed52512cfbaf2b0f900e76605bc0b5c8264cc`；2026-10-14 定點查核時目前 Git HEAD 為 `03b85e16c000d7a194aa9cc724b070c11f7a5ba4`。CR-2026-026 已在目前 HEAD，CR-2026-027 尚在工作目錄。
- 彈性襪八頁的圖片、生成 HTML 與文字紀錄相對目前 HEAD 無差異；清冊舊雜湊與依目前 HEAD 證據重新計算的結果不一致。定點提案只同步八筆機械雜湊及 `checked_at`，沒有修改其內容或人工欄位。完整證據見 `compression-stockings-fingerprint-sync-2026-10-14.md`。
- 兩份 sitemap 相對目前 HEAD 均為 9 個營養品 URL 新增、0 個 URL 移除；另有 349 個既有 URL 的 `lastmod` 差異，其中 263 個移除、86 個改為內容日期。現行 `build.py` 對靜態頁不輸出 `lastmod`，對圖卡頁使用 `data/card_content.json` 的內容日期，因此這批差異屬完整建置的正常正規化輸出；兩份 sitemap 結果一致，本次不還原。

## 驗證結果

- 三份 JSON 語法檢查通過。
- `python -B scripts/check_site.py`：通過；193 個高信心文字頁皆有靜態文字及 SEO 欄位。
- `python -B scripts/check_project_management.py`：0 個管理錯誤。
- `python -B scripts/test_project_management.py`：18 項通過。
- 九個新頁最終 `--propose`：零差異、零移除、零來源錯誤。
- `public.html` 本機手機寬度預覽可見「營養品怎麼選」入口；第一與第九張圖片完整，圖下翻頁列及 1/9、9/9 循環正常。
- 第一頁文字版可展開，內容更新日、資料查核日、來源連結及固定頁尾存在。
- 兩份 sitemap、`all-cards.html`、`seo.json`、`sw.js` 都包含九個新頁或資產。
- 完整建置造成的舊頁批次差異已收斂；`cards/` 下的既有修改仍只有開工前的三頁，另加本次九個新頁。

機械檢查只確認結構與輸出，不代表人工醫療複核、搜尋排名或正式部署。本次未 Commit、Push 或查核 GitHub Pages。
