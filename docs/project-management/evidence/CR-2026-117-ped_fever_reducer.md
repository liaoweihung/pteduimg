# CR-2026-117 安佳熱、依普芬網頁文字與SEO更新

- 範圍：series:ped_fever_reducer；直接修改 antiphen、ibuprofen_sol；idofen_suspension、macsafe_suspension、notice_ped_fever_reducer 只隨建置更新系列導覽連結文字。圖卡與舒抑痛頁內容不動。
- 基準檔：outputs/mgmt-before-20261123-0025.json
- 素材來源：AI_doc_exchange_v2/04_delivery/antiphen-ibuprofen-seo-2026-11-22-v2.md A～C 節（2026-11-23 00:32:33 存檔；SHA-256 503f7d1d6d199cb69bcd05f41f9a3c0a569b9fa76cba9d85366d83fdbe390e0a；較 00:02:48 版增兩段圖卡使用溫度加註）。
- 藥師決定：照試建方案；內部連結用 related_links 放頁尾；接受排版微調；「沿用既有 label_links 連結（不改）」不上頁；體溫說法已定案、圖不改；依普芬頁成大公告用 116279717.pdf。
- 工作區：藥師同意保留 project-dashboard.md、search-console-history.json 兩份既有改動（不碰、不提交）後 pull --ff-only 開工。
- 複核：antiphen、ibuprofen_sol；複核者：藥局衛教助手製作者；日期：2026-11-23；依據：上述 00:32:33 版 v2 定稿；藥師原話：「定稿算是複核」。頁面不顯示審閱狀態、不加 lastReviewed。
- 檢查結果：增量建置通過（CR共影響5頁；v2加註與複核後重建2頁）；5頁清冊提議零差異；JSON OK；check_site通過；變更追蹤確認本次變更連結CR-2026-117（指令另列既有2筆舊commit缺連結）；兩頁title、description、H1、仿單區塊、參考資料、推薦閱讀及兩段溫度加註正確；手機寬度無橫向溢出；antiphen、ibuprofen_sol已登記藥師複核；基準比對 new=0、worsened=0。
