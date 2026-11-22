# CR-2026-114 新增吃藥會讓我變胖嗎系列（5張）

- 範圍：series:drug_weight_gain｜page:drug_weight_gain_1～drug_weight_gain_5（5 頁）。連帶變更的既有頁：insomnia_card12、11、10、09、14、ped_cold_cypromin、kidsolone_oral_solution、contraceptive_pills_how_to_take。
- 基準檔：outputs/mgmt-before-20261122-1158.json
- 素材來源：圖片 `D:\Downloads\1綠色分類與頁碼標示-2.png`～`5戒菸後體重與用藥指南-6.png`（加黑字Logo轉WebP）；文字依 2026-11-22 藥師確認文字稿（v7）與網頁文字與SEO（v1）。
- 仿單連結：共 27 筆食藥署仿單連結寫入 label_links.json 與 card_content references。
- 內部連結：5 頁互設連結，並回連 8 頁既有頁面（insomnia_card12、11、10、09、14、ped_cold_cypromin、kidsolone_oral_solution、contraceptive_pills_how_to_take）。
- 複核：needsMedicalReview 為 false；依藥師 2026-11-22 確認定稿文字稿 v7 當場複核（複核者：藥局衛教助手製作者，日期：2026-11-22，依據：吃藥會讓我變胖嗎_文字稿_v7.md）。
- 檢查結果：增量建置 13 頁完成（5 新頁 + 8 既有頁回連）；13 頁清冊提議零差異；JSON OK；check_site 通過；變更追蹤確認有 CR-2026-114 紀錄；5 頁 title、H1、文字重點、FAQ 與 27 筆仿單連結正常；基準比對 new=0、worsened=0（resolved=4）。
