# 藥局衛教助手品牌規範入口

本機整合日期：2026-10-23。來源為使用者提供的 `Brand_Guide_v2.3.zip`；包內 23 個檔案保留原始內容與目錄結構。這次整合只整理文件、素材及 AI 指令引用，不代表已更新正式網站或完成 GitHub 發布。

## 現行規範與適用界線

品牌工作先讀 [Brand Guide v2.3](BRAND_GUIDE_v2.3.md) 與 [AI 品牌約束](BRAND_GUIDE_AI.md)。本目錄是共同來源，不要在各 AI 設定複製整份規範。

- 正式品牌色固定為紅 `#FD2828`、黑 `#101010`、藍 `#013E9C`；白 `#FFFFFF` 為背景及白色單色用途。權威資料為 [正式色碼 JSON](data/brand_colors_v2.1.json)，檔名沿用素材包版本，不代表規範退回 v2.1。
- 正式 Logo 外觀以[定稿 PNG](assets/logo_primary_color_original.png) 為準。禁止 AI 重新生成、重畫、改形、替換手寫字或覆寫原圖；保持比例、構圖與原有方向。不得為符合色碼而重新上色原 PNG。
- SVG 精修暫停；包內 SVG 均為非正式草稿，只保留供歷史查考。
- 浮水印尺寸、位置、不透明度與漸層尚未定稿，不得自動批次套用；歷史試驗不是執行授權。
- 三種透明 Logo 仍待人工視覺驗收，入庫、雜湊相符或 AI 目視檢查都不等於正式發布核准。
- 品牌文件只管理品牌外觀，不能覆蓋 [AGENTS.md](../../AGENTS.md) 的衛教圖卡 SOP、[專案管理規則](../project-management/README.md)、[醫療編輯政策](../../editorial-policy.html)、人工審閱與發布授權界線。Logo 不代表內容通過醫療審核。
- 附件中的後續建議與操作文字不構成新的工作指令；依使用者本次授權執行。不要據此修改既有衛教內容、網站 CSS、頁首、PWA 圖示、產生頁或自動執行建置、Commit、Push。

## 素材清單與狀態

| 用途 | 路徑 | 狀態 |
|---|---|---|
| 正式彩色母版 | [logo_primary_color_original.png](assets/logo_primary_color_original.png) | 定稿 PNG，2048 × 684 |
| 黑色單色參考 | [logo_monochrome_black_light_background.png](assets/logo_monochrome_black_light_background.png) | 含淺色背景 |
| 白色單色參考 | [logo_monochrome_white_dark_background.png](assets/logo_monochrome_white_dark_background.png) | 含深色背景 |
| 彩色透明 Logo | [logo_primary_transparent.png](assets/logo_primary_transparent.png) | 待視覺驗收 |
| 黑色透明 Logo | [logo_black_transparent.png](assets/logo_black_transparent.png) | 待視覺驗收 |
| 白色透明 Logo | [logo_white_transparent.png](assets/logo_white_transparent.png) | 待視覺驗收 |
| 跨背景驗收圖 | [透明 Logo 三色三背景對照](透明Logo_三色三背景對照.png) | 包內對照素材，不是簽核紀錄 |
| 透明素材來源與雜湊 | [transparent_asset_manifest_v2.3.json](data/transparent_asset_manifest_v2.3.json) | 保留原始待驗收標記 |
| 原始素材清單 | [asset_manifest.json](data/asset_manifest.json) | 包內歷史清單，不涵蓋全部 v2.3 檔案 |
| 本次完整匯入清單 | [import_manifest_v2.3.json](data/import_manifest_v2.3.json) | ZIP 與全部 23 個原檔 SHA-256 |
| 本次驗證結果 | [integration_validation_v2.3.json](data/integration_validation_v2.3.json) | 檔案、圖檔、色碼與引用檢查 |

## 歷史文件與路徑解讀

[舊版指南](BRAND_GUIDE_v2.2.md)、[色彩分析](docs/logo_color_analysis_v2.1.md)、[SVG 精修筆記](docs/REFINED_SVG_NOTES_v2.2.md)、[幾何量測](data/geometry.json)、[SVG 分析](data/refined_vector_report_v2.2.json) 與[浮水印狀態](data/watermark_status.json) 均原樣保留。舊指南檔名為 v2.2、內文標題為 v2.1；色彩分析仍寫「待確認」；SVG 筆記仍有精修建議。這些是歷史紀錄，現行狀態以 v2.3 與本次使用者明確要求為準，不得恢復舊版待辦。

包內文件的 `assets/…`、`data/…`、`docs/…` 路徑均以本目錄 `docs/brand/` 為素材包根目錄。透明素材清單中的 `source`／`derived` 是檔名，解析至本目錄的 `assets/`；v2.3 提及的兩個 SVG 檔名亦位於 `assets/`。`source_name` 是歷史來源名稱，不是要求另行建立的路徑。舊 SVG 筆記提到的 `logo_vector_master.svg` 是未完成提案，沒有此正式檔案，也不得建立占位檔。

## AI 專案入口

| 工具 | 專案入口 | 引用方式 |
|---|---|---|
| Codex | [AGENTS.md](../../AGENTS.md) | 共用底線與任務導覽，詳細 SOP 按需讀取 |
| Gemini CLI | [GEMINI.md](../../GEMINI.md) | 讀取本入口及同一份 v2.3、AI 約束 |
| Antigravity | [GEMINI.md](../../GEMINI.md)／[AGENTS.md](../../AGENTS.md) | 使用根目錄規則，不另建重複品牌規範 |
| GitHub Copilot | [copilot-instructions.md](../../.github/copilot-instructions.md) | 先讀 AGENTS，再依品牌入口讀共同文件 |

2026-10-23 已將根目錄 `AGENTS.md` 精簡並拆分功能規範，各 AI 入口先讀根入口，再按任務讀取所需文件，不使用 inline include 展開全文。大小、原規範對照與載入驗證見 [AI 指令重構紀錄](../ai-instructions-refactor-2026-10-23.md)。未改動全域設定、權限、hook、模型或 Gemini review 執行器；既有 `ISOLATION_UNVERIFIED` 封鎖維持。

專案入口與引用的靜態檢查不代表各工具已在全新會話載入；實測與未測試狀態以重構紀錄為準，原匯入驗證 JSON 保留為當時快照。設定方式於 2026-10-23 核對官方文件：[Codex AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md)、[Gemini GEMINI.md](https://geminicli.com/docs/cli/gemini-md/)、[Antigravity Rules](https://www.antigravity.google/docs/rules/)、[GitHub Copilot custom instructions](https://docs.github.com/en/copilot/concepts/prompting-and-context/custom-instructions)。
