# 圖卡熱門度報表

每日台灣時間凌晨 4 點後，GitHub Actions 會產生：

- `reports/card-popularity.md`
- `reports/card-popularity.json`

需要在 GitHub Secrets 設定：

- `GA4_PROPERTY_ID`
- `GA4_OAUTH_CLIENT_ID`
- `GA4_OAUTH_CLIENT_SECRET`
- `GA4_OAUTH_REFRESH_TOKEN`

報表使用 GA4 事件：

- `view_instruction_card`
- `page_view`

並使用已建立的自訂維度：

- `card_title`
- `card_id`

排程時間：

- 每天台灣時間 04:05 開始跑
- 通常會在 07:00 前完成
- 也可到 GitHub Actions 手動執行 `Card popularity report`
