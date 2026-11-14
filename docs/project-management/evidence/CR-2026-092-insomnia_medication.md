# CR-2026-092 失眠藥物代表產品仿單連結

- 範圍：insomnia_card04–09 六頁新增七個食藥署仿單連結；不改衛教正文、圖片或醫療日期。
- 素材來源：六頁逐頁文字紀錄的「代表藥品」品名與許可證字號（2026-11-13 版）；藥師於本次對話要求加入所舉例藥物的仿單連結。
- 檢查基準：`outputs/mgmt-before-20261114-insomnia-labels-01.json`（修改前，BASELINE OK）。
- 建置：`build.py --incremental` 成功重產 insomnia_card04–09 六頁，並更新 `sw.js`。
- 驗證結果：2026-11-15 續作時先標記 CR 完成，再合併六頁 `last_updated_at`、`last_updated_cr` 機械欄位；清冊提案零差異、三份 JSON 與 `check_site.py` 通過、變更追蹤確認 CR 連結、七筆連結均出現在六頁 HTML。
- 基準比對：沿用原始基準檔，new=0、worsened=0、resolved=12；本次續作未重新建置，也不 commit／push。
- 外部連結限制：柔速瑞與美舒鬱的食藥署網址由既有許可證字號組成，網頁查閱工具無法開啟；沒有把技術檢查當作醫療複核。
