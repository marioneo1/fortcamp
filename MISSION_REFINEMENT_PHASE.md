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
