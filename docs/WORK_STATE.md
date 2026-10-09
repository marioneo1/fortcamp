# Current work and parked threads

Updated October 8, 2026. Read this at session start and when the user pivots.
This is a concise checkpoint, not a substitute for system documents or backlog.

## Active: dev and production publication

- User authorized pushing current dev and production; preserve production saves.
- Production port 5173 is stopped. Release builder retains credentials, backs up
  SQLite and uses release flags; QA tools/tests/drafts excluded.
- Name uploads remain drafts, not installed runtime content.
- Validation/publication results recorded in RELEASE_PREPARATION.md.

## Active: starting race eligibility - implemented in dev

- Previous creator/API allowed 41 races, including Secret Werewolf.
- Approved 14 starting choices enforced by creator and API; full 42-race
  content catalogue and existing saves retained. Five onboarding tests, creator
  test and frontend build pass. Production unchanged; restart dev backend
  when reload is off. See design/STARTING_RACE_AUDIT.md.
- User has supplied seven race_names JSON files in content/drafts/names;
  ingestion/validation is pending, not cancelled by the race-selection audit.
- Retain all 42 races for names, recruitment and Battle Lab. Eligibility changes
  must preserve existing characters and use one server-authoritative policy.

## Active: withdrawal controls - corrected and browser-verified

- User requests Leave Map in Actions, shown at extraction and greyed during HOLD;
  Retreat All in Commands, removed from Battle Options, standardized style/order.
- Implemented conditional backend context entry and disabled UI; Leave Map hidden
  off EXIT, L while Actions open. Retreat All uses R and retains second-press
  confirmation. Order: Move/Attack/(Subdue)/Throw/Actions/End Turn/Retreat All.
- User removed Guard button; End Turn help explicitly describes its conditional
  25% next-direct-hit protection. Space/G end turn. Six standard buttons use
  three columns; optional Subdue uses four. Shared CSS/width column variable.
- Fixed old Retreat All grid-column:1/-1 rule causing a clipped third row.
  Actual isolated browser checks at 1440/1000px pass, including capture gear.
- Desktop two-row commands; mobile swipe row remains. No extraction
  or retreat mechanics changed. 15 backend tactical/411 frontend tests and build
  pass; manual browser review pending. Restart backend for new context entries
  when dev reload is disabled; browser refresh alone cannot update Python.
- Prior old-HP diagnosis: dev launch 21:07/reload off preceded 21:41 profile edits.
  Fresh creation verified all 12 revised layouts. Well fieldstone/Supply timber;
  Pickpockets outdoor/no buildings. Do not rewrite existing saved battles.
- Short class reference is complete at docs/design/CLASSES_AT_A_GLANCE.md.

## Parked: E-rank batch 2 - implemented, ready for player review

- Goblin Pickpockets, Movement at the Old Well, Small Supply Watch: four layouts
  each; lore/dressing/counts reviewed, recruitable Fighter/Rogue/Ranger/Snarer
  compositions, modest HP/ATK budgets. Geometry and starter Jobs retained.
- Normal all-layout Human/Fairy/Ogre simulations: 432 fights, 371 wins, no errors.
  Same-map bear seed 74: 36 fights, 34 wins, no errors. These test AI, not human
  balance; Engineer/Druid automatic choices need separate work.
- User clarified radiant bear is ALREADY in the same mission map, independent
  and hostile to both sides, potentially fighting local enemies on arrival.
  Implemented saved 3% roll, arrival notice, wounded skirmish where legal,
  optional base-objective exclusion, normal recovered loot, 5% Bear Claws/pelt.
- Validation: 38 focused backend tests, 411 frontend tests and build pass.
- Nine bear sounds (three attack/hurt/death) generated and integrated. One 5x4
  equipment sheet installed as 20 icons; no individual image generations.
  Sources/prompts retained; human listening/visual/play review pending.
- Canonical: [batch audit](design/E_RANK_COMBAT_AUDIT.md),
  [radiants](design/RADIANT_ENCOUNTERS.md), [art/audio](art/FIELD_GEAR_V1.md),
  [workflow](design/ENCOUNTER_AUDIT_WORKFLOW.md).
- Next audit: optional combat work sites, defense/prisoner-story maps; do not
  silently skip their distinct objectives. No prod/save changes.
- Broader tests exposed two stale capture fixtures; logged in backlog. No
  Capture mechanics changed to accommodate old tests.

## Parked: animal portraits and rat/wolf sound

- User requires the usual 5-column x 4-row sheets for future image batches.
  Ten previously queued individual portraits completed; reuse them. No image
  generation remains running. Originals/prompts preserved; runtime copies installed.
- 27 rat/wolf sounds generated and integrated. No prod/save changes.
- [Art/audio handoff](art/ANIMAL_CRITTERS_V1.md) records paths, code changes,
  verification and outstanding visual/listening/manual review. Do not regenerate.

## Parked: larger race-name pools

- Single-file prompt ready: docs/content/RACE_NAMES_GPT_BRIEF.md. Fresh GPT chat,
  seven batches of six races; user says Next between outputs.
- Return files race_names_001.json through race_names_007.json under
  docs/content/drafts/names/. Names-0.1 is an authoring format, not a live importer.
- Covers current gender rules, D&D-style/inspired and original alternatives,
  ordinary/leader names and contextual titles/epithets. Protected identities stay.
- Waiting for generated files. Next: review/validate, then integrate gender-aware,
  seeded name selection across recruitment and combat without renaming saves.
- Sources and limits: docs/content/RACE_NAMES_WORKFLOW.md. No runtime names changed.

## Parked: E-rank balance, first three missions

- Rats in the Storehouse, The Unwanted Toll, Wolves at the Fence.
- Four authored layouts each. Enemy profiles/behavior apply to all layouts;
  geometry/deployment tests cover all four. Earlier combat simulations sampled
  seeds and did not exercise every layout after the swarm/AI changes.
- Explicit all-layout simulations now complete: 432 runs, 377 wins, zero exceptions,
  all twelve Jobs across Human/Fairy/Ogre and all twelve mission/layout pairs.
  Fourteen location/profile tests pass. Results are in the audit reference.
- Latest implemented: per-layout compositions now vary rats/wolves between two
  and four bodies with adjusted stats, clusters/separated groups and two outdoor
  rats in the delivery-court layout. Toll keeps two humans, varying roles and
  formation to honor its description. User requires only modest difficulty variation.
- Repeated all-layout comparison: 432 fights, 377 wins, zero exceptions; 60 focused
  and integration tests pass. Earlier runs were fixed-count baselines. No existing
  saved battles are rewritten. Opening activity uses positions/props/History,
  not newly animated feeding/patrol behavior.
- Next step: manual playtest new compositions, especially toll 4 and wolf openings;
  separate AI/setup limits from difficulty before further stat changes.
  Engineer/Captor remain weaker in auto-play. Auto-play is not human balance proof.
- Source: [E-rank audit](design/E_RANK_COMBAT_AUDIT.md).
- Batch 2 is now implemented above; optional-combat and special-objective
  encounters remain to audit.

## Parked: character-life authoring process

- Two drafts: Strategist Fighter/Ranger caravan guard, Dutiful Engineer artisan.
- Revision 3 passed structural checks. Original submissions remain untouched.
- User delegated choices: nonfinancial guard trust test; reserve the particular
  cap-bearing story for one character per player. Ordinary traits are reusable.
- Still needed: concrete trust scene, final cap-repair rules, approved rewards
  and one implemented story slice. No stories/importer are live. No further
  GPT upload required from the user now; old brief requested the completed rev 3.
- [Short overview](content/CHARACTER_LIFE_OVERVIEW.md),
  [decisions](content/reviews/character_blueprints_pilot_001_design_decisions.md),
  [workflow](content/CHARACTER_LIFE_WORKFLOW.md),
  [content/status index](content/CHARACTER_STORY_CONTENT_INDEX.md).
- User wants one upload file, minimal administrative work, maintained readable
  summaries and consultation on consequential changes to established behavior.

## Continuity rules

Update this checkpoint when the user pivots: active objective, parked objective,
decisions, unresolved work and next concrete step. Put detailed facts in their
canonical document and link them here. Keep historical decisions; mark superseded
ones rather than treating omission as cancellation. Do not infer that a new topic
cancels a parked task or authorizes implementation of a proposal.
