# Refined SVG Notes v2.2

## Status
Draft refined vector, generated from the approved full-color PNG by deterministic color segmentation and contour cleanup. This is **closer to a usable master** than the old auto-trace reference, but it is **not yet the final authoritative Bézier master**.

## What changed
- Re-segmented the approved PNG using the approved brand colors:
  - Red `#FD2828`
  - Black `#101010`
  - Blue `#013E9C`
- Extracted clean region masks for red face, black beard/facial lines, and blue handwritten `助手`.
- Removed small specks and simplified contour noise.
- Rebuilt the vector as grouped filled paths with `fill-rule="evenodd"`.

## Output files
- `assets/logo_vector_refined_draft_v2.2.svg`
- `assets/logo_vector_refined_preview_v2.2.png`
- `data/refined_vector_report_v2.2.json`

## Limitations
- Curves are cleaner than the previous autotrace, but still derived from raster contours.
- Exact Bézier handles, stroke logic, and designer-grade node economy are not yet manually polished.
- Before declaring a final master, compare this SVG visually against the approved PNG at large size and inspect key areas: brows, eye arcs, moustache center join, beard bottom curve, and handwritten `助手` endpoints.

## Recommended next decision
If the draft is visually acceptable, use it as the base for **manual node reduction / curve polishing** in a vector editor, then publish a final `logo_vector_master.svg`.
