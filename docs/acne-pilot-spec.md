# 青春痘 Topic Pilot 規格 v1.0

本規格記錄已確認的基本版型與導覽層級，不固定細部視覺數值。

## 適用範圍

目前 Pilot 為以下四張既有圖卡，不自動擴大到其他頁面：

| Pilot | 頁面 |
|---|---|
| A01 | `cards/acne_stage.html` |
| A04 | `cards/acne_topicals_02_retinoids.html` |
| A15 | `cards/acne_patch_when_to_use.html` |
| A17 | `cards/acne_patch_broken_skin.html` |

## 基本頁面順序

圖卡 → 上一張／下一張 → 文字版重點（預設收合） → 你可能想知道 → 查看青春痘完整主題 → 頁尾

| 區塊 | 用途與基本原則 |
|---|---|
| 圖卡 | 保留現有圖卡主要呈現方式。 |
| 上一張／下一張 | Series：保留現有系列閱讀功能，不因新增問題導覽而移除。 |
| 文字版重點 | 使用三角形 disclosure／details，預設收合，供使用者展開閱讀。 |
| 你可能想知道 | 使用者 Path：以問題引導下一步閱讀，使用簡潔文字列表，不做大型 CTA 卡片。 |
| 查看青春痘完整主題 | Topic Hub：通往 `topics/acne.html` 的次要導覽。 |
| 頁尾 | 保留既有頁尾內容，本站資訊連結放在最底部。 |

問題列表與 Hub 入口位於文字版之後、details 之外。展開文字版時，後續導覽自然下移。

## Navigation visual hierarchy

- Series navigation 是主要導航。
- Text details 是內容展開，維持頁面的自然閱讀感。
- Next questions 是簡潔問題列表，視覺重量低於系列導航。
- 每頁原則上約 3 個問題，以最可能的下一問為主；這是編輯原則，不是硬性數量限制。
- Topic hub 是較低視覺層級的次要入口，不做醒目的大型 CTA。
- 上述基本區塊順序保持不變；使用者明確要求改版時，可同步調整規格。

## 頁尾與首頁功能

一般圖卡頁不顯示「恢復圖卡預設排列／醫藥計算器」等首頁功能按鈕；這兩項功能按鈕只保留在 `index.html` 與 `public.html`，不放入共用 footer。

共用 footer 依序呈現：

1. 該頁既有的衛教用途提醒。
2. Copyright 與意見回饋。
3. 關於本站／作者資訊／編輯與資料來源政策，放在最底部。

沿用既有文字、連結與分隔方式，手機版保持置中。

## 資料與維護

下一問集中維護於 `data/acne_navigation.json`，使用既有的 `page_id`、`next_questions`（`label`／`target`）與 `topic_hub` 欄位，不在各頁分別硬寫。連結指向確實存在的內容；完整主題由 `topics/acne.html` 承接。

以下調整可正常進行，不需要升版：

- 字級與顏色。
- margin／padding 與分隔線。
- 問題文字與 next question 連結。
- 小幅 responsive 調整。
- accessibility 改善。

修改內容、連結、樣式或修 bug 時，不順便重構基本版型。未來使用者明確要求改版時，可以修改本規格；v1.0 並非不可變動。

既有結構驗證入口為 `scripts/check-acne-pilot-layout.js`，並整合於 `scripts/check_site.py`。目前檢查器仍有 2–3 題限制；未來調整問題數量時可一併對齊本規格，本次僅整理文件，不修改程式。

## 版本紀錄

Pilot v2 正式成為 v1.0。

Version: 1.0
Date: 2026-10-08
