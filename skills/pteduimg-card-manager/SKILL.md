---
name: pteduimg-card-manager
description: Use when working in the pteduimg GitHub Pages repository to add or update pharmacy/public education image cards, scheduled releases, card series, images, metadata, generated pages, and the related project-management records and verification outputs.
---

# pteduimg Card Manager

Use this skill for the `pteduimg` static GitHub Pages site when the user asks to add a new card series, append images to an existing card, schedule a card for future publication, update card metadata, or prepare generated card pages and their project-management records for publishing.

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
- Do not hand-create `cards/*.html` pages. Choose a full or selected-page build as described below.
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

For new card series, if the user has not provided search keywords, tags, or labels, ask what keywords or labels they want before finalizing metadata.

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
5. Run the appropriate existing `build.py` mode. A new image, series, order, or visibility change requires one full build because global indexes, SEO, sitemaps, and PWA outputs change. This technical regeneration is not a full-site medical audit. Do not redesign the header/footer or modify unrelated databases, calculators, or card series. Compare the before/after diff and isolate unexpected effects from pre-existing working-tree changes.
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

Add the stable `series:<id> -> page:<id>` `has_card` rows to `content-relations.csv`. Add topic/subtopic relations only when they are within the authorized scope, and reference the same page from multiple topics instead of duplicating content. If the work introduces an authorized topic node, update `content-topics.json` with its truthful `formal_page`, `planned`, or `collection_only` state; do not create a public topic page implicitly. Update the applicable CR and `project-dashboard.md`; add a focused evidence record when useful. Update `audit-history.md` or `audit-register.json` only when an audit conclusion or evidence version actually changes.

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

Also perform the relevant desktop/mobile and page-flow checks below. Record the actual command outcomes in the CR/evidence and final response; do not convert a structural pass into a medical signoff.

The Git-based tracker derives the changed pages and series automatically. Reuse or update the applicable CR before the final check. If a new CR is committed together with the card changes, use `same_commit` in its `git_commit` field; do not leave a completed request at `unknown`. A missing management link is a failed workflow even when the site tests pass.

## Adding Images To An Existing Card

1. Put the image files under `img/`.
2. Convert PNG/JPG/JPEG to WebP unless the user asks to keep the original format.
3. Use lowercase English filenames with underscores and numeric suffixes when possible.
4. Add each `img/...webp` path to the target card's `steps` array in `cards.json`.
5. Update `cards.manual.json` if the same card exists there. If the manual entry omits `steps`, keep metadata consistent and only add steps when the file's local pattern clearly does so.
6. Add the required per-image text, dates, and verified sources to `data/card_content.json`.
7. Run `python build.py`.
8. Verify JSON validity and generated pages, including the new-card publication checklist below.

## Adding A New Card Series

1. Add a top-level card key to `cards.json`.
2. Include title, category, order, hidden, icon, steps, and useful search keywords/tags. Include suitable `topics` for public cards or `departments` for pharmacist cards, using the IDs in `AGENTS.md`.
3. Mirror the appropriate metadata in `cards.manual.json`.
4. Add the required per-image text, dates, and verified sources to `data/card_content.json` for every new image.
5. Run `python build.py`.
6. Verify generated static pages and build outputs, including the new-card publication checklist below.

Example shape:

```json
"bugspray": {
  "title": "防蚊液",
  "category": "public_education",
  "order": 8,
  "hidden": false,
  "icon": "🦟",
  "tags": ["防蚊", "蚊蟲叮咬"],
  "topics": ["insect_repellent"],
  "steps": [
    "img/bugspray_1.webp",
    "img/bugspray_2.webp"
  ]
}
```

## Scheduling A Future Card Release

Use this flow when the user asks to publish a card at a specific future time instead of making it visible immediately.

Current automation is manual: `.github/workflows/scheduled-card-publish.yml` has `workflow_dispatch` only. `publish_at` sets the due-time threshold, not an automatic trigger. Explain the actual release mechanism; do not promise unattended publication or silently add a recurring schedule. See the current workflow/output and pending-text-check limitations in `AGENTS.md` before using this flow.

Represent a scheduled card series with:

```json
"dry_eye": {
  "title": "乾眼症",
  "category": "public_education",
  "order": 1,
  "hidden": true,
  "publish_at": "2026-06-01T09:00:00+08:00",
  "icon": "👁️",
  "tags": ["乾眼症", "人工淚液"],
  "topics": ["eyes"],
  "steps": [
    "img/dry_eye_1.webp"
  ]
}
```

Rules:

- Prefer explicit Taiwan time with offset, for example `2026-06-01T09:00:00+08:00`.
- If the user gives a local Taiwan date/time without a timezone, convert it to ISO format with `+08:00`.
- Keep `publish_at` in both `cards.json` and `cards.manual.json`.
- Keep `hidden: true` until the card is due.
- Complete all required per-image text, dates, and verified sources before scheduling. `hidden: true` alone does not exclude a card from static pages/indexes; pending exclusion requires `publish_at` too. Neither flag makes committed files private.
- `build.py` skips generated pages, SEO entries, sitemap entries, and service worker cache entries for cards where `hidden` is true and `publish_at` is present.
- Image files should still exist under `img/`, and the scheduled card should still list its `steps`.
- Do not add scheduled cards to homepage featured/hot lists unless the user explicitly wants them there after release. If a scheduled card must become featured at release time, note that an extra homepage edit is needed when publishing.

Check due scheduled cards:

```powershell
python scripts/publish_scheduled_cards.py --dry-run
```

Test a specific time without publishing:

```powershell
python scripts/publish_scheduled_cards.py --now 2026-06-01T09:00:00+08:00 --dry-run
```

When publication is authorized, publish due cards locally and verify:

```powershell
python scripts/publish_scheduled_cards.py
python build.py
python -m json.tool cards.json
python -m json.tool cards.manual.json
python -m json.tool data/card_content.json
python scripts/check_site.py
```

The publish script changes due card series from `hidden: true` to `hidden: false` in both JSON files and updates `CHANGELOG.md` when present. After that, `build.py` creates the static share pages and updates SEO, sitemap, robots, and service worker outputs.

Inspect and include all affected outputs in the release commit using the checklist in `AGENTS.md`; the existing workflow's commit list is incomplete. A local build or successful workflow alone does not prove a fully synchronized deployment. If no cards are due and no other site change requires it, skip the full build to avoid an unnecessary worker-version change.

## Retiring Or Replacing Cards

Follow `AGENTS.md`'s retirement flow and the schema in `scripts/card_archive.py`. Remove the retiring image from active card metadata, record its actual retirement date/reason and valid replacement links in `cards.retired.json`, and retain its image and historical URL. Run a full build to generate the retirement notice (`noindex`) and archive entry; verify removal from active indexes and working replacements. Do not delete old URLs, reuse image identities for unrelated material, or invent a replacement if the current schema cannot represent the intended retirement.

## Image Conversion

Use Pillow when available:

```python
from PIL import Image

with Image.open(src) as image:
    image.save(dst, "WEBP", quality=90, method=6)
```

After conversion, keep only the source files the user wants preserved.

## Required Build And Verification

Choose the scope using `AGENTS.md`:

- Use a full `python build.py` run for new/removed cards, series/order/visibility/retirement changes, shared templates, and changes affecting global generated outputs. It clears and regenerates the card HTML directory and restores retirement pages; review the diff for unintended changes.
- `python build.py --only IMAGE_ID [IMAGE_ID ...]` is available for existing individual pages when URLs, navigation and publication state are unchanged. IDs are image filename stems. This does not update global SEO/indexes/sitemaps, the integration report, retirement pages, or the worker version. If any are affected, selected-page output is only an intermediate preview, not a complete release.
- Documentation-only changes require no build. If full generation conflicts with the user's scope, explain the conflict before broadening work.

After the appropriate build, validate source data:

```powershell
python -m json.tool cards.json
python -m json.tool cards.manual.json
python -m json.tool data/card_content.json
```

Check that:

- every new `img/...` path exists
- every listed unscheduled image has a generated `cards/{image_filename_without_extension}.html`
- scheduled hidden cards do not generate public card pages yet
- both `sitemap.xml` and `sitemap-main.xml`, `all-cards.html`, and `seo.json` contain the expected active entries after a full build
- `sw.js` lists generated pages/images where expected; list membership does not mean install-time pre-caching (only `coreUrlsToCache` is installed eagerly)

For each newly added card, also verify before declaring it ready to publish:

- `data/card_content.json` is valid JSON; each new image has exactly one correctly matched record with the required fields.
- The generated HTML contains the actual text summary/sections, visible content update date, source-check date, and working direct source links. An expandable native `<details>` is acceptable; JavaScript must not be required to load the content.
- Text agrees with the image and cited sources; attribution and review status describe work that actually occurred.
- Dates are real content/verification dates, not automatically refreshed build timestamps.
- For scheduled hidden cards, validate the source records before scheduling and verify the visible HTML when publication generates it.

The existing `scripts/check_site.py` does not by itself certify source accuracy or these per-new-card completeness requirements. Perform these checks explicitly and report any unresolved gaps.

Its static-text check currently also expects HTML for pending high-confidence records, although scheduled hidden pages are intentionally absent. Follow the diagnostic guidance in `AGENTS.md`: report the limitation and targeted checks, do not remove text or alter publication/matching state just to pass. Check the integration report for the same pending-page issue. Do not claim all checks passed if they did not.

If `build.py`, homepage behavior, card page layout, service worker caching, analytics, generated card pages, or scheduled publication behavior changed, also run:

```powershell
python scripts/check_site.py
```

## Local Testing Focus

For public education cards, check `public.html`.

For pharmacist cards, check `index.html`.

For generated card pages, verify:

- image appears below the top toolbar
- previous/next arrows work within the same series
- `返回首頁` goes to `public.html` for `public_education` and `index.html` for other categories
- QR/share URLs point to `/cards/xxx.html`
- favorites use the existing `favImages` localStorage format

Use browser verification when frontend behavior, layout, generated pages, or homepage featured/hot lists changed in a way that should be visually checked.

## Final Response Checklist

Summarize:

- card series or images changed
- scheduled release time, if any
- whether a scheduled card is still hidden or was published
- build and verification commands run
- new-card text, update dates, source-check dates, sources, and any unresolved gaps
- include `data/card_content.json` in the commit/push file list when changed
- all changed sources and generated outputs in the `AGENTS.md` publishing checklist, plus commit/push status if requested; otherwise list files for GitHub Desktop

Mention the important publish chain:

```text
image exists -> synchronized series metadata -> per-image text, dates and verified sources -> appropriate build and checks -> relevant changes committed/pushed -> Pages deployment completes
```

For pending cards, the due-card publisher must actually run before they become visible; `publish_at` alone does not trigger publication.
