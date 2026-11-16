# CR-2026-101 希普利敏液頁新增網頁文字

- 範圍：page:ped_cold_cypromin（series:pediatric_cold_syrup）；圖片 img/ped_cold_cypromin.webp 不變。
- 基準檔：outputs/mgmt-before-20261116-2030.json
- 素材來源：網頁文字由 Claude 依現有圖卡內容撰寫，查核來源為核准適應症（晟德希普利敏液，衛署藥製字第043588號）、臺北市立聯合醫院用藥指導單張（TPE202309）、國嘉喜普錠仿單（同成分禁忌）。TFDA 仿單頁本次未能直接開啟。
- 藥師定稿確認：2026-11-16 使用者回覆「確認」（確認文字定稿；未表示已複核，needsMedicalReview 維持 true）。
- 備註：圖卡列「促進食慾」不在核准適應症，網頁文字另段說明。
- 檢查結果：增量建置 12 頁；JSON OK；check_site 通過；清冊 12 頁合併後零差異；變更追蹤未提交變更有 CR 連結；基準比對 new=0、worsened=0。
