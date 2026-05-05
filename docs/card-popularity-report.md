# 圖卡熱門度自動報表設定

這個流程會每天自動整理圖卡熱門度，不需要手動進 GA4。

## 會產生什麼

每天台灣時間 04:05 後，GitHub Actions 會產生：

- `reports/card-popularity.md`
- `reports/card-popularity.json`

Actions 執行頁面也會顯示同一份 Markdown 摘要。

## 報表內容

圖卡角度：

- 最近上架的 20 張圖卡
- 上架後最近 24、48、72、96、120 小時的點擊
- 圖卡點擊 / 網站瀏覽比例
- 20 張圖卡的相對分數，平均 = 100

網站角度：

- 過去 24、48、72、96、120 小時點擊前 20 名
- 前 20 名圖卡的點擊 / 網站瀏覽比例
- 前 20 名圖卡的相對分數，平均 = 100
- 過去 14 天每天都在前 20 的圖卡
- 最近 72 小時排名往前的圖卡

## 需要設定的 GitHub Secrets

到 GitHub 專案：

`Settings` > `Secrets and variables` > `Actions` > `New repository secret`

新增：

- `GA4_PROPERTY_ID`
- `GA4_SERVICE_ACCOUNT_JSON`

## GA4 權限

請在 GA4 property 裡，把 service account 的 email 加成可以讀取資料的使用者。

需要可讀取：

- `page_view`
- `view_instruction_card`
- 自訂維度 `card_title`
- 自訂維度 `card_id`

## 上架時間如何判斷

目前圖卡資料沒有正式的上架日期欄位，所以報表會從 Git 歷史推估：

- 第一次出現在 `cards.json` 的時間 = 推估上架時間

若某張圖卡找不到 Git 歷史，報表會標示為 `未知`。
