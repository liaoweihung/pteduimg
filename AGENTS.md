# pteduimg Codex Instructions

This repository is a static GitHub Pages site for pharmacy/public education image cards.

Project skill: for card additions, scheduled card releases, image conversion, and generated-page verification, also consult `skills/pteduimg-card-manager/SKILL.md`.

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

## 新增圖卡的文字與可信度要求

自本規則建立起，未來新增的每張衛教圖卡（包含新系列、既有系列追加圖片及排程發布圖卡）都必須具備以下資訊，不能只上傳圖片：

- **文字版重點**：與該張圖卡相符的簡短摘要及分段重點，保留重要操作步驟、適用條件與注意事項。以可直接閱讀的靜態 HTML 文字呈現在該張圖卡頁，不得只存在圖片、alt、metadata 或由 JavaScript 動態載入。
- **內容更新日期**：標示該張內容實際建立或實質修訂的日期，格式為 `YYYY-MM-DD`。初次發布可使用內容完成日期；不得把每次建置、部署或排版調整的日期當成醫療內容更新日期。
- **資料來源**：列出實際閱讀、核對且能支持該張重點的來源名稱與直接連結，優先採用官方資料、核准仿單、專業學會／診療指引及適當醫學研究。標題宜包含發布單位與文件名稱，版本或發布日期已知時一併註明；不可只列機構首頁、搜尋結果、AI 回答或對話紀錄。
- **資料查核日期**：標示實際核對上述資料的日期，與內容更新日期分開記錄。不得虛構引用、查核日期、作者資格或審閱狀態；AI 可協助整理，但不能作為醫療證據來源。

依現有 `data/card_content.json` 與 `build.py` 機制保存及產生上述資訊，欄位與驗證步驟見 `skills/pteduimg-card-manager/SKILL.md`。系列可共用確實適用的來源，但每張圖卡頁都必須能看到自己的文字重點、日期與來源連結。

資料不足時，先查找可查證來源；仍無法確認的內容應列明缺項並向使用者釐清，不得用猜測或占位資料宣稱完成。完成上述資訊並驗證頁面後，才可將新增圖卡視為可發布；排程圖卡也須於設定發布前備齊。

本規則不要求自動回補或批次重建既有圖卡。僅修改製作規則時，不執行 `build.py`；未經要求不擴大至舊卡內容改寫。資料選用原則應與 `editorial-policy.html` 一致。

## 新增衛教圖卡標準作業流程

使用者要求「新增圖卡」、「新增圖卡系列」或在既有系列追加圖片時，視為授權完成該次新增工作的完整本機流程；依序處理來源資料、必要建置、管理紀錄與驗證，不要只完成圖片或 `cards.json`。若使用者另有限定範圍，以該範圍為準；未另外授權 Commit、Push 或發布時，到本機驗證完成即停止。

1. **先查現況與需求**：執行 `git status --short`，檢查目標系列、相近系列、`docs/project-management/change-requests.csv`、`page-inventory.csv`、`content-relations.csv` 與總控台。以需求名稱、說明、範圍及 `related_ids` 搜尋既有 CR；同一需求沿用原編號，只有沒有涵蓋本次範圍的紀錄時才新增下一個 `CR-YYYY-NNN`。需求登記不等於核准，但使用者在目前任務的明確新增指示可如實記為該範圍的執行授權。
2. **確認最小新增範圍**：確認系列 ID、分類、topics/departments、排序、標籤、圖數、頁面 ID 與公開／排程狀態。資料不足時先查證或列為待確認；不得猜測醫療內容、作者／審閱者、授權、商業揭露或日期。不要順帶修改其他系列、藥品資料庫或計算器。
3. **處理圖片**：依本檔命名及 WebP 規則處理格式、檔名與 `img/` 路徑，保留穩定的頁面 ID、URL 及收藏識別，不重用已退出頁的 ID。
4. **同步系列與逐頁內容**：同步更新 `cards.json` 與 `cards.manual.json`，並為每張新圖在 `data/card_content.json` 建立唯一、正確配對的紀錄。內容須包含標題、摘要、分段、替代文字、直接來源、真實 `updatedAt`、真實 `sourceCheckedAt` 與修訂歸屬；新內容預設 `needsMedicalReview: true`，除非已有可追溯的人工醫療複核證據。
5. **加入正確入口與順序**：依 `category`、`topics`／`departments` 及 `order` 使系列出現在 `public.html` 或 `index.html` 的指定位置。首頁清單目前由圖卡資料驅動時，優先修改權威 metadata；只有另有手工精選／導覽清單且本次明確需要時，才最小修改對應 HTML。不要重新設計既有頁首、頁尾或導覽。
6. **使用既有產生器**：不要手寫 `cards/*.html`。新增圖片、系列或排序會影響全域索引，依本檔的 Full build 規則執行一次 `python build.py`，沿用現有頁首、頁尾、SEO、JSON-LD、sitemap 與 PWA 規則。完整建置是必要的技術輸出更新，不是重新進行全站醫療審核；建置前後檢查 Git diff，避免把無關工作目錄修改混入本次成果。
7. **增量更新管理系統**：先以 `python -B scripts/check_project_management.py --propose --page PAGE_ID`（每個新 `page_id` 可重複傳入 `--page`）取得新頁機械欄位。人工檢視 stdout 後，按 `page_id` 合併到 `page-inventory.csv`；只更新提案中的機械欄位，新頁人工欄位填 `unknown` 或有真實證據的狀態。不得整列覆蓋既有頁、清掉 `known_issue_ids`、改寫人工簽核或把 `needsMedicalReview` 當成藥師已複核。
8. **補齊關聯與工作紀錄**：在 `content-relations.csv` 加入每個 `series:<id> -> page:<id>` 的 `has_card` 關聯；只有本次確有主題範圍時才增補主題／子題關聯，不複製圖卡內容。更新該 CR 的狀態、證據、驗證結果及完成日期，並更新 `project-dashboard.md` 的數量、進度與待確認事項；需要保存一次性證據時放在 `docs/project-management/evidence/`。只有既有盤點結論或證據版本真的改變時才追加 `audit-history.md`／`audit-register.json`，不可為新增卡重寫舊報告。
9. **驗證並收斂提案**：至少執行三份 JSON 語法檢查、`python -B scripts/check_site.py`、`python -B scripts/check_project_management.py`、針對新頁的 `--propose`，以及 `python -B scripts/test_project_management.py`。完成合併後，目標頁 `--propose` 應為零差異；並依變更範圍檢查新頁的文字、雙日期、來源、翻頁、返回入口、收藏、分享、桌機／手機版面及全域輸出。
10. **完成回報與發布界線**：回報新增系列／頁面數、CR、清冊與關聯變更、建置／測試結果、未完成項目及人工醫療待確認狀態。除非使用者明確要求發布，不自動 Commit、Push 或宣稱 GitHub Pages 已部署。

`--propose` 只提供唯讀機械差異，不會更新 CSV。完整欄位責任、穩定 ID、人工欄位與增量合併規則以 `docs/project-management/README.md` 為準。任何自動化都不得覆蓋 `medical_review_status`、reviewer、review_date、歷史證據、已知問題或其他人工欄位。

## Static Card Pages

This site uses Route B static card share pages.

Every active image listed in a card's `steps` should have a generated page, except pending cards with both `hidden: true` and `publish_at`:

```text
cards/{image_filename_without_extension}.html
```

Example:

```text
img/oral_hygiene_01.webp
cards/oral_hygiene_01.html
```

Do not create these HTML files by hand. For a full build, run:

```bash
python build.py
```

Choose the build scope before running:

- Full build: required when adding/removing cards, changing series membership/order, visibility, retirement, or shared templates/site indexes. It clears and regenerates `cards/*.html`, then restores retirement pages; inspect the resulting diff rather than assuming only the requested page changed.
- Selected-page build: `python build.py --only IMAGE_ID [IMAGE_ID ...]` can regenerate existing individual pages when their URLs, series/navigation, and publication state are unchanged. `IMAGE_ID` is the image filename stem. This does not update `seo.json`, indexes, sitemaps, retirement pages, the integration report, or `sw.js`; if any of these are affected, it is only a preview/intermediate step, not a complete release. It also does not trigger a new service-worker version/update pill.
- If a task prohibits bulk regeneration but requires changes to global generated outputs, explain the scope conflict before claiming completion; do not silently use a full build.
- Documentation-only edits do not require either build mode.

A full `build.py` run generates/updates:

- `cards/*.html`
- root `404.html`
- `cards/404.html`
- `sitemap.xml`
- `sitemap-main.xml`
- `all-cards.html`
- `retired-cards.html` and retired URL notice pages from `cards.retired.json`
- `data/card_text_web_integration_report.md`
- `seo.json`
- `robots.txt`
- `sw.js`

Generated card pages must keep static Open Graph tags in the HTML head. Do not rely on JavaScript to inject OG tags.

## Static All Cards Index

`build.py` also generates `all-cards.html`, a plain static HTML index of every public card page. This page is part of the SEO crawl surface and must stay updated whenever cards are added, removed, hidden, published, or reordered. Do not edit `all-cards.html` by hand; run:

```bash
python build.py
```

After changes, verify that `all-cards.html` links to the expected generated `cards/*.html` pages and that `sitemap.xml` / `sitemap-main.xml` include `all-cards.html`.

Current visibility limitation: the generator excludes cards only when BOTH `hidden: true` and `publish_at` are present. `hidden: true` alone is not a guarantee that the HTML, static index, or sitemap will exclude a card. Neither flag provides access control for files committed to the public repository. Check the actual generated outputs when changing visibility; do not describe unpublished files as private.

## Adding A New Image To An Existing Card

1. Put the image in `img/`.
2. Prefer `.webp`. If the user gives PNG/JPG files, convert them to WebP first unless they ask not to.
3. Add the `img/...webp` path to the correct card's `steps` array in `cards.json`.
4. If the same card exists in `cards.manual.json`, update that file too. Some manual entries omit `steps`; when in doubt, keep metadata consistent and ask only if needed.
5. Add one correctly matched record per new image to `data/card_content.json`, including text highlights, actual content update date, source-check date, verified direct references, and truthful revision attribution as specified in the project skill.
6. Run the full build (new images affect site indexes):

```bash
python build.py
```

7. Verify:

```bash
python -m json.tool cards.json
python -m json.tool cards.manual.json
python -m json.tool data/card_content.json
python scripts/check_site.py
```

8. For a non-pending card, check that the generated page exists, for example:

```text
cards/wound_4_soln.html
```

9. Check the page's static text, visible update/check dates and source links, and the corresponding entries in both sitemaps, `all-cards.html`, `seo.json`, and the `sw.js` generated asset list. For pending cards, verify source completeness and exclusion from public generated outputs instead; see scheduled-check limitations below.

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

Then mirror the appropriate metadata in `cards.manual.json`, prepare the required per-image records in `data/card_content.json`, and follow the full build and verification steps above. Example tags are illustrative; follow the keyword clarification rule for the actual request. Pharmacist series must use suitable `departments` instead of public-card `topics`.

## Retiring Or Replacing Cards

- For an intentional retirement, remove the image from active `steps` in both card sources where present, and add its record to `cards.retired.json`; do not simply delete its image or old URL.
- Follow the schema validated by `scripts/card_archive.py`: `image`, `page`, `title`, `retired_at` (`YYYY-MM-DD`), `reason`, and non-empty `replacements`. Preserve the old image and URL; replacement `page` values must refer to active cards. Inspect existing records for the full replacement shape. If no suitable replacement exists, report the current schema limitation instead of inventing one.
- Preserve existing text provenance and unrelated image/favorite identities. Do not reuse a retired URL for unrelated content.
- Run a full build to generate the old URL notice with `noindex`, replacement links, and `retired-cards.html`. Verify removal from active indexes, availability of the old URL and image, the archive entry, and working replacement links with `python scripts/check_site.py` plus targeted inspection.

## Scheduled Card Publishing

Prepared card series can be committed before they are visible on the site.

Use:

```json
"hidden": true,
"publish_at": "2026-06-01T09:00:00+08:00"
```

Rules:

- Add `publish_at` to both `cards.json` and `cards.manual.json`.
- Keep `hidden: true` until publication time.
- Use an ISO 8601 date-time with timezone. Prefer Taiwan time with `+08:00`.
- The current `.github/workflows/scheduled-card-publish.yml` has only `workflow_dispatch` (manual trigger), not an hourly schedule. `publish_at` is a due-time threshold; reaching it alone does not publish anything. State the actual trigger mechanism when preparing a release, and do not enable recurring publication merely to match old documentation.
- Prepare the required text, dates, and verified sources before scheduling. Validate source records while pending and rendered pages upon publication.
- While a card has both `hidden: true` and `publish_at`, `build.py` treats it as pending:
  - it is not included in generated `cards/*.html`
  - it is not included in `sitemap.xml`
  - its images are excluded from the generated service-worker asset list (which is distinct from the smaller install-time core pre-cache)
- When the workflow is manually triggered and `publish_at` has arrived, it:
  - changes `hidden` to `false` in both JSON files
  - updates `CHANGELOG.md`
  - runs `python build.py`
  - runs JSON checks and `python scripts/check_site.py`
  - commits the files explicitly listed in its `git add` command
- If no scheduled cards are due, the workflow makes no commit.

Current workflow limitation: that commit list omits some full-build outputs, including `all-cards.html`, `sitemap-main.xml`, `retired-cards.html`, and the integration report. Before using it for a release, address this within the authorized publishing task or use a verified local build/commit that includes all affected outputs. Do not report a fully synchronized publication merely because the workflow succeeded.

Manual local test:

```bash
python scripts/publish_scheduled_cards.py --dry-run
python scripts/publish_scheduled_cards.py --now 2026-06-01T09:00:00+08:00 --dry-run
```

## Image Conversion

Use Pillow when available:

```python
from PIL import Image

with Image.open(src) as image:
    image.save(dst, "WEBP", quality=90, method=6)
```

Keep filenames lowercase English when possible, with underscores and numeric suffixes:

```text
img/bugspray_1.webp
img/bugspray_2.webp
img/bugspray_3.webp
```

## Local Testing

After running `build.py`, test:

- `public.html` for public education cards.
- `index.html` for pharmacist cards.
- The generated card page under `cards/`.

For card pages, verify:

- Image appears below the top toolbar.
- Previous/next arrows work within the same series.
- `返回首頁` returns to `public.html` for `public_education` cards and `index.html` for other cards.
- QR uses the `/cards/xxx.html` URL.
- Share uses the `/cards/xxx.html` URL.
- Favorite uses the existing `favImages` localStorage format.

## Offline Cache and Update Experience

The site intentionally uses a cache-first service-worker strategy for HTML, scripts, and data. Serve the cached page immediately for a fast, reliable offline-friendly experience, while fetching a newer version in the background. Do not change this to network-first or add cache-busting query parameters unless the user explicitly requests it.

Only `coreUrlsToCache` is pre-cached during installation. The larger generated `urlsToCache` list is not proof that all images/pages have been downloaded; non-core assets are generally cached when fetched. Preserve the stable runtime cache for previously viewed content.

Keep the existing update pill (`#update-light`) on both `index.html` and `public.html`. When a new service worker has installed while an older one controls the current page, the pill must appear. The current worker uses `skipWaiting()` and `clients.claim()` to activate/take control automatically; this is distinct from reloading the displayed document. Users choose when to reload via the pill. Do not force reloads or silently replace the displayed page, and do not redesign worker activation as part of unrelated edits.

## Regression Check

After changing homepage behavior, card page layout, service worker caching,
analytics, generated card pages, or `build.py`, run:

```bash
python scripts/check_site.py
```

This checks key site invariants, including:

- `cards.json` and `cards.manual.json` are valid JSON.
- Referenced images and generated `cards/*.html` pages exist.
- Homepage viewer keeps both transparent side-tap navigation and visible bottom navigation buttons.
- Homepage card data loading does not bypass cache.
- Service-worker fresh assets remain cache-first, with background updates.
- The update pill remains available for user-initiated version updates.
- Static card pages register the service worker.
- Static card pages keep side navigation and bottom page navigation.
- Static card page titles do not include redundant step-number suffixes.
- Local/private-network previews do not load GA unconditionally.
- `sw.js` keeps the stable runtime cache for previously viewed pages/images.

These checks do not certify medical accuracy or universally require sources/update dates for new cards. Explicitly verify the new-card checklist in the project skill as well.

Current pending-card limitation: `check_static_card_text_content` includes all non-retired `matchConfidence: "high"` records, even for scheduled hidden cards whose pages are intentionally not generated. This can cause a missing-page failure; other pending records may also affect the integration report. Diagnose and report this separately from actual published-page failures. Do not lower matching confidence, remove required text, or publish early to make a check pass. Fix the check when that work is in scope; otherwise report the unresolved limitation and targeted checks performed, not an all-pass result.

## Pharmacy Tool Pages and Hub Synchronization

Whenever adding, modifying, renaming, moving, retiring, or removing a pharmacy work tool page, check the corresponding hub pages as part of the same task and update them when needed.

- The tool directory is a separate page: `https://liaoweihung.github.io/hub/pharmacy-tools.html`.
- `https://liaoweihung.github.io/hub/index.html` contains only the directory entry. Keep `藥局工作用工具` as the last entry, immediately after `藥師自我學資料分享`; do not embed the tool list in the hub homepage.
- Tool implementations and their assets may remain in `/pteduimg/`. Hub tool links must point to their correct published URLs, including any nested paths such as `/pteduimg/web/`.
- For new public pharmacy work tools, add an entry to `hub/pharmacy-tools.html`. For existing tools, check the displayed name, description, URL, ordering, and availability; update affected entries and any displayed tool count. Do not automatically list unpublished prototypes or hidden tools.
- Tool return links, including links rendered by shared JavaScript shells, should lead to `https://liaoweihung.github.io/hub/pharmacy-tools.html`. Check the directory link in `pteduimg/calc.html` as well.
- Verify the hub homepage entry, the complete tool directory, tool destinations, and return navigation. If a tool change does not require a hub edit, explicitly report that the hub was checked and remains consistent.
- `hub` and `pteduimg` are separate Git repositories. Locate the hub checkout and verify its remote is `https://github.com/liaoweihung/hub.git` before editing. A checkout may exist at `output/hub/`, but this is a local working location, not the published URL. Never stage the nested hub repository as part of a pteduimg commit.
- If hub source is unavailable, obtain the repository or report the missing synchronization work; do not silently mark the task complete. When publishing is requested, commit/push each affected repository separately and identify both results. Publish a new hub directory page before links that depend on it.
- Changes to tool navigation must preserve the existing cache-first strategy and user-initiated update experience. Run `python scripts/check_site.py` after changes to tool navigation or shared tool shells.

## Git / Publishing

The user often publishes with GitHub Desktop.

After verification, inspect the diff and identify all files affected by this task. Include only changed, relevant sources and generated outputs; the following is a checklist, not a command to stage everything:

- changed image files under `img/`
- changed `cards.json`
- changed `cards.manual.json` when applicable
- `data/card_content.json`
- `cards.retired.json` when retiring cards
- generated `cards/*.html`
- `sitemap.xml`
- `sitemap-main.xml`
- `all-cards.html`
- `retired-cards.html`
- root `404.html` and `cards/404.html`
- `data/card_text_web_integration_report.md`
- `CHANGELOG.md` when updated
- `seo.json`
- `robots.txt`
- `sw.js`
- any source/template files changed, especially `build.py`

If commit/push is requested, perform it within the authorized scope; otherwise tell the user which files to publish through GitHub Desktop. Keep unrelated untracked work and the nested hub repository out of the commit. A successful push is not proof of a completed Pages deployment.

The current `auto-build.yml` triggers only on `index.html` or `img/**` changes and commits only `sw.js`, despite running a full build. Do not rely on it to publish all generated changes or to update the worker for every kind of edit; prepare and verify the complete release locally or address the workflow explicitly when in scope.

Do not include Python cache files. `.gitignore` already ignores:

```text
__pycache__/
.codex_index_*
```

## Important Rule

Uploading an image to `img/` is not enough. A card appears on the site only after:

```text
image exists -> synchronized series metadata -> per-image text, dates and verified sources -> appropriate build and checks -> relevant changes committed/pushed -> Pages deployment completes
```

For pending cards, publication additionally requires the due-card publisher to actually run and switch the card to visible; saving `publish_at` alone is insufficient.

## Acne Topic Pilot

青春痘 Pilot 的版型規格以 `docs/acne-pilot-spec.md` 為準。
修改青春痘 Pilot 頁面或相關生成程式前，先閱讀該規格。

青春痘主題全部系列的手機圖卡、翻頁列與共用頁尾套用規則見 `docs/acne-mobile-card-rollout.md`。使用者已確認三張示範頁，後續套用時遵循該文件的範圍與驗收要求；翻頁按鈕排在圖卡下方的正常文件流中，不固定於螢幕底部。此套用不擴大四頁 Pilot 的問題導覽名單。

未經使用者明確要求，不要自行改變以下基本順序：

圖卡 → 上一張／下一張 → 文字版重點 → 你可能想知道 → 查看青春痘完整主題 → 頁尾

如果任務只是修改內容、連結、樣式或修 bug，不要順便重構這個版型。
若未來使用者明確要求改版，可以正常修改規格，不需要把目前 v1.0 視為不可變動。
