# 失眠與失眠藥物雙系列本機整合

日期：2026-11-13。需求：CR-2026-086。狀態：本機完成，未 Commit／Push，未證實 Pages 部署。

## 範圍與來源

- 依使用者提供的 `AI_doc_exchange_v2/01_production/失眠藥物/insomnia_medication_education_v2.md` 與 `v1/失眠用藥_card01.png`～`card09.png` 製作。使用者表示 2026-11-13 已完成查核；原圖保留於交換區。
- 民眾系列 `insomnia_public`：圖卡 01～03，`public.html` 的 `sleep` 分類。
- 藥師特定產品系列 `insomnia_medication`：圖卡 04～09，`index.html` 的 `pharmacy_general` 科別。兩系列以 `related_series` 在生成頁互相連結。
- 兩系列採用使用者確認的搜尋標籤；各有首頁縮圖。九張原圖轉為 WebP，按右下角背景明度選擇既有深色或淺色單色透明 Logo，等比縮放至圖高約 3.2%，不覆蓋原圖。
- 每頁以 `data/card_content.json` 提供靜態文字、內容日期、查核日期與直接來源。Ramelteon 頁改用現行許可證字號相符的耕莘醫院藥劑部產品資料；提供的光田 PDF 讀取被網站阻擋，未列為該頁直接來源。其他已開啟比對的來源包括中山醫訊及悠樂丁、使蒂諾斯、達衛眠與美舒鬱仿單。

## 醫療與品牌狀態

使用者的「今天查核完成」提供查核日期；尚無具名、限定九張成品版本的醫療複核紀錄，因此新內容保留 `needsMedicalReview: true`，清冊人工狀態為 `unknown`。技術檢查不視為醫療簽核。品牌透明衍生 Logo 仍依品牌文件列為待人工視覺驗收；本次只用於這九張新圖，須在正式發布前目視確認。

## 建置與驗證

- `python -B build.py --incremental insomnia_card01 ... insomnia_card09`：產生九頁，更新 `seo.json`、`all-cards.html`、兩份 sitemap、`sw.js`、整合報告與最近新增。`data/recent-changes.json` 第一筆為 CR-2026-086 的民眾系列。
- 九頁 `--propose`：0 差異、0 移除、0 來源錯誤。`python -B scripts/check_site.py` 通過。
- 全量管理檢查：1158 errors、19 warnings；未提供可信基準，不能判定新增錯誤數。診斷不含本次九頁 ID，既有規則指紋及歷史紀錄問題仍在。
- `project_change_tracker.py --check` 仍因兩筆既有提交缺管理連結及未提交變更狀態退出 1；本次未改動該歷史問題。
- 桌機／手機瀏覽器操作驗收與九張圖卡 Logo 視覺確認尚待完成。

## 收尾核對補記（2026-11-13）

- `python -B scripts/test_project_management.py`：18 項中 16 通過、2 失敗；失敗為既有 snapshot 漂移（1157 項，如 `rules-v2: historical page IDs differ`），與 CR-2026-083 同狀況。全量管理錯誤不含本次九頁 ID。
- **sw.js 版本退回（已修正）**：增量建置把 `coreUrlsToCache` 的 `./css/base.css?v=7`（CR-2026-084 手動升版）改回 `v=6`，因 `build.py` 寫死 `v=6`。經藥師同意並確認改法，`build.py` 新增 `_page_css_ref()`，建置時從 `index.html`（base、pharmacist）與 `public.html`（public）讀取實際引用的 CSS 版本，找不到即報錯。之後執行 `python build.py` 完整建置：`sw.js` 維持 `base.css?v=7`；`all-cards.html`、`seo.json`、兩份 sitemap、首頁與整合報告內容不變。
- **完整建置附帶產物**：266 張既有圖卡頁唯一差異為返回導覽 `topicTitles` 補上 `"sports_injury": "運動傷害"`（CR-2026-083 新增分類時只做增量建置，舊頁未同步）；`cards/bzd_z_sleep_aids.html`（同屬睡眠主題）新增「失眠怎麼辦？睡眠與用藥入門」系列連結。以上為現行模板的技術輸出，未改任何衛教正文。
- **建置後檢查**：`check_site.py` 通過；九頁 `--propose` 零差異；管理測試仍 16/18。全量管理錯誤 1157 → 1158，新增一項為 `skin_glue_care_1: machine field drift: source_sha256`（該頁 HTML 因上述 `topicTitles` 改變而雜湊漂移）。經藥師同意，依 `--propose --page skin_glue_care_1` 只合併該列 `source_sha256`、`rules_sha256`、`checked_at` 三個機械欄位，人工欄位未動；合併後該頁提案零差異，全量管理錯誤降為 1156，`check_site.py` 通過。
- **系列縮圖功能與圖示調整（已確認保留）**：`index.html`、`public.html` 系列列表在系列有 `thumbnail` 時改顯示 48×64 縮圖、否則維持 icon。藥師 2026-11-13 指示：失眠兩系列（`insomnia_public`、`insomnia_medication`）首頁列表改顯示 emoji，不要縮圖。移除兩系列的 thumbnail 設定，`insomnia_medication` 的 icon 從 💊 改為 🌙，與 `insomnia_public` 一致。來源資料與 `cards.json` 保持一致，`index.html`／`public.html` 的縮圖程式保留、本系列不使用縮圖，兩系列 icon 統一為 🌙。重新建置後兩系列列表皆顯示 🌙，`check_site.py` 通過。
- **版本核對**：九頁逐頁文字與 `insomnia_medication_education_v2.md` 第三部分一致（非 v1）：柔速瑞字號 061977（v1 為 025852）、靜安能字號 049273、500 勒克斯均在；達衛眠在圖與文字皆寫「非管制藥品」，與 v2 一致。v1、v2、九頁文字及圖卡均無「FM2／第三級」。
- **圖卡目視附記**：card09 右側中段有一塊鮭紅色矩形，原始 `v1/失眠用藥_card09.png` 即有，非轉檔造成；card06、card07 Logo 底下的深藍／淡紫色塊待 Logo 目視驗收一併確認。
- **來源待藥師決定**：
  - card02 `tendays.com.tw` 支撐：CBT-I 為首選且較持久（與臺灣醫學會共列）、刺激控制「躺床逾 20 分鐘起身、固定時間起床」、限眠療法「每週增加 15～30 分鐘」。
  - card08 `leepsyclinic.com` 支撐：低劑量 25～100 mg 與阻斷 5-HT2A、H1、α1 的鎮靜效果（與美舒鬱仿單共列）。
  - card09 「機轉與定位」段：靜安能仿單（已讀）只支持成人短期緩解入睡困擾、隔日開車小心、連續兩星期未改善應停藥就醫；不含血腦障壁或耐受性。克胺寧三總仿單連結被 Cloudflare 阻擋未能讀取。`ysp.com.tw` 為澄清醫院藥師專文，支撐「親脂性高、穿越血腦障壁」；`e-pharm.info` 為亞東醫院藥學部，支撐「鎮靜延至白天、較少用於慢性失眠」。「容易產生耐受性（連吃數天效果遞減）」在現有來源中均未找到支撐。故未直接替換為仿單連結。
  - **藥師決定（2026-11-13）**：card09「容易產生耐受性」敘述維持原文，不改寫、不補來源；card09 現有五項來源不變。card02 Tendays 與 card08 李政洋身心診所來源保留。
