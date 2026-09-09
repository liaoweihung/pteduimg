# 青春痘系列重整與後續製作紀錄

重整日期：2026-09-08。

## 現有圖卡分組

| 系列代碼 | 名稱 | 現有張數 | 預計張數 |
|---|---|---:|---:|
| acne | 青春痘與粉刺：先認識，再照護 | 3 | 3 |
| acne_topical_medicines | A酸、杜鵑花酸、BPO、水楊酸怎麼用？ | 4 | 4 |
| acne_antibiotics | 痘痘抗生素與複方藥膏怎麼用？ | 3 | 3 |
| acne_application | 痘痘藥怎麼搭，才不會越擦越刺激？ | 4 | 4 |
| acne_patch_use | 痘痘貼與破皮照護 | 3 | 3 |
| rosacea_care | 臉紅又冒痘：酒糟與用藥 | 3 | 3 |

20 張現有圖卡各歸屬一個系列；既有圖片路徑、分享網址維持不變，本次新增圖片各有獨立分享網址。
`favorite_keys` 保留重整前的收藏識別（例如 `acne-7`），請勿按新順序重編。
酒糟系列放在「皮膚與傷口」，不列入一般青春痘用藥的翻頁。

## 退出紀錄

權威資料：`cards.retired.json`。執行 `python build.py` 會產生：

- `retired-cards.html`：可搜尋的退出紀錄網頁，列出日期、原因、完整舊網址與目前閱讀入口。
- 各筆紀錄的原 `cards/*.html`：退出說明、替代連結及可展開的歷史圖片。

退出頁保留 HTTP 200，不自動跳轉；標示 `noindex, follow`，不進入主要目錄、SEO 索引或 sitemap。歷史圖片不刪除。

| 退出網址 | 退出圖卡 |
|---|---|
| cards/acne.html | 青春痘大解密：藥師圖卡懶人包 |
| cards/comedo_dailycare.html | 輕度粉刺日常保養這樣做 |
| cards/acne_dailycare_2.html | 中度發炎型青春痘用藥期間注意事項 |

詳細原因與替代網址以 `cards.retired.json` 為準，不手改產生的 HTML。
原文字資料仍保留於 `data/card_content.json`；建置及文字驗證排除已退出圖片，避免將舊內容重新推為現行版本。

## 已補充

- 痘痘破皮後的清潔、擦藥與單純水膠體痘痘貼判斷。
- 青春痘與酒糟的辨識線索，以及眼痛、畏光、視力模糊的就醫警訊。
- 酒糟肌的清潔、保濕、防曬、減少刺激與誘因紀錄。

## 待補充：後續再製作

1. 痘痘破了怎麼辦？還能擦藥、貼痘痘貼嗎？——加入 `acne_patch_use`。
2. 青春痘還是酒糟？哪些線索值得就醫確認？——加入 `rosacea_care`，排在 Metronidazole 前。
3. 酒糟肌如何清潔、保濕、防曬與減少刺激？——加入 `rosacea_care`。

## 現有圖片的後續改版

- `acne_stage.webp`：聚焦外觀辨識與就醫時機，避免把外觀分級當成自行選藥依據。
- `comedo.webp`：精簡粉刺拔除的固定恢復時間表，聚焦溫和清潔、不反覆擠壓及傷口狀態。
- `acne_dailycare.webp`：聚焦清潔、保濕、防曬與不亂擠；藥物細節交給用藥系列。
- 新製的 12 張 `acne_topicals_*`：後續重繪時移除圖內原始「01／12～12／12」，改由網頁顯示組內頁碼。本輪圖片不變，網頁附有原始編號說明。
- 若重繪原圖，延用目前圖片檔名與頁面網址；必須先重新查核用藥內容。

參考依據：

- [AAD acne guideline](https://www.aad.org/member/clinical-quality/guidelines/acne)
- [NICE acne recommendations](https://www.nice.org.uk/guidance/ng198/chapter/Recommendations)
- [AAD rosacea treatment](https://www.aad.org/public/diseases/rosacea/treatment/diagnosis-treat)
