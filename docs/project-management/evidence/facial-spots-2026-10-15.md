# CR-2026-028｜新增「臉部斑點」六張圖卡

## 授權與範圍

- 使用者於 2026-10-15 確認在 `public.html` 新增「臉部斑點」系列，共六張不重複圖卡。
- 系列依「斑點類型、淡斑成分、保養步驟、防曬、就醫警訊」排序；公開分類為 `skin_wound`，排序在「富貴手」之後。
- 使用者提供圖卡與文字草稿；本次依圖面內容整理逐頁靜態文字及直接來源。
- 新內容保留 `needsMedicalReview: true`；清冊人工醫療狀態、reviewer 與 review date 均為 `unknown`。

## 新增頁面

- `facial_spots_types_sun_freckles`
- `facial_spots_types_melasma_acne_marks`
- `facial_spots_brightening_ingredients`
- `facial_spots_skincare_routine`
- `facial_spots_sun_protection`
- `facial_spots_when_to_see_dermatologist`

六張來源 PNG 由使用者指定的同批下載檔案提供，逐張確認圖面後轉為穩定英文檔名的 WebP；沒有修改或刪除原始 PNG。

## 內容與來源

- 內容更新日期：2026-10-15
- 資料查核日期：2026-10-15
- 主要來源：American Academy of Dermatology 的肝斑治療、自我照護、防曬及黑色素瘤 ABCDE 衛教；DermNet 的曬斑、雀斑、肝斑及色素斑資料。
- 文字版明確區分曬斑、雀斑、肝斑與發炎後色素沉澱；口服傳明酸、Hydroquinone、Tretinoin 及雷射等內容保留醫師評估限制。
- ABCDE 僅作觀察提醒，不宣稱可自行診斷；小於 6 mm 的病灶仍可能需要評估。

## 建置方式

- 因工作目錄已有未提交的 `build.py`、`scripts/site_footer.py` 與三張舊圖卡 HTML 修改，完整建置在隔離暫存副本中執行。
- 暫存建置帶入目前兩份產生器檔、三份本次來源資料及六張新圖片；產生 361 個現行靜態圖卡頁並保留 4 個退出頁。
- 比對後只帶回六張新頁，以及本次確實需要更新的 `all-cards.html`、兩份 sitemap、`seo.json`、`sw.js` 與文字整合報告；`404.html`、`cards/404.html`、`retired-cards.html`、`robots.txt` 雜湊均未變。
- 既有三張未提交圖卡頁與其他工作資料未被覆寫或清理。

## 管理增量

- 需求：`CR-2026-028`
- 新增六筆 `page-inventory.csv`，人工欄位皆維持 `unknown`。
- 新增 `topic:facial-pigmentation` 與 `subtopic:facial-pigmentation:education` 管理集合；兩者皆為 `collection_only`，不是新疾病頁。
- 新增兩筆主題／系列關聯與六筆 `has_card` 關聯。
- 建置前保存 AUD-007 的 193 頁文字整合報告快照；建置後為 199 頁、0 失敗。
- 初次唯讀提案保存在 `facial-spots-proposals-2026-10-15.json`。

## 驗證結果

- `cards.json`、`cards.manual.json` 與 `data/card_content.json` 三份 JSON 語法檢查通過。
- `python -B scripts/check_site.py` 通過；六頁均有靜態文字、內容更新日、資料查核日、直接來源、SEO、共用頁尾及同系列翻頁。
- `python -B scripts/check_project_management.py` 為 0 errors；六頁最終 `--propose` 為零差異、零移除、零 source errors；`python -B scripts/test_project_management.py` 18 項通過。
- 六頁均出現在 `all-cards.html`、兩份 sitemap、`seo.json` 與 `sw.js`；`public.html` 搜尋「臉部斑點」可找到 6 張系列入口。
- 以 390×844 手機視窗抽查第一張、淡斑成分頁及最後一張：圖片寬度未超出內容區、頁面沒有橫向溢出、圖卡後依序出現同系列翻頁列，上一張／下一張可正確循環，文字來源與單一共用頁尾皆存在。
- `git diff --check` 通過；未覆寫工作開始前已存在的其他修改。

機械檢查只確認結構與輸出，不代表人工醫療複核、搜尋排名或正式部署。本次未 Commit 或 Push。
