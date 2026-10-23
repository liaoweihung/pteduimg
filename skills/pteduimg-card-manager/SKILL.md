---
name: pteduimg-card-manager
description: Use when working in the pteduimg GitHub Pages repository to add or update pharmacy/public education image cards, scheduled releases, card series, images, metadata, generated pages, and the related project-management records and verification outputs.
---

# pteduimg Card Manager

Use this skill for the `pteduimg` static GitHub Pages site when the user asks to add a new card series, append images to an existing card, schedule a card for future publication, update card metadata, or prepare generated card pages and their project-management records for publishing.

## 按任務讀取

先遵循 [根目錄指令](../../AGENTS.md)。本專案版 Skill 管理圖卡內容、來源及新增流程；已安裝的舊版同名 Skill 不取代它。以下是檔案導覽，不使用 inline include，也不要求無關任務讀取全部文件。

- 新增／變更系列 metadata：讀 [圖卡資料模型與分類](references/card-data.md)，包含合法 topics/departments、雙 JSON 同步與新系列範例。
- 新增／追加圖卡：讀本檔 Required Text、Before Editing、End-to-End Workflow、Image Conversion，完成完整本機流程。
- 建置、排程、退出、頁面驗證或發布：操作前讀 [網站建置與發布](../../docs/site-build-and-release.md) 的對應章節；範圍與完整輸出以該文件為準。
- 清冊／關聯／人工欄位：讀 [專案管理 SOP](../../docs/project-management/README.md)。
- 品牌或 Logo：先讀 [品牌入口](../../docs/brand/README.md)；一般圖卡轉 WebP 的建議不適用於覆寫正式 Logo PNG。

命令與資料路徑均以 repository 根目錄為準；Markdown 連結相對於本檔。

## Repository Scope

This skill applies to the repository whose root contains:

- `cards.json`
- `cards.manual.json`
- `build.py`
- `public.html`
- `index.html`
- `img/`
- `cards/`

If these files are not present, first confirm you are in the correct repository.

## Core Rules

- `cards.json` is the runtime data source.
- `cards.manual.json` is the human-maintained companion source.
- When adding a card or changing card metadata, keep both JSON files in sync unless the user explicitly says not to.
- Image paths live under each card's `steps` array.
- Public education cards use `category: "public_education"` and appear on `public.html`.
- Pharmacist cards usually use `category: "pharmacist_general"` or `category: "pharmacist_product"` and appear on `index.html`.
- Scheduled releases use `hidden: true` plus `publish_at`.
- Do not hand-create `cards/*.html` pages. Choose a full, selected-page, or safe incremental build in [網站建置與發布](../../docs/site-build-and-release.md).
- Prefer WebP images in `img/`.
- Do not include Python cache files in the final file list.
- Every newly added image/card must meet the text, dates, and source requirements below, including additions to existing series and scheduled releases. Also follow the repository's `AGENTS.md`.

## Required Text, Dates, And Sources For New Cards

For every new image, add a corresponding record to `data/card_content.json`. This file is the per-image text source; do not replace `cards.json` / `cards.manual.json` series metadata or hand-edit generated HTML. Read the current `build.py` renderer before assuming new fields are supported.

Required record fields with the current renderer:

- `cardId`, `image`, `url`: identify the correct series, exact image path, and canonical generated card URL.
- `title`, `summary`, `sections`: provide a meaningful title, concise summary, and non-empty sections with `heading` and `text`. Summarize this specific image's key points, steps, applicable conditions, and cautions faithfully; do not silently add unsupported medical advice.
- `altText`: an accurate image description, not a substitute for the visible text version.
- `updatedAt`: actual content creation or substantive revision date (`YYYY-MM-DD`), not the build/deployment date. Do not advance it for formatting-only changes.
- `revisionCredit`: truthful attribution for the actual preparation/revision. The current renderer only displays the update line when BOTH `updatedAt` and `revisionCredit` are present. Do not invent a reviewer or professional review to satisfy this condition; clarify attribution if unknown.
- `references`: a non-empty list of `{ "title": "...", "url": "https://..." }` objects. Use verified direct sources supporting this image, with institution/document name and known version/date in the title. Prefer official information, approved product leaflets, professional societies/guidelines, and suitable medical research, following `editorial-policy.html`.
- `sourceCheckedAt`: the actual source verification date (`YYYY-MM-DD`), recorded separately from `updatedAt`.
- `matchConfidence`: the current loader only includes records marked `"high"`. Confirm the text belongs to the exact image before setting this; this field denotes image/text matching, NOT medical review or evidence quality.

Read and verify the medical sources. AI output, conversation IDs, search snippets, or institution homepages alone are not supporting medical references. Preserve truthful provenance and review status; do not mark `needsMedicalReview: false` solely because AI generated or checked the text. Missing facts, dates, sources, or attribution must be resolved or reported as incomplete, never invented.

Each new card page must contain static, readable HTML for its text, update date, source-check date, and real source links. Series may reuse genuinely applicable sources, but each page must display them. Prepare these records before scheduling a release, even though scheduled hidden pages are not generated until publication.

This rule applies prospectively. Do not backfill or rebuild existing cards merely to update these instructions; documentation-only changes do not require running `build.py`.

## Before Editing

Inspect the working tree, current card structure, and existing management scope before editing:

```powershell
git status --short
python -m json.tool cards.json > $null
python -m json.tool cards.manual.json > $null
python -m json.tool data/card_content.json > $null
```

Read `docs/project-management/README.md`, then search `change-requests.csv`, `page-inventory.csv`, `content-relations.csv`, and `project-dashboard.md` for the proposed series, page IDs, and request scope. Reuse an existing CR that covers the work; create the next stable `CR-YYYY-NNN` only when no existing request covers it. Registration alone is not approval. A user's explicit instruction to add the cards authorizes that stated scope, and the CR should record that authorization accurately.

For a new card or series, if the user has not provided search keywords, tags, or labels, ask what keywords or labels they want before finalizing metadata.

For ambiguous cards, identify:

- card key
- title
- category
- order
- icon
- hidden state
- `publish_at`, if the card should publish later
- image filenames
- keywords/tags, if supported by the nearby data model

## End-to-End New Card Workflow

For a request to add cards, add a series, or append images, complete the whole local workflow unless the user explicitly narrows it. Do not stop after copying images or editing one metadata file.

1. Establish the exact scope: series ID, page IDs, card count, category, `topics` or `departments`, order, tags, visibility/schedule, and which homepage (`public.html` or `index.html`) must list it. Check nearby series and the Git diff so unrelated work is preserved.
2. Process the images under `img/`: use stable lowercase English names when possible, convert suitable PNG/JPG/JPEG inputs to WebP, and keep every filename stem unique. Do not reuse retired IDs or change unrelated favorite identities.
3. Update the matching series metadata in both `cards.json` and `cards.manual.json`. The current homepage lists are data driven, so category, filters, and `order` normally place the series; edit a hand-maintained featured/navigation list only when the requested placement actually depends on one.
4. Add exactly one correctly matched `data/card_content.json` record per image with title, summary, sections, alt text, direct references, real content/source-check dates, and truthful revision attribution. Leave `needsMedicalReview: true` for new material unless traceable human medical-review evidence says otherwise. Missing facts remain unresolved; never invent a date, source, author, reviewer, authorization, or commercial disclosure.
5. Run the appropriate `build.py` mode. For a new visible series, appending images at the end of a series, or scoped content/SEO updates, use `python -B build.py --incremental IMAGE_ID [IMAGE_ID ...]`; supply new/edited image stems and at least one image from each metadata-changed series. The builder expands affected navigation and updates complete global indexes, SEO, sitemaps, the integration report and PWA data. Removal, retirement, visibility/scheduling, regrouping/reordering, shared templates or unsafe baseline changes require a reviewed full build. `--only` still rebuilds selected pages without global outputs and is not a complete new-card release. Follow the safety/rejection rules in the build SOP; never force a full build to erase conflicting manual edits. This technical regeneration is not a full-site medical audit. Do not redesign the header/footer or modify unrelated databases, calculators, or card series. Compare the before/after diff and isolate unexpected effects from pre-existing working-tree changes.
6. Synchronize the project-management layer using the incremental procedure below, then run source, site, management, and relevant UI checks. Report new page/record counts, tests, unresolved items, and medical-review status. Stop before Commit, Push, or publication unless the user separately authorized them.

### Incremental project-management update

The authoritative field ownership and ID rules are in `docs/project-management/README.md`. The management files index the website sources; they do not replace `cards.json`, `data/card_content.json`, or the original audit reports.

After generating the new pages, run a targeted read-only proposal for all new page IDs, for example:

```powershell
python -B scripts/check_project_management.py --propose --page new_page_1 --page new_page_2
```

Review the JSON printed to stdout and merge by exact `page_id` into `docs/project-management/page-inventory.csv`:

- copy only the proposed machine fields;
- initialize a new page's manual fields to `unknown` or another state supported by real evidence;
- preserve all manual fields on existing rows, including medical review, reviewer/date, audit history, known issues, and last human confirmation;
- never replace the complete CSV with generated output, replace an existing row wholesale, or clear manual data to make validation pass;
- keep new medical content unreviewed: `needsMedicalReview: true` in the content source and no `pharmacist_reviewed` management status without actual signoff evidence.

Add the stable `series:<id> -> page:<id>` `has_card` rows to `content-relations.csv`. Add topic/subtopic relations only when they are within the authorized scope, and reference the same page from multiple topics instead of duplicating content. If the work introduces an authorized topic node, update `content-topics.json` with its truthful `formal_page`, `planned`, or `collection_only` state; do not create a public topic page implicitly. Update the applicable CR status, evidence, validation result and completion date, and the counts, progress and unresolved items in `project-dashboard.md`; add a focused evidence record under `docs/project-management/evidence/` when useful. Update `audit-history.md` or `audit-register.json` only when an audit conclusion or evidence version actually changes.

Run the targeted proposal again after the merge. It should report no machine-field proposals, no unexpected removed IDs, and no source errors for the affected pages. `--propose` never writes files and cannot approve content or overwrite manual review decisions.

For every new-card workflow, finish with the full management checks as well as the site checks:

```powershell
python -B scripts/check_site.py
python -B scripts/check_project_management.py
python -B scripts/check_project_management.py --propose --page new_page_1 --page new_page_2
python -B scripts/test_project_management.py
python -B scripts/project_change_tracker.py --check
python -B scripts/test_project_change_tracker.py
```

The Git-based tracker derives changed pages and series. Reuse or update the applicable CR before the final check. A new CR committed with the card changes may use `same_commit`; a missing management link is not a completed workflow.

Also perform the relevant desktop/mobile and page-flow checks below. Record the actual command outcomes in the CR/evidence and final response; do not convert a structural pass into a medical signoff.

## Adding Images Or A New Series

兩者都依上述完整新增流程，不維護第二套簡化 SOP。追加圖片要寫入正確 `steps`，同步已存在的 manual 系列；若 manual 項目省略 `steps`，依該檔附近資料慣例保持一致，不猜測缺少資料。新系列 schema 與分類 ID 見 [圖卡資料模型](references/card-data.md)。

轉檔後每個圖片 stem 都必須唯一、保留穩定 URL／收藏識別。可見新圖必須有對應 `cards/{stem}.html`；新增可見系列或在系列末尾追加圖片可用安全增量模式，不能只跑 `--only`。增量／完整建置後均須核對實際文字、雙日期、來源、兩份 sitemap、靜態索引、SEO 與 worker 清單，以及受影響舊頁的翻頁／張數。pending／可見性與退出變更使用完整建置；pending 卡先驗證來源完整與公開輸出排除。增量機制只縮小網站生成範圍，不省略醫療資料核對、圖文一致性、人工複核、管理更新或發布授權。

## Scheduling And Retirement

排程前讀 [Scheduled Card Publishing](../../docs/site-build-and-release.md#scheduled-card-publishing) 與同檔「排程的補充操作」。手動觸發、時區、完整來源、pending 生成排除、workflow 提交漏項及既有檢查器限制都仍適用。

退出／替代前讀 [Retiring Or Replacing Cards](../../docs/site-build-and-release.md#retiring-or-replacing-cards) 與 `scripts/card_archive.py` 的實際 schema；保留舊圖、ID／URL 與修訂歸屬，不發明替代頁。

## Image Conversion

Use lowercase English filenames with underscores and numeric suffixes when possible, for example `img/bugspray_1.webp`, `img/bugspray_2.webp`, `img/bugspray_3.webp`. Convert PNG/JPG/JPEG to WebP unless the user asks to retain the original format; do not apply this conversion rule to overwrite the brand PNG master.

Use Pillow when available:

```python
from PIL import Image

with Image.open(src) as image:
    image.save(dst, "WEBP", quality=90, method=6)
```

After conversion, keep only the source files the user wants preserved.

## Required Build And Verification

建置範圍、完整產物、三份 JSON 檢查、靜態頁／索引／快取與 pending 診斷統一依 [網站建置、驗證與發布](../../docs/site-build-and-release.md)。執行建置前讀對應章節；不要只憑本 Skill 的摘要跳過檢查。純文件整理不執行建置。

每張新卡的文字／日期／來源完整性要額外人工核對，不能由 `check_site.py` 通過推定；以該文件的「新卡發布前的額外檢查」逐項驗證。新增流程的管理檢查與定點 `--propose` 零差異要求仍依上述增量流程。

## Local Testing Focus

依 [Local Testing](../../docs/site-build-and-release.md#local-testing) 檢查對應首頁、工具列下方圖卡、同系列翻頁、返回入口、QR／分享 URL 與 `favImages` 收藏格式。前端或生成頁有變更時依範圍驗證手機／桌機及操作，不用純靜態檢查代替瀏覽器驗收。

## Final Response Checklist

Summarize:

- card series or images changed
- new series/page counts, the CR, inventory/relation changes and the remaining human medical-review status
- scheduled release time, if any
- whether a scheduled card is still hidden or was published
- build and verification commands run
- new-card text, update dates, source-check dates, sources, and any unresolved gaps
- include `data/card_content.json` in the commit/push file list when changed
- all changed sources and generated outputs in the [publishing checklist](../../docs/site-build-and-release.md#git--publishing), plus commit/push status if requested; otherwise list files for GitHub Desktop

Mention the important publish chain:

```text
image exists -> synchronized series metadata -> per-image text, dates and verified sources -> appropriate build and checks -> relevant changes committed/pushed -> Pages deployment completes
```

For pending cards, the due-card publisher must actually run before they become visible; `publish_at` alone does not trigger publication.
