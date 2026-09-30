# Alpha 0.3.1 scope

> Historical alpha scope reference. FEATURE_BACKLOG.md in the repository root tracks current implemented and pending work.

Core loop under test:

1. Create the player character.
2. Start at a Tent + Campfire.
3. A guild-wide mission pool refreshes every 30 minutes.
   The pool contains E through S ranks. E has a configurable baseline, D adds seven fixed contracts per registered player, and the first player guarantees floors of four C, two B and one A before additional scaling rolls. S is 1% per attempt, with at most three attempts per player. Ranks above each player's Guild Hall visibility are redacted.
4. Inspect a mission and select its exact required team.
5. Equipment, traits, race, series/origin, stats, buildings and named-character identity can satisfy requirements or alter hidden/critical paths.
   Role-based missions also require a character in each named slot and show recommended combat ratings.
6. See exact d20 outcome probabilities before claiming.
7. First valid player to claim owns that mission instance.
8. Characters deploy for the mission duration and cannot be used/equipped elsewhere.
9. Mission resolves in the backend even if the Activity is closed, as long as the Python server remains online.
10. Rewards feed back into base progression: materials, gear, blueprints and recruits.
11. Mission completion produces authored aftermath text and an outcome-specific sound when watched live.
12. Buildings expose their real grid footprint during placement and can be selected and moved after construction.
13. Procedural recruits can be generated from mission-specific profiles so race/background fits where they were found.

Not in 0.3: raids, shared multi-team missions, PvP, mod uploader, production hosting, or public verification.

- Optional admin-only debug mission completion via `GAME_DEBUG_MODE=true`, including instant completion of available missions without meeting normal party or eligibility requirements.
- Admin-only immediate mission-pool rerolls with a selectable regional event while debug mode is enabled.
- Regional mission-board events with themed contracts, board/bot banners, event recruits, and rare event-only Champions.
- Full-Activity regional palettes and CSS ambient effects, plus stacked duplicate contracts to reduce board clutter.
- Authored Critical Success criteria are hard gates; missions without those criteria use normal stat-based critical odds.
- Tiered proficiency perks trained through matching facilities and consumable manuals, plus standalone perks that have no tier ladder.
- Mission reward hooks for direct perks, advanced training items, and rare race transformations.
- Player portrait URLs can be edited after creation and are limited to HTTP(S).
- Any owned roster character can use a locally uploaded PNG, JPEG, GIF or WebP portrait up to 4 MB.
- Characters include STR, DEX, AGI, VIT, INT and LUK. CON is derived primarily from VIT; DPS scales from STR, DEX or INT according to the equipped weapon.
- Mission visibility progresses from E to D by constructing the Guild Hall, then through C, B, A and S via Guild Hall upgrades.
