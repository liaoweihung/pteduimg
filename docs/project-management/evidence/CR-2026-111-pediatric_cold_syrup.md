# CR-2026-111 息咳寧糖漿頁文字補強

- 範圍：page:ped_cold_secorine（系列 pediatric_cold_syrup），逐頁文字與換圖。
- 基準檔：outputs/mgmt-before-20261121-1020.json
- 素材來源：藥師 2026-11-21 於對話中確認文字定稿（摘要 OK、用量段分三段、資料來源 OK）；新增參考資料 https://www.drjadenhealth.com/l/secorine/
- 複核：藥師未表示已複核 → needsMedicalReview=true、清冊改 pending_pharmacist。
- 新圖：藥師提供 D:\Downloads\息咳寧糖漿兒科用藥資訊圖.png（941×1672，9:16，2026-11-21；依提示詞修正適應症為喀痰、瓶身不寫口味、表格「未滿 6 歲」），轉檔加黑色 Logo 覆蓋 img/ped_cold_secorine.webp；圖上文字逐項核對與頁面一致；altText 依新圖更新；imageUpdatedAt=2026-11-21。
- 檢查：清冊提議零差異；JSON OK；check_site 通過；變更追蹤有 CR-2026-111（既有提交 97575424、05e105a1 缺管理連結，非本次）；revisedImageUrls 含新圖；基準比對 new=0、worsened=0。
- 複核：ped_cold_secorine；複核者 藥局衛教助手製作者；2026-11-21；依據本 CR 定稿版本（含新圖）；藥師原話「已覆核 可以commit/push」。登記後重建、清冊零差異、check_site 通過、基準比對 new=0、worsened=0。
