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
- Pharmacist cards generally use:
  - `category`: `pharmacist_general` or `pharmacist_product`
  - pharmacist page: `index.html`

## Static Card Pages

This site uses Route B static card share pages.

Every image listed in a card's `steps` should have a generated page:

```text
cards/{image_filename_without_extension}.html
```

Example:

```text
img/oral_hygiene_01.webp
cards/oral_hygiene_01.html
```

Do not create these HTML files by hand. Run:

```bash
python build.py
```

`build.py` generates/updates:

- `cards/*.html`
- root `404.html`
- `cards/404.html`
- `sitemap.xml`
- `all-cards.html`
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

## Adding A New Image To An Existing Card

1. Put the image in `img/`.
2. Prefer `.webp`. If the user gives PNG/JPG files, convert them to WebP first unless they ask not to.
3. Add the `img/...webp` path to the correct card's `steps` array in `cards.json`.
4. If the same card exists in `cards.manual.json`, update that file too. Some manual entries omit `steps`; when in doubt, keep metadata consistent and ask only if needed.
5. Run:

```bash
python build.py
```

6. Verify:

```bash
python -m json.tool cards.json
python -m json.tool cards.manual.json
```

7. Check that the generated page exists, for example:

```text
cards/wound_4_soln.html
```

8. Check that `sitemap.xml`, `all-cards.html`, and `sw.js` mention the new generated page/image.

## Adding A New Card Series

Add a new top-level key to `cards.json`, for example:

```json
"bugspray": {
  "title": "防蚊液",
  "category": "public_education",
  "order": 8,
  "hidden": false,
  "icon": "🦟",
  "steps": [
    "img/bugspray_1.webp",
    "img/bugspray_2.webp",
    "img/bugspray_3.webp"
  ]
}
```

Then mirror the appropriate metadata in `cards.manual.json`, run `python build.py`, and verify generated pages.

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
- The scheduled GitHub Actions workflow runs `scripts/publish_scheduled_cards.py` hourly.
- While a card has both `hidden: true` and `publish_at`, `build.py` treats it as pending:
  - it is not included in generated `cards/*.html`
  - it is not included in `sitemap.xml`
  - its images are not added to the service worker pre-cache
- When `publish_at` has arrived, the workflow:
  - changes `hidden` to `false` in both JSON files
  - updates `CHANGELOG.md`
  - runs `python build.py`
  - runs JSON checks and `python scripts/check_site.py`
  - commits the updated data and generated static files
- If no scheduled cards are due, the workflow makes no commit.

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
- Static card pages register the service worker.
- Static card pages keep side navigation and bottom page navigation.
- Static card page titles do not include redundant step-number suffixes.
- Local/private-network previews do not load GA unconditionally.
- `sw.js` keeps the stable runtime cache for previously viewed pages/images.

## Git / Publishing

The user often publishes with GitHub Desktop.

After changes are verified, tell the user to commit/push these updated files:

- changed image files under `img/`
- changed `cards.json`
- changed `cards.manual.json` when applicable
- generated `cards/*.html`
- `sitemap.xml`
- `all-cards.html`
- `seo.json`
- `robots.txt`
- `sw.js`
- any source/template files changed, especially `build.py`

Do not include Python cache files. `.gitignore` already ignores:

```text
__pycache__/
.codex_index_*
```

## Important Rule

Uploading an image to `img/` is not enough. A card appears on the site only after:

```text
image exists -> cards.json references it -> python build.py has been run -> changes are committed/pushed
```
