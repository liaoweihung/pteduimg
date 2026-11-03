# 衛教圖卡自動化：歷史工作紀錄（原提案已撤回）

> 2026-11-03：使用者撤回圖卡交接規範及其強制多 AI 審核流程。本文件僅保留先前工程查核與提案歷史，不再作為接續指令；下列原流程與停止條件不適用於一般圖卡工作。圖卡工作回到現行 AGENTS.md 與專案 Card Manager，審核工具不自動啟用。

查核日期：2026-11-02（Asia/Taipei）。本文件是工程可行性與待辦，不是醫療複核、隔離驗收或發布核准。

## 已確認

- 使用者確認 Claude Pro；不新增付費 API、不開啟額外用量購買。
- 原提案採用當時的 v1.1 圖卡交接主稿（已撤回）、`skills/gemini-review` 共用審核合約與 `skills/claude-review` 接頭／比較器，不建立第二套內容資料庫。
- 開工 HEAD 為 `e589592`。既有未提交工作包括 Gemini Manual／LibraryOnly 相關修改與整個 Claude review 目錄；本次保留原樣。
- 本次離線實跑：Claude 18、Gemini 28、Gemini Manual 21 項斷言通過。合成測試不代表模型已審核或隔離已驗證。
- PATH 與 `.local/bin/claude.exe`、AppData npm shim 常見位置未找到 Claude CLI；不能推論全機沒有安裝。Windows Appx 清單查詢存取被拒，Desktop 安裝狀態未確認。
- 找到 `C:\Users\liaow\AppData\Local\agy\bin\agy.exe`；本次未啟動。歷史版本 1.4.0 未重新確認。
- Claude phase-one 證據檔不存在；Gemini Live 硬封鎖維持。未執行真實雙模型審核、製圖、網站建置或 Git 發布。

### 同日安裝／登入檢查更新

使用者同意安裝後執行官方 WinGet 安裝命令；WinGet 回報既有套件已安裝且無可用升級，沒有重新安裝。已找到並實際執行：

`C:\Users\liaow\AppData\Local\Microsoft\WinGet\Packages\Anthropic.ClaudeCode_Microsoft.Winget.Source_8wekyb3d8bbwe\claude.exe`

- `--version`：2.1.302。
- `auth status`：exit 0、loggedIn=true、authMethod=claude.ai、subscriptionType=pro；未保存帳號識別資訊。
- 該執行程序環境的 `ANTHROPIC_API_KEY` 未設定；此項不是所有設定／計費路徑的完整稽核。
- 目前 shell 的 PATH 仍未解析出 `claude`，後續可使用已確認絕對路徑，不需重新登入或變更全域 PATH。
- 未呼叫模型、未建立 phase-one approved 證據；合成審核與隔離驗證仍待逐項授權和實測。

## 官方可行性與限制

- [Claude Pro 訂閱登入](https://support.claude.com/en/articles/11145838-using-claude-code-with-your-pro-or-max-plan)：可用同一訂閱登入 Claude Code，共享用量限制。API key 環境變數可能改走 API 計費，啟用前須確認登入路徑，不能讀出或保存金鑰。
- [Claude 非互動 CLI](https://code.claude.com/docs/en/headless)：支援 `-p`。一般模式會自動載入部分上下文／設定；`--bare` 不使用訂閱 OAuth，因此不作本流程捷徑。
- [Claude Windows 安裝](https://code.claude.com/docs/en/setup)：支援原生 Windows；原生 Windows shell sandbox 不受支援。工具禁用、上下文載入控制與 OS 隔離須分別驗證。
- [Cowork](https://support.claude.com/en/articles/13345190-get-started-with-claude-cowork)：Windows 與付費訂閱有官方支援；本次未證實存在可供 Codex 直接呼叫的 Cowork 任務介面，不能承諾自動串接。
- [Antigravity CLI sandbox](https://antigravity.google/docs/sandbox?tab=cli)：目前官方 Windows 要求 Windows 11 24H2 與 2026 年 8 月或更新修補；Windows auto mode 標示 1.4.4+。文件不是本機 1.4.0 的驗收證據，terminal sandbox 也不是所有工具禁用。
- [Codex 非互動模式](https://learn.chatgpt.com/docs/non-interactive-mode)：可供後續腳本協調；本輪已有 Codex 工作環境，不另建 API 工作協調器。

## 原接續提案（已撤回）

1. 確認／安裝 Claude CLI，以 Pro 帳號登入。依既有 Claude Skill 的逐項批准要求進行版本、auth、合成輸入與輸出格式實測，不先建立 approved 證據。
2. 檢驗候選參數、空工具／MCP、hooks／CLAUDE.md 載入、繁體中文往返及程序逾時。任一無法證實即維持 blocked；不得用模型自述代替證據。
3. Gemini 獨立完成其隔離缺項後才考慮啟用；不直接繞過 runner 呼叫 agy。未完成時只提供明確標為手動的交接包，不將手動結果偽裝成 Live。
4. 一次任務以同一 handoff 主稿產生兩份審核輸入。兩模型都先獨立作答，不預先看到另一模型結論。保存來源摘錄、版本指紋、結果及人工決策至既有 evidence 慣例。
5. 現有合約的 URL 只是標籤，審核器不讀原文：這是「獨立判讀提供的摘錄」，尚非獨立來源查核。先由 Codex 核對直接來源並提供完整相關段落；若要求模型各自查原文，須另設受控取證階段，不能默默開啟審核器工具。
6. 現有比較器不接受 Manual 結果，且可能把同義改寫判為分歧。保留 STOP，由人核對來源；不自動改寫結論以通過。後續若擴充手動比較，必須保持 USER_SUPPLIED_UNVERIFIED，測試拒絕混用／過期結果。
7. 內容方向及文字確認後，以 `cardCopy` 作 HTML/CSS 唯一文字來源；插圖作獨立素材、正式 Logo 使用既有檔案，再輸出 PNG/WebP。新增渲染器前先檢查既有可用實作，不修改正式網站模板來代替製圖模板。
8. 比對主稿與 DOM 文字、表格列欄、溢出及輸出尺寸；實際開啟最終 PNG/WebP 與手機尺寸檢視。DOM 相同不代表成圖無裁切，OCR 也不能代替人工醫療審閱。
9. 最後沿用 Card Manager 的網站與管理驗證；取得人工醫療審閱和發布同意才 Commit／Push。歷史缺證保留，不列為本輪修復範圍。

## 首張測試卡提案

候選：「到藥局諮詢前，先準備哪些用藥資訊？」採單張、無劑量、無療效比較的低風險題材。先核對官方來源，再請使用者確認文字與風格。搜尋標籤提案：用藥諮詢、用藥清單、藥師；尚未定稿，未建立系列或正式頁 ID。

目前端到端狀態：**未完成，停在模型連線與隔離驗證前**。不得以 67 項合成斷言替代雙模型審核、製圖或發布驗收。

## 接續狀態

原雙模型審核接續提示詞已移除。安裝、登入、離線測試與隔離限制的歷史記錄保留；不因本紀錄自動恢復交接規範、呼叫模型或執行製圖／發布。
