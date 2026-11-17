# CR-2026-106 執行紀錄：失眠藥物系列重製換圖與追加卡10-14

- **變更範圍**：series:insomnia_public, series:insomnia_medication, page:insomnia_card01 ~ page:insomnia_card14
- **開工基準**：outputs/mgmt-before-20261117-1122.json
- **素材來源**：
  - 圖片：d:\\Downloads\\失眠圖卡_更新專案說明後\\insomnia_cards_2026-11-17\\insomnia_cards_2026-11-17\\images（14 張 PNG，重製插畫風，加 Logo 轉為 img/insomnia_card01.webp ~ img/insomnia_card14.webp）
  - 依據文件：2ea94ff0-insomnia_medication_education_v6.md（卡 10–14 醫療內容已於 2026-11-14 查核）
  - 文字檔：insomnia_card10-14_card_content.json（5 筆新卡，needsMedicalReview: true）
  - 仿單檔：insomnia_card10-14_label_links.json（5 筆食藥署仿單連結）
  - 卡 01~09 沿用既有文字並更新 imageUpdatedAt 為 2026-11-17
- **系列設定調整**：insomnia_medication 標題改為「失眠藥物：代表產品與安全提醒」，新增卡 10-14 steps、texts、favorite_keys 與 tags

## 檢查結果

- 增量建置14頁完成；14頁清冊提議零差異；JSON OK；check_site通過；變更追蹤確認有CR-2026-106紀錄；基準比對 new=0、worsened=0。
