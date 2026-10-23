# 圖卡資料模型與分類

新增或修改系列 metadata 前讀取本檔；所有程式／資料路徑以 repository 根目錄為準。完整本機流程見 [Card Manager](../SKILL.md)，建置規則見 [建置與發布](../../../docs/site-build-and-release.md)。

## Card Data Model

- `cards.json` is the main runtime data source.
- `cards.manual.json` is a human-maintained companion source. When adding a new card or changing card metadata, keep both files in sync unless the user explicitly says otherwise.
- Card image paths live under each card's `steps` array.
- Card series should include useful search keywords or tags when available. If the user asks to add a new card/card series and does not provide keywords or tags, ask what search keywords or labels they want to use before finalizing the metadata.
- Public education cards use:
  - `category`: `public_education`
  - public page: `public.html`
  - a non-empty `topics` array so the card appears in one or more public-page topic filters. Without `topics`, the card appears only in `全部圖卡`.
- Use one or more of these public-card topic IDs in `topics`:
  - `skin_wound`
  - `eyes`
  - `oral_health`
  - `throat`
  - `infectious_diseases`
  - `heat_illness`
  - `insect_repellent`
  - `gastrointestinal`
  - `elimination_care`
  - `growth`
  - `chronic_conditions`
  - `sleep`
  - `pregnancy`
  - `travel_medication`
- When adding a public education card, add the same `topics` metadata to both `cards.json` and `cards.manual.json`. Use multiple topic IDs when the card genuinely belongs to more than one topic.
- Pharmacist cards generally use:
  - `category`: `pharmacist_general` or `pharmacist_product`
  - pharmacist page: `index.html`
  - a non-empty `departments` array so the card appears in the `index.html` horizontal “依科別瀏覽” navigation. Use one or more applicable IDs:
    - `ophthalmology`
    - `ent`
    - `dermatology`
    - `plastic_surgery`
    - `colorectal_surgery`
    - `dentistry`
    - `obstetrics_gynecology`
    - `pediatrics`
    - `chest_medicine_smoking_cessation`
    - `cardiology`
    - `chinese_medicine`
    - `pharmacy_general`
- When adding a pharmacist card, add the same `departments` metadata to both `cards.json` and `cards.manual.json` when the card exists in both files. Use multiple IDs when the card genuinely belongs to more than one department. Without `departments`, the card appears only under `全部圖卡`.

## Adding A New Card Series

Add a new top-level key to `cards.json`, for example:

```json
"bugspray": {
  "title": "防蚊液",
  "category": "public_education",
  "order": 8,
  "hidden": false,
  "icon": "🦟",
  "topics": ["insect_repellent"],
  "tags": ["防蚊", "蚊蟲叮咬"],
  "steps": [
    "img/bugspray_1.webp",
    "img/bugspray_2.webp",
    "img/bugspray_3.webp"
  ]
}
```

Then mirror the appropriate metadata in `cards.manual.json`, prepare the required per-image records in `data/card_content.json`, and follow the full build and verification steps in `docs/site-build-and-release.md`. Example tags are illustrative; follow the keyword clarification rule for the actual request. Pharmacist series must use suitable `departments` instead of public-card `topics`.


完整新增前確認 title、icon、系列／頁面 ID、分類、topics/departments、排序、標籤、圖數與公開／排程狀態。示例標籤不是未經使用者確認的預設值。
