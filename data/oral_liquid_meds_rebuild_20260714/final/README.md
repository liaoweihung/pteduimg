# 台灣口服液劑網站資料

`oral_liquid_meds_final.json` 由上層正式 CSV 關聯表以 `build_final_json.py` 機械產生。

- 僅包含正式有效產品；105 筆 unresolved 候選不會進入此檔案或網站統計。
- 成分僅輸出 `role=active` 且 `confirmation_status=confirmed` 的關聯列。
- `display_concentration` 保留官方顯示格式；`normalized_value_per_ml` 僅供相容單位的內部比較。
- 加水配製產品若沒有明確配製後濃度，會保留 `concentration_pending=true`，不推測濃度。

重建與驗證：

```powershell
python build_final_json.py
python verify_oral_liquid_website_export.py
```
