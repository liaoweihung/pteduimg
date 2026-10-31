# CR-2026-057 胃藥怎麼吃？七張圖卡系列與定稿文字整合證據（2026-11-01）

## 1. 任務與授權背景
- 使用者指示依據 `C:\Users\liaow\.codex\visualizations\2026\10\30\01a18d9e-3bc9-7891-9781-008b81cce2c9\stomach_medicine_antigravity_20261101` 資料夾內之「Antigravity接手指令.md」，將七張胃藥圖卡與定稿文字整合至本機 `pteduimg` 專案。
- 沿用現有圖片與定稿文字，完成必要本機建置及驗證；不要 Commit、Push 或部署，保留修改供使用者透過 GitHub Desktop 提交。

## 2. 圖卡與頁面識別對照
七張既有圖卡均維持 9:16 或大字直式排版，右下角具正式黑色單色品牌 Logo。原圖由 Pillow 轉換為高品質 WebP（quality=90, method=6），原 PNG 原檔保留於交接暫存區不覆寫：

| 順序 | 原始圖檔名稱 | WebP 路徑 | 頁面 ID / URL | 主標題 | SHA-256 (原圖) |
|---|---|---|---|---|---|
| 1 | 胃藥怎麼吃_圖卡01_開頭_9x16.png | `img/stomach_medicine_guide.webp` | `stomach_medicine_guide` | 胃藥怎麼吃？飯前、飯後、睡前一次看懂 | 797a08e4ff9e9dddb19ae5e4a12d4180c6c80a484b8595e9c03838566d0857c6 |
| 2 | PPI 怎麼吃？用藥重點圖解.png | `img/stomach_medicine_ppi.webp` | `stomach_medicine_ppi` | PPI怎麼吃？耐適恩、泰克胃通服用時間說明 | c3922ccf9a68eda8433ad36e870ef3a04b6d8a396367ec7e80d47b64de9dd7fe |
| 3 | 胃藥怎麼吃_圖卡03_H2阻斷劑_品牌修正版.png | `img/stomach_medicine_h2_blocker.webp` | `stomach_medicine_h2_blocker` | H2阻斷劑怎麼吃？發馬Famotidine服用時間 | 753e4874752123a7bc9995b8275a49270754f6ebce7d0afa155e927cd15270cb |
| 4 | 鎂鋁制酸劑用藥指南.png | `img/stomach_medicine_antacid.webp` | `stomach_medicine_antacid` | 制酸劑怎麼吃？氧化鎂、息痛佳音服用時間與注意事項 | ecda699efad69d06f7cbb4e7620c864b123116495d72320db080783f32abda31 |
| 5 | 胃藥怎麼吃_圖卡05_原始Logo覆蓋版.png | `img/stomach_medicine_alginate.webp` | `stomach_medicine_alginate` | 海藻酸鹽類怎麼吃？胃逆舒、艾胃逆服服用時間 | 3096d994eacf737e02060587ec8385c84bc6a75905331050f01ac1aecfc73d04 |
| 6 | 胃藥怎麼吃？Sucralfate用藥指南.png | `img/stomach_medicine_sucralfate.webp` | `stomach_medicine_sucralfate` | Sucralfate怎麼吃？保胃懸乳液、安胃寧服藥指引 | 35ae6162506594903353f2489deb1afa5b57dc18dfb40b228699ed74933973b8 |
| 7 | 五類胃藥服用時間總整理.png | `img/stomach_medicine_timing_summary.webp` | `stomach_medicine_timing_summary` | 胃藥服用時間總整理：五類胃藥怎麼吃？ | a6d6f6ee0cead2ca24cd6921391a2aeaac0b152662e56e995f232ada53fb4360 |

## 3. 系列設定與分類
- 系列識別碼：`stomach_medicine`（新系列，無既有同名衝突）。
- 分類：`category: "public_education"`（於 `public.html` 展示）。
- 主題：`topics: ["gastrointestinal"]`（對應腸胃篩選分類）。
- 排序：`order: 21.1`（排於幽門桿菌檢查 21 之後，維持腸胃主題聚合）。
- 圖示：`icon: "💊"`。
- 共通頁尾：`showFooter: true`。
- 系列標籤（23個去重關鍵字）：包含 PPI、耐適恩、泰克胃通、百抑潰、H2阻斷劑、發馬、Famotidine、制酸劑、氧化鎂、息痛佳音、海藻酸鹽、胃逆舒、艾胃逆服、Sucralfate、保胃懸乳液、安胃寧、胃黏膜保護劑等。
- 收藏識別鍵：`stomach_medicine-0` 至 `stomach_medicine-6`，逐張穩定對應。
- 系列資料同步寫入 `cards.json` 與 `cards.manual.json`。

## 4. 醫療直接來源定點查核
依定稿主張與圖卡內容，避免單純全篇複製六個連結，定點查核各頁專屬直接來源：
1. **圖卡 1（總入口）**：中國醫藥大學附設醫院（胃藥怎麼吃才對？）、臺大醫院健康教育資訊網（胃食道逆流用藥簡介）、美國胃腸病學會（ACG GERD 指引 2022）。
2. **圖卡 2（PPI）**：臺大醫院健康教育資訊網（PPI 餐前服用與特殊劑型說明）、中國醫藥大學附設醫院（氫離子幫浦抑制劑使用指引）、美國 ACG GERD 指引。
3. **圖卡 3（H2阻斷劑）**：高雄市立凱旋醫院（發馬膜衣錠 Famo 20mg 仿單與用法用量）、中國醫藥大學附設醫院（法瑪鎮膜衣錠用藥提醒）、MedlinePlus（Famotidine 用藥指引）。
4. **圖卡 4（制酸劑）**：中國醫藥大學附設醫院（息痛佳音與胃立舒泰含局部麻醉劑建議飯前整粒吞服、氧化鎂雙重用途）、臺大醫院健康教育資訊網（制酸劑種類與副作用）、英國 NHS（Antacids 制酸劑交互作用）。
5. **圖卡 5（海藻酸鹽）**：英國 NHS（Gaviscon 海藻酸鹽服用時機與機轉）、臺大醫院健康教育資訊網（艾胃逆服咀嚼錠嚼碎服用說明）、中國醫藥大學附設醫院（胃逆舒懸浮液使用提醒）。
6. **圖卡 6（Sucralfate）**：MedlinePlus（Sucralfate 空腹服用與制酸劑/甲狀腺素間隔）、國軍台中總醫院（保胃懸乳液 Scrat 仿單指引）、耕莘醫院（安胃寧錠 500mg 用藥須知）、元宙化學製藥（益胃錠 1000mg 產品與仿單資訊）。
7. **圖卡 7（總整理）**：中國醫藥大學附設醫院（五類胃藥功效與答客問）、臺大醫院健康教育資訊網（胃藥服用原則與交互作用）、美國 ACG GERD 指引。

- 雙日期設定：實際查核日 `sourceCheckedAt: "2026-11-01"`；內容定稿日 `updatedAt: "2026-11-01"`。
- 編修歸屬：`revisionCredit: "使用者提供文案；本站依定稿與官方/學會直接來源核對整理"`。
- 圖文核對：實際放大核對七張圖片之藥名、成分、用法、警語與品牌 Logo，確定與網頁段落完全一致，設置 `matchConfidence: "high"`。
- 醫療審核界線：具名臨床審核證據未提供，保留 `needsMedicalReview: true`，管理清冊之人工醫療審核欄位維持 `unknown`，`review_required: "yes"`。

## 5. 網站建置與驗證結果
- 增量建置：執行 `python -B build.py --incremental stomach_medicine_guide stomach_medicine_ppi stomach_medicine_h2_blocker stomach_medicine_antacid stomach_medicine_alginate stomach_medicine_sucralfate stomach_medicine_timing_summary`。
  - 成功生成七張獨立靜態卡片頁（`cards/stomach_medicine_*.html`）。
  - 全域產物同步更新：`seo.json`、`all-cards.html`、`sitemap.xml`、`sitemap-main.xml`、`sw.js`、`data/card_text_web_integration_report.md`（高信心文字頁面由 245 增至 252 頁，成功率 100%，0 失敗）。
- 網站迴歸檢查：`python -B scripts/check_site.py` 完整通過（Site check passed）。
- 專案管理定點提案：執行 `python -B scripts/check_project_management.py --propose` 七頁回報零差異、零移除、零來源錯誤。
- 專案管理關聯：於 `docs/project-management/content-relations.csv` 登記七筆 `series:stomach_medicine -> page:stomach_medicine_*`（`has_card`）。
- 需求登記：於 `docs/project-management/change-requests.csv` 登記 `CR-2026-057`。
- 變更追蹤驗證：執行 `python -B scripts/project_change_tracker.py --check` 通過。

## 6. 本次變更檔案清單（供 GitHub Desktop 審核）
- `img/stomach_medicine_guide.webp`
- `img/stomach_medicine_ppi.webp`
- `img/stomach_medicine_h2_blocker.webp`
- `img/stomach_medicine_antacid.webp`
- `img/stomach_medicine_alginate.webp`
- `img/stomach_medicine_sucralfate.webp`
- `img/stomach_medicine_timing_summary.webp`
- `cards/stomach_medicine_guide.html`
- `cards/stomach_medicine_ppi.html`
- `cards/stomach_medicine_h2_blocker.html`
- `cards/stomach_medicine_antacid.html`
- `cards/stomach_medicine_alginate.html`
- `cards/stomach_medicine_sucralfate.html`
- `cards/stomach_medicine_timing_summary.html`
- `cards.json`
- `cards.manual.json`
- `data/card_content.json`
- `data/card_text_web_integration_report.md`
- `seo.json`
- `all-cards.html`
- `sitemap.xml`
- `sitemap-main.xml`
- `sw.js`
- `docs/project-management/page-inventory.csv`
- `docs/project-management/content-relations.csv`
- `docs/project-management/change-requests.csv`
- `docs/project-management/project-dashboard.md`
- `docs/project-management/evidence/stomach-medicine-2026-11-01.md`
