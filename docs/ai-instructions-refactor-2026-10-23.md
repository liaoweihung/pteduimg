# AI 指令架構重構與驗收紀錄

日期：2026-10-23（Asia/Taipei）。範圍為本機 `liaoweihung/pteduimg` 的 AI 指令、SOP 導覽與必要說明修正；原重構驗證階段尚未授權 Commit／Push，後續提交授權見下方整合紀錄。未修改衛教正文、圖卡資料、Logo、產生器、網站頁面、CI 或全域設定。

## 架構與讀取方式

共同入口為 [AGENTS.md](../AGENTS.md)，保留醫療與人工簽核、資料責任、建置、可見性、快取、Git、品牌及特殊任務的關鍵限制。使用者任務涉及哪項功能，就先讀任務表對應文件；不以入口摘要取代完整 SOP，也不預先 inline 展開整套文件。

- 圖卡操作沿用 [專案 Card Manager](../skills/pteduimg-card-manager/SKILL.md)，保留逐頁文字／日期／來源 schema、完整新增工作與清冊增量程序。
- 分類 ID 與 metadata 範例移至該 Skill 的 [card-data.md](../skills/pteduimg-card-manager/references/card-data.md)。
- 原根目錄的共用建置、退出、排程、UI 檢查、快取與發布細節集中到 [site-build-and-release.md](site-build-and-release.md)，不再於 Skill 重複維護同一套程序。
- Hub 詳細規則移到 [pharmacy-tools-maintenance.md](pharmacy-tools-maintenance.md)。既有專案管理、品牌、青春痘及搜尋 SOP 沿用原文件。
- [GEMINI.md](../GEMINI.md) 與 [Copilot 入口](../.github/copilot-instructions.md) 要求先讀 AGENTS，再按任務讀文件；仍直接連到同一份品牌規範。
- 沒有新增規則目錄或 inline include 載入；所有新增路由皆為普通 Markdown 連結與明確開檔要求。迴鏈供返回導覽，不要求遞迴展開。

## 檔案大小與異動清單

大小以實際 UTF-8 bytes 計，非字數；下表保留遠端同步前的本輪重構驗證快照，來源為當時工作目錄（含既有未提交變更）。遠端同步後的必要合併另記於下方。

<!-- SIZE_TABLE_START -->
| 檔案 | 本輪異動 | 重構前 bytes | 重構後 bytes |
|---|---|---:|---:|
| [AGENTS.md](../AGENTS.md) | 修改 | 28,048 | 11,997 |
| [GEMINI.md](../GEMINI.md) | 修改 | 1,212 | 1,152 |
| [.github/copilot-instructions.md](../.github/copilot-instructions.md) | 修改 | 901 | 888 |
| [skills/pteduimg-card-manager/SKILL.md](../skills/pteduimg-card-manager/SKILL.md) | 修改 | 21,027 | 15,891 |
| [docs/brand/README.md](brand/README.md) | 修改 | 5,763 | 5,841 |
| [docs/project-management/README.md](project-management/README.md) | 修改 | 14,209 | 14,293 |
| [docs/project-management/search-tracking.md](project-management/search-tracking.md) | 修改 | 5,025 | 5,199 |
| [skills/pteduimg-card-manager/references/card-data.md](../skills/pteduimg-card-manager/references/card-data.md) | 新增 | 0 | 3,427 |
| [docs/site-build-and-release.md](site-build-and-release.md) | 新增 | 0 | 14,529 |
| [docs/pharmacy-tools-maintenance.md](pharmacy-tools-maintenance.md) | 新增 | 0 | 2,665 |
| [docs/ai-instructions-refactor-2026-10-23.md](ai-instructions-refactor-2026-10-23.md) | 新增 | 0 | 16,403 |
<!-- SIZE_TABLE_END -->

### 提交流程的遠端同步

後續使用者明確授權兩筆 Commit 與 Push，且指定不做新增載入、建置或全站醫療測試。同步時遠端 `main` 已增加網站變更追蹤：保留遠端 [專案管理 SOP](project-management/README.md#網站變更自動追蹤) 原文，把此規則接入 [網站建置／發布 SOP](site-build-and-release.md#網站變更追蹤) 與 [Card Manager Skill](../skills/pteduimg-card-manager/SKILL.md)，不以舊本機副本覆蓋遠端管理文件。根 `AGENTS.md` 為 11,984 bytes；合併後 Skill 為 16,226 bytes、建置 SOP 為 15,316 bytes。遠端尚無原工作目錄未追蹤的 `docs/acne-mobile-card-rollout.md`，因此正式入口只連已入庫的 Pilot 規格，手機版的關鍵限制留在 AGENTS，不把該份範圍外文件混入提交。這次只核對提交差異與路徑，未重做下方記錄的 AI 載入或網站測試；下方驗證數字皆指先前快照。

刪除檔案：無。`GEMINI.md`、Copilot 入口與品牌 README 在本次開始前已存在，即使仍為 Git untracked，也列為本輪「修改」。原始素材包 23 個檔案及兩份品牌匯入／驗證 JSON 保持原樣；舊驗證 JSON 是當時快照，不當成此次重構的驗證結果。

## 原 AGENTS.md 到現行規範的對照

原檔 SHA-256：`5f31ac3f187936a26bc9aa04e03e4824d12b4378004f3fd3c25a7d07575b386b`。

原檔 28,048 bytes，19 個二級章節；下列行號指本輪開始時的工作目錄原檔，不是 Git HEAD。原開頭的網站用途與專案 Skill 入口保留於新 AGENTS 開頭及任務表。

| 原章節／原行號 | 現行位置 | 保留內容與整理方式 |
|---|---|---|
| 品牌規範，7–14 | [品牌入口](brand/README.md)、[AI 約束](brand/BRAND_GUIDE_AI.md)、AGENTS「品牌與特殊頁面」 | 固定三色、PNG 母版、禁重畫、透明版待驗收、SVG 暫停、浮水印未定稿、醫療／發布界線；原包不改 |
| Card Data Model，16–58 | [資料模型](../skills/pteduimg-card-manager/references/card-data.md#card-data-model) | 原章完整搬移：雙 JSON、steps、兩類入口、15 個 topics、12 個 departments、多分類與缺分類後果 |
| 新增圖卡的文字與可信度要求，60–73 | [Skill](../skills/pteduimg-card-manager/SKILL.md#required-text-dates-and-sources-for-new-cards)、AGENTS「醫療內容與人工簽核底線」 | 逐圖靜態文字、雙日期、直接來源、修訂歸屬、缺項處理、前瞻適用、不回補舊卡；沿用 Skill 更完整的欄位定義 |
| 新增衛教圖卡標準作業流程，75–90 | [Skill 完整流程](../skills/pteduimg-card-manager/SKILL.md#end-to-end-new-card-workflow)、[管理 SOP](project-management/README.md)、AGENTS「圖卡工作與資料責任／管理紀錄與完成標準」 | 原十步合併到既有流程；逐步對照見下表，不另建立第三份 SOP |
| Static Card Pages，92–136 | [建置模式](site-build-and-release.md#static-card-pages) | 原章完整搬移：Route B、URL 對應、full／selected 條件、全部產物、靜態 OG、範圍衝突 |
| Static All Cards Index，138–148 | [靜態索引](site-build-and-release.md#static-all-cards-index) | 原章完整搬移：不手改、重建時機、兩 sitemap 收錄、hidden 非隱私控制 |
| Adding A New Image To An Existing Card，150–178 | [Skill 新增圖片](../skills/pteduimg-card-manager/SKILL.md#adding-images-or-a-new-series)、Image Conversion、[建置驗證](site-build-and-release.md) | img／WebP／命名、steps 同步與 manual 例外、唯一文字紀錄、full build、三 JSON、生成頁與全域輸出；合併原本重複流程 |
| Adding A New Card Series，180–201 | [資料模型範例](../skills/pteduimg-card-manager/references/card-data.md#adding-a-new-card-series)、Skill 完整流程 | 原範例保留，尾句由「上述建置」改指獨立建置文件；分類與標籤確認要求不變 |
| Retiring Or Replacing Cards，203–208 | [退出規範](site-build-and-release.md#retiring-or-replacing-cards) | 原章完整搬移：active steps／retired schema、原圖與舊 URL、替代頁、noindex、索引與連結驗證 |
| Scheduled Card Publishing，210–247 | [排程規範](site-build-and-release.md#scheduled-card-publishing)、同檔「排程的補充操作」 | 原章完整搬移；加回既有 Skill 的台灣時區轉換、精選清單、無到期卡跳過建置等獨有細節 |
| Image Conversion，249–266 | [Skill 轉檔](../skills/pteduimg-card-manager/SKILL.md#image-conversion)、完整流程 | Pillow quality=90／method=6、英文小寫底線數字檔名、來源保留；品牌 PNG 母版明確排除覆寫 |
| Local Testing，268–283 | [頁面操作檢查](site-build-and-release.md#local-testing) | 原章完整搬移：兩入口、工具列下方圖片、同系列翻頁、返回、QR／分享、favImages |
| Offline Cache and Update Experience，285–291 | [快取規範](site-build-and-release.md#offline-cache-and-update-experience)、AGENTS「快取、發布與證據界線」 | 原章完整搬移：cache-first／背景更新、core 與 runtime、更新 pill、接管與重載分開、不強刷 |
| Regression Check，293–318 | [回歸檢查](site-build-and-release.md#regression-check) | 原章完整搬移，僅將 project skill 引用改可點擊連結；所有 invariants、pending 缺頁限制及不得造假通過保留 |
| Pharmacy Tool Pages and Hub Synchronization，320–332 | [Hub 規範](pharmacy-tools-maintenance.md#pharmacy-tool-pages-and-hub-synchronization) | 原章完整搬移：獨立目錄、首頁最後入口、完整 URL／返回、工具數、私有原型排除、兩 repo 與發布順序 |
| Git / Publishing，334–367 | [發布清單](site-build-and-release.md#git--publishing)、AGENTS「快取、發布與證據界線」 | 原章完整搬移：僅相關變更、所有來源／生成輸出、未授權不發布、auto-build 限制、Python cache 排除 |
| Important Rule，369–377 | [完整發布鏈](site-build-and-release.md#important-rule)、Skill Final Response | 原章完整搬移，保留圖片到 Pages 的完整鏈及 pending 必須實際執行 publisher |
| Acne Topic Pilot，379–391 | [既有 Pilot 規格](acne-pilot-spec.md)、AGENTS「品牌與特殊頁面」的手機摘要 | 沿用既有兩份規格：閱讀順序、正常文件流、四頁導覽範圍、非順帶重構、明確改版可修訂 |
| Search Performance Tracking，393–395 | [搜尋 SOP](project-management/search-tracking.md)、AGENTS「快取、發布與證據界線」 | 保留落檔授權、日期／證據／總控台、歷史與缺資料界線；歷史 JSON 改用明確完整路徑 |

原十步 SOP 的逐項核對：

| 原步驟 | 現行對應／仍須履行 |
|---|---|
| 1 查現況與需求 | Skill Before Editing：Git、鄰近系列、四份管理檔、CR 範圍搜尋、沿用／新編及授權區分 |
| 2 最小新增範圍 | Skill End-to-End #1 與資料模型：ID、分類、篩選、排序、標籤、數量、公開／排程；資料不足不猜 |
| 3 圖片處理 | Skill End-to-End #2、Image Conversion：格式、穩定 stem／URL／收藏、不重用退休 ID |
| 4 雙 metadata 與逐頁內容 | Skill End-to-End #3–4、Required Text：唯一配對、全部欄位、真實來源與日期、needsMedicalReview 預設 |
| 5 入口與順序 | Skill End-to-End #3、#5：資料驅動優先，手工精選只做本次需要，不重設導覽 |
| 6 既有產生器 | Skill End-to-End #5、建置 SOP：必要 full build、建置前後 diff、不混入無關改動 |
| 7 增量清冊 | Skill Incremental project-management update：定點 propose、按 ID 只合併機械欄位、保護人工欄位 |
| 8 關聯與工作紀錄 | 同節：has_card、授權主題、CR 狀態／證據／驗證／完成日期、總控台數量／進度／未解、證據與歷史更新條件 |
| 9 檢查及零差異 | Skill Before Editing／增量流程、建置 SOP、AGENTS：三 JSON、site／management／test、目標 propose 零差異及 UI／全域檢查 |
| 10 回報與發布 | Skill End-to-End #6／Final Response、AGENTS：系列／頁數、CR／清冊／關聯、命令結果、未完成、醫療待確認、未授權不 Commit／Push |

## 矛盾、重複與失效規則處理

| 發現 | 本次處理／限制 |
|---|---|
| 根 AGENTS 與 Skill 各自維護建置、排程、退出、UI 與發布說明 | 集中到建置 SOP；Skill 保留觸發條件與必要摘要，根入口保留立即生效的底線 |
| Skill 指示分類 ID 在 AGENTS、或依 AGENTS 查完整排程／退休／產物清單 | 改為新資料模型與建置 SOP 的明確連結；不留下被搬走章節的懸空依賴 |
| GEMINI／品牌 README 稱 AGENTS 仍超過單檔限制 | 改成精簡入口＋按需讀取，大小見本報告；不使用全文 include |
| 管理 README 末段仍要求「下一次確認是否採用入口」 | 遠端後續已將變更追蹤列為規範並啟用唯讀 CI；同步時保留遠端新版，人工欄位、排程與發布界線不放寬 |
| 搜尋 SOP 稱 `pteduimg-sitemap` 為現有工作、沿用頻率 | 標為建立時歷史敘述，要求核對當前設定與授權；本次不檢查或改動任何 automation，不依舊文重建／重啟 |
| 根搜尋規則只寫 `search-console-history.json`，根目錄並無此檔 | 改成 `docs/project-management/search-console-history.json` 明確連結 |
| 已安裝的全域同名 Card Manager 缺少新醫療內容與管理 SOP | 讀取確認後在根入口／專案 Skill 明確要求使用專案版；不改使用者全域 Skill，不宣稱已全域同步 |
| 新卡圖片優先 WebP vs 正式 Logo 為定稿 PNG | 明確區分一般圖卡轉檔與品牌母版；不把一般建議套成重製／覆寫 Logo 的授權 |
| 原品牌包舊版文件仍寫色碼待確認、SVG 下一步精修 | 依品牌 README 已有的歷史說明及 v2.3 現行狀態，不改原檔或其雜湊 |
| 手動排程 workflow 漏提交部分 full-build 輸出；auto-build 僅提交 sw.js | 對照實際兩份 YAML，限制仍有效，保留原規則；本次不改 CI |
| pending high-confidence 文字的缺頁檢查限制 | 對照 `check_static_card_text_content`，限制仍在；保留診斷與禁止造假通過規則，不改檢查器 |

## AI 載入方式與實測界線

2026-10-23 核對官方文件：[Codex AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md)、[Gemini GEMINI.md](https://geminicli.com/docs/cli/gemini-md/)、[Antigravity Rules](https://www.antigravity.google/docs/rules/)、[Copilot custom instructions](https://docs.github.com/en/copilot/concepts/prompting-and-context/custom-instructions)。

Codex 使用根 AGENTS；Gemini CLI 使用根 GEMINI；Antigravity 支援根 AGENTS／GEMINI；Copilot 的專案入口是 `.github/copilot-instructions.md`。本地檔名與引用符合這些入口方式。普通 Markdown 連結不是自動全文匯入，必須由工具依指令開檔。只有入口與檔案可達性確認，不能推論每種客戶端必定遵循。

| 工具 | 本輪載入驗證 | 結果 |
|---|---|---|
| Codex 當前對話 | 實讀精簡入口、專案 Skill、各功能文件；人工檢查下列任務路由 | 已讀取；不是全新會話自動載入證據 |
| 獨立 Codex CLI | 以 `--no-daemon`、`--ephemeral`、`--ignore-user-config`、`--sandbox read-only`、`-a never` 嘗試讀取與問答；不指定答案 | **未測試**：exit 1，`state_5.sqlite` 無法開啟及 app-server 初始化 `Access denied`，模型未回答 |
| Gemini CLI | 本輪未重試模型呼叫；前一輪唯讀呼叫未取得回答，已中止 | **未測試**，不沿用舊入口結果當成新架構通過 |
| Antigravity | 入口與無 include 靜態驗證；現有 review 的 Live 封鎖仍在 | **未測試**，未繞過 `ISOLATION_UNVERIFIED` |
| Copilot | 專案入口與連結靜態驗證；前一輪未找到可呼叫 CLI／擴充入口，本輪未安裝或連線 | **未測試** |

任務路由的文件檢查（非獨立 AI 行為測試）：新增圖卡 → Skill／資料模型／管理 SOP／建置；品牌 → Brand Guide／AI 約束／定稿 PNG；退出／排程 → 建置相應章節；藥局工具 → Hub 維護；青春痘 → 既有 Pilot 規格與根入口手機規則；搜尋 → 追蹤流程與完整歷史路徑。每條路由都能找到對應規範。

品牌五題核對仍為：母版 `docs/brand/assets/logo_primary_color_original.png`；三色 `#FD2828`、`#101010`、`#013E9C`；禁止 AI 重畫；SVG 不是正式母版；浮水印未定稿、不得自動批次套用。

## 驗證紀錄

<!-- VALIDATION_START -->
- `AGENTS.md` 實測 11,997 bytes，落在 8,000–12,000 目標；三個 AI 入口都小於 24,000 bytes，沒有 inline import 指令。
- 本輪 11 個新增／修改文件共有 134 個本機 Markdown 引用（其中 28 個含章節錨點），路徑與錨點全部存在；檢查包括分類、品牌、管理、建置、Hub、青春痘、搜尋與 Gemini review 的導覽。
- 12 個原根章節以文字比對確認搬移完整（只允許已列明的引用改址）；另外 7 個章節及原十步 SOP 依上表逐項語意核對。這是規範覆蓋檢查，不是醫療或模型行為測試。
- 專案 Skill 執行 `python -B -X utf8 C:/Users/liaow/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/pteduimg-card-manager`，結果 `Skill is valid!`。
- `git diff --check` 通過；新建／原為 untracked 的文件亦逐行檢查行尾空白，全部通過。
- 開工時 1,109 個既有檔案的 SHA-256 比對：僅 7 個預期指令／SOP 文件改變，其餘 1,102 個不變，包含網站原始碼、衛教內容、品牌原始資產與 Gemini review 執行器。新建 4 個文件、未刪除既有檔案。
- 原工作目錄已有其他修改；上述保護比較採本輪開工快照，不以 Git HEAD 當成乾淨基準，不還原使用者既有工作。
- 獨立模型測試結果依上表，未完成者均為「未測試」。無 Commit、Push、網站建置或全域設定變更。
<!-- VALIDATION_END -->

文件變更沒有必要建置，未執行 `build.py` 或網站／醫療回歸測試，也未以此宣稱網站部署或內容已通過審核。全新會話的跨工具載入仍標記未測試；後續提交授權不等於這些測試通過。
