# CR-2026-108 證據紀錄

- 範圍：`series:acne_patch_use`（`acne_patch_how_to_use`、`acne_patch_when_to_use`、`acne_patch_broken_skin`）
- 基準檔：`outputs/mgmt-before-20261119-1406.json`
- 素材來源：`AI_doc_exchange_v2/01_production/痘痘貼/痘痘貼系列_文字與SEO_2026-11-19.md`（2026-11-19 定稿，藥師指示先上線、醫學查核之後補，`needsMedicalReview: true`）
- 備註：圖片不動；逐頁 `keywords` 因 `build.py` 僅由系列層級 `tags` 自動產生且 `apply_card_content_seo()` 未支援逐頁欄位，依指示跳過。
- 檢查結果：增量建置3頁、三頁清冊提議零差異、JSON OK、check_site通過、變更追蹤連結CR-2026-108、兩頁HTML確認標題/摘要/分段重點/推薦閱讀/日期與共用頁尾；基準比對 new=0、worsened=0（resolved=6）。
