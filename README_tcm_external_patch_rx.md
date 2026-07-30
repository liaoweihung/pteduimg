# 中藥外用貼布與處方外用藥資料集

本資料集只從專案既有的中成藥資料分檔重建，供 `tcm_external_patch_explorer.html` 使用。

```powershell
python scripts/build_tcm_external_patch_rx.py
```

輸出固定為 577 筆：564 筆藥膠布劑與 13 筆須由中醫師處方使用的外用產品（油膏劑、外用粉劑、軟膏劑、硬膏劑）。

母方與加減藥材為既有組成相似度推測，不是歷史源流、製造商聲明或確定處方來源。
