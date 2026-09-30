# Mission Refinement Phase

This file records the rules for expanding Fortcamp's missions without turning their results into mechanical reports.

## Story rules

- Results should read as short scenes. Use concrete actions, setbacks, decisions, and consequences.
- Keep the useful invented connective moments that make a mission feel lived in.
- Never print internal condition names such as `event race or relic affinity`, rule IDs, score formulas, or hidden team requirements in story text.
- Put exact kills, captures, recovered objects, and combat statistics in the separate tactical report. The scene can use those facts, but it should turn them into narrative rather than list them.
- Appearance is optional context. Do not force a hair, eye, race, weapon, or clothing description into a paragraph merely because metadata exists.
- Content remains SFW. Fork of Chains may be studied for pacing and result structure, but its prose is not copied and unsuitable material is excluded.

## Mission identity

- Ordinary quest NPCs receive stable names generated from the mission seed. Replaying or reopening the same mission preserves those identities; a new mission produces new people.
- Champions and Celestials are authored limited characters. Their identity is persistent and globally unique rather than regenerated per mission.
- Internal unit IDs remain stable so saves and battle rules do not depend on a displayed name.

## Mission forms

The board should mix several forms rather than treating every contract as combat:

- expedition and profession rolls;
- dialogue and negotiation choices with clear information;
- tactical combat;
- rescue, extraction, capture, defense, pursuit, and escape objectives;
- consequence missions that appear on a later board because of an earlier outcome;
- private mission chains belonging to the player who started them.

## Rewards

- Give every mission a reason for its rewards. Logging and mining contracts may provide bulk materials; a prisoner rescue should not produce arbitrary lumber or stone.
- Maintain a useful baseline reward, then add mission-specific discoveries, equipment, perks, recruits, intelligence, or story items.
- Some rewards require behavior rather than a better roll. Capturing a named target alive, recovering evidence, protecting a witness, or leaving an enemy alive can each unlock distinct loot.
- Failure gives little or nothing. Critical failure may also cause injuries or new hostile consequences.
- Event rewards should carry the event's identity through their name, use, perks, or later mission access.

## Prison foundation

Captured unconscious enemies now become persistent prisoner records. Each record keeps the person's generated identity, portrait, race, weapon, capture mission, and whether they are a priority target. A Prison Cell holds four captives securely and accepts one character assignment as its Warden.

Overflow captives enter the temporary stockade with one hour before removal. The allowance belongs to the prisoner: moving them into a cell pauses it, and moving them back resumes the remaining time rather than resetting it. Players can swap prisoners between the cell and stockade or sell any captive for gold. Recruitment, negotiation, release, and ransom remain locked until their rules and costs are authored. Later work should add Warden effects, escape risk, treatment, loyalty, and consequences for holding important prisoners.

## Planned content passes

1. Audit every existing mission for clear stakes, mission form, outcome scenes, sensible baseline rewards, critical requirements, secret routes, and consequence hooks.
2. Build race gameplay identities: meaningful strengths, weaknesses, movement traits, resistances, profession affinities, and rare drawbacks such as loyalty limits. Elements should be added only alongside readable combat interactions and counters.
3. Author Champion acquisition chains around places and conflicts that fit each character's source lore. A Champion can be acquired once, and discovery should result from a memorable route rather than a generic reward roll.
4. Expand prisoner play with recruitment, exchange, ransom, release, and faction consequences.

The proposed goblin diplomacy route belongs in the Champion pass: bringing a goblin chieftain changes an assault into negotiation, opens goblin-only follow-ups, and a disastrous village raid can cause Goblin Slayer to enter the chain. Exact hidden requirements remain concealed until the player's selected party can trigger a clue.

## Current first pass

- Goblin Warcamp and The Captive Cart use generated mission identities and authored tactical aftermath scenes.
- Captured enemies persist in the roster's Prisoners collection.
- Capturing a warcamp chieftain alive unlocks a roll for the Chieftain's Command Horn. Securing the battlefield improves the chance from 20% to 35%.
- Capturing a cartmaster alive unlocks a roll for the Cartmaster's Route Book. Recovering the dispatch satchel improves the chance from 35% to 55%.
- Internal trigger labels no longer appear in result prose; invented character moments remain available.

## Catalog audit completed

- All 116 current templates now carry an audited mission form and a plain-language objective. The forms distinguish recovery, rescue, escort, defense, hunt, containment, investigation, infiltration, and broader operations.
- The mission board shows that form on each card and shows the objective in mission details before party selection.
- Generic event outcomes now use short scene structures appropriate to the mission form. Mission results still include useful invented character moments, but those moments use concrete actions rather than repeating a character's stat or specialty.
- Event material bundles now follow the work performed. Combat sites favor captured provisions and equipment, building sites yield usable structure material, medical and magical sites produce their relevant supplies, and survival expeditions return plausible field resources.
- Event keepsakes use rank-scaled drop chances. Critical caches, critical recruits, Champion encounters, permanent boons, transformations, consequence relics, and consequence perks all make visible seeded rolls rather than being silently guaranteed.
- Story finales still guarantee their permanent world outcome. Their trophy relic and personal perk roll separately, so completing an arc matters even when its rare equipment does not drop.
- Consequence chapters continue to unlock through board-followup rolls, while their special discovery items have their own drop chances.

The encounter architecture and first race gameplay identity pass are now recorded in `MISSION_ENCOUNTER_ARCHITECTURE.md`. Mission purpose is separate from current resolution, intended encounter mode, and combat disclosure. The next implementation pass is the first branching investigation with bodyguard selection, followed by the Private Contracts foundation and authored Champion acquisition chains. Champion chains should replace unrelated random Champion appearances as their authored routes are completed.
# September 30: immediate private leads, combat routing, roster usability

Earned follow-up rolls now create owner-only Private Contracts immediately. Discovery chances stay unchanged; a discovered contract lasts 24 hours from the source mission's completion. Guild Hall visibility gates the shared pool, not a lead the player already earned. Existing unexpired leads are recovered from completed missions without resetting their deadline. Older public consequence copies are moved into private ownership when still unclaimed. Result screens link directly to ready contracts, and the Private Contracts tab shows an available count.

Eleven explicitly hostile contracts now launch tactical battles: Highway Ambush, Bandit Outpost, Goblin Warren, Goblin Chieftain, Goblin Boar Riders, Hobgoblin Vanguard, Bone Patrol, Undead Bone Collectors, Undead Death Knight, The Tithe Convoy, and Court of the Empty Crown. Road, camp, ruin, and court blueprints reserve deployment cells and open routes. Enemy counts and strength scale by rank; racial health, movement, armor, evasion, and resistances apply. Loot remains rolled. A living commander capture plus a secured field and standing party is the critical objective for living factions; undead encounters require a secured field and standing party. Peaceful missions and deserted checkpoints remain roll-driven. These are the first reusable encounter layouts; advanced escort, stealth, and dungeon progression remain separate future passes.

Roster management has search, race/status/type filters, CON/DPS sorting, 24-character pages, independent list scrolling, and separate Overview / Equipment / Appearance tabs. Collection and prisoner browsing sits below the roster. Equipment slots have search fields; appearance drafts persist during redraws and character switches. Polling does not replace focused roster inputs, textareas, or selectors. Browser fixtures exercise 300 characters at desktop and narrow widths.

## September 30: consequential choices, perk mechanics, and layered loot

Four contracts have authored decision scenes, and twelve tactical contracts offer direct attack, a checked ambush, or an Engineer/trained-builder blockade. Optional failure can remove a discovery without ending the contract; other failures end the job or launch a fight. Exceptional investigation failures can bring a stronger named officer with a separately rolled, recovery-dependent trophy. Three timed contracts can transition from critical failure into a playable recovery encounter without prematurely applying terminal rewards or injuries. Bodyguards do not improve primary mission checks. Saved node revisions reject repeated choices.

General and faction caches now select rank-weighted rarities. Eight new exclusive equipment pieces have separate drop checks and never enter broad pools. Fifty-eight core perks have bounded shared mechanics, including equipment-granted effects; all forty-two racial identities disclose their implemented modifiers in the roster. The larger Champion perk catalog remains an authored follow-up, rather than being declared complete.

The standing design requirements and remaining scope are recorded in GAMEPLAY_VISION.md. Night approaches, full stealth, larger deployments, and continuing a decision scene after its battle require later passes. Verification: 138 Python tests, seven JavaScript tests, production frontend build, and browser previews of decisions and racial effects passed.

## September 30: immediate decisions, aftermath layout, and audio controls

Contract acceptance now includes the first saved choice scene in the same response. The client renders it immediately, clears the planner, resets scroll and focuses the first available choice. Closing still preserves server-side progress. Other expeditions completing in the background do not replace an open mission screen.

Aftermath shows the outcome first, gives the story and recovered rewards separate columns, and collapses mechanical checks and loot rolls. Device-local audio controls expose Master, Music, Interface & Mission Sounds, and Battle Effects, plus mute, defaults, and previews. Interface clicks and all four mission outcomes share one channel as requested; playing file-based effects respond immediately to changes.

FEATURE_BACKLOG.md now collects pending UI, performance, and gameplay work. MUSIC_GENERATION_GUIDE.md proposes a warm, restrained fantasy palette without piercing high leads. No paid music generation has occurred. Music playback awaits approved tracks. Equipment/inventory redesign, board art/VFX, and measured responsiveness work remain deferred.

Verification: 139 Python tests and eleven JavaScript tests passed, including acceptance-response and immediate-opening regressions; production frontend build passed. Browser previews verified four audio channels and the aftermath layout. A local Git baseline covers source, tests, docs, and configuration; secrets, player data, generated assets, and builds are excluded. No remote is configured.

## September 30: four guild-board music auditions

At the user's request, generated Lanternlight, Guildhall Shuffle, Roads Waiting, and Mapmaker's Clock as four distinct 120-second instrumental guild-board candidates. Exact requests and immutable originals are retained under staging-music/guild-board-candidates-v1. Listening copies use two-pass integrated-loudness matching around -20 LUFS; true peaks are below -5 dBFS. Each has a separate end-to-start cyclic-crossfade trial. Musical continuity, melody, fatigue, and subjective treble comfort await user listening.

LISTEN.html and listen_music_candidates_windows.bat open the four-track comparison. Only one audition player runs at once; the page provides a common volume control, original repetition, loop trials, and downloads. A hosted copy is linked from Sound settings. No track is selected as gameplay background music yet, and all candidates remain available. The generation utility reuses saved originals and blocks automatic retries of uncertain paid requests.

## September 30: music rotation, transitions and launcher inventory

Approved all four guild tracks, applied gentle three-second endings to playback copies, and preserved source downloads. Generated three additional 120-second location themes: Hearth & Camp, Roads Under Pressure, and Goblin Warcamp. A seven-track listening library replaces the standalone music batch shortcut. Runtime music rotates board tracks and selects base/general/goblinoid battle themes, crossfades over three seconds, unlocks after a user gesture, follows the Master/Music mix, and pauses when hidden. Normal redraws do not restart the music.

WINDOWS_TOOLS.md distinguishes source/dependency checks from actual launcher operation. Start/setup working directory handling was corrected; the development backend uses the project's venv explicitly. Install, stop, crop mutation, GUI launch and public-tunnel actions were not exercised against the live game. Remaining investigation, undead, siege, boss and Starfall prompts are in MUREKA_MUSIC_PROMPTS.md for the user's website subscription; no additional ElevenLabs generations were made after that request.


## September 30: Mureka imports, popup-safe transitions, documentation and GitHub

Installed eight distinct corrected Mureka uploads: Boss 1/2, Defense 1/2, Investigate 1/2, and Undead 1/2. Originals are archived without overwriting; the importer records source hashes, matches loudness and applies gentle fades without network/API requests. The local and hosted listening library now contains 15 tracks, with context filters and loop trials.

Runtime playlists distinguish major bosses, defense, undead, goblins, ordinary combat, and sustained interactive investigations. Short popups leave background music alone. Investigations wait eight seconds, ordinary tab switches 700 ms, and return from encounters five seconds. Three-second crossfades and remembered playback positions prevent abrupt restarts. Tests cover delayed switching, cancellation, return position, fade reversal, and encounter precedence.

Organized design, art, audio, reference, and historical documents under docs. Root DOCUMENTATION.md provides the index; existing portrait and SFX tool-dependent guide locations remain unchanged. Legacy portrait prompts and the original README are preserved. Corrected prison backlog status to reflect implemented selling, swaps, and individual stockade clocks. Regional prompts cover all five actual events, including hostile Starfall impacts.

Validation: all 20 frontend tests and the production build passed; import and library scripts compile. Markdown links and Git history were checked before public publication. The user authorized uploading code to marioneo1/fortcamp; secrets, player data, generated media, and build outputs remain excluded. No new paid generation requests were made.


## September 30: regional playlists and sparse ambience

Imported ten Mureka regional uploads, two per event, with preserved originals and source hashes. Regional browsing now chooses the actual event playlist; base, interactive investigations, and encounter-specific battle music retain precedence. The 25-track listening library includes regional filters.

Generated seven environmental accents (64 requested seconds; API receipts total 640 credits): goblin chatter/camp, ash procession, arcane disturbance, beast call/passage, and damaged alien machinery. Stored originals and exact prompts separately. Runtime uses one clip at a time, delayed initial play, randomized 45?80-second gaps, variant alternation, context fades, hidden-page suspension, missing-file suppression, and a separate Ambient Sounds channel. No continuous ambience bed is used. Auditions are linked in Sound settings. Technical level checks passed; subjective listening review remains necessary.

Validation: 26 frontend tests passed, including ambience gesture/sparsity/alternation, fade cancellation, mute/background behavior, missing-file suppression, regional playlist priority, and settings migration. Production build and source-script compilation passed. Music imports make no API calls; new sound-effect generation was limited to the seven requested accents.

## Guild ambience and proposed board redesign

Generated one 16-second guild chatter clip (API receipt: 160 credits) and wired it exclusively to the ordinary Mission Board. Regional or combat ambience takes precedence; other general guild-music tabs do not play chatter. Preserved the source and reused it after correcting very quiet source gain before loudness normalization; no repeat generation was made. Current ambience pack has eight clips. A separate mission-board plan describes a 24-icon shared sheet, stronger card hierarchy, stable navigation/refresh state, and restrained event animation. No board rebuild or UI image generation occurred before proposal review.


## September 30: painted contract board and stable refreshes

Following user approval, generated one 6x4 transparent painted icon atlas using existing prop and combat UI artwork as style references. Extracted six rank seals, eight mission forms, five event emblems, and five utilities. Removed small disconnected row-border flecks, retained alpha, and normalized without aspect distortion. Original source, exact prompt, extraction preview, and board screenshots are preserved.

Public and private work now share the Contracts destination with inner navigation and saved-expedition access. Cards separate premise, duration/party, role recommendations, possible reward previews, requirements, and explicit inspection. Rank groups retain unlock concealment and collapsed state. Filter controls remain reachable on desktop, active chips remove filters, and unchanged polling keeps the existing DOM and focus. Countdowns update independently. Event headers use generated emblems, regional colors and bounded motion; the old full-screen particle pattern is removed. Hidden-page and reduced-motion rules apply.

Verification: all 33 frontend tests and the production build passed. Local browser checks verified 24 loading assets, no script errors, hidden locked names, focus and collapse retention through refresh, combined filtering, public/private navigation and Inspect buttons, reduced motion, and a one-column 390-pixel layout without overflow. The actual board renderer was used with representative safe fixtures; no live user game state was modified. Discord-specific network performance remains a later measured pass.


## September 30: full-board event atmosphere

The user clarified that leaves, ash, arcane pulses and alien light should appear in the board background, not just its emblem. Added a dedicated canvas behind public/private contract views, with distinct event particles/light motion and stronger banner scenes. Cards and controls remain above it. Motion uses at most 24 draws per second, bounded resolution and particle count, and retains state during polling. Battles, unrelated tabs, general events and hidden pages stop the effect. Reduced motion renders a static frame with no animation loop.

Verification: all 36 frontend tests and production build passed. Browser pixel comparisons confirmed active background motion for all five events and a frozen frame under reduced motion; the ordinary board hides the effect. Existing navigation, focus, filtering, stacking, locked-content and narrow-layout checks still pass. No new image or sound generations were made in this pass.

## 2026-09-30: Painted board background effects

Generated one new transparent 6x4 effects atlas with the built-in image tool and extracted 24 padded PNGs without flattening soft alpha. Public/private regional backgrounds now use painted leaf variation, ash and mist, green/orange embers, rotating cyan/violet glyphs, alien ribbons/motes and an occasional comet. A shared lazy loader caches images and failures once, preserves aspect ratios, and makes the pack available for later weather/skills without implementing those systems now. Existing motion limits, visibility suspension, fallback shapes and reduced-motion still rendering remain. Exact prompt and asset guide are documented; source media stays local and excluded from public Git.

Validation: 38 frontend tests and production build passed; browser checks confirmed all board textures loaded, every event animated, reduced motion stayed static, ordinary boards hid the backdrop, mobile had no overflow, and polling preserved focus/collapse state. Inspected extracted preview and the rendered Beast Tide board.
