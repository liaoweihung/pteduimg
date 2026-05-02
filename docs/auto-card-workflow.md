# Codex + GitHub Actions 圖卡自動化流程

這份流程用來手動輸入一個熱門主題，產生一張醫療衛教圖卡，並先以 `hidden: true` 草稿方式存進網站資料。

## 設定 OPENAI_API_KEY

1. 到 GitHub 專案頁面。
2. 進入 `Settings` > `Secrets and variables` > `Actions`。
3. 點 `New repository secret`。
4. `Name` 填入 `OPENAI_API_KEY`。
5. `Secret` 貼上 OpenAI API key，儲存。

沒有設定 `OPENAI_API_KEY` 時，workflow 會停止，並顯示缺少金鑰的錯誤訊息。

## 手動產生圖卡

1. 到 GitHub 專案的 `Actions` 頁籤。
2. 選擇 `Generate Draft Education Card`。
3. 點 `Run workflow`。
4. 在 `topic` 輸入主題，例如：`眼藥水怎麼點`。
5. 執行後會自動產生圖片，存到 `images/pending/`，並更新：
   - `cards.manual.json`
   - `cards.json`
   - `sw.js`
   - `sitemap.xml`

## 審核 hidden 草稿

新產生的資料會在 `cards.manual.json` 裡新增一筆，預設包含：

```json
"hidden": true
```

這代表圖卡先不會公開出現在網站列表。請先檢查：

- 圖片內容是否適合醫療衛教。
- 文字是否正確、清楚，沒有過度承諾療效。
- 是否需要補充「請諮詢醫師或藥師」等提醒。
- 主題、分類、標籤是否需要調整。

## 改成公開上線

確認可以公開後：

1. 打開 `cards.manual.json`。
2. 找到該圖卡資料。
3. 把：

```json
"hidden": true
```

改成：

```json
"hidden": false
```

4. 執行或等待建置更新 `cards.json`。
5. commit 後網站就會顯示該圖卡。

## 常見錯誤排除

### 找不到 OPENAI_API_KEY

請確認 GitHub Actions Secrets 裡有 `OPENAI_API_KEY`，名稱必須完全相同。

### cards.manual.json 不是合法 JSON

workflow 會停止，不會繼續改資料。常見原因是：

- 少了逗號。
- 多了逗號。
- 字串沒有用雙引號。
- 大括號或中括號沒有成對。

可以先用 GitHub 的檔案預覽或本機 JSON 工具檢查格式。

### images/pending/ 不存在

腳本會自動建立，不需要手動新增。

### OpenAI 圖片產生失敗

workflow 會顯示 OpenAI API 回傳的錯誤原因。常見原因包括：

- API key 無效。
- 帳號額度不足。
- 圖片模型暫時不可用。
- prompt 內容被安全系統拒絕。

### 圖卡沒有出現在網站

請先確認該筆資料是不是仍然是 `hidden: true`。如果要公開，需改成 `hidden: false`，並重新產生 `cards.json`。
