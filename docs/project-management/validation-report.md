# v1 本機驗證與交付紀錄

日期：2026-10-13。驗證對象為本機工作目錄；基準 HEAD `333ed52512cfbaf2b0f900e76605bc0b5c8264cc`。本次沒有 Commit、Push、部署或網站建置；既有網站與報告維持原狀。

## 交付狀態

- **已完成**：六個核心管理檔案、使用說明、37份歷史證據索引、338個非退出圖卡網址與4退出頁的唯一清冊、青春痘試點關聯及唯讀驗證工具。
- **部分完成**：舊專案的證據與待辦已整合；缺少日期、簽核、來源或測試的部分明確保留unknown。資料庫只在專案／報告／原始佇列層整合，不另複製產品資料。
- **尚未完成且不在本次實作範圍**：24組歷史／技術待辦的修正、醫療複核、資料庫候選解決、計算器公式验证、真實病例測試、AEO／搜尋成效測量、線上部署確認。登記不表示已核准執行。

## 新增檔案（11個）

| 檔案 | 用途 |
|---|---|
| [project-dashboard.md](project-dashboard.md) | 專案狀態、數量口徑、下一步及未納入範圍 |
| [page-inventory.csv](page-inventory.csv) | 342唯一頁：334 current、4 hidden、4 retired；分離人工與機械欄位 |
| [change-requests.csv](change-requests.csv) | 25筆：24 registered/not_approved，1筆本次管理建置completed |
| [audit-history.md](audit-history.md) | 舊結果、後續變化、衝突、Commit及追加規則 |
| [content-topics.json](content-topics.json) | 25節點；正式主題、規劃、內容集合分開 |
| [content-relations.csv](content-relations.csv) | 396條多對多關聯；單一卡頁可被多處引用 |
| [README.md](README.md) | 權威來源、狀態字典、增量工作流程及人工保護規則 |
| [audit-register.json](audit-register.json) | 37份報告的穩定ID、來源、日期、版本、指紋 |
| [validation-report.md](validation-report.md) | 本次交付範圍與驗證紀錄 |
| [check_project_management.py](../../scripts/check_project_management.py) | 預設唯讀檢查；--propose只輸出機械欄位差異 |
| [test_project_management.py](../../scripts/test_project_management.py) | 記憶體內負向測試，不修改測試用網站檔案 |

## 數量與已知問題

清冊來自83系列、342次steps引用、338個唯一非退出網址；4張混擦卡同屬兩系列而不複製頁面。另4退出頁保留原URL與圖片。`cards/404.html`不納入清冊。4個hidden系列無publish_at，HTML仍存在，不能宣稱隱藏檔案是私密。沒有pending系列。

37份既有文件包含26份盤點／品質／測試報告、5份維護交接、4份建置摘要、1份生成報告與1份規格；19份未明示實際盤點日期，保持unknown。Git提交日另列，不補造盤點日。沒有刪除或重寫原報告。

目前有24組未結案需求，312個非退出頁關聯至少一項已知問題或結構／證據缺項，其中114頁需定點複核、224頁醫療狀態unknown、0頁標為藥師已複核。這些集合重疊，不能加總成醫療錯誤數。4筆清冊documented_status=conflict；中藥POC的信心方法衝突另在報告層。未重新閱讀全站圖片或外部醫療文獻。

技術讀取結果：176頁有文字區塊（175段落原文字串一致、1處字詞差異），162頁無文字；91頁有引用連結、247缺少；70頁可見雙日期、21頁只有部分標示、247缺少；338頁SEO基本標记通過；133頁JSON-LD可解析、205頁缺少；55頁有共用頁尾基本結構、283頁缺少。**這些是明確限定的機械事實，不是醫療／法律審查或完整SEO/AEO驗收。**

一處生成字詞差異是`09_australia_usa_china`：來源含「不保證」，build.py既有字串清理移除「保證」後HTML不同。CR-2026-023記錄兩種檢查口徑，不因舊整合報告176成功而自動判定無問題；本次不修改原文或產生器。

## 青春痘關聯測試

| 檢查 | 結果 |
|---|---|
| 疾病→五個現有公開區塊→系列→圖卡 | 7系列、33張核心／酒糟延伸卡與權威metadata一致 |
| 正式頁與錨點 | topics/acne.html及face-wash、identify、medicines、now、marks存在 |
| 四頁Pilot範圍 | acne_stage、acne_topicals_02_retinoids、acne_patch_when_to_use、acne_patch_broken_skin；沒有新增Pilot來源 |
| 下一問與回主題 | 12條下一問＋4條回主題關聯，與acne_navigation精確一致；HTML實際href存在 |
| 共用頁多對多 | scar_remove_detail及scar_remove在青春痘、傷口管理關係引用同一page ID，仍屬原scar_care系列 |
| 酒糟鑑別與工具 | 關係可表達；Phase1鑑別／成分工具提案保持documented_proposal，不宣稱已實作 |
| 未建立主題 | 飲食／荷爾蒙／口服治療planned；皮膚、長照、婦幼、乾眼、香港腳等collection_only；沒有新建公開HTML |
| 全部關聯端點 | 396條均可解析；342條原始has_card與cards.json完整對應 |

## 執行結果

```text
python -B scripts/check_project_management.py
PASS: 0 management validation errors. Read-only; no files written.

python -B scripts/check_project_management.py --propose
machine_field_proposals: []
removed_ids_require_manual_retirement_check: []
source_errors: []

python -B scripts/test_project_management.py
Ran 18 tests — OK

git diff --check
通過
```

管理驗證的NOTE包含19份未知盤點日期及未取得完整臨床簽核，這些是保留的資料限制；PASS只代表管理資料一致，不會把unknown清成通過。

18個測試包含正常基準、重複頁ID、重複需求ID、缺頁、缺關聯、失效目標、退出頁誤列、非法狀態／日期、缺證據、未簽核卻宣稱藥師通過、內容版本改變、Pilot多加連結、報告指紋變動、未核准結案、收藏鍵變動，以及禁止寫檔與保留人工欄位。所有故障均在記憶體複本注入；真實網站與管理資料未被測試竄改。

工作開始時對`git ls-files -co --exclude-standard`可見的1,155個既有一般檔案記錄SHA-256；完成前逐檔比對：**0個既有檔案被修改或刪除**。不涵蓋.git內部、被忽略的依賴與其他repository。新檔只限上列11個，沒有Python cache交付檔。

未執行build.py或scripts/check_site.py：本次沒有改網站行為，依AGENTS文件型任務不需建置；獨立管理驗證不取代將來網站變更必須執行的原有回歸檢查。沒有瀏覽器操作、網路查核、Search Console存取、全站醫療重審或部署驗證。

## 下一階段

先把總控台／README作日常任務入口，試行一次單頁修改及一次新卡追加。依--propose只合併受影響機械欄位，保留人工簽核與未結案需求；驗證成功後追加對應歷史事件。之後再視實際使用經驗，另案決定是否將入口加入AGENTS或加入CI唯讀檢查，避免現在就擴張為自動发布或全站重審。

## 2026-10-14 追加：CR-2026-026 新卡增量試行

上方為管理系統初建時的歷史驗證，不以本次數量覆寫。本次新增「彈性襪」八頁，public.html 一般系列列表置頂；依授權完整建置網站索引、PWA及新頁，未擴大改寫既有圖卡。

- 清冊由342列增為350列；原342列人工欄位完全保留。新頁的人工醫療狀態unknown，原始文字 needsMedicalReview=true。
- 管理主題增加2個 collection_only 節點，關聯由396增為406；沒有虛構已上線的主題專頁。原24筆未核准需求保持原狀，CR-2026-026 完成本機製作，不表示發布或臨床簽核。
- --propose 先輸出8筆新增，逐筆合併機械欄位後再次檢查為零差異、零移除、零來源錯誤；[提案留存](evidence/compression-stockings-proposals-2026-10-13.json)。
- check_site.py 通過；check_project_management.py 零管理錯誤；test_project_management.py 18項通過。保留18份未知報告日期及未取得完整臨床簽核提示。
- 八頁皆有靜態收合文字、真實雙日期、直接來源、SEO與共用頁尾，並出現在兩份sitemap、all-cards、seo及service-worker資產清單。
- 八頁分別以1280×720及390×844檢查圖片、無橫向溢出及同系列翻頁；翻頁列位於圖下，不浮在螢幕底部。返回public入口、收藏及QR操作正常。
- 原343個HTML逐檔對照開工快照不變；AUD-007原報告快照先保存再登記新版本與指紋，既有文字差異CR-2026-023仍保持conflict。
- 本次未Commit/Push；沒有宣稱GitHub Pages已部署。內容與來源日期為2026-10-13，驗收日為2026-10-14。

完整範圍、圖片對應與測試限制見[任務證據](evidence/compression-stockings-2026-10-13.md)。

## 2026-10-14 追加：CR-2026-027 營養品系列

上方初建與 CR-2026-026 紀錄保持歷史版本。本次新增「營養品怎麼選」九頁，完整建置網站索引、PWA、新頁與管理增量，不重新進行全站醫療盤點。

- 清冊由350列增為359列；新頁人工醫療狀態均為 unknown，來源 `needsMedicalReview=true`。
- 管理主題增加2個 `collection_only` 節點，關聯由406增為417；沒有建立或宣稱獨立疾病主題頁。
- `--propose` 先輸出9筆新增，合併後為零差異、零移除、零來源錯誤。提交前 Git 定點查核確認彈性襪八頁的圖片、HTML與文字紀錄相對目前 HEAD 無差異；原清冊雜湊已與可重算證據不一致，因此只同步八頁機械雜湊與檢查日期，人工欄位及頁面內容未改。證據見 `evidence/compression-stockings-fingerprint-sync-2026-10-14.md`。
- `python -B scripts/check_site.py` 通過；`check_project_management.py` 為0錯誤；`test_project_management.py` 18項通過；三份JSON語法檢查通過。
- 九頁皆有靜態收合文字、雙日期、直接來源、SEO、JSON-LD與共用頁尾，並出現在兩份 sitemap、all-cards、seo 及 service-worker 資產清單。
- 手機寬度預覽確認 public 入口、第一與第九張圖片、圖下翻頁、1/9與9/9循環、文字來源及固定頁尾。
- 完整建置後將原本乾淨的舊圖卡頁還原；`git diff --name-only -- cards` 仍只有開工前已存在的三張修改頁，本次新增九張頁另為 untracked。
- AUD-007 的184頁報告先保存快照，再更新為193頁版本；舊字詞差異 CR-2026-023 仍保留。
- 本次未 Commit、Push 或驗證 GitHub Pages 部署。內容及來源查核日為2026-10-14。

完整範圍、來源與測試限制見[任務證據](evidence/elderly-nutrition-supplements-2026-10-14.md)。

## 2026-10-15 追加：CR-2026-028 臉部斑點系列

上方初建與先前新增系列紀錄保持歷史版本。本次新增「臉部斑點」六頁，完整建置公開入口、網站索引、PWA、新頁與管理增量，不重新進行全站醫療盤點。

- 清冊由359列增為365列；新頁人工醫療狀態均為 unknown，來源 `needsMedicalReview=true`。
- 管理主題增加2個 `collection_only` 節點，關聯由417增為425；沒有建立或宣稱獨立疾病主題頁。
- `--propose` 先輸出6筆新增，合併後為零差異、零移除、零來源錯誤；原清冊人工欄位未覆蓋。
- `python -B scripts/check_site.py` 通過；`check_project_management.py` 為0錯誤；`test_project_management.py` 18項通過；三份JSON語法檢查及 `git diff --check` 通過。
- 六頁皆有靜態文字、雙日期、直接來源、SEO與共用頁尾，並出現在兩份 sitemap、all-cards、seo 及 service-worker 資產清單。
- 390×844 手機預覽確認 public 搜尋入口、第一張、中間淡斑成分頁與最後一張；圖片沒有橫向溢出，圖下翻頁列及首尾循環正確，文字來源與單一共用頁尾存在。
- AUD-007 的193頁報告先保存快照，再更新為199頁版本；既有字詞差異 CR-2026-023 仍保留。
- 本次未 Commit、Push 或驗證 GitHub Pages 部署。內容及來源查核日為2026-10-15。

完整範圍、來源與測試限制見[任務證據](evidence/facial-spots-2026-10-15.md)。

## 2026-10-16 追加：CR-2026-029 護膝怎麼穿系列

上方初建與先前新增系列紀錄保持歷史版本。本次新增「護膝怎麼穿？」七頁，完整建置公開入口、網站索引、PWA、新頁與管理增量，不重新進行全站醫療盤點。

- 清冊由365列增為372列；使用者聲明文字與圖卡內容已人工審核，但因未提供審核者姓名、資格與日期，正式醫療複核欄位維持 unknown，來源 `needsMedicalReview=true`。
- 管理主題增加2個 `collection_only` 節點，關聯由425增為434；沒有建立或宣稱獨立疾病主題頁。
- `--propose` 先輸出7筆新增，合併後為零差異、零移除、零來源錯誤；原清冊人工欄位未覆蓋。
- `python -B scripts/check_site.py` 通過；`check_project_management.py` 為0錯誤；`test_project_management.py` 18項通過；四份JSON語法檢查及 `git diff --check` 通過。
- 七頁皆有靜態文字、內容更新日、資料查核日、直接來源、SEO、JSON-LD與共用頁尾，並出現在兩份 sitemap、all-cards、seo 及 service-worker 資產清單。
- 390×844 手機檢查確認 public 入口位於彈性襪之後；七頁無橫向溢出，均有圖下兩個翻頁按鈕、系列循環、文字日期、來源與單一共用頁尾。
- AUD-007 的199頁報告先保存快照，再更新為206頁版本；既有字詞差異 CR-2026-023 仍保留。
- 本次未 Commit、Push 或驗證 GitHub Pages 部署。內容及來源查核日為2026-10-16。

完整範圍、來源與測試限制見[任務證據](evidence/knee-brace-2026-10-16.md)。

## 2026-10-17｜CR-2026-030 除疤凝膠和貼片如何使用

- 完整 `python build.py` 成功：374 個靜態圖卡頁；文字整合報告 212 成功、0 失敗。
- 四份 JSON 語法檢查、`python -B scripts/check_site.py` 與 `git diff --check` 通過。
- 六頁 `--propose` 為零機械差異、零移除、零來源錯誤；新頁的文字、雙日期、參考連結、SEO、JSON-LD、圖下翻頁與共用頁尾均為 `machine_pass`。
- `check_project_management.py` 與其 18 項測試未全數通過，原因是既有全站清冊的舊頁 `source_sha256`、`rules_sha256`／部分 JSON-LD 指紋漂移，以及既有缺失證據；本次六頁沒有新增該類錯誤，未在本次任務大量覆寫歷史人工或機械欄位。
- 內建瀏覽器無法連入隔離工作樹的本機預覽埠，故未完成實機手機截圖抽查；未 Commit、Push 或驗證 Pages 部署。
