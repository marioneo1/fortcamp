# Male portrait rollout

Plan: one common visual role per generic race, with existing same-race/gender fallback supplying other classes. These are artwork themes, not class restrictions. Each sheet has twenty adult masculine identities in a square five-column/four-row layout. Use the full production male prompt in PORTRAIT_GENERATION_GUIDE.md and explicit species biology; generate new images rather than editing counterparts. Keep the authoritative art reference and male presentation reference separate in purpose.

## Installed or already available

Human, Goblin, Dwarf and Kobold have installed male pools. October 3 Goblin melee/ranged installations added twenty per role. Approved Aasimar male healer is now installed with twenty stable IDs and square full/thumb plus separate originals; sixty files and exact/fallback role matching verified. Portrait Lab now lists 1,844 portraits. Celestials are individually named characters, not generic male pool targets.

## Batch 001 — approved and installed in dev

- Half-Orc melee, Orc melee, Hobgoblin melee.
- Wood Elf ranged, Halfling ranged.
- Tiefling magic, High Elf magic.
- Gnome worker.

Files and exact expanded prompts: staging-portraits/MALE_BATCH_001.md. All eight requested sheets are saved, 160 portraits total, each actual file 1254×1254. Nine image calls were used because Halfling was generated again to strengthen adult proportions. The first attempt is retained as a comparison. The user approved the batch; all eight sheets are now installed in dev, twenty stable IDs per pool with full/thumb/original files. Runtime exact-role and same-race/gender fallback were verified. Existing portraits and production are unchanged.

Review notes retained for future refinement: some Halfling/Gnome faces read youthful, some Tiefling horn tips sit close to source edges, and several related face structures recur despite the diversity prompt. The user approved these images. Do not claim perfect identity diversity or full horn clearance. Grid decode/boundaries were checked and complete outputs inspected.

## Batch 002 — approved and installed in dev

Bugbear, Lizardfolk, Minotaur and Dragonkin melee; Harpy, Centaur, Faun and Catfolk ranged. Eight fresh sheets, 160 portraits, saved with exact expanded prompts in staging-portraits/MALE_BATCH_002.md. Each decodes at 1254×1254 with five columns and four rows; boundary evidence is recorded in data/portrait_audit/male_batch_002/manifest.json. User approved; installed twenty stable IDs per pool with square full/thumb and separate original images. Canonical source copies are in portraits/.

Female sheets were inspected for established species anatomy, but generation references remained the authoritative art reference and male Human presentation sheet. Some horn/ear tips approach edges. Harpy wing-arm anatomy is difficult to establish in the close crop; Centaur bodies are partly visible and their smaller faces will need careful circle framing. Complete generated sheets were inspected; file/grid validation does not establish anatomical correctness or perfect face diversity.

## Batch 003 — approved and installed in dev

Revenant, Vampire, Ogre and Troll melee; Alien ranged; Undead, Manaforged and Dreamkin magic. Eight fresh sheets, 160 portraits, with exact expanded prompts and review links in staging-portraits/MALE_BATCH_003.md. All decode at 1254×1254; five-column/four-row boundary evidence recorded in data/portrait_audit/male_batch_003/manifest.json. User approved; installed twenty stable IDs per pool with square full/thumb and separate original images. Canonical source copies are in portraits/.

Combined installation verified all 960 assets, exact-role and alternate-role selection, and Portrait Lab coverage (1,824 total). Installed montage and report: data/portrait_audit/male_batch_002_003_install/. Existing assignments and production unchanged.

Inspected all outputs. Face/crest repetition is notable in Alien; some Troll ears and Manaforged crystal tips approach or touch edges. Ogre faces lean angular; circle framing cannot recover clipped source pixels. Undead retains the existing preserved humanoid design. Validation covers file decoding and grid evidence, not perfect anatomy or unique face detection.

## Batch 004 — approved and installed; generation plan complete

| Common portrait role | Races |
|---|---|
| Magic | Astral Elf, Voidsent, Dark Elf, Foxkin, Fairy |
| Healer | Homunculus, Merfolk |
| Worker | Automaton |
| General, no class suffix | Slimefolk, Werewolf |

Ten fresh sheets (200 portraits), saved with exact expanded prompts and review links in staging-portraits/MALE_BATCH_004.md. All decode at 1254×1254, five columns/four rows; grid evidence recorded in data/portrait_audit/male_batch_004/manifest.json. User approved and all ten installed into dev with stable IDs, square full/thumb assets and separate originals. Verified 600 files, exact and alternate-role matching, and installed montage in data/portrait_audit/male_batch_004_install/. Inspected complete outputs; some face repetition, tight ears/horns/fur, subtle Homunculus markings and luminous Slimefolk cores remain review notes. Per-image appearance metadata tagging is pending.

No further generic male generation targets remain in this plan. User excluded Banshee and Dryad: new recruits and combat enemies now generate female only, regardless of available male artwork or a conflicting profile gender preference. Saved identities are retained. Named Champions/Celestials are not generic generation targets.

Do not reuse the Dwarf reference for unrelated races or opposite-gender race anatomy. Preserve source sheets and prompts in staging; use canonical IDs and separate original/square assets when installing. Existing character portraits must not be rerolled.

## Deferred female review

User requested another quality pass on female pools after consuming these males. Audit race fidelity, underlying face variety and composition against approved style before choosing individual sheets for fresh regeneration. Preserve legacy sources and stable identity order; do not replace every female pool indiscriminately.
