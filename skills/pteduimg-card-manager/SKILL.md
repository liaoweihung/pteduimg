---
name: pteduimg-card-manager
description: Use when working in the pteduimg GitHub Pages repository to add or update pharmacy/public education image cards, scheduled card releases, card series, card images, card metadata, generated static share pages, or related build/verification outputs.
---

# pteduimg Card Manager

Use this skill for the `pteduimg` static GitHub Pages site when the user asks to add a new card series, append images to an existing card, schedule a card for future publication, update card metadata, or prepare generated card pages for publishing.

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
- Do not hand-create `cards/*.html` pages. Run `python build.py`.
- Prefer WebP images in `img/`.
- Do not include Python cache files in the final file list.

## Before Editing

Inspect the current card structure:

```powershell
python -m json.tool cards.json > $null
python -m json.tool cards.manual.json > $null
```

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

## Adding Images To An Existing Card

1. Put the image files under `img/`.
2. Convert PNG/JPG/JPEG to WebP unless the user asks to keep the original format.
3. Use lowercase English filenames with underscores and numeric suffixes when possible.
4. Add each `img/...webp` path to the target card's `steps` array in `cards.json`.
5. Update `cards.manual.json` if the same card exists there. If the manual entry omits `steps`, keep metadata consistent and only add steps when the file's local pattern clearly does so.
6. Run `python build.py`.
7. Verify JSON validity and generated pages.

## Adding A New Card Series

1. Add a top-level card key to `cards.json`.
2. Include title, category, order, hidden, icon, steps, and useful search keywords/tags when the existing schema supports them.
3. Mirror the appropriate metadata in `cards.manual.json`.
4. Run `python build.py`.
5. Verify generated static pages and build outputs.

Example shape:

```json
"bugspray": {
  "title": "防蚊液",
  "category": "public_education",
  "order": 8,
  "hidden": false,
  "icon": "🦟",
  "tags": ["防蚊", "蚊蟲叮咬"],
  "steps": [
    "img/bugspray_1.webp",
    "img/bugspray_2.webp"
  ]
}
```

## Scheduling A Future Card Release

Use this flow when the user asks to publish a card at a specific future time instead of making it visible immediately.

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

Publish due cards for real:

```powershell
python scripts/publish_scheduled_cards.py
python build.py
python -m json.tool cards.json
python -m json.tool cards.manual.json
python scripts/check_site.py
```

The publish script changes due card series from `hidden: true` to `hidden: false` in both JSON files and updates `CHANGELOG.md` when present. After that, `build.py` creates the static share pages and updates SEO, sitemap, robots, and service worker outputs.

## Image Conversion

Use Pillow when available:

```python
from PIL import Image

with Image.open(src) as image:
    image.save(dst, "WEBP", quality=90, method=6)
```

After conversion, keep only the source files the user wants preserved.

## Required Build And Verification

After changing card data or images, run:

```powershell
python build.py
python -m json.tool cards.json
python -m json.tool cards.manual.json
```

Check that:

- every new `img/...` path exists
- every listed unscheduled image has a generated `cards/{image_filename_without_extension}.html`
- scheduled hidden cards do not generate public card pages yet
- `sitemap.xml` mentions generated pages for visible cards
- `sw.js` mentions generated pages/images for visible cards where expected

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
- any files the user should commit/push through GitHub Desktop

Mention the important publish chain:

```text
image exists -> cards.json references it -> python build.py has been run -> changes are committed/pushed
```
