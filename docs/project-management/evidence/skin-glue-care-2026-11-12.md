# CR-2026-080 皮膚組織膠返家照護（skin_glue_care）定點證據

日期：2026-11-12

## 範圍

- 依 AI_doc_exchange 交換流程第 5 步上架皮膚組織膠衛教圖卡。
- 新增公眾衛教系列 `skin_glue_care`（`public_education`，topics：`skin_wound`，order 3.55，`showFooter: true`），共 1 張圖卡：
  1. `skin_glue_care_1` 傷口用了皮膚組織膠，回家怎麼照顧？
- 圖片由使用者於交件箱提供（`03_img_codex/皮膚組織膠_card01_v2_done/皮膚組織膠_card01.png`），經步驟 4 審查通過。轉為 WebP（`img/skin_glue_care_1.webp`，quality 90, method 6）。轉檔時使用網站現有定稿深色單色透明 Logo（`docs/brand/assets/logo_black_transparent.png`），配置於右下角（高 58px，右距 30px，底距 25px）等比縮放，不遮到文字與警示框，原圖完整保留。
- 寫入 `data/card_content.json`：標題、摘要、各段重點、AEO 問答、altText、雙日期（`2026-11-12`）、直接來源（美國 FDA、衛福部食藥署、NHS、臺中榮總），`needsMedicalReview: false`（藥師已審，Claude 04 核對通過）。
- `seo.json`：title、description、h1、image_alt、keywords、og 依使用者提供之定稿 SEO 設定。
- 站內互連：
  - 連至術後傷口照護（`postoperative_wound` -> `postoperative_wound.html`）。
  - 連至傷口敷料（`wound_dressings` -> `oint_choose.html`）。
  - 連至除疤照護（`scar_care` -> `prevent_scar.html`）。

## 2026-11-12 上線後檢查修正（v2）

- 依步驟 6（Claude）複查意見修正：
  1. 推薦閱讀連結 404 修正：敷料改為 `oint_choose.html`、除疤改為 `prevent_scar.html`。
  2. 回診就醫警訊三條改為標號分條呈現（① ② ③），改善頁面閱讀性。
  3. `data/recent-changes.json` 重新生成並確認第一筆為 `skin_glue_care`。
  4. 規範補全：於 `AGENTS.md` 與 Card Manager Skill 明確載入「先將 CR 標為 completed，再做最後一次 build」。
  5. 完整建置完成，`check_site.py` 與定點 `--propose` 零差異通過。
