# 傷口照護系列重整

實作日期：2026-09-09。新系列搜尋標籤已由使用者確認。

## 新配置

| 代碼 | 系列 | 張數 |
|---|---|---:|
| fall_wound | 小傷口怎麼處理？ | 6 |
| wound_dressings | 敷料怎麼選、怎麼換？ | 5 |
| scar_care | 傷口好了，如何照顧疤痕？ | 3 |
| bruise_care | 瘀青怎麼處理？ | 1 |
| stretch_marks_care | 妊娠紋與肥胖紋 | 1 |
| burn_first_aid | 燙傷怎麼辦？ | 6 |

原 fall_wound 的 12 張圖片各自保留原檔名及分享 URL，透過 favorite_keys 保留原 fall_wound-0 至 fall_wound-11 收藏識別。不要依新順序重編。

新增 4 張：wound_when_to_seek_care、wound_tetanus、hydrocolloid_how_to_use、wound_healing_signs。新增圖片不沿用任何舊收藏識別。

既有圖卡以改版取代，沒有退出或刪除舊分享網址。一般傷口與燙傷的關鍵警訊保留在各自情境中；疤痕產品與類型介紹各自聚焦，避免重複長清單。

另外修訂 burn_first_aid_05，區分敷料的吸收與抗菌用途；修訂 bruising_care_3，避免用力按摩瘀青及把靜脈紅腫當一般瘀青自行處理。

## 文案與來源

`data/wound_care_revision_20260909.json` 保存 18 張改版／新增圖片的標題、逐段文字、提醒與來源；`data/card_content.json` 保存對應網頁文字及查核日期。資料來源查核不表示已由臨床人員簽核，保留 needsMedicalReview 標記。

18 張圖卡均已使用內建 image_gen 完成並轉為 WebP quality 90、method 6。續作補齊疤痕類型、燙傷敷料、瘀青藥膏三張舊圖與四張新增圖卡；四張暫用 SVG 已移除。輸出與核對記錄保存在 `output/wound-care-20260909/generation-log.json`，新增卡提示詞保存在 `new-card-prompts.json`；白底、藍綠標題、圓角區塊、大字繁體中文、四個重點段落及底部警訊為共通規格。

## 後續維護

- 修改圖片時同步更新逐字文案、網頁文字、必要的 tags 與 texts。
- 系列互連使用 related_series，不在多個 steps 重複引用同一張圖片。
- 妊娠紋同時出現在 skin_wound、pregnancy。
- 縫合／術後傷口、糖尿病足、長者皮膚撕裂傷保留為第二批提案，本輪未新增。
- 重新產生頁面使用 python build.py，完成後執行 python scripts/check_site.py。

## 驗證

已完成全部圖片的文案與版面核對、網站重建及 `python scripts/check_site.py` 驗證。文字索引移除四筆暫用圖片格式的重複紀錄，104 張高信心文字頁整合通過。

新增回歸檢查會比對十二張原圖收藏編號、五個系列的資料同步、唯一文字紀錄及 SEO 關鍵字／分享圖片。套用腳本使用改版前固定對應，避免重跑後依新順序重編收藏。

瀏覽器已驗證民眾首頁五個新系列、人工皮搜尋、圖片位於工具列下方、同系列下一張、返回民眾首頁、收藏後由首頁再次開啟同圖、QR 對話框與分享網址；藥師版瘀青系列、新版第三張、文字來源與返回藥師首頁亦正常。測試新增的收藏已移除。社群平台抓圖結果仍需發布後才可驗證。

`python output/wound-care-20260909/verify_revision.py` 通過：重跑套用腳本後四個資料檔雜湊不變，十二張原收藏逐一符合改版前 Git 版本。`git diff --check` 與兩份卡片 JSON 格式檢查通過。

## 發布檔案

GitHub Desktop 提交本次 `img/*.webp`、`cards.json`、`cards.manual.json`、`data/card_content.json`、`data/wound_care_revision_20260909.json`、文字整合報告、`build.py`、`scripts/check_site.py`、`cards/*.html`、`all-cards.html`、`seo.json`、`sitemap.xml`、`sitemap-main.xml`、`sw.js`、`CHANGELOG.md` 與本次文件，再 Push 才會更新正式網站。`robots.txt` 本次沒有差異；`output/` 的 PNG 與執行記錄為製作留存，並非網站執行必需。
