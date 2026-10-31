# CR-2026-056 NTG 舌下錠與避孕藥系列共 7 頁靜態文字補齊與圖卡修正證據（2026-10-31）

- 依交接包 `outputs/handoffs/2026-10-31-ntg-contraceptive-text/`（`NTG.handoff.json`、`contraceptive_pills.handoff.json`）與使用者授權，補齊既有兩系列共 7 頁之網頁靜態文字、直接查核來源與雙日期（`updatedAt: "2026-10-31"`, `sourceCheckedAt: "2026-10-31"`），並同步修正現有 6 張圖卡中之醫療細節、漏字與殘影：
  1. `NTG_1`（`img/NTG_1.png`）：修正第 2 點贅字「吞吞下去」為「吞下去」，第 3 點刺痛感說明改為「含服時可能有輕微刺痛或灼熱感，但有無此感覺均不能用來判斷藥效，勿自行試含或加量。」
  2. `NTG_2`（`img/NTG_2.png`）：修正時鐘下方漏字「等分鐘」為「等 5 分鐘」。
  3. `NTG_3`（`img/NTG_3.webp`）：修正第 1 點「塑膠盒盒」、第 2 點重複編號「2. 2.」、清除第 3 點右側日曆上方跨卡殘影文字，並將第 3 點保存文字修正為「瓶身記錄開封日；部分院所建議 6 個月更換，實際應依藥袋與藥師指示，勿逾效期。」（不新增「3～6 個月」說法）。
  4. `contraceptive_pills_how_to_take`（`img/contraceptive_pills_how_to_take.webp`）：標明適用一般複方製劑，並將月經第 2～5 天開始說明改為「一般複方通常不需額外避孕／部分品牌前7天配保險套(依仿單)」。
  5. `contraceptive_pills_missed_dose`（`img/contraceptive_pills_missed_dose.webp`）：修正複方含藥錠漏服分界（未滿 48 小時 vs 連漏 2 顆以上達 48 小時）、第一週連漏評估事後藥與避免自行將 UPA 與原避孕藥接續使用、最後一週連漏略過停藥／安慰劑及單方黃體素／多相製劑依仿單處理。
  6. `emergency_contraceptive_pills_how_to_take`（`img/emergency_contraceptive_pills_how_to_take.webp`）：原圖經核對無醫療錯誤或錯漏字，維持原圖。
  7. `emergency_contraceptive_pills_notice`（`img/emergency_contraceptive_pills_notice.webp`）：修正機轉說明、嘔吐補服評估（3 小時內嘔吐依仿單為 2 或 3 小時）、後續避孕（LNG 可立即開始或恢復並加用保險套 7 天；UPA 須等滿 5 天第 6 天才開始或恢復荷爾蒙避孕藥，等待期間及重新服藥後 7 天使用保險套或避免性行為）、月經延遲超過 7 天或服藥後 3 週未出血應驗孕，以及移除「一年不超過 2 次」絕對限制。
- 實際檢視修正後 7 張圖卡與正文確認一致後，於 `data/card_content.json` 設定 `matchConfidence: "high"`；保留 `needsMedicalReview: true`，管理清冊 `medical_review_status` 維持 `unknown`，不宣稱已完成具名人工醫療複核。
- 系列 ID（`NTG`、`contraceptive_pills`）、頁面 URL、圖片路徑與副檔名、收藏鍵及分類標籤均維持不變。
- 執行 `build.py --only` 更新 7 張舊版 HTML 結構後執行 `build.py --incremental`，成功整合靜態文字並更新 `seo.json`、`all-cards.html`、`sitemap.xml`、`sitemap-main.xml`、`data/card_text_web_integration_report.md` 及 `sw.js`。
- `scripts/check_site.py` 通過；7 頁 `scripts/check_project_management.py --propose` 零差異、零移除、零來源錯誤。
- 未 Commit、Push 或部署。

## 變更檔案清單（供 GitHub Desktop 審核）

- `img/NTG_1.png`
- `img/NTG_2.png`
- `img/NTG_3.webp`
- `img/contraceptive_pills_how_to_take.webp`
- `img/contraceptive_pills_missed_dose.webp`
- `img/emergency_contraceptive_pills_notice.webp`
- `data/card_content.json`
- `cards/NTG_1.html`
- `cards/NTG_2.html`
- `cards/NTG_3.html`
- `cards/contraceptive_pills_how_to_take.html`
- `cards/contraceptive_pills_missed_dose.html`
- `cards/emergency_contraceptive_pills_how_to_take.html`
- `cards/emergency_contraceptive_pills_notice.html`
- `all-cards.html`
- `seo.json`
- `sitemap.xml`
- `sitemap-main.xml`
- `sw.js`
- `data/card_text_web_integration_report.md`
- `docs/project-management/page-inventory.csv`
- `docs/project-management/change-requests.csv`
- `docs/project-management/project-dashboard.md`
- `docs/project-management/evidence/ntg-contraceptive-text-2026-10-31.md`
