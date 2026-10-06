# Ranger V1 art — October 6

One generated 4×4 sheet, referenced against the approved Rogue icon style. Top two rows contain eight square gilded painted skill icons; bottom two supply arrow, arrow trail, poison arrow/contact, rupture burst, quarry ring, stationary ring and critical spark. The source is `staging-ui/ranger-v1/atlas.png`; import manifest records exact source bounds.

Installed assets: `frontend/public/assets/ranger-v1/`. Reimport with:

```powershell
.\.venv\Scripts\python.exe tools/import_ranger_atlas.py staging-ui/ranger-v1/atlas.png
```

Framed icons keep opaque art. Effects extract black to alpha and preserve silhouette/aspect ratio. Per-effect crop boundaries were reviewed against the source because the generated rows are not perfectly even: ordinary equal cells included blood from the following row and clipped arrow tips. Reviewed contact sheet: `staging-ui/ranger-v1/effects-contact-sheet.png`.

`ranger-effects.js` reuses the existing Web Animations/attack-packet pipeline, not another particle engine. Physical arrow flight starts at 30 ms and reaches the target at 220 ms; Poison contact/rupture or a Longshot critical spark appears at contact. Basic Ranger bow attacks and Rapid Fire fallback also render an arrow; imbued attacks use the green arrow/contact. Effects clean up after completion, respect detached maps, hidden pages and reduced motion, and never control gameplay timing.

The existing `bow_release`, `arrow_hit`, miss and defeat cues share the same contact packet. No additional generated audio or extra runtime dependency was required. Trail and steady-ring sprites are available for later polish rather than adding continuous visual clutter now.

Isolated QA uses `tools/build_ranger_preview.py`, `tools/serve_board_preview.mjs` and `tools/ranger_browser_qa.mjs` with headless Chrome on port 9229. It does not contact the live game API or read/write saves. Screenshots under `staging-ui/ranger-v1/` record Marksman, DoT and volley views. These preview files are generated, not production application code.

Generated media is intentionally excluded from Git; the local installed files and staging source are preserved for the existing release-copy workflow.
