# Monk V1 art and presentation

October 5, 2026. Implemented in dev. One generated 4?4 atlas supplies eight skill icons and eight reusable effect sprites. Reference: `staging-ui/martial-jobs-v1/icons-atlas.png`. Retained source: `staging-ui/monk-v1/atlas.png`; generated image origin: `C:/Users/neo_m/.codex/generated_images/01a0b5d5-838b-7532-a029-207add4a0d21/exec-7c42b554-8e12-4752-bb69-97bf236e96d9.png`. Generated media stays outside the public code repository under the existing ignore policy; local release builds copy the asset tree.

Art direction: equal 4?4 cells, consistent fantasy painted square ability icons, gold/jade martial force, wrapped fists and distinct palm sequences; effect rows use black backgrounds for mechanical alpha extraction. No unused corners, labels, generic magic casting or armor rendering. First two rows: Rapid Palm, Crushing Fist, Iron Reversal, Breaking Combination, Heaven-Piercing Strike, Sweeping Dash, Perfect Rhythm, Flowing Footwork. Last two rows: palm contact/expand, force lance/fade, defensive flow/expand, dash ribbon, broken guard.

Reimport without modifying originals:

```powershell
.venv\Scripts\python.exe tools\import_monk_atlas.py staging-ui\monk-v1\atlas.png
```

Importer crops equal cells with a small inset, resizes to 256 square and converts the effect rows' black backing to alpha. Output: `frontend/public/assets/monk-v1/`. Pass a different atlas path to import a replacement; output stays in the dev asset directory. Manifest is stored beside the source atlas. Inspect source and output before approving a replacement.

Runtime modules: monk-effects.js/css, combat-impact.js, combat-audio.js and status presentation. The physical finisher projects an authored lance; defensive form surrounds the portrait with a slowly moving crescent; multi-hit contact images and numbers use shared contact timing. Reduced motion disables the persistent aura loop. Existing approved fist/flesh/hard-contact audio is reused; repeated swing volume is quieter. No new SFX was generated in this pass. Spare effect frames remain available for later refinement, not additional gameplay mechanics.

Validation: five equipped skill icons loaded in a 1440?1100 browser fixture; stage meter cycled without runtime errors. Timing tests synchronize three punch contacts, audio and subsequent actor/defeat playback. Final gameplay/aesthetic feedback remains pending.
