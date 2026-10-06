# Rogue V1 art and audio

October 5, 2026. Implemented in dev. One generated equal 4x4 atlas produces eight square skill icons and eight effect sprites. Style reference: `staging-ui/monk-v1/atlas.png`. Retained source: `staging-ui/rogue-v1/atlas.png`; source generation: `C:/Users/neo_m/.codex/generated_images/01a0b5d5-838b-7532-a029-207add4a0d21/exec-2b0628bf-1133-4c98-ba45-47130ee5cc2f.png`.

Art direction: painted fantasy square icons with gold framing; red offensive cuts, amber control/traps, violet shadow movement and teal escape. First rows: Cheap Shot, Crippling Cut, Exploit Weakness, Shadowstep, Caltrops, Backflip, Trap Expert, Throwing Knife. Effect rows: knife, knife trail, departure/arrival shadow, steel caltrop tile, cut contact, afterimage and landing dust. Equal isolated cells avoid neighbouring-image spill. Icons stay opaque; black-backed effect art is converted to alpha. Spare cut/trail/afterimage sprites are retained for future polish; existing approved weapon-contact art remains the normal melee delivery.

```powershell
.venv\Scripts\python.exe tools\import_rogue_atlas.py staging-ui\rogue-v1\atlas.png
```

Outputs: `frontend/public/assets/rogue-v1/*.png`, 256 square; source crop manifest beside retained atlas. Sprite effects use lightweight Web Animations, not an additional Effekseer package: short teleport fades, established leap motion, flying knife, static steel ground scatter. Shared contact and playback timeline synchronizes knife impact at 280 ms. Hidden pages/reduced motion are respected. New art/assets follow existing repository ignore rules; local release builder carries the public asset directory.

Four new ElevenLabs physical/airy clips: rogue_shadowstep, rogue_backflip, rogue_caltrops, rogue_knife_throw. Prompts/durations are in SFX_GENERATION_GUIDE.md. Generate with the existing `tools/generate_sfx_pack.py --pack rogue-actions-v1`; sources and report remain in staging-sfx/rogue-actions-v1. Re-running reuses completed sources. Preview at `/assets/sfx/preview-rogue-actions-v1.html`. All four installed WAVs are 48 kHz, nonempty and have zero clipped output samples. The API required minimum requested duration 0.5 s for the knife clip; output is 0.46 s. Total API-reported character cost 26. Existing approved stab flesh/hard contact handles actual knife impact; launch gain stays quiet.

Actual battle UI fixture checked selectors, preview cells, R rotation, free Cancel, selected Shadowstep destination and knife main-attack selection without JavaScript exceptions. This does not replace player feedback on aesthetics or balance. No new global UI framework, production data or credentials were introduced.
