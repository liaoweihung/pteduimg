# CR-2026-119 全站分頁圖示改為單色大鬍子臉（2026-11-23）

- 範圍：所有既有 `rel="icon"`；`build.py`、`scripts/card_archive.py` 經作者同意只改 favicon 一行。
- 基準檔：`outputs/mgmt-before-favicon-20261123-012227.json`。
- 素材：作者提供的 `04_delivery/favicon-mono/` 內 `favicon-mono-32.png`、`favicon-mono-192.png`，原檔複製。
- 結果：完整建置468張卡片頁、4個退出頁與退出紀錄頁；10頁既有產物漂移還原為只留favicon差異並重算sw快取版本；502個原有favicon的已追蹤HTML均為兩行新連結、舊連結殘留0、其他內容零差異；清冊僅合併127頁192個本次機械指紋欄位（原有漂移未動，故未做全站提議零差異）；JSON OK；check_site通過；變更追蹤確認本次變更有需求紀錄（另列4筆舊commit缺連結）；16種頁面瀏覽器實測新圖示可載入；基準比對 new=0、worsened=0。
- 既有漂移10頁（待另案）：10_common_questions、breastfeeding_minor_engorgement、drug_weight_gain_1～5、ear_1、hydrocolloid_how_to_use、motion_sickness_meds_2。
