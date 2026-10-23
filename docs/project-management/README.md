# 藥局衛教助手專案管理系統 v1

建立日期：2026-10-13。這是本機管理層，不是另一套圖卡內容資料庫，也不會被網站載入。從 [總控台](project-dashboard.md) 看下一步，先查 [需求登記](change-requests.csv)，再用 [頁面主清冊](page-inventory.csv) 找受影響頁及既有證據。

搜尋與AI可見度追蹤另依 [搜尋追蹤流程](search-tracking.md) 維護 [Search Console歷史資料](search-console-history.json)：逐筆提交與每次觀測都附證據並累積保存；資料取得日、報表日、比較窗及檢索日分開。此授權不包含自動提交索引、修改網站或發布。

本次只建立文件、管理資料與獨立唯讀驗證工具。沒有執行 build.py、沒有重讀全站圖片或外部醫療文獻、沒有修改網站及既有報告、沒有 Commit/Push。工作開始前已有未提交網站修改，狀態是「本機工作目錄」而非可宣稱已部署的版本。

## 權威來源與責任邊界

| 資訊 | 權威來源 | 管理層做什麼 |
|---|---|---|
| 系列 ID、steps、排序、visibility、favorite_keys | `cards.json`；`cards.manual.json` 為人工伴隨來源 | 清冊是唯讀投影，不能反向更新來源 |
| 圖卡文字、引用、來源查核日期、原始修訂資訊 | `data/card_content.json` | 記錄欄位／HTML 是否存在，引用原紀錄；不再抄存正文 |
| 退出頁與替代頁 | `cards.retired.json` | 保留 ID/URL，退出頁不計入現行醫療工作量 |
| 真正的生成頁 | `cards/*.html`、`build.py` | 讀取檔案證據；存在不等於部署完成 |
| Pilot 問題導覽與規格 | `data/acne_navigation.json`、`docs/acne-pilot-spec.md` | 匯入關聯以供查詢；不取代來源、不擴大四頁範圍 |
| 主題公開內容 | `topics/acne.html` | 主題階層只索引現有區塊或明示未建立的提案 |
| 搜尋輸出與網站技術 | `seo.json`、兩份 sitemap、模板、PWA、既有 scripts/tests | 本次只讀；不以語法／欄位檢查宣稱排名或 AEO 成效 |
| 藥品資料庫與待核資料 | 原各資料集、final JSON、manual_review_queue 等 | 總控台引用原表；不複製數萬筆藥品資料 |
| 人工決策／藥師簽核／作者授權 | 有姓名、日期、版本、範圍的實際確認紀錄 | 人工欄位；自動工具不得賦值或覆蓋 |
| 工作是否核准 | 使用者明確授權與需求的 approval | `registered` 不代表核准；本次匯入的歷史問題均未核准執行 |

眼藥需以 `js/medicine-explorer-config.js` 與 `eye_drop_explorer_readme.md` 指向的 final JSON 為目前入口依據。根目錄 README 記載的 `data/eye_meds/`、舊頁／舊腳本已不在目前 checkout，不照舊說明另建資料庫（CR-2026-009）。三個沒有 manual 系列項目的 ID 為 `onitment_general`、`site_instruction`、`add_to_desktop`；保留現状，不推論一定是缺陷，也不自行回填。

## 檔案與識別

六個核心檔案：`project-dashboard.md`、`page-inventory.csv`、`change-requests.csv`、`audit-history.md`、`content-topics.json`、`content-relations.csv`。輔助 `audit-register.json` 保存報告 ID、原始證據雜湊與版本索引；它不保存醫療正文。`validation-report.md` 保存本次驗證範圍與結果。

- `page_id` 為既有圖片檔名 stem，保留大小寫（例如 `Ped_abx_susp_1`）；不另編會變動的流水頁號。
- `series_ids` 保留所有既有系列 ID；`primary_series_id` 依目前 build.py 首個可生成系列規則。四張 `over_one_oint_*` 同屬兩系列，只各占一筆頁面。
- `favorite_keys` 是 JSON object，逐系列保存原 `favorite_keys[index]` 或原有預設 `series-index`（從 0 開始）。退出頁若來源沒有可證實的舊鍵，空 object 表示未提供，不猜測。
- 圖卡、系列關聯使用 `page:<原ID>`、`series:<原ID>`；主題／子題／工具使用 `topic:`、`subtopic:`、`tool:`。A01/S01 等舊報告代碼僅為歷史別名，不取代網站 ID。
- 關聯 `REL-` 為 source/type/target 的穩定雜湊；需求 `CR-YYYY-NNN`、報告 `AUD-NNN` 一經使用不重編、不回收。
- CSV 為 UTF-8 BOM；list/object 欄位使用合法 JSON，其餘多值 ID 使用 `|`。數量按唯一頁 ID 計，不把多系列引用重複算頁。
- `current` 表示至少一個未隱藏系列引用；`hidden` 表示所有引用系列均 hidden；`retired` 以退出表為準。`generated_state` 另外記 present/pending/missing。**hidden 不代表沒有靜態頁或私密**；只有 hidden + publish_at 才是生成器的 pending 排除條件。

## 清冊欄位：自動事實與人工判断分開

| 欄位 | 維護者與定義 |
|---|---|
| page_id/page_path/url/title/primary_series_id/series_ids/image_path/favorite_keys | 程式可同步；title 優先實際 H1，不重新命名 URL |
| visibility/generated_state | 程式可同步；來源與 HTML 分開判斷 |
| text_status | 程式檢查 article 中 summary 及各 section 原文，僅合併空白；不刪字來製造通過 |
| reference_status | 程式檢查 high 紀錄的非空引用名稱、HTTP(S) URL、HTML 實際連結；**不代表來源支持主張或仍可連線** |
| date_status | 程式檢查文字區內「內容更新：updatedAt」及「資料查核：sourceCheckedAt」兩個標示；同一天不能只憑字串出現一次就算雙日期齊全；不把今日檢測日寫成內容更新日 |
| seo_basic_status | 程式檢查 title、單一 H1、description、canonical、靜態 OG 的基本存在／配對 |
| jsonld_status | 程式檢查 application/ld+json 存在及 JSON 可解析；**不驗證 Schema.org 語意、作者資格或 Google rich results** |
| footer_status | 程式檢查單一 site-footer 與本站資訊三連結存在；不代表像素版面或模板逐字相同 |
| source_needs_medical_review | 原欄位投影，保留 true/false/"unknown"；false 不推論已藥師審閱 |
| content_sha256 | 原圖 bytes 與對應原始文字紀錄雜湊；供人工簽核限定版本 |
| source_sha256 | 個頁 HTML/圖片/文字、所屬系列與 manual、退出資訊雜湊；改動後提出局部同步差異 |
| rules_sha256 | 共用產生器、頁首／頁尾、Pilot 資料規則指紋；改變時所有適用頁須重新做技術檢測，**不代表重審醫療內容** |
| checked_at/evidence_sources | 程式檢測日及實際證據路徑；不是藥師確認日 |
| medical_review_status/medical_review_evidence/reviewer/review_date/reviewed_content_sha256 | **人工專用**，簽核需實際人員、日期、證據檔與內容指紋；保留歷史簽核，内容改變另開定點複核 |
| documented_status/audit_ids/history_note | **人工專用**，記錄舊報告範圍及是否過時；不得用報告總數推認個頁通過 |
| seo_aeo_status | **人工專用**，涵蓋內容適配與實際成效的證據；本輪皆 unknown |
| known_issue_ids/review_required/review_reason/last_human_confirmed_at | **人工專用**，需求關聯、定點待複核原因及實際確認日期 |

狀態字典與 CSV 欄位的可執行定義在 `scripts/check_project_management.py`。自動欄位只接受 `machine_pass / missing / partial / invalid / unknown / not_applicable`。`machine_pass` 僅代表上表列出的機械檢測。退出及 pending 頁的內容檢查為 not_applicable，歷史內容仍在原資料。

人工醫療狀態：`unknown / pending_pharmacist / pharmacist_reviewed / conflict`。文件狀態：`unknown / documented_complete / historical_only / conflict`。SEO/AEO：`unknown / documented_complete / pending / conflict`。`review_required=yes` 必須有理由；沒有證據的項目保持 unknown，不自動變為 no。

`documented_complete` 指明確文件記錄的該項完成，例如既有文字整合報告；不是藥師簽核。本輪不建立任何 pharmacist_reviewed。文件互相矛盾則保留 conflict 與兩方證據；能由日期、實際檔案及後續 Commit 解釋的改變是 superseded，不把時間演進誤當矛盾。未簽核與缺文字是不同欄位，不能加總成「醫療錯誤張數」。

## 日常增量流程

1. 開工先查需求與清冊的 page_id、系列、audit_ids；查看 Git 工作目錄，確認既有改動。讀原報告中相關段落，不重跑全站醫療審核。
2. 沒有既有需求才登記新 CR，寫清範圍、證據、是否須藥師確認、作者授權與商業揭露。需求类型支援：新增圖卡、修改醫療內容、SEO/AEO、作者或審閱者、網站連結、賣場連結、疾病主題、計算器、資料庫、網站功能。
3. 狀態從 registered（僅登記）→ needs_confirmation/approved → in_progress → completed；也可 blocked/cancelled。沒有實際授權不得從登記直接施工。P0–P3 是管理排序，不等於臨床嚴重程度。此流程不要求對已有使用者授權重複詢問。
4. 只在授權工作中改原始權威資料，依既有 AGENTS 決定建置範圍；本管理工具從不呼叫 build.py。
5. 用唯讀差異工具取得機械欄位提案；按 `page_id` 合併，人工欄位逐一保留。**禁止整列替換、以新產生 CSV 覆蓋主清冊，或自動清掉 known_issue_ids。** 新頁的人工欄位先填 unknown，只有真實證據可改。
6. 人工判斷哪些舊結論受改動影響。日期／樣式改動通常只重驗技術項；醫療正文或圖片改動才看對應主張與簽核範圍。來源不足、衝突或證據確實失效的頁才加入定點複核。
7. 更新受影響的關聯、需求、總控台；歷史檔追加日期／判斷與證據，原報告不改、不刪。整合報告被重建覆蓋後，先保存舊記錄引用的 Git 版本或可追溯快照，再追加新事件並更新 audit-register 指紋，不能僅刷新 hash 消除警告。
8. 執行管理驗證，記錄完成日期、相關 Commit（本機未提交用 unknown）及測試結果。完成不代表已發布；Commit、Push、Pages部署另在授權發布任务記錄。

### 各種變更如何處理

| 變更 | 最小維護範圍 |
|---|---|
| 新增圖卡／系列追加 | 原 steps 與文字來源依專案規則備齊；清冊新增唯一頁、has_card 關聯，按需要加入主題；新內容人工初始 unknown |
| 修改舊頁文字／圖片 | 更新该頁機械欄位、相關系列導覽指紋；保留原人工簽核與歷史，用新需求限定待審內容；不重審無關頁 |
| 隱藏／排程／退出 | 比對 metadata、退出表與實際HTML，保留舊ID/URL；刪除管理中的現行關聯前確認替代目的地，不刪歷史 |
| 新增疾病主題 | nodes 增加 topic/subtopic；先標 planned 或 collection_only；只有實際專頁存在才設 formal_page；用多對多 shares_card 共用原頁 |
| 第二作者／審閱者 | CR類型「作者或審閱者」；記錄本人同意、角色、顯示姓名、範圍、日期及證據檔；作者署名不等於醫療簽核，沒有同意不發布 |
| 外部連結 | CR類型「網站連結」；記錄目的地、涉及頁、引用/延伸閱讀用途、查核日期與重新導向；不可據連結存在自動關案 |
| 賣場連結 | CR類型「賣場連結」；記錄是否聯盟／付費、授權、揭露文字與位置及審核證據；unknown 不能轉成已揭露 |
| AEO/SEO規則 | 以 Git diff 定位模板與生成器，再依 rules_sha256/適用頁列出技術影響；本文更動才定點重核醫療。效能/排名需獨立時間窗與資料，不由 JSON-LD 通過推測 |
| 計算器／資料庫 | 仍使用原資料／測試／佇列，總控台記錄版本與未解事項；公開工具的 hub 同步依 AGENTS，隱藏 POC 不自行列入 |

新作者授權、藥師簽核等證據可新增在本目錄的 `evidence/`，用實際紀錄檔名引用；本輪沒有虛構範例簽核或建立空白授權檔。需求範圍可用 related_ids 精確定位；`description` 保存待改連結及揭露要求。完成時 `validation_result` 應含可重現命令與證據，不填籠統「OK」。

## 網站變更自動追蹤

網站檔案的技術變更不再依賴人工把 Git 狀態抄到總控台。`scripts/project_change_tracker.py` 直接讀取管理系統 v1 建立後的 Git 歷史與目前工作目錄，列出受影響檔案、圖卡頁面、系列及對應 CR；因此已提交與尚未提交的變更都能在需要時重新查詢。總控台保留專案判斷與下一步，Git 事實以此工具的即時結果為準。

常用查詢：

```powershell
python -B scripts/project_change_tracker.py
python -B scripts/project_change_tracker.py --page comedo
python -B scripts/project_change_tracker.py --series pediatric_cold_syrup
python -B scripts/project_change_tracker.py --request CR-2026-032
python -B scripts/project_change_tracker.py --json
python -B scripts/project_change_tracker.py --check
```

`--check` 在網站變更沒有連結 CR 時回傳失敗；純 `sw.js` 自動更新會標為自動產生後續。新 CR 與網站變更放在同一次提交時，`git_commit` 可填 `same_commit`，工具會由該次 CSV 差異解析實際 Commit，不再要求事後手抄 SHA。歷史補登則填實際 SHA，必要時以 `|` 保存同一需求的多個 Commit。

GitHub 的 `.github/workflows/project-management-check.yml` 會對 Push／Pull Request 執行相同唯讀檢查。它不修改網站、不自動核准需求、不更改醫療狀態，也不 Commit 或 Push。工作目錄中尚未提交的變更可即時查詢；只有真正進入 Git 的內容才會成為永久歷史。

自動追蹤只負責可由檔案與 Git 證明的事實。藥師複核、作者授權、商業揭露、Search Console 實際操作與成效仍需真實證據，不會由工具自動判定。

## 唯讀工具

在 repository 根目錄執行（Python 3.10+，只用標準函式庫）：

```powershell
python -B scripts/check_project_management.py
python -B scripts/check_project_management.py --summary --report-file outputs/management-check-latest.json
python -B scripts/check_project_management.py --summary --baseline-file PATH_TO_REVIEWED_REPORT
python -B scripts/check_project_management.py --propose
python -B scripts/check_project_management.py --propose --page comedo
python -B scripts/test_project_management.py
python -B scripts/test_management_output.py
python -B scripts/project_change_tracker.py --check
python -B scripts/test_project_change_tracker.py
```

預設驗證全份管理資料的一致性；這是幾秒內的機械讀取，**不是全站醫療盤點**。`--propose` 只將新增／變動頁的自動欄位與移除 ID 提示列在 stdout，沒有 write/fix/sync 模式。`--page` 可重複使用，僅篩選提案；最後仍需完整一致性驗證。這個設計讓人先看清差異，且程式沒有覆蓋人工結果的入口。

`--summary` 執行相同的完整驗證，只在終端顯示總數、分類與必要差異；原命令仍保留逐筆完整輸出及相同退出碼。`--report-file PATH` 會在指定路徑寫入完整 JSON 診斷（含原始錯誤與警告），僅在明確指定時產生；`outputs/` 已被 Git 忽略。`--baseline-file PATH` 只接受此工具產生、內容自洽且經人工確認可信的完整報告，以穩定的錯誤範圍／類型識別比較新增、已解決、惡化與仍存在的問題；未知類型一律顯示。沒有可信基準時只能報目前總數，不能宣稱「新增錯誤為零」。摘要模式不減少任何檢查，也不把失敗改判為成功。`--page` 僅限制提案，不限制完整驗證；CI 既有執行範圍維持不變。

指紋可找出圖片、文字、實際HTML或同系列導覽的相關變動，即使尚未 Commit 也能發現；不依賴不可靠的檔案 mtime。共用规则變動會觸發技術欄位提案，絕不自動改 medical_review_status。報告雜湊改變會要求追加歷史說明；來源查核日期不跟著提案更新。

驗證器檢查頁面集合、stem碰撞、缺圖／缺頁、孤立HTML、退出錯列、所有has_card、關聯目標與型別、Pilot範圍、重複ID、枚舉、證據檔與報告雜湊、簽核欄位和內容版本。它不查網路、不改任何檔案、不保證醫療、法律或搜尋成效。`--propose` 和驗證都只讀網站來源與管理檔案。

## 避免重複盤點

處理一頁時，先回答「已有哪個報告、證據是哪個版本、這次哪些欄位真的變了」。若只因報告變老而無新變更，不重新看全部圖片；若某筆簽核內容指紋不同，保留舊簽核作歷史，針對差異另開待審。歷史 `high`、PASS、ready_for_site、目前有文字或已能生成都不是臨床批准。

自 2026-10-21 起，AGENTS 與圖卡技能都把變更追蹤列為收尾必做項目，GitHub 另有唯讀檢查。這些機制只補上追溯閉環；仍只更新本次受影響資料，不重做全站醫療盤點。
