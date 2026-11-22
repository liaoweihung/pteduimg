# CR-2026-115 修正吃藥會讓我變胖嗎系列分類與尼古丁貼片回連

- 範圍：series:drug_weight_gain, series:Nicotine｜page:Nicotine_1。
- 基準檔：outputs/mgmt-before-20261122-1243.json
- 修改內容：
  1. drug_weight_gain 的 topics 移除 travel_medication，僅保留 chronic_conditions。
  2. Nicotine 系列（Nicotine_1 頁面無 card_content.json 紀錄）設定 related_series: ["drug_weight_gain"]，透過相關系列區塊提供回連。
- 複核：系列設定修改，不涉及醫療內容變更。
- 檢查結果：增量建置完成（Nicotine_1 更新相關系列、drug_weight_gain 更新 topics 為 chronic_conditions）；6頁清冊提議零差異；JSON OK；check_site通過；變更追蹤確認有CR-2026-115紀錄；抽查insomnia_card12、Nicotine_1、drug_weight_gain_5連結正確；基準比對 new=0、worsened=0（resolved=3）。
