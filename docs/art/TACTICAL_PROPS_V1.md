# Tactical props pack V1

Implemented in dev, October 6, 2026. One generated transparent equal 4x4 atlas, pure top-down camera, matching `combat-terrain/props/camp-v1/ballista_loaded.png` as style reference. Retained source: `staging-terrain/tactical-props-v1/atlas.png`; generated original: `C:/Users/neo_m/.codex/generated_images/01a0b5d5-838b-7532-a029-207add4a0d21/exec-939fb34e-021e-43c1-9f55-353ee64095ec.png`.

| Atlas row | Cells left to right | Usage |
|---|---|---|
| 1 | Rust scatter A, rust scatter B, dark steel scatter, casting scatter | First three are seeded Caltrops ground props; casting scatter reserved |
| 2 | Scrap Turret ready, fire, recoil, destroyed | Installed on existing Engineer deployment |
| 3 | Bolt, short trail, heavy turret ready, heavy turret wreck | Bolt live; other three reserved |
| 4 | Repair tool chest, spare bolts, open bear trap, closed bear trap | Reserved for future props/deployments |

All 16 PNGs are installed at `frontend/public/assets/tactical-props-v1/`. No terrain is mixed into this pack. Unused art is deliberately retained for later Engineer/trap polish, without introducing unsupported gameplay. Mobile summons still use the existing portrait approach.

```powershell
.venv\Scripts\python.exe tools\import_tactical_props.py staging-terrain\tactical-props-v1\atlas.png
```

The importer requires real alpha transparency. Caltrops use equal isolated cell crops, 384 square output with original transparent spacing. All four turret frames share their canvas and anchor; the firing bolt extends slightly above the generated grid into empty gutter, so extraction expands that crop without recentering any frame. Gallery and source-box manifest remain next to the atlas. Browser screenshot review confirmed clean silhouettes and no circular portrait clipping on turrets.

Caltrops: 72% tile art canvas (actual visible scatter smaller), deterministic three-way variants; grounded contact shading comes from the artwork. Existing subtle 2.4 s scale/glow pulse respects reduced motion. Layer 60 keeps traps above map art while preserving interaction controls and combat feedback.

Scrap Turret: stationary prop with HP and existing hover/target controls. Firing frame at attack start; recoil/projectile launch at 45 ms; bolt arrival at 220 ms matches existing contact audio/damage timeline; ready frame restored at 350 ms. Projectile cleaned up after its flight. Aimed bearing rotates north-authored art toward the target. Reduced motion omits recoil/flight but retains targeting and contact feedback. Existing mechanical bow-release/arrow-contact sounds reused. No new audio generation or resource/cost/AI changes. Additional heavy turret functionality remains deferred.

Generated assets stay local per repository media policy; release builder must carry `frontend/public/assets` when this is eventually deployed. This pass does not publish production.
