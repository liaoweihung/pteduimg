# CR-2026-083 運動扭傷三張圖卡定點證據

- 日期：2026-11-13（Asia/Taipei）。
- 範圍：`sports_sprain` 三頁（`sports_sprain_1`、`sports_sprain_2`、`sports_sprain_3`），民眾頁「運動傷害」分類。網站未顯示審核者身分。
- 作者授權與人工覆核：使用者於本對話表示「藥師覆核通過」，其後明確表示「上架。藥師就是網站作者……剛剛覆核」。此紀錄僅指本系列三張圖卡及交接的網頁文字；不是其他頁面的簽核。
- 關鍵字與標籤：使用者於本對話選擇「採用建議」，核准關鍵字「運動扭傷、腳踝扭傷、扭傷急救、扭傷冰敷、扭傷何時就醫、扭傷後運動」及標籤「運動傷害、扭傷、急性處置、恢復運動」。
- 分類修改：使用者另明確同意新增「運動傷害」篩選，核准修改 `public.html`、`build.py` 的分類名稱表及 `skills/pteduimg-card-manager/references/card-data.md` 的合法分類清單。未更動其他建置邏輯。
- 圖文來源：`AI_doc_exchange/03_img_codex/` 中各卡最高版本 `_done` 圖片與 `04_check_seo_claude/運動扭傷_page_seo_v5_done.md`；三份最新 imgcheck 皆「通過」。原 PNG 保留於交換資料夾，網站使用從其轉製的 WebP，右下方以既有 `docs/brand/assets/logo_black_transparent.png` 等比疊圖（高 60px），無白框，不遮字。
- 醫療來源：NHS〈Sprains and strains〉、NHS〈Ibuprofen for adults〉、CUH〈Discharge advice: Following attendance with ankle sprain〉、ACR〈Acute Trauma to the Ankle〉及健保署〈肌肉拉傷、關節扭傷、脫臼及骨折〉。交接草稿於 2026-11-12 直接查核；Codex 於 2026-11-13 再讀 NHS、CUH、健保署頁。ACR 本次讀取受 403 阻擋，沿用 2026-11-12 Claude 的直接查核紀錄。
- 內容建立／修訂日：2026-11-12。資料查核日沿用 2026-11-12；上架與建置不刷新醫療日期。
- 建置：`python -B build.py` 完整建置產生 437 個現行頁；因新分類名稱映射使 266 個無關舊頁各產生一行變動，逐檔確認僅該映射後還原，保留三個新頁及全域產物。其後修正頁面修訂歸屬為不揭露審核者的「Codex 草稿、Claude 修訂」，以 `python -B build.py --incremental sports_sprain_1 sports_sprain_2 sports_sprain_3` 更新三頁與 `sw.js`。CR 已先設 `completed`，最後建置後 `data/recent-changes.json` 第一筆為本系列。
- 清冊：三頁由 `--propose --page` 建議的機械欄位逐列合併，追加三筆 `has_card` 關聯；再次執行同一提案為零差異、無來源錯誤、無移除頁。人工複核欄位只對本次三頁寫入使用者聲明與對應內容指紋，未觸動舊頁人工欄位。
- 三頁 `content_sha256`：`sports_sprain_1` = `64ebf5c921d8bd042d6a1f5ce7e2518e7a30876e39e0a19c66e043ddcc5f718c`；`sports_sprain_2` = `11e7a3918c8b4413821796f2b2296af583127640bf3a15f50992f4afc303cc0b`；`sports_sprain_3` = `03d4794058e77b1cfc2212f8482fdc980ac6aee82b4fecf05eee3380cad971e6`。
- 檢查：`python -B scripts/check_site.py` 通過；三頁逐一確認靜態文字、雙日期、來源連結、翻頁、推薦閱讀、SEO／OG、QR／分享／收藏程式入口、共用頁尾、兩份 sitemap、all-cards、PWA 圖檔與最近新增。右下 Logo 以三張圖合併預覽確認未遮字。
- 全量管理檢查：1160 errors、19 warnings，報告在忽略輸出 `outputs/management-check-sports-sprain-2026-11-13.json`；本次三頁及 CR-2026-083 無錯誤或警告。未提供可信基準，因此不能宣稱整站沒有新增錯誤。`scripts/test_project_management.py` 18 項中 16 通過，兩項現況快照測試因上述 1160 筆錯誤失敗。`scripts/project_change_tracker.py --check` 識別本次未提交變更連到 CR-2026-083，但因既有提交 `97575424`、`05e105a1` 缺管理連結而退出碼 1；未在本次範圍補登。
- 瀏覽器：本機服務與本機檔案無法經此工作階段的瀏覽器工具開啟，桌機／手機實際互動驗收未完成；靜態 HTML 與圖片檢查不等於瀏覽器操作驗收。
