# 台灣局部眼用藥品資料庫交接包

版本：2026-07-10_v01；資料更新／檢查日：2026-07-10

## 建議匯入順序

1. sources.csv、normalization_rules.csv
2. products.csv、substances.csv、indications.csv、drug_classes.csv
3. product_substances.csv、product_indications.csv、product_classes.csv
4. 四個 statistics/cooccurrence 檔
5. excluded_records.csv、manual_review_queue.csv

## 檔案用途

- products.csv：一張藥證一筆產品；含眼用判定、狀態、預設查詢／統計旗標與保存劑狀態。
- substances.csv：物質主檔；角色不可只讀此表，實際分析以 product_substances.role 為準。
- product_substances.csv：產品配方關聯、含量、角色、製劑功能與確認狀態。
- indications.csv / product_indications.csv：高階適應症群組及產品對應；原文在 products.indication_raw。
- drug_classes.csv / product_classes.csv：ATC、AHFS/DI 分類及產品對應。
- active_ingredient_statistics.csv：適應症－有效成分出現數與比例。
- preservative_statistics.csv：保存劑使用與保存劑狀態。
- excipient_statistics.csv：各製劑功能及劑型下可觀察的賦形劑使用。
- substance_cooccurrence.csv：有效成分或賦形劑的產品層級共現。
- excluded_records.csv：母體中未收錄藥證及原因。
- manual_review_queue.csv：不能安全自動判定或缺詳細成分的紀錄。
- sources.csv / source_manifest.csv：官方來源、資料日期及來源壓縮檔雜湊。
- normalization_rules.csv：本版標準化規則。
- methodology.md / data_quality_report.md：方法、品質檢查與限制。
- HANDOFF_MANIFEST.json：交接完整性、計數與所有檔案 SHA-256。

## 重新產生統計

以 products.default_include_in_statistics=true 篩出產品，連接 product_substances，依 role 分流。active 統計不可加入 preservative 或其他賦形劑；共現以每產品內去重後的 base_substance_group 組合計數。適應症分母來自 product_indications 中各 indication_id 的有效產品數。

## 不可自行推論

- 沒列保存劑不等於無保存劑。
- 缺成分、含量、中文名、使用途徑或賦形劑不可從商品網站補寫。
- confirmed=false 的角色不可稱為官方認定。
- IND999 不可當作具體診斷。
- 失效藥證不可預設進入查詢或統計。
