# CR-2026-074 常見腹瀉藥物（diarrhea_drugs）定點證據

日期：2026-11-12

## 範圍

- 新增民眾衛教系列 `diarrhea_drugs`（`public_education`，topics：`gastrointestinal`，order 36.1，`showFooter: true`），五張圖卡：
  1. `diarrhea_drugs_1` 常見止瀉藥怎麼選？正露丸、暮帝納斯、高克痢、Loperamide 用法與注意事項
  2. `diarrhea_drugs_2` 正露丸、暮帝納斯：熟悉的名字，成分不同
  3. `diarrhea_drugs_3` 黃連素類複方：看清楚的不只是黃連素
  4. `diarrhea_drugs_4` 高嶺土＋果膠：高克痢怎麼用？
  5. `diarrhea_drugs_5` Loperamide：減少跑廁所，但要用對情況
- 圖片由使用者提供，轉為 WebP（quality 90, method 6）。轉圖時使用網站現有定稿母版之彩色透明 Logo（`docs/brand/assets/logo_primary_transparent.png`），於圖底預留約 8% 空白橫帶水平置中等比縮放（高 40px，y=971~1011），原圖完整保留；轉圖加 Logo 流程載入 `AGENTS.md` 與 Card Manager。
- 逐頁 `data/card_content.json`：標題、摘要、分段重點、AEO FAQ 問答、altText、雙日期（`2026-11-12`）、12 項直接來源；`needsMedicalReview: true`。
- `seo.json`：title、description、og:title、og:description 依使用者指示設定。
- 內部連結：
  - 本系列頁面連至舒腹達（`smecta_1`）、瀉必寧（`ped_diarrhea_hidrasec`）、腹瀉怎麼辦（`diarrhea_care_1`, `diarrhea_care_2`）。
  - 上述既有頁面之 `related_links` 與 `related_series` 同步回連至本系列第一張（`diarrhea_drugs_1`）。

## 驗證

- 三份 JSON 可正常解析。
- `python -B build.py --only ...` 與全域索引建置完成。
- `python -B scripts/check_site.py`：通過。
- 五頁 `--propose` 合併後：0 提案、0 移除、0 來源錯誤。
- Chrome headless 390px 手機版面截圖檢查正常。
- 具名醫療簽核證據未提供，人工欄位維持 unknown。
