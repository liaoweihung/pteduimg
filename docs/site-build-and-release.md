# 網站建置、驗證與發布規範

本檔承接根目錄 AGENTS.md 的技術操作細節。修改產生器、頁面、導覽、快取或進行排程／退出／發布前，讀取相應章節；所有程式與資料路徑、命令工作目錄均以 repository 根目錄為準。圖卡來源與醫療要求另見 [Card Manager](../skills/pteduimg-card-manager/SKILL.md)，人工欄位依 [專案管理 SOP](project-management/README.md)，藥局工具依 [Hub 維護規範](pharmacy-tools-maintenance.md)。

## 章節導覽

- [建置模式與完整輸出](#static-card-pages)
- [靜態索引與可見性](#static-all-cards-index)
- [退出與替代](#retiring-or-replacing-cards)
- [排程](#scheduled-card-publishing)
- [頁面操作驗證](#local-testing)
- [離線快取與更新體驗](#offline-cache-and-update-experience)
- [回歸檢查與 pending 限制](#regression-check)
- [Git 與發布清單](#git--publishing)

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

These checks do not certify medical accuracy or universally require sources/update dates for new cards. Explicitly verify the new-card checklist in the [Card Manager](../skills/pteduimg-card-manager/SKILL.md) as well.

Current pending-card limitation: `check_static_card_text_content` includes all non-retired `matchConfidence: "high"` records, even for scheduled hidden cards whose pages are intentionally not generated. This can cause a missing-page failure; other pending records may also affect the integration report. Diagnose and report this separately from actual published-page failures. Do not lower matching confidence, remove required text, or publish early to make a check pass. Fix the check when that work is in scope; otherwise report the unresolved limitation and targeted checks performed, not an all-pass result.

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


## 排程的補充操作

- 使用者提供未註明時區的台灣時間時，以 `+08:00` 轉成 ISO 8601。圖片仍需存在於 `img/` 並列於 `steps`。
- pending 卡排除於 SEO 與公開生成輸出；不得自行加入首頁精選／熱門清單。若使用者要求發布時加入手工精選清單，發布時另做已授權的入口更新。
- 已授權本機發布時，先執行 `python scripts/publish_scheduled_cards.py`，再完整建置及檢查三份 JSON、網站與相關管理資料；沒有到期卡且沒有其他建置必要時，跳過完整建置，避免無意義的 worker 版本變更。

## 新卡發布前的額外檢查

建置後執行來源語法檢查（不是醫療簽核）：

```powershell
python -m json.tool cards.json
python -m json.tool cards.manual.json
python -m json.tool data/card_content.json
```

- 每張新圖在 `data/card_content.json` 有唯一且正確配對的完整紀錄；三份 JSON 均可解析。
- 實際生成 HTML 含摘要、分段重點、內容更新日期、資料查核日期與直接來源連結。原生 `<details>` 可接受，不可依賴 JavaScript 載入正文。
- 圖片、文字、來源一致；修訂歸屬與審閱狀態真實；日期不是自動刷新的建置時間。
- pending 卡先檢查來源完整，發布後才檢查生成 HTML；不能用缺頁誤報為理由提前發布、降低配對信心或刪文字。
- 完整建置後檢查兩份 sitemap、`all-cards.html`、`seo.json`、`sw.js` 的預期條目，並確認 active／pending／retired 的實際結果。
- 前端行為、版面、生成頁或首頁精選清單有變更時，依範圍做桌機／手機瀏覽器檢查；靜態驗證不代替目視與操作測試。

## 網站變更追蹤

所有會影響公開網站、生成頁、圖片、樣式、JavaScript、公開資料、SEO、PWA 或建置／發布流程的工作，結束前都須沿用或更新對應 CR，並執行 `python -B scripts/project_change_tracker.py --check`。查詢可用 `--page PAGE_ID`、`--series SERIES_ID` 或 `--request CR-ID`；工具從 Git 歷史與目前工作目錄取得技術變更，不覆寫人工審核欄位。

新 CR 與網站變更同次提交時 `git_commit` 可填 `same_commit`，歷史補登填實際 SHA。檢查顯示缺少管理連結時，不得宣稱管理紀錄已同步。完整欄位責任與唯讀 CI 行為以 [專案管理 SOP](project-management/README.md#網站變更自動追蹤) 為準；此流程不授權 Commit、Push 或醫療簽核。

## Git 工作目錄保護

只暫存使用者授權範圍內且實際改動的來源、管理紀錄與必要產物；不要使用 `git add .` 混入既有工作，不做 `reset --hard` 或強制推送來處理分歧。遇到遠端新提交先比較再整合。文件／指令整理不修改工作流程或啟用排程。
