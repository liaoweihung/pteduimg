# 台灣眼科外用藥品資料庫驗證報告

## 1. 納入條件
本資料庫只納入「有明確藥品許可證、可作為市售藥品使用的眼科外用產品」。

納入主表需同時符合：
- 有明確藥品許可證字號
- 有商品名或製劑名稱
- 有眼科外用劑型，例如眼藥水、點眼液、眼用懸液、眼用凝膠、眼用軟膏
- 有明確適應症
- 是最終藥品製劑，不是原料藥

判斷優先欄位：許可證種類、劑型、適應症、包裝／規格、商品名、英文品名。

## 2. 排除條件
已排除原料藥、藥品原料、Active Pharmaceutical Ingredient / API、bulk drug substance、中間體、製劑用原料、非最終銷售製劑，以及缺少明確商品名、劑型、規格或適應症的品項。

判斷為原料藥或非最終製劑者，不放入主表，改列於 `excluded_eye_products.csv`，排除原因為「原料藥／非最終製劑」。

## 3. 更新後資料量
- 主表產品數：514
- 排除產品數：581
- 其中原料藥／非最終製劑：40
- 成分數：146
- 適應症摘要數：21

## 4. 推定用途分類
- NSAID 消炎型：8
- 人工淚液／潤滑型：59
- 其他眼科外用藥：60
- 抗病毒眼藥：1
- 抗菌型：51
- 抗過敏型：15
- 散瞳／睫狀肌麻痺：57
- 疲勞／調節改善型：23
- 眼藥膏：16
- 複方眼藥：8
- 角膜修復／促進上皮修復：29
- 退紅／血管收縮型：57
- 青光眼用藥：69
- 類固醇消炎型：61

## 5. 防腐劑摘要
- 否：510
- 待確認：1
- 是：3

## 6. 產出檔案
- eye_meds_tw_raw.csv
- eye_meds_tw.xlsx
- eye_ingredient_indication_matrix.csv
- eye_ingredient_profiles.csv
- eye_ingredient_cooccurrence.csv
- eye_indication_profiles.csv
- eye_explorer_data.json
- eye_drop_explorer_data.json
- verification_report_eye_meds.md
- excluded_eye_products.csv

## 7. 資料來源
- TFDA 藥品有效許可證資料 InfoId=37
- TFDA 藥品詳細處方成分資料 InfoId=43
- TFDA 仿單與外盒連結資料 InfoId=39
- 查詢入口：https://lmspiq.fda.gov.tw/web/DRPIQ/DRPIQ

## 8. 注意事項
本資料庫依 TFDA 開放資料欄位與規則自動整理，藥品分類、成分標準化與適應症摘要仍建議在實務使用前回查原始許可證與仿單。
