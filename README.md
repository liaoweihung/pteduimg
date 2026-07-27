# pteduimg

這是靜態 GitHub Pages 專案，包含藥師與民眾教育工具。

## 台灣局部眼用藥品資料庫

藥師版查詢頁：

- `eye-meds.html`
- 網站資料：`data/eye_meds/site_data.json`
- 清理後資料庫：`data/eye_meds/clean_products.json`
- 交接包：`research/work_handoff/2026-07-10_v01/`
- 匯入報告：`research/work_handoff/IMPORT_REPORT.md`
- 資料稽核：`DATA_AUDIT.md`

## 資料更新流程

1. 從 Work 交接包取得 `HANDOFF_MANIFEST.json` 狀態為 `ready` 的最新版。
2. 將整包資料 materialize 到 `research/work_handoff/<version>/`。
3. 執行：

```powershell
python scripts/build_eye_meds_site.py
```

這會驗證 manifest、檔名、大小、SHA-256、CSV 可讀性與欄位，並重新產生：

- `research/work_handoff/IMPORT_REPORT.md`
- `DATA_AUDIT.md`
- `data/eye_meds/clean_products.json`
- `data/eye_meds/site_data.json`
- `data/eye_meds/active_ingredient_analysis.json`
- `data/eye_meds/preservative_analysis.json`
- `data/eye_meds/excipient_analysis.json`
- `data/eye_meds/summary.json`

人工修正規則不得直接寫入輸出 JSON；請更新交接包中的 `normalization_rules.csv` 或新增可檢查的對照表後再重建。

## 本機啟動

靜態頁需要透過本機伺服器載入 JSON：

```powershell
python -m http.server 8000
```

開啟：

```text
http://localhost:8000/eye-meds.html
```

## 測試

資料與網站基本檢查：

```powershell
python scripts/check_eye_meds_site.py
```

既有卡片網站回歸檢查：

```powershell
python scripts/check_site.py
```

瀏覽器互動測試需要本機 Chrome 與 Playwright 套件：

```powershell
node scripts/smoke_eye_meds_browser.mjs http://127.0.0.1:8000/eye-meds.html
```

JSON 檢查：

```powershell
python -m json.tool data/eye_meds/site_data.json
python -m json.tool data/eye_meds/clean_products.json
```

## 專業聲明

本資料庫供藥師專業查詢與教育參考。資料來源以衛福部食藥署開放資料與交接包列示來源為主；臨床決策仍須以最新仿單、藥證公告、院內規範與病人狀況為準。
