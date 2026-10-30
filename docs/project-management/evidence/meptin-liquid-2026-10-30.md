# CR-2026-049 滅喘淨液新增證據（2026-10-30）

- 使用者提供 `D:\Downloads\滅喘淨液兒童用藥衛教海報.png` 與文字、關鍵字，明確表示圖卡與文字已人工審核，要求插入兒科感冒藥水第四張，段落後引用碼移除、來源集中底部。
- 審核者姓名、資格及簽核版本證據未提供；如實保存聲明，needsMedicalReview=true，正式醫療欄位unknown。網頁不加審核待確認樣板。
- 圖片1024×1536轉WebP，原PNG保留。新頁 `ped_asthma_meptin_liquid`；既有10張URL與收藏鍵不變，新鍵 `pediatric_cold_syrup-10`，顯示順序第四。
- 今日建立網站文字版，updatedAt=2026-10-30；直接來源今日閱讀核對，sourceCheckedAt=2026-10-30。來源不放各段末尾。
- 仿單：https://www.csh.org.tw/into/pharm/DESC/MEPTL1.pdf （G-6765，衛署藥製字第043122號）。核對成分、成人／兒童劑量、年齡表、禁忌、交互作用及副作用。
- 保存來源：https://www.cth.org.tw/?aid=606&iid=1155&page_name=detail&pid=0 。核對15～30°C、避光、開封30°C以下4週與兒童拿不到處。該院常用劑量摘要與仿單略異，本頁劑量依仿單。
- 圖片為體重換算表，提供文字為年齡參考表；靜態文字同時保留兩者並區分，不讓讀者誤認兩表相同。副作用標題精確化為「常見或已知」及「嚴重不良反應（發生率不明）」，未新增用藥處方。
- 採用使用者較短版頁面標題方向與建議H1、meta description，保留既有產生器由內容title生成SEO title的行為；FAQ六題以可見靜態段落呈現，沒有聲稱搜尋排名或FAQ rich result。
- 執行完整build.py，396非退出頁、4退出頁；整合文字235成功0失敗。無關舊頁JSON-LD模板差異回復至開工乾淨版本，並重新由原產生器更新sw.js指紋。
- check_site.py通過；11頁 --propose 零差異、零移除、零來源錯誤。逐項靜態檢查順序、收藏鍵、雙日期、來源底部位置、FAQ、返回與QR／分享URL、五項全域輸出皆通過；舊正文及所有既有人工欄位逐欄比對不變。
- 完整管理驗證401錯誤、19警告：375機械欄位舊差異、14缺證據路徑、12報告版本差異。與本次開工實測420錯誤逐條集合比對：新增0、解決19、持續401；診斷存在忽略目錄 outputs/meptin-before.json 與 meptin-final.json，不將新快照冒稱人工批准基準。
- 管理測試18項：16通過，test_current_snapshot及test_read_only_and_preserves_manual_data失敗；收尾修正本次CR完成日期後重跑這兩項，確認僅仍有401項既有快照錯誤。
- project_change_tracker.py --check：本次20個網站檔案已連結CR-2026-049；整體exit 1來自歷史7c201523缺管理連結，未擴大改歷史。git diff --check通過。
- 圖片原有資料查核標示2026/10/20保留；網站資料查核日2026-10-30是本次實際直接來源核對日。
- 本機HTTP伺服器啟動後，內建瀏覽器127.0.0.1預覽回傳ERR_FAILED；桌機／手機視覺、收藏與QR／分享點擊未測試，不能以靜態檢查當操作驗收。
- 開工既有Search Console歷史、10/26證據及總控台搜尋追蹤修改保留；未Commit、Push或部署。

## 本次GitHub Desktop審核清單

總控台同時包含開工既有搜尋追蹤修改，提交時須按差異選取；search-console-history.json與10/26搜尋證據不屬本次範圍。

- `all-cards.html`
- `cards.json`
- `cards.manual.json`
- `cards/ped_cold_cetirizine.html`
- `cards/ped_cold_cough_mixture.html`
- `cards/ped_cold_cypromin.html`
- `cards/ped_cold_exdila_liquid.html`
- `cards/ped_cold_guaphen_syrup.html`
- `cards/ped_cold_koko_sou_syrup.html`
- `cards/ped_cold_mintapp_syrup.html`
- `cards/ped_cold_musco_solution.html`
- `cards/ped_cold_peace_syrup.html`
- `cards/ped_cold_secorine.html`
- `data/card_content.json`
- `data/card_text_web_integration_report.md`
- `docs/project-management/audit-history.md`
- `docs/project-management/audit-register.json`
- `docs/project-management/change-requests.csv`
- `docs/project-management/content-relations.csv`
- `docs/project-management/page-inventory.csv`
- `docs/project-management/project-dashboard.md`
- `seo.json`
- `sitemap-main.xml`
- `sitemap.xml`
- `sw.js`
- `cards/ped_asthma_meptin_liquid.html`
- `img/ped_asthma_meptin_liquid.webp`
- `docs/project-management/evidence/meptin-liquid-2026-10-30.md`
