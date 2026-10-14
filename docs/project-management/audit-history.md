# 盤點與維護歷史索引

整合日期：2026-10-13。納入37份既有文件：26份盤點／品質／測試報告、5份維護交接紀錄、4份建置摘要、1份生成整合報告、1份Pilot規格。每份保留原檔，下面是管理摘要，非新的醫療審查。未知盤點日期保持unknown；Git提交時間只證明檔案版本，不能代替實際盤點日。

機器可核對索引：[audit-register.json](audit-register.json)。每個AUD ID穩定，後續只追加事件，不重編。`current_structural`只表示仍可引用結構/方法限制，不是外部醫療資料仍有效。原報告提過的線上成果本次均未重新確認。

## 已知跨報告／版本變化

| 範圍 | 舊結論 | 後續證據與管理處理 |
|---|---|---|
| 歷史文字復原 | 263母體、11→26→65文字；early unmatched | 當前179筆原紀錄含3退出；176現行文字區塊。保留歷史配對，不把unmatched當現在缺文字 |
| 部署前14樣本 | 11 PASS、3 REVIEW | 14個精確頁ID連回AUD-001；PASS非藥師審閱。兒科糖漿已移除文字，口腔/驗孕REVIEW未見結案 |
| 青春痘 | Phase1 20頁/6系列、無專頁、提案關聯 | dc60f74專頁與四頁Pilot；ae69011洗臉13張；10914b0手機套用。現為7系列33頁，不能把Phase1全網提案當完成 |
| 青春痘維護 | 三頁同列已補與待補 | **conflict**，836428a及現行metadata證明已存在；CR-2026-018保留文件矛盾，不重新造頁 |
| 傷口 | 第二批列為提案 | 6d04b3e及現行postoperative_wound/diabetic_foot/elderly_skin_tear已存在；提案狀態過時 |
| 浣腸 | 11頁與早期讀圖誤述 | 同文件10-11明確更正；737f2ab退出enema_comp後10頁，原圖待核未結案 |
| 三頁SEO | 107文字頁、三頁展開文字 | 803a359有修訂；a04524d後兩張糖漿無文字，不沿用舊完成作現況 |
| 文字整合報告 | 176成功、0失敗 | **conflict（驗證口徑）**：目前逐段原文比對175一致、1字詞差異；09_australia_usa_china有「不保證」被生成器刪詞。保留兩個結果，不宣稱舊檢查涵蓋此問題 |
| 中藥POC | 80/80 high | **conflict（方法）**：後輪明確否定legacy formulaId可作ground truth。樣本不同不能直接比率比較，需專家確認方法；不取較好數字 |
| 咳嗽POC | synthetic/adversarial成功率 | 真實病例0、雙人標註0，not_assessed；不是已完成臨床驗證 |
| 共用頁尾/JSON-LD | 生成器已具共用功能 | 實際HTML只部分覆蓋；333ed52僅修改3頁structured data。不得由程式支援推認全站完成 |

## 文件明細

### AUD-001 — 圖卡文字頁部署前品質抽查

- 盤點日期：2026-08-23；依據：report_text。範圍：14 張部署前抽樣；當時 65 筆文字。
- 原始報告：[data/card_text_predeploy_audit.md](../../data/card_text_predeploy_audit.md)。本機狀態：tracked。
- 當時結果：11 PASS、3 REVIEW、0 FAIL；PASS 是版本一致性抽查，不是藥師簽核。
- 已知／未處理：口腔清潔、驗孕判讀仍待人工確認；兒科糖漿舊文字已移除。
- 後續修正／現況：三頁修訂後另移除兒科糖漿文字；不能沿用舊 PASS/REVIEW 當現況。
- 後續對照 Commit：`803a35938468c96376d5ec32d2e1bec46b931c9e`, `a04524d218cb408ed6c423afaef9714ae94a07e0`。此欄是相關變化，並非所有問題已結案。
- 報告最後 Commit：`3fcde82522f5f0aba7bf2916c70cf6d9c7d699ff`；提交時間：2026-08-23T12:01:44+08:00（非盤點日期）。
- 有效性：`partially_superseded`。證據 SHA-256：`d9f8f53f453e3b333908be12d7292d8a1a89e8ff614890f60089fa68007c8b02`。

### AUD-002 — 圖卡與歷史文字配對摘要

- 盤點日期：unknown；依據：unknown。範圍：第一批 263 張歷史文字配對。
- 原始報告：[data/card_content_match_summary.md](../../data/card_content_match_summary.md)。本機狀態：untracked。
- 當時結果：high 20、medium 7、unmatched 236。
- 已知／未處理：初批結果不代表現在無文字；對話匯出檔未在本機根目錄找到。
- 後續修正／現況：後續復原與現行 card_content 已取代數量。
- 後續對照 Commit：unknown。此欄是相關變化，並非所有問題已結案。
- 報告最後 Commit：`unknown`；提交時間：unknown（非盤點日期）。
- 有效性：`historical_only`。證據 SHA-256：`e1f0a2c7eda8e1a2defd8bc264e5549bedaba9392ce8c283ad937d7adae93b81`。

### AUD-003 — 圖卡歷史文字復原報告

- 盤點日期：unknown；依據：unknown。範圍：263 張歷史文字復原。
- 原始報告：[data/card_content_recovery_report.md](../../data/card_content_recovery_report.md)。本機狀態：untracked。
- 當時結果：high 11、medium 51、low 57、not_found 144。
- 已知／未處理：未取得直接定稿證據者不可自動升級。
- 後續修正／現況：後續批次已變更配對數；保留原始版本。
- 後續對照 Commit：unknown。此欄是相關變化，並非所有問題已結案。
- 報告最後 Commit：`unknown`；提交時間：unknown（非盤點日期）。
- 有效性：`historical_only`。證據 SHA-256：`32423301baabac444fc9db73250fe285f933b5cf1abcf3f982febbeccacdf1f5`。

### AUD-004 — Medium 第二輪人工複核報告

- 盤點日期：unknown；依據：unknown。範圍：36 張 medium 第二輪複核。
- 原始報告：[data/medium_review_report.md](../../data/medium_review_report.md)。本機狀態：untracked。
- 當時結果：保留 36 張 medium；包含換藥頻率差異。
- 已知／未處理：不能從相似主題對話推認圖卡最後版本。
- 後續修正／現況：傷口後續改版已取代舊換藥問題；其他個別結果須按圖片 ID 查。
- 後續對照 Commit：`f6513c5fc2fbdc6d4ee537fd361fd08cdec748bb`。此欄是相關變化，並非所有問題已結案。
- 報告最後 Commit：`unknown`；提交時間：unknown（非盤點日期）。
- 有效性：`partially_superseded`。證據 SHA-256：`e0928b23ac6fffdb65313c43ce1a05f37d4c1a4fe36379da7b6b17ae3b35045a`。

### AUD-005 — 第二批 medium 圖卡文字整合報告

- 盤點日期：unknown；依據：unknown。範圍：36 張 medium。
- 原始報告：[data/card_text_batch2_report.md](../../data/card_text_batch2_report.md)。本機狀態：untracked。
- 當時結果：無升 high；26 個文字頁；1 個實質矛盾。
- 已知／未處理：未定位最後定稿的 36 張保留；非 36 張醫療錯誤。
- 後續修正／現況：傷口改版；眼藥資料庫紀錄不能冒充眼藥膏圖卡文字。
- 後續對照 Commit：`f6513c5fc2fbdc6d4ee537fd361fd08cdec748bb`。此欄是相關變化，並非所有問題已結案。
- 報告最後 Commit：`unknown`；提交時間：unknown（非盤點日期）。
- 有效性：`partially_superseded`。證據 SHA-256：`7324c992d0632f8ccd29672427da1bc9bf20adccd131577f6564e4869e406cd8`。

### AUD-006 — Card Text Recovery Round 3 Report

- 盤點日期：unknown；依據：unknown。範圍：57 low、144 not_found。
- 原始報告：[data/card_text_recovery_round3_report.md](../../data/card_text_recovery_round3_report.md)。本機狀態：untracked。
- 當時結果：39 新增 high，累計 65 文字頁；61 needsMedicalReview。
- 已知／未處理：配對 high 不等於醫療審閱。
- 後續修正／現況：現行 179 筆原始文字紀錄，含退出資料；舊總數已過時。
- 後續對照 Commit：unknown。此欄是相關變化，並非所有問題已結案。
- 報告最後 Commit：`unknown`；提交時間：unknown（非盤點日期）。
- 有效性：`historical_only`。證據 SHA-256：`3c9eec8f0891bdf2df5cb5dc9310ddfe7157ee3b84293fa97e7c348ce8b15907`。

### AUD-007 — 圖卡文字網頁整合報告

- 盤點日期：unknown；依據：unknown。範圍：176 頁靜態文字整合。
- 原始報告：[data/card_text_web_integration_report.md](../../data/card_text_web_integration_report.md)。本機狀態：tracked。
- 當時結果：文件記錄 176 成功、0 失敗；僅涵蓋 title/meta/h1/alt/text。
- 已知／未處理：本次另比較段落文字；09_australia_usa_china 字詞差異，原檢查未覆蓋。
- 後續修正／現況：保留文件成功與嚴格段落比對差異；不推論全站 AEO 或醫療通過。
- 後續對照 Commit：`333ed52512cfbaf2b0f900e76605bc0b5c8264cc`。此欄是相關變化，並非所有問題已結案。
- 報告最後 Commit：`737f2ab9c395636bc838c426c585842233f9f3a5`；提交時間：2026-10-13T00:23:33+08:00（非盤點日期）。
- 有效性：`conflict`。證據 SHA-256：`216c6f181c80ccaba29a07d695366ede86b3b3a93a543d853c5ad03e620cec9e`。

### AUD-008 — 三頁 SEO 與圖卡修訂紀錄

- 盤點日期：2026-09-27；依據：report_text。範圍：混擦、息咳寧、勝克敏三頁。
- 原始報告：[data/seo_three_pages_20260927.md](../../data/seo_three_pages_20260927.md)。本機狀態：tracked。
- 當時結果：圖文修訂；2026-09-28 驗證；未有醫藥人員審閱紀錄。
- 已知／未處理：混擦鄰頁規則仍不一致；成效未追蹤；作者署名待確認。
- 後續修正／現況：後續兒科糖漿文字移除；原 GSC 30 天數據不能當目前成效。
- 後續對照 Commit：`803a35938468c96376d5ec32d2e1bec46b931c9e`, `a04524d218cb408ed6c423afaef9714ae94a07e0`。此欄是相關變化，並非所有問題已結案。
- 報告最後 Commit：`803a35938468c96376d5ec32d2e1bec46b931c9e`；提交時間：2026-09-28T02:10:34+08:00（非盤點日期）。
- 有效性：`partially_superseded`。證據 SHA-256：`504f584ad19fa998b1ac03dbdc93b79618cb49cfd014c2c09beeddb8bedfc165`。

### AUD-009 — 青春痘系列圖文待修清單

- 盤點日期：2026-10-02；依據：report_text。範圍：青春痘 12 頁新版文字與舊圖。
- 原始報告：[data/acne_image_text_followup_2026-10-02.md](../../data/acne_image_text_followup_2026-10-02.md)。本機狀態：tracked。
- 當時結果：粉刺、抗生素等圖文差異及視覺風險分級。
- 已知／未處理：修圖待辦仍保留；A 酸/BPO/杜鵑花酸非本報告圖文衝突。
- 後續修正／現況：文字已在 Git；未提交說法過時；Phase 1 再區分視覺風險。
- 後續對照 Commit：`95b316405a2db991dc8fed2920e94318f594cd27`。此欄是相關變化，並非所有問題已結案。
- 報告最後 Commit：`95b316405a2db991dc8fed2920e94318f594cd27`；提交時間：2026-10-02T17:28:02+08:00（非盤點日期）。
- 有效性：`partially_superseded`。證據 SHA-256：`b4949b756ec522ef9883ab7cf625104b85aa84bca6bda05aeebeb054ed65611f`。

### AUD-010 — 青春痘內容體系 Phase 1 — 既有內容重新建模與關聯盤點

- 盤點日期：2026-10-06；依據：report_text。範圍：20 核心頁、6 系列、10 共用資產、3 退出頁。
- 原始報告：[docs/acne-phase1-content-map.md](../../docs/acne-phase1-content-map.md)。本機狀態：tracked。
- 當時結果：19 靜態文字、12 日期來源齊；列 P0-P3 與 Phase 2 缺口。
- 已知／未處理：粉刺/抗生素/混擦風險；部分來源缺漏；多數建議關聯未實作。
- 後續修正／現況：現有主題頁及 13 張洗臉卡；Pilot 僅四頁；不能把全份建議視為完成。
- 後續對照 Commit：`dc60f74e8201f7edf6cb3cee8fd23e3ff5b035cd`, `ae69011781335ab90f6cacc59a253d3744b21c58`, `10914b07ef109bb5f523674b96373776a937dab3`。此欄是相關變化，並非所有問題已結案。
- 報告最後 Commit：`dc60f74e8201f7edf6cb3cee8fd23e3ff5b035cd`；提交時間：2026-10-09T10:01:33+08:00（非盤點日期）。
- 有效性：`partially_superseded`。證據 SHA-256：`ed4ad35c6e1f6621cf888aeb1cc5c0140fc016ba613dd186b9463e00d93d9cd6`。

### AUD-011 — 青春痘系列重整與後續製作紀錄

- 盤點日期：2026-09-08；依據：report_text。範圍：6 系列重整與退出。
- 原始報告：[docs/acne-series-maintenance.md](../../docs/acne-series-maintenance.md)。本機狀態：tracked。
- 當時結果：20 張分組與收藏識別保留。
- 已知／未處理：同時寫已補充與待補充三張，文件 conflict。
- 後續修正／現況：三頁已存在；完成與待補文字衝突未修改原報告。
- 後續對照 Commit：`733f3269410cfdc127c392d1b2fda22461493caa`, `836428ac6166af5193c9732eba8d9e3919aca975`。此欄是相關變化，並非所有問題已結案。
- 報告最後 Commit：`836428ac6166af5193c9732eba8d9e3919aca975`；提交時間：2026-09-09T09:46:31+08:00（非盤點日期）。
- 有效性：`conflict`。證據 SHA-256：`43275998d42de0f54a1b1c6b59215c6c66566216ecfe172852fb2dfd6ff230ed`。

### AUD-012 — 青春痘 Topic Pilot 規格 v1.0

- 盤點日期：2026-10-08；依據：report_text。範圍：四頁 Pilot v1.0；含 10-10 更新。
- 原始報告：[docs/acne-pilot-spec.md](../../docs/acne-pilot-spec.md)。本機狀態：modified。
- 當時結果：規範區塊順序、下一問來源與主題頁。
- 已知／未處理：規格不等於所有頁完成；本機有未提交修改。
- 後續修正／現況：本次沿用四頁清單；不擴大問題導覽。
- 後續對照 Commit：`dc60f74e8201f7edf6cb3cee8fd23e3ff5b035cd`, `ae69011781335ab90f6cacc59a253d3744b21c58`。此欄是相關變化，並非所有問題已結案。
- 報告最後 Commit：`ae69011781335ab90f6cacc59a253d3744b21c58`；提交時間：2026-10-10T09:28:11+08:00（非盤點日期）。
- 有效性：`current_structural`。證據 SHA-256：`2291b77879efa08f6f87ec7828559c7adcaf31ed5d5da89c2211fa84ff258922`。

### AUD-013 — 青春痘圖卡手機版面套用工作規則

- 盤點日期：2026-10-10；依據：report_text。範圍：7 系列 33 張手機版面。
- 原始報告：[docs/acne-mobile-card-rollout.md](../../docs/acne-mobile-card-rollout.md)。本機狀態：untracked。
- 當時結果：文件記錄本機預覽與測試；翻頁不固定螢幕底部。
- 已知／未處理：本機未追蹤文件；發布狀態未由線上驗證。
- 後續修正／現況：對應實作已提交；頁面存在不能证明 Pages 部署。
- 後續對照 Commit：`10914b07ef109bb5f523674b96373776a937dab3`。此欄是相關變化，並非所有問題已結案。
- 報告最後 Commit：`unknown`；提交時間：unknown（非盤點日期）。
- 有效性：`partially_superseded`。證據 SHA-256：`914bbeda05931b01569b5cb06a6670aa1a443cebc66b2896cc6e1d863898e2ce`。

### AUD-014 — 傷口照護圖卡盤點與重整建議

- 盤點日期：2026-09-09；依據：report_text。範圍：12 傷口、6 燙傷及相鄰系列抽查。
- 原始報告：[docs/wound-care-review-2026-09-09.md](../../docs/wound-care-review-2026-09-09.md)。本機狀態：tracked。
- 當時結果：提出重新分組、4 新卡與舊圖風險。
- 已知／未處理：醫療簽核未確認；後續修訂優先引用維護文件。
- 後續修正／現況：維護紀錄及 revision JSON 已記載第一批修正。
- 後續對照 Commit：`f6513c5fc2fbdc6d4ee537fd361fd08cdec748bb`。此欄是相關變化，並非所有問題已結案。
- 報告最後 Commit：`f6513c5fc2fbdc6d4ee537fd361fd08cdec748bb`；提交時間：2026-09-10T08:59:19+08:00（非盤點日期）。
- 有效性：`partially_superseded`。證據 SHA-256：`19d94934aa9be4cddc6c09fdafba297e9ce1f141944867653b0e9cbf698cdeec`。

### AUD-015 — 傷口照護系列重整

- 盤點日期：2026-09-09；依據：report_text。範圍：18 張改版/新增及系列收藏。
- 原始報告：[docs/wound-care-maintenance.md](../../docs/wound-care-maintenance.md)。本機狀態：tracked。
- 當時結果：18 圖與來源、網頁及收藏回歸完成記錄。
- 已知／未處理：來源查閱不等於臨床簽核；部署未重查。
- 後續修正／現況：文件列第二批提案：術後傷口、糖尿病足、長者撕裂傷現已存在。
- 後續對照 Commit：`f6513c5fc2fbdc6d4ee537fd361fd08cdec748bb`, `6d04b3e5778061e2b5893d968148418cdb8e509e`。此欄是相關變化，並非所有問題已結案。
- 報告最後 Commit：`f6513c5fc2fbdc6d4ee537fd361fd08cdec748bb`；提交時間：2026-09-10T08:59:19+08:00（非盤點日期）。
- 有效性：`partially_superseded`。證據 SHA-256：`69d64ade14fa50c886216bd07c153ccb1e5ae5b0ade81d2ed8f2df819514f588`。

### AUD-016 — 浣腸使用系列文字與來源整理

- 盤點日期：2026-10-09；依據：report_text。範圍：10-09 十一頁；10-11 修訂；10-12 退出。
- 原始報告：[docs/enema-series-maintenance-2026-10-09.md](../../docs/enema-series-maintenance-2026-10-09.md)。本機狀態：tracked。
- 當時結果：臺灣甘油文字重製；比較卡退出；文件明確更正早期讀圖誤述。
- 已知／未處理：插入深度、回溫、留置時間等原圖仍待確認；不要沿用已撤回的 PEG 錯誤引述。
- 後續修正／現況：現行 10 張；退出 1 張；文件未 commit 字句已過時。
- 後續對照 Commit：`306b956653446bfb8c6e0c88763fd511253a2873`, `737f2ab9c395636bc838c426c585842233f9f3a5`。此欄是相關變化，並非所有問題已結案。
- 報告最後 Commit：`737f2ab9c395636bc838c426c585842233f9f3a5`；提交時間：2026-10-13T00:23:33+08:00（非盤點日期）。
- 有效性：`partially_superseded`。證據 SHA-256：`60dffcd6fa887122f1d162cee33c7dd32e03b0559dc57a7a5781b14408cc3e02`。

### AUD-017 — 中成藥母方查詢交接說明

- 盤點日期：unknown；依據：unknown。範圍：中成藥母方研究工具。
- 原始報告：[docs/tcm_formula_explorer_handover.md](../../docs/tcm_formula_explorer_handover.md)。本機狀態：tracked。
- 當時結果：記錄 21196 產品、204 母方、32 分檔；已移除公開入口。
- 已知／未處理：演算法推測易被當官方；編碼、效能及專業審查未完成。
- 後續修正／現況：保留頁面不等於允許重上公開入口。
- 後續對照 Commit：`1b064456e3edc2d0d24dacc407759f17c0d4aad5`。此欄是相關變化，並非所有問題已結案。
- 報告最後 Commit：`1b064456e3edc2d0d24dacc407759f17c0d4aad5`；提交時間：2026-07-27T23:52:52+08:00（非盤點日期）。
- 有效性：`current_structural`。證據 SHA-256：`bc76fa164cbfc423add65efeabbab069754bdaf0256b44ac053057785bab2fe4`。

### AUD-018 — 民眾圖卡搜尋熱度排序（2026-09-06）

- 盤點日期：2026-09-06；依據：report_text。範圍：民眾系列關鍵字代理排序。
- 原始報告：[data/public_search_popularity_20260906.md](../../data/public_search_popularity_20260906.md)。本機狀態：tracked。
- 當時結果：Google Trends 臺灣過去12個月，乾眼症近似校準。
- 已知／未處理：不是本站流量、疾病盛行或醫療優先；目前成效 unknown。
- 後續修正／現況：後續新增與分組不可直接沿用舊排名。
- 後續對照 Commit：unknown。此欄是相關變化，並非所有問題已結案。
- 報告最後 Commit：`4443bd2f6dfcae19d3f2a7f51e0615e8a30c5af9`；提交時間：2026-09-07T00:14:19+08:00（非盤點日期）。
- 有效性：`historical_only`。證據 SHA-256：`c5a6f10ad1f5c16e9fc35303c00411932d630d71cf26e7a84c12beb3066a19f8`。

### AUD-019 — Eye Meds Final Data Quality Report

- 盤點日期：2026-07-14；依據：report_text。範圍：眼用藥 492 品項。
- 原始報告：[data/eye_meds_rebuild_20260711/final/data_quality_report.md](../../data/eye_meds_rebuild_20260711/final/data_quality_report.md)。本機狀態：tracked。
- 當時結果：461 有 confirmed active、31 缺、50 unknown role 關聯。
- 已知／未處理：角色與缺失待複核；不是492品项均完成藥師簽核。
- 後續修正／現況：網站配置仍指向 final JSON；未重新審查藥證。
- 後續對照 Commit：`a0f4676e3e6c01762b68e5c53677509da360dfd8`。此欄是相關變化，並非所有問題已結案。
- 報告最後 Commit：`a0f4676e3e6c01762b68e5c53677509da360dfd8`；提交時間：2026-07-14T01:50:45+08:00（非盤點日期）。
- 有效性：`historical_only`。證據 SHA-256：`4b704cdb71818004acfae6d9f36f5e959616545ded2e0b0c6d6a5cc779b482be`。

### AUD-020 — Eye Meds Final Build Summary

- 盤點日期：2026-07-14；依據：report_text。範圍：眼用藥 final 匯出。
- 原始報告：[data/eye_meds_rebuild_20260711/final/final_build_summary.md](../../data/eye_meds_rebuild_20260711/final/final_build_summary.md)。本機狀態：tracked。
- 當時結果：492 products、195 substances、476 manual-review rows。
- 已知／未處理：部分報告列出的來源 CSV 不在現有 checkout；不能推測可完整重建。
- 後續修正／現況：匯出與清單存在；原建置輸入完整性待處理。
- 後續對照 Commit：`a0f4676e3e6c01762b68e5c53677509da360dfd8`。此欄是相關變化，並非所有問題已結案。
- 報告最後 Commit：`a0f4676e3e6c01762b68e5c53677509da360dfd8`；提交時間：2026-07-14T01:50:45+08:00（非盤點日期）。
- 有效性：`historical_only`。證據 SHA-256：`129af5b67f5a6f9ad88544e24eac8b59364e7e646f598206c6d207a2abf29e62`。

### AUD-021 — Build summary

- 盤點日期：unknown；依據：unknown。範圍：口服液劑 Phase 2。
- 原始報告：[data/oral_liquid_meds_rebuild_20260714/build_summary.md](../../data/oral_liquid_meds_rebuild_20260714/build_summary.md)。本機狀態：tracked。
- 當時結果：905→1034；129納入、205排除、105未解。
- 已知／未處理：105未解；濃度不應猜測。
- 後續修正／現況：現有網站配置 1034，未更新藥證現況。
- 後續對照 Commit：`935f9cd799b0843534d9e7df8b7a4fb1bf3f5814`。此欄是相關變化，並非所有問題已結案。
- 報告最後 Commit：`95ae78e2b6e735eb36a42ee444d07ab3805e6f76`；提交時間：2026-07-14T17:47:19+08:00（非盤點日期）。
- 有效性：`historical_only`。證據 SHA-256：`14722462bef2e0a0a596942188a58a1f55d151424a0b20b18eb8c451c6f9054a`。

### AUD-022 — Data quality report

- 盤點日期：unknown；依據：unknown。範圍：口服液劑 1034。
- 原始報告：[data/oral_liquid_meds_rebuild_20260714/data_quality_report.md](../../data/oral_liquid_meds_rebuild_20260714/data_quality_report.md)。本機狀態：tracked。
- 當時結果：954 display concentration、937 per-mL；88品項/140列濃度待核。
- 已知／未處理：105 候選未解與濃度待核佇列分開計數。
- 後續修正／現況：現有匯出可引用；ready_for_site 不是醫療簽核。
- 後續對照 Commit：`935f9cd799b0843534d9e7df8b7a4fb1bf3f5814`。此欄是相關變化，並非所有問題已結案。
- 報告最後 Commit：`95ae78e2b6e735eb36a42ee444d07ab3805e6f76`；提交時間：2026-07-14T17:47:19+08:00（非盤點日期）。
- 有效性：`historical_only`。證據 SHA-256：`053975b9e521fb88b45ccd9ed3deaf15bef66500473bd9234491193b31608635`。

### AUD-023 — Sample validation

- 盤點日期：unknown；依據：unknown。範圍：30 筆規則驗證樣本。
- 原始報告：[data/oral_liquid_meds_rebuild_20260714/sample_validation.md](../../data/oral_liquid_meds_rebuild_20260714/sample_validation.md)。本機狀態：tracked。
- 當時結果：依劑型及核准口服途徑選入。
- 已知／未處理：僅規則樣本，無全資料臨床複核。
- 後續修正／現況：保留 sample_validation.csv，不重跑醫療審查。
- 後續對照 Commit：`935f9cd799b0843534d9e7df8b7a4fb1bf3f5814`。此欄是相關變化，並非所有問題已結案。
- 報告最後 Commit：`95ae78e2b6e735eb36a42ee444d07ab3805e6f76`；提交時間：2026-07-14T17:47:19+08:00（非盤點日期）。
- 有效性：`historical_only`。證據 SHA-256：`f3c6caa3397ab9f4498991a7139312edf03674bb91b5bc5acd3ea750b9f8c1f1`。

### AUD-024 — Build summary

- 盤點日期：unknown；依據：unknown。範圍：18 噴劑候選。
- 原始報告：[data/spray_meds_rebuild_20260714/build_summary.md](../../data/spray_meds_rebuild_20260714/build_summary.md)。本機狀態：tracked。
- 當時結果：1 納入、12 排除、5 unresolved。
- 已知／未處理：5 lidocaine sprays 不入正式統計。
- 後續修正／現況：現有配置141；ready_for_site僅核心欄位。
- 後續對照 Commit：`935f9cd799b0843534d9e7df8b7a4fb1bf3f5814`。此欄是相關變化，並非所有問題已結案。
- 報告最後 Commit：`21a026a9576b2c89ff936e475b041d734370ae5d`；提交時間：2026-07-14T11:45:56+08:00（非盤點日期）。
- 有效性：`historical_only`。證據 SHA-256：`d5d3bacfb369383d00c8dc9bb301393a97f49b4a42b65944f99b88d8c5404570`。

### AUD-025 — Data quality report

- 盤點日期：unknown；依據：unknown。範圍：141 局部噴劑。
- 原始報告：[data/spray_meds_rebuild_20260714/data_quality_report.md](../../data/spray_meds_rebuild_20260714/data_quality_report.md)。本機狀態：tracked。
- 當時結果：鼻97/咽30/口腔14；核心100%，選填17.6%。
- 已知／未處理：5未解；防腐/賦形/仿單缺漏不猜測。
- 後續修正／現況：不代表最新核准資料或專業簽核。
- 後續對照 Commit：`935f9cd799b0843534d9e7df8b7a4fb1bf3f5814`。此欄是相關變化，並非所有問題已結案。
- 報告最後 Commit：`21a026a9576b2c89ff936e475b041d734370ae5d`；提交時間：2026-07-14T11:45:56+08:00（非盤點日期）。
- 有效性：`historical_only`。證據 SHA-256：`4f3e5e595c75576d3424234456cdfb543ca77a151ffef369a9758f44642d13bd`。

### AUD-026 — 20-record rule-validation sample

- 盤點日期：unknown；依據：unknown。範圍：20 筆規則樣本。
- 原始報告：[data/spray_meds_rebuild_20260714/sample_validation.md](../../data/spray_meds_rebuild_20260714/sample_validation.md)。本機狀態：tracked。
- 當時結果：含納入、排除、未解與零命中負向控制。
- 已知／未處理：無 bulk 仿單/OCR；不能外推臨床可靠度。
- 後續修正／現況：保留可追溯抽樣範圍。
- 後續對照 Commit：`935f9cd799b0843534d9e7df8b7a4fb1bf3f5814`。此欄是相關變化，並非所有問題已結案。
- 報告最後 Commit：`21a026a9576b2c89ff936e475b041d734370ae5d`；提交時間：2026-07-14T11:45:56+08:00（非盤點日期）。
- 有效性：`historical_only`。證據 SHA-256：`d0801a53306840a5c3a6a591c2ced97d78b333e502074de0c75c22897e0a4743`。

### AUD-027 — Build summary

- 盤點日期：unknown；依據：unknown。範圍：塞劑 Phase 1。
- 原始報告：[data/suppository_meds_rebuild_20260714/build_summary.md](../../data/suppository_meds_rebuild_20260714/build_summary.md)。本機狀態：tracked。
- 當時結果：基於既有快取的資料建置。
- 已知／未處理：optional detail 不補猜測。
- 後續修正／現況：只資料成果，不是發布驗證。
- 後續對照 Commit：`935f9cd799b0843534d9e7df8b7a4fb1bf3f5814`。此欄是相關變化，並非所有問題已結案。
- 報告最後 Commit：`27e82ef67145b9d5b6c5f74de9513caf4e4721b2`；提交時間：2026-07-14T12:19:58+08:00（非盤點日期）。
- 有效性：`historical_only`。證據 SHA-256：`2c5b48ef8d963b5cbd7e24c0b9e3b2905446ca007d8a294ac88d996d389308ec`。

### AUD-028 — Data quality report

- 盤點日期：unknown；依據：unknown。範圍：148 正式產品。
- 原始報告：[data/suppository_meds_rebuild_20260714/data_quality_report.md](../../data/suppository_meds_rebuild_20260714/data_quality_report.md)。本機狀態：tracked。
- 當時結果：直腸85/陰道63，65 manual review，作用範圍32 unclear。
- 已知／未處理：65候選未解；選填0%。
- 後續修正／現況：正式匯出排除待核候選。
- 後續對照 Commit：`935f9cd799b0843534d9e7df8b7a4fb1bf3f5814`。此欄是相關變化，並非所有問題已結案。
- 報告最後 Commit：`27e82ef67145b9d5b6c5f74de9513caf4e4721b2`；提交時間：2026-07-14T12:19:58+08:00（非盤點日期）。
- 有效性：`historical_only`。證據 SHA-256：`39c2527951fe390607aa926668605199bb2b1f741ad0ec12789aece92c899cf0`。

### AUD-029 — 20-record validation sample

- 盤點日期：unknown；依據：unknown。範圍：20 筆含正負向對照。
- 原始報告：[data/suppository_meds_rebuild_20260714/sample_validation.md](../../data/suppository_meds_rebuild_20260714/sample_validation.md)。本機狀態：tracked。
- 當時結果：劑型/途徑/名稱規則通過文件記錄。
- 已知／未處理：非個別藥證當前效力查核。
- 後續修正／現況：保留CSV證據。
- 後續對照 Commit：`935f9cd799b0843534d9e7df8b7a4fb1bf3f5814`。此欄是相關變化，並非所有問題已結案。
- 報告最後 Commit：`27e82ef67145b9d5b6c5f74de9513caf4e4721b2`；提交時間：2026-07-14T12:19:58+08:00（非盤點日期）。
- 有效性：`historical_only`。證據 SHA-256：`35bacb5982e3333f69ded191c3a339bb0798fe25b687c8f2a0fd44cb1be472b5`。

### AUD-030 — Data Quality Report — 台灣吸入劑藥品資料庫

- 盤點日期：2026-07-16；依據：report_text。範圍：吸入劑68品項。
- 原始報告：[data/inhaler_meds_20260716/data_quality_report.md](../../data/inhaler_meds_20260716/data_quality_report.md)。本機狀態：tracked。
- 當時結果：86候選、18排除、15人工複核事項。
- 已知／未處理：15為事項數，不能與品項數混加。
- 後續修正／現況：現有資料仍版本v02；本次不查藥證更新。
- 後續對照 Commit：unknown。此欄是相關變化，並非所有問題已結案。
- 報告最後 Commit：`e41dd7878bd2b47bc4f0828c8eab93c3ec2d6c26`；提交時間：2026-07-17T19:51:19+08:00（非盤點日期）。
- 有效性：`historical_only`。證據 SHA-256：`c9e92b7627b527aadedc0663a894b646d2e43fc9fc77e29bbb703c86d35063b6`。

### AUD-031 — 中藥外用貼布與處方外用藥資料品質報告

- 盤點日期：unknown；依據：unknown。範圍：577 中藥外用品。
- 原始報告：[data_quality_report_tcm_external_patch_rx.md](../../data_quality_report_tcm_external_patch_rx.md)。本機狀態：tracked。
- 當時結果：564貼布、13處方外用；保留處方身分。
- 已知／未處理：母方與加減藥材僅推測。
- 後續修正／現況：引用現有資料集，未重抓來源。
- 後續對照 Commit：`2649b7abeec10e4067c9c5c5428de052960b137f`。此欄是相關變化，並非所有問題已結案。
- 報告最後 Commit：`2649b7abeec10e4067c9c5c5428de052960b137f`；提交時間：2026-07-30T19:00:14+08:00（非盤點日期）。
- 有效性：`historical_only`。證據 SHA-256：`79b981c868bdc91c5d52fabdec855ab4c4a7dc678fdaceaa2263051bc65e7966`。

### AUD-032 — 資料品質報告

- 盤點日期：unknown；依據：unknown。範圍：577 外用品配方。
- 原始報告：[data/tcm_external_formula_patterns_20260730/data_quality_report.md](../../data/tcm_external_formula_patterns_20260730/data_quality_report.md)。本機狀態：tracked。
- 當時結果：11138材料列、58群、29待核名稱。
- 已知／未處理：相似度分群不是療效或傳統母方證據。
- 後續修正／現況：持續引用 material_normalization_review_queue.csv。
- 後續對照 Commit：`75920a861982780a88cf352469fa0520adfe52b9`。此欄是相關變化，並非所有問題已結案。
- 報告最後 Commit：`e514cb8e6c23888f8fb17983d88053a9950e40d9`；提交時間：2026-07-30T19:55:34+08:00（非盤點日期）。
- 有效性：`historical_only`。證據 SHA-256：`74a5aa7cf6c25523d1bd01110ee93e7fda311b5b2ef5e0ef18f69f146b033cea`。

### AUD-033 — 中藥辨證－固有成方 POC：資料品質報告

- 盤點日期：2026-08-19；依據：report_text。範圍：辨證POC 6主症/26關聯/80產品。
- 原始報告：[data/tcm_syndrome_poc_20260819/data_quality_report.md](../../data/tcm_syndrome_poc_20260819/data_quality_report.md)。本機狀態：untracked。
- 當時結果：80/80 high；治理佇列2。
- 已知／未處理：高信心沿用演算法 formulaId，後輪質疑。
- 後續修正／現況：不可採信80/80為完成；與壓力測試方法衝突保留待專家決策。
- 後續對照 Commit：unknown。此欄是相關變化，並非所有問題已結案。
- 報告最後 Commit：`unknown`；提交時間：unknown（非盤點日期）。
- 有效性：`conflict`。證據 SHA-256：`7e6ace27f2604474659ac39cc3525e723dee119f6c4cacf211e803c37a37aec5`。

### AUD-034 — tcm_syndrome_poc 第二階段壓力測試

- 盤點日期：unknown；依據：unknown。範圍：100 困難產品壓力測試。
- 原始報告：[data/tcm_syndrome_poc_20260819/stress_test_20260819/validation_report.md](../../data/tcm_syndrome_poc_20260819/stress_test_20260819/validation_report.md)。本機狀態：untracked。
- 當時結果：high/medium/low 1/13/86；100需人工。
- 已知／未處理：不同樣本非簡單比例對比；第一階段基準過度樂觀。
- 後續修正／現況：否定沿用formulaId為ground truth；未有臨床簽核。
- 後續對照 Commit：unknown。此欄是相關變化，並非所有問題已結案。
- 報告最後 Commit：`unknown`；提交時間：unknown（非盤點日期）。
- 有效性：`conflict`。證據 SHA-256：`f330c18ed2e8e3dcf32c4ecb00479e48539c6074275af7cb92982dc58b7665bb`。

### AUD-035 — 咳嗽症狀導向中成藥選擇 POC 測試報告

- 盤點日期：2026-08-27；依據：report_text。範圍：30 synthetic cases。
- 原始報告：[data/cough_poc_test_report.md](../../data/cough_poc_test_report.md)。本機狀態：untracked。
- 當時結果：30/30預期模式；14 manual review。
- 已知／未處理：模擬資料不能當真實病例驗證。
- 後續修正／現況：下一輪50邊界案例；正式真實案例仍0。
- 後續對照 Commit：unknown。此欄是相關變化，並非所有問題已結案。
- 報告最後 Commit：`unknown`；提交時間：unknown（非盤點日期）。
- 有效性：`historical_only`。證據 SHA-256：`82ba46d5e6a9d8ba93739155a42832859b2742069ff3977f99b4a8276a8b01d5`。

### AUD-036 — 咳嗽 POC 第二階段：邊界案例與重疊規則審查

- 盤點日期：2026-08-27；依據：report_text。範圍：50 adversarial cases。
- 原始報告：[data/cough_adversarial_test_report.md](../../data/cough_adversarial_test_report.md)。本機狀態：untracked。
- 當時結果：Top1 44/50、Top2 50/50；安全4/4。
- 已知／未處理：小樣本/人工規則不能推論實際診斷效度。
- 後續修正／現況：下一階段真實案例gate未評估。
- 後續對照 Commit：unknown。此欄是相關變化，並非所有問題已結案。
- 報告最後 Commit：`unknown`；提交時間：unknown（非盤點日期）。
- 有效性：`historical_only`。證據 SHA-256：`6cb3733fa3acfa72ed6ec601368eacc3771342f1f290f18b1d53b2c4573fb704`。

### AUD-037 — 咳嗽中成藥 POC 第三階段：真實案例驗證報告

- 盤點日期：2026-08-27；依據：report_text。範圍：真實案例驗證框架。
- 原始報告：[data/cough_real_case_validation_report.md](../../data/cough_real_case_validation_report.md)。本機狀態：untracked。
- 當時結果：真實案例0、雙人標註0、not_assessed。
- 已知／未處理：需實際案例與雙人標註；不可用模擬補足。
- 後續修正／現況：框架已存在；病例驗證未完成。
- 後續對照 Commit：unknown。此欄是相關變化，並非所有問題已結案。
- 報告最後 Commit：`unknown`；提交時間：unknown（非盤點日期）。
- 有效性：`current_structural`。證據 SHA-256：`fbce3034df690711194b0b4f07aaf43c6df93bb8255d8bd0c6f1fce9c3c7199b`。

## Git與現行程式補充證據（不計入37份報告）

- `333ed52`：structured data作者與日期修正，diff只列三張圖卡，不代表全部頁重建。
- `c7124dd`：兩份sitemap加入本站資訊與青春痘主題；這是本機Git證據，非搜索引擎收錄。
- `306b956`：浣腸文字與共用頁尾；當前尚有生成器與三張頁面的未提交修改，必須區分來源與輸出。
- `935f9cd`：藥品查詢共用介面；實際目前資料路徑由js/medicine-explorer-config.js確認。
- `1b06445`：移除中成藥母方公開入口，檔案保留作研究用途。
- `47f4486`、`9dad424`、`6844fc4`：經期計算器、互動追蹤與科別入口；未找到可代替公式/邊界驗證的完整報告。
- `.github/workflows/auto-build.yml`、`scheduled-card-publish.yml`及AGENTS記錄目前發布限制；未觸發任何workflow。

## 追加格式

後續每次只在此追加：日期、CR、精確頁/系列/工具ID、變更前證據指紋/Commit、修改範圍、新驗證、尚未解决事項、簽核是否失效、對應Commit/部署狀態。不要重寫上方歷史或改原報告數字。報告文件本身更新時，在追加事件中記錄舊SHA/版本、新SHA與理由，再更新audit-register的目前指紋。

## 2026-10-13｜CR-2026-026 新增彈性襪

- 範圍：series:compression_stockings 的八個新頁，以及索引、PWA 與管理投影；來源與圖文對應見 [任務證據](evidence/compression-stockings-2026-10-13.md)。未改既有圖卡內容或人工醫療欄位。
- AUD-007 舊版本為 176 成功、0 失敗。先保存 [重建前原報告快照](evidence/card-text-integration-before-compression-2026-10-13.md)，SHA-256：216c6f181c80ccaba29a07d695366ede86b3b3a93a543d853c5ad03e620cec9e；原檔最後 Commit 為 737f2ab9c395636bc838c426c585842233f9f3a5，舊盤點日仍 unknown。
- 本次完整建置新增八頁，報告變為 184 成功、0 失敗；新 SHA-256：c64abda5ebc0555284d331f61a2fef08e124c9bfb1063a3e68750359f3db91c9。audit-register 保留 previous_versions，不以單純更新 hash 消除舊結論。
- 增量 --propose 只提出八個新 ID，沒有舊頁異動、移除或來源錯誤；[原提案](evidence/compression-stockings-proposals-2026-10-13.json)保留。新頁人工欄位 unknown，needsMedicalReview 保持 true。
- 既有 CR-2026-023 字詞比對差異仍未解，AUD-007 的 conflict 保留；機械通過不代表藥師確認、全站 AEO 或搜尋成效。
- 未新增／撤銷任何醫療簽核。Commit、Push、Pages 部署均未執行；最終測試記錄補於任務證據與 validation-report。

## 2026-10-14｜CR-2026-026 本機驗收完成

- 網站回歸檢查、管理一致性與18項管理測試通過；最終 --propose 無差異、無移除、無 source errors。
- 八頁桌面／手機圖片與循環翻頁通過，public 列表第一個系列為彈性襪。原342頁人工欄位與343個舊HTML快照比對無變動。
- CR 結案僅表示授權的本機製作及管理維護完成；不代表醫療簽核、Git提交或正式網站部署。來源查核與內容日期未隨驗收更新。
- 細節見 [任務證據](evidence/compression-stockings-2026-10-13.md)及 [驗證報告](validation-report.md)。原 CR-2026-023 與其他未核准需求不變。
