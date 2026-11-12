# 2026-11-12 Search Console noindex 查核

- 資源：`https://liaoweihung.github.io/`
- 查核時間：2026-11-12 16:25（Asia/Taipei，約）；Search Console 索引報表更新至 2026-11-09。
- 索引報表顯示已索引 28 頁、未索引 3 頁（3 種原因）；其中「遭到 noindex 標記排除」1 頁，驗證尚未開始。
- [noindex 詳細報表](https://search.google.com/search-console/index/drilldown?resource_id=https%3A%2F%2Fliaoweihung.github.io%2F&item_key=CAMYCCAC) 的唯一示例為 `https://liaoweihung.github.io/pteduimg/cards/acne.html`；首次偵測日期 2026-11-07，上次檢索日期 2026-11-06。
- 本機 `cards.retired.json` 記載該頁已於 2026-09-08 退出。`cards/acne.html` 是保留舊網址的退出頁，含 `<meta name="robots" content="noindex, follow">` 和替代頁連結。
- 本次唯讀確認 `sitemap-main.xml`、`sitemap.xml`、`all-cards.html`、`public.html`、`index.html` 均未包含 `cards/acne.html`。
- 判讀：這 1 頁的 noindex 是刻意退出設定，不代表現行圖卡遭到錯誤排除。無須移除 noindex 或啟動「驗證修正後的項目」。本次未逐頁審查其餘未索引原因，也未驗證所有現行圖卡。
- 未修改網站、未要求建立索引、未執行建置或發布。
