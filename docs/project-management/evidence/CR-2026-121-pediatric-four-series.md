# CR-2026-121 新增兒科四系列圖卡（尿布疹、蚊蟲叮咬、異位性皮膚炎、過敏性鼻炎，共22頁）

- 範圍：series:diaper_rash、insect_bites、atopic_dermatitis、allergic_rhinitis｜page:22頁。連帶變更的既有頁／系列：topics/pediatric-medicine.html、bugspray_1、ped_cold_cetirizine。
- 基準檔：outputs/mgmt-before-20261124-1014.json
- 素材來源：AI_doc_exchange_v2\01_production 22 張 PNG 圖檔（加黑字 Logo 轉 WebP）；文字依 兒科四系列_上架文字與SEO_2026-11-24.md。
- 內部連結：照 E 節，四系列均連至兒科用藥主題頁；異位性皮膚炎↔過敏性鼻炎；尿布疹 04、蚊蟲叮咬 02→異膚 04；蚊蟲叮咬 01→bugspray_1；過敏性鼻炎 04→ped_cold_cetirizine。
- 複核：依藥師 2026-11-24 確認定稿當場複核，needsMedicalReview 為 false（複核者：藥局衛教助手製作者，日期：2026-11-24，依據：兒科四系列_上架文字與SEO_2026-11-24.md）。
- 檢查結果：build.py --only 建置 22 頁完成；22 頁清冊提議零差異；JSON OK；check_site.py 通過（378 頁靜態文字與 SEO 正常）；變更追蹤確認 48 個未提交網站檔案均連結 CR-2026-121；基準比對 new=0、worsened=0。
