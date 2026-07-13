# 台灣局部眼用藥品查詢工具

## 檔案

- `eye_drop_explorer.html`
- `css/eye-drop-explorer.css`
- `js/eye-drop-explorer.js`
- `data/eye_meds_rebuild_20260711/final/eye_meds_final.json`

## 資料來源

本工具只讀取 `data/eye_meds_rebuild_20260711/final/eye_meds_final.json`。

不重新下載 TFDA 資料、不重新執行 OCR、不修正成分角色、不讀取已刪除舊版資料。

## 呈現規則

- 只有 `substance_role=active` 且 `confirmed_status=confirmed` 的資料會顯示為有效成分。
- 無 confirmed active ingredient 的產品顯示「有效成分待確認」。
- unknown substance 不混入有效成分。
- 保存劑、賦形劑或仿單資料缺漏時顯示「資料未提供」或 leaflet unavailable 狀態，不視為產品錯誤。
- 適應症優先呈現官方原文。

## 功能

- 關鍵字搜尋：中文商品名、英文商品名、藥證字號、有效成分、適應症。
- 篩選：劑型、藥品分類、藥證年份、藥證狀態、成分確認狀態。
- 結果列表分頁載入。
- 產品詳細資料。
- 點選有效成分、分類可反查/套用條件。

## 上線整合

- `calc.html` 已加入「眼科外用藥品查詢工具」入口。
- `sw.js` 已更新快取版本與必要檔案。
