# CR-2026-029 護膝怎麼穿系列證據

## 授權與範圍

- 使用者於 2026-10-16 授權新增「護膝怎麼穿？」七張圖卡至 `public.html`，排序在「彈性襪」之後。
- 原始圖片為使用者指定之同批七張圖，轉為穩定英文檔名的 WebP；未改動其他系列圖片。
- 使用者提供逐張完整文字並聲明文字與圖卡內容已人工完成審核。
- 使用者未提供審核者姓名、專業資格或簽署日期，因此管理清冊的正式醫療複核狀態維持 `unknown`，來源資料維持 `needsMedicalReview: true`；此作法不否定使用者的審核聲明，只避免虛構可追溯簽核。
- 本次未授權 Commit、Push 或發布。

## 系列與頁面

- 系列 ID：`knee_brace_use`
- 分類：`public_education`
- 主題：`chronic_conditions`
- 順序：`order: 0.1`，位於 `compression_stockings` 之後。
- 頁面：`knee_brace_fit`、`knee_brace_sleeve_steps_1_2`、`knee_brace_sleeve_steps_3_4`、`knee_brace_wrap_steps_1_2`、`knee_brace_wrap_steps_3_4`、`knee_brace_tightness`、`knee_brace_safety`。

## 內容與來源

- 七頁均有靜態文字版重點、內容更新日期 `2026-10-16`、資料查核日期 `2026-10-16`、替代文字、直接來源與共用頁尾。
- 使用者文稿是圖文配對與修訂依據；網頁來源另以官方醫療機構資料支持穿戴、皮膚壓迫檢查、清潔保養與就醫警訊。
- 主要來源：Northern Care Alliance NHS Foundation Trust 的 Knee Braces 與 Knee Brace/Splint、Kingston and Richmond NHS Foundation Trust 的 Hinged knee brace、NICE NG226、NHS Knee pain。

## 建置與隔離

- 因工作目錄原有 `build.py`、`scripts/site_footer.py` 與三張舊卡頁等無關修改，完整建置在隔離複本執行。
- 隔離建置產生 368 個現行靜態卡頁，保留 4 個退出頁，文字整合 206 成功、0 失敗。
- 僅將本系列七個新頁及確實變動的全域生成檔帶回工作目錄；既有無關修改未還原或納入本系列工作。
- 建置前 199 頁整合報告已保存為 `card-text-integration-before-knee-brace-2026-10-16.md`。

## 管理增量

- CR：`CR-2026-029`
- 清冊：新增七列；人工欄位未由機械提案覆蓋。
- 關聯：新增一個 topic、一個 subtopic、兩條管理關聯與七條 `has_card` 關聯。
- 初始 `--propose` 輸出保存於 `knee-brace-proposals-2026-10-16.json`。

## 驗證結果

- 三份來源 JSON 與 `content-topics.json` 語法檢查通過。
- `python -B scripts/check_site.py` 通過；206 張高可信文字頁均有靜態文字及 SEO 欄位。
- `python -B scripts/check_project_management.py` 通過，0 個管理錯誤；保留既有未知盤點日及臨床簽核不足提示。
- 七個新頁的最終 `--propose` 為零差異、零移除、零來源錯誤。
- `python -B scripts/test_project_management.py` 共 18 項通過。
- 390×844 手機檢查確認 `public.html` 顯示本系列且位於彈性襪之後；七頁無橫向溢出，均有圖下兩個翻頁按鈕、靜態文字、日期、來源與單一共用頁尾。
- `git diff --check` 通過。

## 限制

- 技術驗證不等於醫療、法規或搜尋排名驗收。
- 本機完成不代表 GitHub Pages 已部署。
