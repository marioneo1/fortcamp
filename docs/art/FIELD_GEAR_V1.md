# Field gear V1 and bear combat audio

October 8, 2026; installed in dev. One generated transparent **5-column x 4-row**
sheet, 20 items. Existing item art references supplied to match painted fantasy
inventory style. No individual item generations and no existing icons replaced.

Source and exact prompt: `staging-ui/field-gear-v1/atlas.png`, `prompt.txt`.
Stable cell IDs: `docs/art/FIELD_GEAR_V1_MANIFEST.json`. Safe importer:
`tools/import_field_gear.py`; detects separate silhouettes, checks count and
refuses overwrites. Uses existing crop-audit helpers to prevent neighbor bleed.
Installed 192px transparent icons: `frontend/public/assets/catalogue/items/`.
Review sheet/report: `staging-ui/field-gear-v1/installed-preview.jpg`,
`import-report.json`. Legacy gear catalogue recognizes these IDs as already
illustrated; it does not reassign their cells to its older 6x6 sheets.

Six knuckle/hand weapons (Bear Claws, Padded Handwraps, Brass Knuckles, Iron
Knuckles, Duelist Cestus, Stonefist Gauntlets); three daggers (Balanced Dagger,
Skinner's Knife, Parrying Dagger); two maces (Oak War Mace, Flanged Mace);
three spellbooks (Weathered Spellbook, Field Grimoire, Runebound Folio);
six armor/accessory pieces (Cloth Headband, Leather Wristguards, Padded Leggings,
Gripsole Boots, Trapper's Charm, Thick Bear Pelt). Stats/availability:
`backend/field_gear.py`. Eighteen ordinary items join weighted E/D loot;
Bear Claws/Pelt are recovered radiant-bear trophies only. Real Monk damage,
body HP/initiative tradeoff and all icon paths are checked by tests.

Bear audio: `staging-sfx/bear-combat-v1/` preserves original MP3s, decoded WAVs,
prompts and `generation_report.json`. Nine ElevenLabs clips: three each of
`bear_attack`, `bear_hurt`, `bear_death`. Runtime mono 48 kHz WAVs installed in
`frontend/public/assets/sfx/`; normalized with zero final clipped samples.
Generation cost recorded by provider: 84 credits total. No extra generation is
needed on resume. Audition `/assets/sfx/preview-bear-combat-v1.html`.
Generator: `tools/generate_sfx_pack.py --pack bear-combat-v1` reuses originals.

`combat-audio.js` keys on `foraging_bear`, mixes quiet attack vocalizations with
existing claw impacts, and sequences hurt/death through animation events.
Automated checks cannot judge sound quality; human listening review remains.
