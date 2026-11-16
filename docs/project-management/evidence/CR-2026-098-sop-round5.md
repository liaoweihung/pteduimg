# CR-2026-098 作業卡第五輪修正：新增共同步驟作業卡

- 範圍：新增 docs/sop/00-common.md；更新 docs/sop/01–07、AGENTS.md、docs/material/README.md（依藥師同意的第五輪規則更新，AI 未額外修改內容）。
- 基準檔：`outputs/mgmt-before-20261116-1225-sop-round5.json`（BASELINE OK；於規則檔已更新後、本 CR 登記前存下）。
- 素材來源：規則更新內容由藥師於 2026-11-16 對話中確認同意；本次不涉及圖卡、圖片或醫療內容，未建置。
- 不包含：工作區同時存在的 CR-2026-097（motion_sickness_meds_2 仿單連結：cards/motion_sickness_meds_2.html、data/label_links.json、sw.js 與其 evidence），本 CR 不碰、不提交。
- 檢查結果：三份 JSON 解析通過；`check_site.py` 通過；變更追蹤未提交變更皆有 CR 連結（僅餘 97575424 舊問題）；基準比對 new=0、resolved=0、worsened=0（persistent=1169）。
