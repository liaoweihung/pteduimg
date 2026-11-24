# CR-2026-122 新增兒科常用藥水系列圖卡（ped_liquid，共 10 頁）

- 範圍：series:ped_liquid｜page:ped_liquid_01～ped_liquid_10。連帶變更的既有頁／系列：topics/pediatric-medicine.html、wempty_suspension、ped_cold_peace_syrup、ped_cold_mintapp_syrup、ped_cold_cetirizine。
- 基準檔：outputs/mgmt-before-20261124-1840.json
- 素材來源：AI_doc_exchange_v2\ped_liquid_gap_20261124\04_images 10 張 PNG 圖檔（加黑字 Logo 轉 WebP）；文字依 05_pages\ped_liquid_pages.md。
- 舊頁互連：wempty_suspension（胃利空）、ped_cold_peace_syrup（鼻福）、ped_cold_mintapp_syrup（敏達）、ped_cold_cetirizine（勝克敏）各加一行互連推薦閱讀。
- 主題頁：topics/pediatric-medicine.html 增加兒科常用藥水系列卡、依藥名找增加 10 項（26→36）及 ItemList 結構化資料。
- 複核：依藥師 2026-11-24 確認定稿當場複核，needsMedicalReview 為 false（複核者：藥局衛教助手製作者，日期：2026-11-24，依據：claude/ped-liquid-gap-10-review-2026-11-24.md 與 ped_liquid_pages.md）。
- 檢查結果：build.py --incremental 14 頁完成（新系列 10 頁＋舊頁 4 頁）；14 頁清冊提議零差異；JSON OK；check_site 通過（388 頁靜態文字與 SEO 正常）；變更追蹤確認 33 個未提交網站檔案均連結 CR-2026-122；基準比對 new=0、worsened=0（resolved=4）。
