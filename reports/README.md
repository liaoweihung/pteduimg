# 圖卡熱門度報表

每日台灣時間凌晨 4 點後，GitHub Actions 會產生：

- `reports/card-popularity.md`
- `reports/card-popularity.json`

需要在 GitHub Secrets 設定：

- `GA4_PROPERTY_ID`
- `GA4_OAUTH_CLIENT_ID`
- `GA4_OAUTH_CLIENT_SECRET`
- `GA4_OAUTH_REFRESH_TOKEN`

報表使用 GA4 資料：

- `page_view`
- `pagePath` 符合 `/pteduimg/cards/*.html` 的頁面會被計為單張圖卡觀看

圖卡對應規則：

- `cards.json` 的每個 `steps` 圖片路徑會對應到 `cards/{圖片檔名不含副檔名}.html`
- 報表用這個靜態網址回推系列名稱與第幾張

排程時間：

- 每天台灣時間 04:05 開始跑
- 通常會在 07:00 前完成
- 也可到 GitHub Actions 手動執行 `Card popularity report`
