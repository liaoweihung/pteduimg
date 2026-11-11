# CR-2026-073 腹瀉、拉肚子注意什麼？（diarrhea_care）定點證據

日期：2026-11-11

## 範圍

- 新增民眾衛教系列 `diarrhea_care`（`public_education`，topics：`gastrointestinal`、`infant_care`，order 36，`showFooter: true`），六張圖卡：
  1. `diarrhea_care_1` 成人腹瀉怎麼辦？補水、飲食與居家照顧
  2. `diarrhea_care_2` 拉肚子何時要看醫生？成人腹瀉警訊
  3. `diarrhea_care_3` 小孩拉肚子怎麼辦？補水與飲食照顧
  4. `diarrhea_care_4` 兒童腹瀉何時就醫？尿量、精神與危險徵兆
  5. `diarrhea_care_5` 寶寶拉肚子奶要停嗎？母乳、配方奶與副食品照顧
  6. `diarrhea_care_6` 嬰兒腹瀉何時就醫？尿布、喝奶與脫水警訊
- 圖片由使用者提供（PNG），轉為 WebP（quality 90）。
- 逐頁 `data/card_content.json`：摘要（SEO meta description 草稿）、分段重點、每頁一組 AEO 問答、altText、雙日期、直接來源；`needsMedicalReview: true`。
- 搜尋標籤取自使用者提供的 SEO 草稿建議搜尋詞。

## 相對於使用者文字草稿的來源調整

- 嬰兒脫水徵兆採 NIDDK「3 小時以上沒有濕尿布」（先前對話草稿為 6 小時，無直接來源支持）。
- 兒童口服電解質液量採 WHO 年齡分級：10 歲以下每次水便後 100～200 mL；未滿 2 歲 50～100 mL；未滿 6 個月補充前先詢問醫師或藥師。
- 諾羅病毒「症狀停止後 48 小時內避免備餐」改引美國 CDC（台灣疾管署 Q&A 未載明時數）。
- 中國醫藥大學附設醫院衛教單張（no=5467）：本站無法連線，由使用者自行開啟核對。

## 驗證

- 三份 JSON 可解析。
- `python -B build.py --incremental diarrhea_care_1 … diarrhea_care_6`：6 頁寫入；seo.json、all-cards.html、兩份 sitemap、sw.js、整合報告更新。
- `python -B scripts/check_site.py`：通過。
- 六頁 `--propose` 合併後：0 提案、0 移除、0 來源錯誤。
- 完整管理檢查：457 項錯誤與 19 項警告，均為既有範圍（便祕系列等），無 diarrhea_care／CR-2026-073 相關錯誤。
- `project_change_tracker.py --check`：未提交變更已連 CR-2026-073；既有提交 97269bc9 缺管理連結（非本次範圍）。
- 本機 http 伺服器 + Chrome headless：`diarrhea_care_6` 手機 390px／桌機 1200px 無 JS 錯誤，文字版重點、雙日期、來源與同系列導覽正常；`public.html` 胃腸相關與嬰幼兒照護篩選均出現本系列。

## 未解

- 具名醫療簽核證據未提供，人工欄位維持 unknown。
- 依使用者指示僅製作頁面：未 Commit／Push，未發布。

## 後續修訂（同日）

- 六頁 `revisionCredit` 依使用者指示改為「使用者提供圖卡、網頁文字與網址；本站整理逐頁靜態文字並核對直接來源」，增量重建六頁。
- 第 5、6 張加入 `related_links`（推薦閱讀）連至 `cards/ped_diarrhea_hidrasec.html`；新增兩筆 `further_reading` 關聯；Hidrasec 頁本身未修改。
- 重建後 `--propose` 合併零差異、`check_site.py` 通過。
