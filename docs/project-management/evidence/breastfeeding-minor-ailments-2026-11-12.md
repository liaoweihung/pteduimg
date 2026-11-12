# CR-2026-076 哺乳期間小毛病（breastfeeding_minor_ailments）定點證據

日期：2026-11-12

## 範圍

- 新增公眾衛教系列 `breastfeeding_minor_ailments`（`public_education`，topics：`pregnancy`、`infant_care`、`gastrointestinal`，order 34，`showFooter: true`），共 9 張圖卡：
  1. `breastfeeding_minor_fever_pain` 哺乳期間頭痛、發燒可以吃什麼？
  2. `breastfeeding_minor_rhinitis` 哺乳期間鼻塞、流鼻水可以用什麼？
  3. `breastfeeding_minor_cough` 哺乳期間咳嗽可以吃什麼？
  4. `breastfeeding_minor_constipation` 哺乳期間便祕可以用什麼？
  5. `breastfeeding_minor_diarrhea` 哺乳期間拉肚子，可以吃止瀉藥嗎？
  6. `breastfeeding_minor_reflux` 哺乳期間胃酸逆流、胃不舒服可以吃什麼？
  7. `breastfeeding_minor_itch` 哺乳期間皮膚癢，可以擦藥或吃藥嗎？
  8. `breastfeeding_minor_insomnia` 哺乳期間睡不好，可以怎麼做？
  9. `breastfeeding_minor_engorgement` 哺乳期間乳房脹痛、塞奶怎麼辦？
- 圖片由使用者提供，轉為 WebP（quality 90, method 6）。轉檔時使用網站現有定稿深色單色透明 Logo（`docs/brand/assets/logo_black_transparent.png`），配置於右下角（高 36px，右距 24px，底距 20px）等比縮放，原圖完整保留。
- 寫入 `data/card_content.json`：標題、摘要、各段重點、AEO 問答、altText、雙日期（`2026-11-12`）、直接來源（LactMed、NHS SPS、ABM Protocol #36），`needsMedicalReview: false`（藥師已審）。
- `seo.json`：title、description、h1、image_alt、keywords、og 依使用者指示設定，keywords 僅保留各卡專屬字詞。
- 站內互連：
  - 與「懷孕期間小毛病」8 張對應卡一對一雙向互連（`pregnancy_minor_ailments` ↔ `breastfeeding_minor_ailments`）。
  - 各卡連至既有相關頁（洗鼻器、鼻噴劑、喉嚨痛、便祕藥、浣腸、腹瀉照護、止瀉藥、胃藥指南、異位性皮膚炎、助眠藥分類）。
  - 卡 1 與 卡 9 雙向互連。
- 主題名稱修改：`build.py` 的 `"pregnancy": "懷孕"` 改為 `"懷孕與哺乳"`。
