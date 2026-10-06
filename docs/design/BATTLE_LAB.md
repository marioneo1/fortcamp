# Battle Lab — implemented development tool

October 6 Mage: choose a Mage Job tester and practice **16 or 20** to unlock the full eight-skill pool, then select any five actives/passives. For elemental testing try Typhoon / Chain Lightning / Flash Freeze / Singularity / Fireball. For Meteor try Fireball / Flash Freeze / Singularity / Meteor / Debuffer. Replace a slot with Enchant Weapon to test chosen Fire/Frost/Lightning on a martial helper. Mage starter practice 0 equips Chain Lightning, Fireball and Typhoon. These are temporary owner-scoped tests; existing roster saves are untouched. See [Mage rules](MAGE_REWORK_REVIEW.md) for friendly Typhoon, channel costs and freeze timing.

## October 5: Monk combo testing

Temporary Job testers ? Monk starts with Rapid Palm, Iron Reversal and Heaven-Piercing Strike. Select 16 successes to unlock the full eight-skill pool, then choose any five active/passive slots. Try reliable skirmisher (Rapid Palm, Iron Reversal, Heaven-Piercing Strike, Perfect Rhythm, Sweeping Dash) or offensive sequence (replace Iron Reversal with Breaking Combination). Battle-only combo/forms persist across commands but reset on a fresh test. Lab cannot edit real progression or saves. Skill damage remains initial tuning; compare against Fighter/Barbarian using the same enemies/weapon tier before declaring final balance.

## October 4: Temporary Job parties

Battle Lab now defaults to Temporary Job testers. Choose up to four of the twelve
starting Jobs independently, with matching poor starter gear and equal starting
attributes. Practice presets are 0, 2, 5, 9, 12, 16 and 20 successful contracts; they unlock
the same skills as real progression without completing or awarding contracts.
Each tester can equip zero to five learned active/passive skills. Skill cards
show actual descriptions. At practice 9, select which one of six skills to omit. Higher tiers expose the additional Fighter and Barbarian choices; capacity stays five.

Use Test characters to switch back to Copies of my roster. The optional temporary
companion is off by default; enable it explicitly for a solo test. Restart Same
Test retains Jobs, practice, selected skills, approach and seed. No tester is
added to the roster, and no gold, fatigue, injuries or save data are changed.
Existing dev-only/admin restrictions, owner isolation and expiry remain enforced.

Validation covers every Job's actual starter weapon/active snapshot, mixed parties,
locked/duplicate skill rejection and unchanged saves. Browser checks cover twelve
choices, skill unlocks, five-slot swaps, request payloads, retained settings and
the roster toggle. Frontend build passes with the existing bundle-size warning.
The browser fixture uses mocked responses; backend tests validate actual units.

## October 3: Named command-location variants

Break the Rival Warband, End the Old Command, Chieftain's Redoubt and The Ironcap Vanguard now expose four verified layout presets through their actual encounter. E/D old-command jobs use compact posts; C–S use full compounds. Labels come from the generated map's template label, so roadside/camp assembly plans display readable names even when they contain multiple buildings. Start a new lab session to see the map; live saved battles are not rebuilt. This extends the existing mission/approach/seed controls without adding another launcher.

## October 2: Fit candidate stone corners and lengths to actual building boundaries

Restored the template's edge-wall collision convention. Candidate perimeter bands now sit 0.38 tile from cell centre; the generated corner's bend sits at the rotated boundary intersection rather than the tile centre. Concave joins retain their template seating. Full bands span one unit, half bands half a unit; corner arms and perimeter T stems extend 0.88 units to meet the neighbouring boundary/divider ports. Centre T/cross arms reach half-unit ports. Dedicated authored corner/T/cross centres remain intact. Only outer arms use uncapped cropped sections of the matching straight/vertical material from the SAME generation; sections repeat at unchanged pixel scale. No image stretching, foreign wall art, centre patches, synthetic overlapping junction bands or extra posts. Added a separate perimeter-T export. Sprites use shared 1024px canvases and port-based anchors.

Reinstallation now calls tools/fit_boxed_wall_ports.py automatically from tools/install_boxed_wall_trial.py; raw recovery is internal, so reimport does not undo calibration. The frontend's native connection ports use these exact arm lengths. Cache stamp updated. Timber/metal and all old stone profiles remain unchanged. Review screenshots of all four complete buildings show boundary corners and continuous wall runs; subtle texture/stone-course transitions still exist and visual approval is not claimed. Verification: four backend material tests, 31 frontend wall tests including corner-to-band/perimeter-T coincidence, frontend build, and four actual-renderer browser maps with loading assets and no procedural junction connectors. The browser screenshots are in staging-terrain/building-toolset-v9-boxed-reference/in-game-1..4.png. Production unchanged.

## October 2: Replace isolated wall displays with full building comparisons

User rejected the candidate's isolated pieces/rotated sample rows as insufficient. The same dev material now rebuilds the four established furnished building plans: gatehouse, divided hall, breached annex and twin stores, using material-layout-1 through material-layout-4. Former boxed-walls-1..4 seeds remain aliases. Stone shells, partitions and authored junctions use the new generated six-piece art at one shared scale; all room floors and original furniture remain. Doors/gates deliberately use working timber leaves, because no matching door art was generated; broken sections use traversable gaps with common stone-debris props. Removed unsupported pillar/stair/brace sample decorations rather than pretending they came from the new atlas. Native masonry occupies its cell; enemy spawn candidates are recalculated to avoid occupied walls. No old stone wall textures are mixed into the new shell.

Verified four complete-building renders and reviewed screenshots of every layout; four backend material tests pass, including full-plan/floor/furniture preservation, working gate pairs, reachable exits and save/owner isolation. Generated thickness/span inconsistencies remain visible and are not called solved. Screenshots: staging-terrain/building-toolset-v9-boxed-reference/in-game-1..4.png. Production and normal mission defaults unchanged. This supersedes the previous individual-piece Battle Lab layouts.

## October 2: Boxed six-piece kit available in dev Battle Lab

Installed the v9 candidate additively as **Polished stone (Boxed six-piece trial)** in Building material tests. Four seeds: boxed-walls-1 (individual pieces), boxed-walls-2 (connected runs), boxed-walls-3 (90-degree connected runs), boxed-walls-4 (180-degree connected runs). Six source silhouettes are exported on shared 640px canvases at unchanged scale; measured intersection anchors seat them on the grid. Removed broad soft-alpha background halos using silhouette ownership with a two-pixel fringe. No texture stretching or independent piece rescaling. The new native_pieces profile draws generated corner/T/cross directly, without procedural connectors, cap overlays or face mirroring. Old material profiles/default maps remain unchanged.

This is an in-game comparison, not an even or seamless kit: generated full/T/cross spans are 397/443/412px, and half width is 218px. Gates, breaches and other parts were not generated and are not substituted from another kit. The dedicated test maps use ordinary destructible blocking walls, owner-scoped temporary Battle Lab parties and reachable exits. Verification: three material tests (all seven material families), 30 wall-renderer tests, frontend build and all four isolated browser renders with every candidate asset loading and zero procedural connector elements. Connected-run screenshot inspected; joins remain subject to visual review. Rebuild tool: tools/install_boxed_wall_trial.py. Browser check: tools/boxed_wall_browser_qa.mjs. Media excluded from Git; stored locally in structures/building-v9-boxed and staging-terrain/building-toolset-v9-boxed-reference.

## October 2: Additive pure overhead stone materials

Restart dev and refresh the client. Open Mission Board > debug controls > Open Battle Lab; set Source to Building material tests. Two additional entries are available: **Polished stone (Pure overhead) building kit** and **Rough stone (Pure overhead) building kit**. The original Polished stone, Rough stone, Timber and Metal entries remain unchanged. Select the same named Map layout (Gatehouse, Divided hall, Breached annex or Twin stores) on old/new entries to compare identical terrain positions and spawn locations. Six materials now provide 24 layouts, with all 16 parts covered across each material's four layouts.

The new profiles use independent limestone_plan/fieldstone_plan IDs and building-v5-topdown art. They are debug tests, not public contracts or default replacements; gates, wall damage, movement boundaries and test/save isolation still use normal rules. Plan-view art rotates without old face mirroring or added corner columns. Separate calibration keeps door/gate open/closed jamb anchors consistent. Screenshots are saved in staging-terrain/building-toolset-v5-topdown. Install/reinstall only the additive candidates with tools/install_topdown_stone_toolsets.py; the older material installer preserves their registered geometry. Generated media are local and excluded from Git.

## Latest stone/metal review (October 2)

Restart dev and refresh the client, then use **Source: Building material tests** to inspect all four layouts. Rough/polished stone now use newly generated v4 bands with caps only at exposed ends; connected metal segments omit repeated posts. Enlarged six-type/rotation screenshots and the 16 full maps are saved in staging-terrain/building-toolset-v4. Sources/prompts and remaining art limitations: ../art/MODULAR_WALL_GENERATION_GUIDE.md. Validation: 325 backend tests, 117 frontend tests, build and enlarged/full-layout browser checks pass. No rewards, save writes or production changes.

## Latest connection review (October 2)

Refresh the client and restart a material test to compare the repaired corners/Ts, short ends and damaged corners. Intact joins now use matching straight-wall textures at exact edge/center positions, rather than the unequal generated join silhouette. All four material layouts remain available. An enlarged six-piece comparison with 0/90/180/270-degree rotation is generated by tools/build_wall_join_preview.py. Validation: 109 frontend tests, build, seven targeted backend tests and enlarged/full-layout browser checks pass; 325 remains the previously verified full-backend baseline.

## Material tests (October 2)

Open **Mission Board → debug controls → Open Battle Lab**. Set **Source** to **Building material tests**, or search **building kit**. Choose Timber, Rough stone, Polished stone or Metal, then select a named **Map layout** and click **Start Test Battle**. Restart the dev launcher after backend changes and refresh the Activity/browser. Production has no access to these tests.

Each material has four distinct footprints: **Gatehouse and courtyard**, **Divided hall and branching partitions**, **Breached annex and repairs**, and **Twin stores and loading court**. The same footprints make comparisons between materials easier. They are diagnostic layouts based on existing reusable buildings, not new public contracts. Four entries join the 73 mission entries, for 77 catalogue entries total.

Across each material's four layouts, all 16 parts appear at least once: wall, corner, centered T, cross, end, breach, closed/open door, closed/open gate, window, pillar, stairs, damaged corner, perimeter T and brace. Expand **Pieces in this layout** in the battle toolbar to see the exact subset used. Gatehouse demonstrates gate states/window/pillar; divided hall demonstrates branching partitions and ends; annex demonstrates an open door, damage and repair brace; twin stores demonstrates stairs and supporting pieces. Doors and walls use normal interactions. Stairs and braces are scenery; changing floors is not implemented here.

Fixed seeds `material-layout-1` through `material-layout-4` select those plans. Custom seeds choose one of the four reproducibly. Sessions use copied characters and the actual combat renderer/engine, remain owner/server-scoped and never write rewards or player saves. The lab provides a visual review workspace; passing coverage checks does not establish subjective art approval.

Current validation: 325 backend tests, 107 frontend tests and frontend build pass. Browser QA launches all 16 material layouts and verifies each material's complete piece coverage, rough-stone v3 assets, ordinary mission workflows and mobile layout. Screenshots: `staging-terrain/building-toolset-v3/<family>-<1..4>-in-game.png`. Art audit: 99 encounter previews, 3,465 references, no missing files. The fixture builders and coverage audit include these diagnostic maps without reading saves.

## Current building preview rules (October 2)

Restart a test battle to see new edge-wall collision and material-specific building art. The divided tool house and partitioned repair hall now have actual T-junctions. Interior edge/corner floor tiles are walkable; centered dividers remain blocking. Existing saves are not regenerated. Rules and source packs: WALL_BOUNDARIES.md and BUILDING_TEMPLATES.md.

Open **Mission Board → debug controls → Open Battle Lab** in the dev game. Restart the dev launcher once after backend changes, then refresh the browser/Discord Activity. `GAME_DEBUG_MODE` must be enabled. Production/release/stable profiles explicitly reject the lab even if debug is accidentally enabled. Server admins can use it; local auth bypass follows the existing debug policy.

The lab replaces the three separate quick-test buttons with one searchable workspace. Currently 73 mission templates expose supported battle encounters; the list is derived from current content, not maintained separately. Search name, faction or mission type and filter by rank or source. Each entry shows its rank, description, regional pool or private follow-up source, faction when provided, and known preceding contracts. The encounter identifier makes it clear when a failed investigation loads a different battlefield.

Choose a story approach and force a supported outcome. Only transitions that actually create a battle are offered; successful investigation results that continue dialogue or finish without combat are omitted. **Direct map test** bypasses the story and uses normal deployment. The lab bypasses party size, unlock and training requirements to make visual testing practical. Combat stats, gear, racial rules, loyalty, movement, AI and terrain still use the actual engine.

Goblin Warcamp supports a head-on attack, scouting an ambush, and building a defensive lane. An ambush success puts enemies asleep for three rounds; attacking wakes everyone. Scouting failures give enemies initiative, and critical failures strengthen the commander. A successful defensive lane adds breakable cover. Trap placement is part of **Hold the Hedgerow Watch**, whose normal preparation screen opens in the lab.

Select one to four roster copies, including busy characters. Their current equipment and stats are used without changing their saved availability. An optional temporary companion fills a solo party to two; it uses fixed modest stats, Skilled combat proficiency, 100 loyalty and no equipment. If no player save exists, a temporary starter is provided. Keep the generation seed for repeatable map, enemy and NPC generation; choose **New seed** to inspect another generation. Restart Same Test repeats the last launched request. Choose Another Map returns to the picker. Closing a preview does not create a resumable mission in Private Contracts.

For authored locations, **Map layout** lists every saved plan with a verified generation seed. Select a plan to fill the seed, then Start Test Battle. Workshop: forge yard, courtyard pair, L-shaped forge or partitioned repair hall. Shed: long store, divided store, annex/yard or twin sheds. Armory: north/south or east/west stores around an open courtyard. Bridge presets expose both crossing positions and the available deck materials. These are actual seeds passed to the normal encounter generator, not a separate test-only map override. Custom seeds remain available; New seed resets the selector to Custom / random seed. Returning to the same mission preserves the last launched preset. Layout options follow the selected battle encounter, so an investigation complication will not advertise its parent mission's map. The battle toolbar shows the selected template name and seed.

Test sessions live only in backend memory, are scoped to both server and player, expire after one hour of inactivity and disappear on server restart. At most four are retained per player and 64 overall. They create no mission records and never resolve real rewards, recruitment, prisoners, injuries, supplies or world outcomes. Auto battle remains available for previewing encounter behavior but pays nothing. The lab is a battle/map tester, not a full dialogue-chain or loot simulator.

## Verification

Nine backend tests cover all catalogued launch targets, authored setups, every listed layout seed, seeded repetition, save isolation, invalid selections, owner/server isolation, expiry/bounds and disabled/production permissions. Frontend build and 103 frontend tests pass. Browser checks cover mission filtering, approach outcomes, launch/restart/return, named workshop presets and their outgoing seeds, Custom/New seed behavior, defense preparation, enlarged wagon art and mobile layout.

For isolated browser QA, run `.venv\Scripts\python.exe tools\build_battle_lab_preview.py`, then `node tools/serve_board_preview.mjs`. Launch headless Chrome with a temporary profile and remote debugging on port 9229, then run `node tools/battle_lab_browser_qa.mjs`. The fixture has four encounter families and uses actual UI modules with mocked API responses; it does not read saves or run the live server. Screenshots go to `staging-ui/battle-lab`. In-game testing supports the full catalogue.

Remaining: subjective visual review and a later balancing pass. Enemy/stat tuning was not changed by this tool.


## Per-tester weapons (October 5)

Open Battle Lab, choose **Temporary Job testers**, then choose **Weapon** on each tester. Starter equipment is the default; Unarmed / fists removes the weapon; all catalogue weapons use their real stats, granted abilities and capture restrictions. A Fighter can test a net; equipping it makes the basic action Subdue. Selection travels with the restart request and survives reopening the tester panel. Changing Job resets to that Job's starter weapon. Copies of the roster keep their original equipment; this override currently applies to temporary Job testers only. No saved roster/inventory writes.

## Rogue test kit (October 5, implemented in dev)

Select Rogue under the existing Job testers. At 16 successful contracts all eight choices are available; equip up to five. Add other testers to check opposite-side Cheap Shot and Fighter push/pull through Caltrops. Start a fresh session for reworked definitions. Mixed trap/knife/Shadowstep targeting uses the same confirmed controls as real combat. Tests and local previews do not change player saves; production debugging remains unchanged.
