# Current work and parked threads

October 9 Git checkpoint requested: publishing the accumulated dev source/docs
through lighting, door/animal behavior and mounted target marker, plus stack
brief. Git-only snapshot; no production deployment/restart or data changes.
Generated art/audio, databases and secrets remain excluded by existing Git rules.
Validation: 444 frontend tests pass; 69 targeted backend checks pass; build and browser checks recorded below.

October 9 stack handoff: verified installed languages/runtime packages, frontend
manifest, server/storage/auth, renderer, dev/release runners and asset workflows.
Copy-paste GPT context saved at docs/design/TECH_STACK_GPT_BRIEF.md and indexed;
no credentials included. Update alongside architecture/dependency changes.

Mounted boar marker follow-up: user requested another 15% size increase;
reticle now spans 147.2% of animal token (23.6% outset). Rider/boar art and hit
targets unchanged. Build passes; no restart/push.

Mounted boar target indicator: restored standard attack/throw reticle around
the wider animal footprint (14% outset, .72 opacity); rider retains portrait
marker. Corpses/support targeting excluded. No hitbox/gameplay changes. Actual
browser CSS checks pass for visible/outset/art match and corpse/support hiding.
Door animal AI and lighting rollout remain implemented; no restart/push.

Animal door rule supersedes previous wolf free-opening behavior: ordinary rat,
wolf, bear and boar profiles cannot operate doors. Blocked pursuit attacks a
destructible door with existing terrain damage/animation and ends the activation,
even on destruction. Next activation/open door resumes normal target pursuit;
no sticky door target. Humanoids/Druid forms retain free opening. Adjacent and
mid-movement breach tests cover four animal profiles, surviving/destroyed doors,
turn advancement and externally opened doors. 37 door/navigation/encounter tests
pass; no restart or push. General wall-breaking path planning remains outside
this door-specific change; existing terrain attacks retain normal action costs.

Enemy door follow-up: wolf/authored-bandit AI retained a stale return-on-open
branch from action-cost doors. Removed it; pursuit also approaches/opens a door
mid-turn and continues with only remaining terrain-adjusted movement. One-door
limit bounds continuation; hazards/control prevent continuing. Regression tests
exercise adjacent wolf, mid-turn approach/attack and zero remaining movement,
including turn advancement. 36 door/navigation/encounter tests pass. No restart
or push; lighting rollout/map/equipment work remains parked.

Active door movement fix: opening/closing remains free once per activation, but
commits approach cost instead of clearing the preview origin and refreshing its
budget. Direct interact and one-click navigate/open both deduct terrain-adjusted
movement, retain main action, permit zero remaining movement and restore allowance
next activation. Changes scoped to door commits; other skill commits unchanged.
23 door/navigation regression checks pass. Mount suite passes; broader approach
has an unrelated missing legacy zone-skill fixture, and two Druid purity assertions
fail because existing lighting initialization adds saved metadata to old fixtures.
These unrelated failures are not changed here. Lighting/map audits remain parked;
no dev restart/push. See COMBAT_CONTROLS.md.

Active lighting rollout/lab consolidation: reverted the single-cell pseudo-art
conversion below. It could anchor to the map for unpositioned terrain, causing
map-sized artwork (user's crater report). Restored original single-cell art;
single-cell palisades keep grading but no generated drop-shadow on HP labels,
and badge box shadows stay removed. Multi-cell art-only shadows remain intact.
Lighting is enabled on ordinary combat maps using saved arrival phase/time;
no extra full-phase cycling or combat modifiers introduced. Separate Lighting
Lab launcher removed; Battle Lab toolbar has Lighting controls. Overrides reset
when entering a normal map. 444 frontend tests, 10 backend timing/isolation
checks, build and browser checks pass; Warcamp screenshot reviewed. No dev
restart or deployment. See BATTLE_LAB.md and DAY_NIGHT_LIGHTING_PROPOSAL.md.

Warcamp stray shadow below wall HP: confirmed single-cell palisades still
filtered their labels (earlier fix covered multi-cell props only). Single-cell
painted terrain art now has its own pseudo-element; label box shadows removed.
Actual Warcamp browser checks confirm artwork preserved and HP excluded from
shadows. No map art or gameplay changes; no restart/push.

October 9 rotated-shadow/mounted follow-up: multi-cell rotated/mirrored art
counter-transforms sun offsets, correcting stray rotated cart/palisade shadows.
Removed extra palisade contact halo. Added directional shadows to living mounted
boar art only, not dismounted portrait tokens. Parting Cut skid preserves attack
facing. Roofed-room contact lighting retained; open-yard inward/outward cast
shadows are plausible, physical roof occlusion remains deferred. 444 frontend
tests, build and real-map lighting browser QA pass. No restart/push.

October 9 wall/cart stability follow-up: painted palisades no longer retain
rectangular fallback shadows/inset highlights. Multi-cell scenery filters apply
to artwork only, excluding HP labels from cast shadows. Shadow length now uses
the camera's final cell size; cloned views do not reset the lighting clock.
Actual Promise Proven open training yard reviewed: inward outdoor shadows are
appropriate; roofed rooms retain small stationary contact shadows. Browser QA
checks three redraws plus a lighting tick without shadow jumps, cart label
exclusion and palisade styling. All 444 frontend tests and build pass. No dev
restart or push. Native Safari/interior light authoring remain deferred.

October 9 prop shadows/cart follow-up: selected raised props get shorter directional
shadows; known roofed building room footprints use stationary contact shadows,
excluding separate yards and mixed/open compounds without authored roof regions.
Optional explicit indoor cells and rotated coverage supported. Prison wagon asset
inspected intact; removed legacy CSS rectangular inset shadow/border under sprite.
Real cart/room browser checks pass; no artwork regeneration, layout or combat changes.
Interior color/local lights still deferred. See DAY_NIGHT_LIGHTING_PROPOSAL.md.
Validation: 444 frontend tests, 12 targeted backend checks, build and browser
cart/interior shadow comparisons pass. QA browser/server closed; no dev restart/push.

October 9 lighting follow-up implemented: stronger evening blue via shared sprite
color matrix, including tree artwork beyond map bounds; subtle directional shadows
on trees/structure props (tester toggle). Battles save arrival phase/timestamp;
elapsed light drift includes time away but clamps within that arrival phase.
Fresh server clock samples survive cached Lab responses. Legacy missions anchor
to claimed_at. Lighting is visual-only, no map rebuild or combat changes. Tester
closing restores saved mission lighting; original-art comparison remains available.
See DAY_NIGHT_LIGHTING_PROPOSAL.md. Deferred: interiors/story-time audit, open-map
full cycles, native Safari profiling. Resource reward UI remains parked.
Validation: 443 frontend tests, 22 targeted backend checks (including lab database
isolation), build and real-map browser QA pass. No dev restart or push.

Earlier initial tester: dev-only Developer Tools consolidates Battle/Portrait/Wall Kit/
Lighting Labs. Lighting preview has draggable day/dusk/night/dawn controls, hour
scrubber, 30-second playback and bounded campfire glow on existing Battle Lab maps.
Closing restores original; ordinary missions unchanged. No map rebuild, world
clock or balance changes. Offline real-map fixture + browser QA, frontend build
and targeted backend checks. Radiant selector added: natural/off/force bear on
eligible pickpockets/well/supply maps, normal arrival popup, rejects unsupported
force requests, no save writes. See BATTLE_LAB.md and DAY_NIGHT_LIGHTING_PROPOSAL.md.
Pending: native Safari profiling, interiors/spell lighting, automatic cycle.
Validation: 440 frontend tests, 17 targeted backend tests, production build and
offline browser checks pass. QA server/browser closed. No dev runner restart or
push; restart dev and refresh to load new backend/steady-client files.
Resource reward UI remains parked.

Prior: day/night visual planning. User proposes 30-minute day/night phases.
Recommended hour-long server-synchronized cycle, gradual transitions, selective
map lighting with readable portraits/UI, localized warm light and mission-authored
overrides. World cycle not implemented. See DAY_NIGHT_LIGHTING_PROPOSAL.md.
Resource reward comparison remains parked/proposed; door changes completed.

Active October 9: door interaction free once per unit activation, preserving
movement/main action, same for enemies. Door controls/AI pursuit/flee routing updated;
28 targeted backend tests pass. Resource reward display remains PROPOSED: compact
four-outcome comparison in briefing, dynamic resource columns/ranges, mobile
stacked rows, real shared award calculations rather than hand-entered placeholders.
Awaiting user UI discussion; see MISSION_RESOURCE_REWARD_PREVIEW.md and COMBAT_CONTROLS.md.

Latest: boar attack/hurt/death vocals (three each) installed; no mounted attack
cry. Battle title/objectives/tools is foremost among HUD groups. Four groups
resize proportionally in Edit Layout, saved independently; original defaults
and existing positions preserved. Mobile layout remains separate. Browser checks,
440 frontend tests/build, nine WAV technical checks pass. No restart/push.
See COMBAT_CONTROLS.md and art/ANIMAL_CRITTERS_V1.md for rules/source paths.

Latest mounted presentation pass completed: zoom-scaled map buffs (22% cell,
36px cap), no stationary facing reset on unrelated redraws, mounted-only overhead
corpses below living units. Earthbreaker/Groundbreaker move surviving linked pairs
once; lethal separate routes and mount falls follow contact/displacement correctly.
65 backend / 438 frontend tests, real lethal Earthbreaker browser QA and build pass.
No restart/push. Fresh deaths needed to test mounted-vs-portrait corpse flag.
See docs/design/ANIMAL_MOUNTS.md for current rules and validation.

October 9 follow-up implemented: species-neutral Rider help, rider-owned Boar
Charge (1.25/1.5/1.75/2x by 1-4 cardinal cells; four-cell hit attempts Stun;
main action, 3-turn cooldown). Mount loss uses 25% hard / 50% rough / 25% safe,
with damage based on mount max HP. See ANIMAL_MOUNTS.md for details.

Updated October 9, 2026. Read this at session start and when the user pivots.
This is a concise checkpoint, not a substitute for system documents or backlog.

## Active: Boar-Rider animal mounts

Implemented separate boar HP, persistent Rider perk, innate Quick Mount/Dismount
(once/activation, no slot), +1 movement, 25% damage reduction for both bodies,
and once-only mount loss: 25% hard fall, 50% rough, 25% safe. Damage uses
50% / 25% mount max HP; hard adds Stun, rough adds Hobble (one turn). Independently
targetable; optional damage sharing remains unselected. First three patrol
layouts start mounted; fourth includes nearby mountable boars. One generated
5x4 overhead atlas with walking/death/icon slices; existing rider portrait above
saddle. Mounted boars skip their own activation and tick statuses with rider.
Death/release presentation follows contact. Targeted checks and 24 D-party fights
pass without stalls (20 wins). Browser fixture confirms loaded art and both hit
areas. See design/ANIMAL_MOUNTS.md and player-reference/RIDERS.md.
All433 frontend tests/build pass. Full1,132 backend run found an expected race
assertion for new mounts (updated) and11 unrelated failures reproduced with
all mount hooks disabled. Logged in ANIMAL_MOUNTS.md/backlog; targeted mount,
D-rank, Druid/Engineer and contract checks validate current behavior. No restart/push.
Animal capture/other mounts remain deferred. Prior threads remain parked.

## Completed: approved female combat voices and cleanup

- Latest preference: Human male attacks sometimes sound hurt/coughing, but user
  explicitly accepts them for now. No generation/replacement. Next voice-generation
  task must use approved female attack delivery as direction: strong proactive
  projected exertion, immediate onset, decisive short finish; adapt timbre to
  race/gender/personality. Audition small batch first. Recorded in SFX guide and
  ENEMY_VOCALS_V1.md; never copy female WAVs into male slots.

- Follow-up fix: final tester headings hardcoded "female" for every row after
  adding male clips. Corrected heading and now-playing gender from clip identity.
  Manifest/file/hash audit confirms all144 filenames match; all72 male/female
  pairs have different audio. Combat mapping was correct; no WAV/routing edits.
  Expanded browser QA verifies every rendered identity and male/female playback
  paths for Human/Goblin Survivor Death3. Earlier QA missed rendered gender labels.

- User approved final v6. Installed 48 revisions: all Human female attacks,
  all Goblin female attacks, Goblin female hurt/death. Final reviewed Guardian
  pain/death variants shared across female Goblin personalities; no unreviewed
  expansion. Death3 trailing breath removed, original voiced opening retained.
- Cleanup deletion blocked by automatic approval review (generic policy reason);
  safely moved obsolete files into staging-sfx/archive/superseded-files-20261009.
  Ten vocal tests, final144-clip browser tester QA and build pass. No push/restart.
- 96 other installed clips unchanged. Voice keys, volumes, event timing and
  character identities unchanged. One tester: assets/sfx/voice-tester/preview.html,
  all144 installed clips, race/gender/personality/event filters, saved ratings,
  feedback export. No further generation or API calls.
- Approved exact WAVs/MP3s/metadata: staging-sfx/enemy-vocals-approved.
  Offline restore tools/rebuild_enemy_vocals.py. Historical source/prompts/scripts
  archived in staging-sfx/archive/female-vocal-review-20261009.zip.
  Superseded public auditions/generation scripts/QA directories moved out of active folders.
- Tripline one continuous1?3 rope, atlas edge clipped, extra outline removed;
  isolated visual check completed. No gameplay changes.
- Parked: exact native-crash cause; growth/rebirth/race bases/weapon overhaul below.

## Completed: readable Unit Details and crash-log investigation

- User requests 1–2 plain-English sentences and actual formulas for each stat.
  Implemented shared numeric source formatting, short read-only descriptions,
  and a separate formula block in pinned tooltips. No combat calculation changes.
  Old saved `//` notation becomes readable division without changing values.
  Hover-following card stays noninteractive; pinned tooltip reuses unchanged content.
- Crash observed in dev-discord-latest.log October 9 at 11:13:34: exit 3221226505
  / 0xC0000409, followed by clean API shutdown at 11:13:37. No traceback, useful
  current Windows event or dump. A different runner-owned service failing first
  is plausible, not proven. Exact cause/module remains unresolved.
- Runner now logs service/PID at launch and unexpected exit, plus Windows hex
  status; no watcher/loading/restart policy changes, prod edits or auto restart.
- References: design/COMBAT_STATUS_PRESENTATION.md, design/SHARED_COMBAT_STATS.md,
  design/DEVELOPMENT_RUNNER.md. Growth/rebirth/race/item work remains parked below.
- Validation: 57 focused backend tests (inspection, shared stats, Druid, runner
  logging/profile isolation) and 33 frontend checks pass; browser build passes
  with its existing chunk warning. Crash cause is not claimed fixed. Restart dev
  and refresh to load the presentation/diagnostic changes; no restart performed.

## Completed: shared combat-stat migration implemented in dev

- Latest "Okay go" authorizes the selected shared ordinary-body 12 HP / 2 Attack
  migration. Implemented in `backend/combat_stats.py`, allied/equipment calculations,
  fresh ordinary NPC reconstruction and frontend roster/help. Rank multiplies raw
  attributes once; gear/proficiency/perk/battle-roll bonuses apply afterward.
- Fresh capture snapshots store unranked allocation + Adventurer Rank; JSON/recruit
  tests cover every audited humanoid layout and equivalent gear. Legacy recruits
  without rank keep their stored attributes at implicit E. Existing saved battles,
  production and database saves were not rewritten. No push/restart performed.
- Fresh contract/scenario enemies rebuilt together with players. Supply/worksite
  rounding targets preserve <=15% layout HP budgets. Boss reconstruction weights
  excess Armor more strongly, with an 80% HP-target floor; D Warcamp chief now
  64 HP / 12 Attack / 6 Armor. Prepared-party boss test now uses D rank on both
  sides and passes. C–S bosses still require manual balance review.
- Validation: 113 task-related backend tests pass, 32 frontend tests pass, browser
  build passes. 396-fight fresh E/D audit covers all exposed layouts of 14 E +
  three D missions with six damage-focused Jobs/two Human allies; see report for
  outcomes and limits. No errors/stalls. Support Jobs, other races and manual
  playtests are not represented. Rank/gear/legacy parity checked independently.
- Broad suite attempted: 1119 tests. Initial 11 failures/6 errors included stale
  expectations and reconstruction regressions corrected by the focused pass.
  Remaining 5 failures/6 errors reproduced under pre-change 24/5 formulas with
  NPC reconstruction disabled: concealment/ambush bookkeeping, legacy ground-
  technique/capture fixtures, mocked capture random values and old recovery-time
  expectation. Do not claim the entire repository suite is green.
- Current reference: design/SHARED_COMBAT_STATS.md; short user checkpoint:
  player-reference/CHARACTER_GROWTH_NEXT_STEPS.md. Historical comparison and paired
  trial evidence retained; trial tool refuses to overwrite it from migrated runtime.
- Next user test: restart dev runner, refresh and create a new battle. Do not
  restart unasked. Old saved fights retain old bodies.
- Still deferred: player rank promotion, Growth Grade assignment/UI, rebirth,
  below-E catch-up, growth reward/cost curve, paid respec, item requirements/rework.
  Race-specific innate HP/base Attack request preserved for later race audit;
  no racial rework in this pass. Guild access is not personal rank promotion.

## Historical growth investigation (superseded implementation status)

The notes below preserve accepted/deferred decisions and pre-migration evidence;
SHARED_COMBAT_STATS.md is authoritative for current formulas.


- Deferred race request: some races may have higher innate HP and/or base
  Attack. Shared 12/2 is a neutral baseline, not an identical racial profile.
  Exact bonuses/stacking deferred to the race audit. Canonical note:
  design/CHARACTER_GROWTH_PROPOSAL.md, "Deferred race pass". No racial changes now;
  preserve player/enemy/recruit parity and avoid double-counting existing modifiers.
- Documentation consolidation suggested for a later housekeeping pass: keep
  current decisions in canonical system docs, short summaries in player-reference,
  and dated alternatives/results as history/evidence. Preserve links and decisions;
  don't delete trial evidence or turn proposals into implemented claims.

- Latest user delegates choosing the best fixed bases. Selected shared 12 HP /
  2 Attack bases, with 4× effective VIT and floor(scaling attribute/2), plus
  racial/perk/gear/training contributions as applicable. Attribute rank once;
  flat bases/weapon power not ranked. This supersedes candidate/unapproved-base
  notes below. Decision recorded at top of CHARACTER_GROWTH_PROPOSAL.md and
  user summary. No runtime/save changes. Zero-base sensitivity checked (Human
  all-6 E: 24 HP/3 Attack vs selected 36/5); no zero-base combat claims.
  Next: coherent shared-formula migration, enemy body/gear/role reconstruction,
  stat explanations and wider/manual validation; never change only player bases.

- User approved the small isolated combat trial; completed with
  tools/trial_character_growth.py. Results: design/CHARACTER_GROWTH_TRIAL.md/CSV.
  216 fights across Toll/Highway/Bone, four layouts each, six starter Jobs,
  two Human allies, three paired arms. Zero errors/stalls; eight focused tests.
  Current: 69/72 wins, 7.0 mean rounds; shared 24/5: 56/72, 8.4 rounds;
  shared 12/2: 64/72, 8.7 rounds. Lower bases are the recommended reconstruction
  candidate, not approved/applied runtime values. All eight lower-base losses
  are Ranger auto-play; no Job retuning justified from this sample alone.
  Next: coherent enemy allocations/gear/role armor, wider-race/manual review.
  Shared arms grant proposed personal D rank; live players lack it. Flat gear/
  perk bonuses stay unscaled. No save, runtime, restart or production changes.

- Latest "Proceed" handled as the proposed concrete before/after comparison.
  Added tools/compare_character_growth.py and design/CHARACTER_GROWTH_COMPARISON.md:
  13 live-preview E/D profiles and 24 S-stage build probes. No runtime/save changes.
  Four accounting tests pass: one rank application, creator-cost parity, cost
  thresholds, monotonic build allocation and pre-rank D baseline extraction.
  Short user reference: player-reference/CHARACTER_GROWTH_NEXT_STEPS.md.
  Current formulas strengthen light enemies; a lower shared-base experiment
  weakens players. The isolated combat trial is now complete above; final bases
  still need reconstruction and wider review. Neither alternative approved/applied.
  The earlier body probes themselves make no win-rate claims.

- User explicitly requests discussion first; no gameplay/UI implementation.
  Preserve existing E/D encounter HP/attack. Proposal distinguishes personal
  Adventurer Rank, Growth Grade allocation budget and Job. See
  design/CHARACTER_GROWTH_PROPOSAL.md for verified formulas, examples and options.
- Critical finding: authored enemies do not derive HP/attack through player
  formulas. Recruitment recomputes allied stats; low enemy HP does not equal
  a proportionally weak recruit. D snapshots already contain ranked attributes;
  use recorded pre-rank baselines to avoid double-counting body potential.
- Creator allowance: six 4s plus 12 points = 36, linear +1 cost, UI minimum 1 /
  maximum 10. Growth 61 would exceed current 60 capacity; no nonlinear cost exists.
- User confirms below-E catch-up and preserving Adventurer Rank during rebirth.
  Growth Grade is the advancement stage completed. Enemy reconstruction should
  keep overall stats/encounter strength approximately comparable using coherent
  rank, growth, allocation, race/perks/gear; exact old HP/attack is not required.
  Tentatively favors random +4–6 gains, no lifetime-gain tally, and attribute-first
  scaling, but is open to output scaling. See proposal follow-up for tradeoffs.
  Explore costs 1 through base stat 10 / 2 through 15 / 3 above, not implemented.
  Guild advancement currently unlocks missions by building/upgrading Guild Hall,
  spending resources; no personal stat rank bonuses or promotion trials exist.
- Park future equipment audit: class compatibility, stat recommendations and
  build-defining weapon-hit effects including skills. Existing proc coverage is
  uneven and multi-hit generic procs can be limited; preserve cross-Job capture
  equipment. No new ranks, items, migrations, reset mechanics or UI implemented.
  Confirmed: preserve cross-Job capture; bows/shields/specific skills need compatible
  gear; item labels distinguish Requires, Scales with and Recommended for.
- D playtest/next batch and all previously parked threads remain pending below.

## Previous: first D-rank audit batch

- User requests E-relative 1.0/1.3/1.6/1.9/2.2/2.5 combat-stat scaling, plus
  three D missions with four different variations each. Implemented rank policy
  for generic contracts and authored D roles; preserves role movement/range,
  percentages and cooldowns. Existing saves/bespoke bosses not migrated.
- Highway Ambush, Bone Patrol and Boar-Rider Patrol: twelve layouts with role
  kits, 3/4-body variations, current building materials and a new two-door timber
  relay office. Undead armor/control identity; mounted Goblin movement; capture
  retains normal Job starters and specialty kits. Patrol ambush text corrected.
- See design/D_RANK_COMBAT_AUDIT.md. Map/rank/recruit checks and regression checks
  pass (90 final focused tests plus 24 map/location checks); final martial sample:
  48 completed fights, 46 wins / 2 losses, no errors
  or stalls. B Redoubt uses the veteran role baseline to remain above D Warcamp.
  Manual playtest remains. Start new battles after restarting
  the dev runner to load backend edits. No production changes or restart performed.
- Next: player review of these three, then another D batch. Defense visual review,
  personality expansion, story authoring and other parked threads remain below.

## Previous: final E-rank maps implemented; personality expansion review

- Latest user pivot: rebuild defense preparation, now implemented for fresh maps.
  Equipped skills only (confirmed). Hedgerow base 12 + 4 per defender; 1-point
  barriers uncapped; pit 2 points, 25% max HP fall and action-based Climb Out
  (confirmed). Proximity bomb 3 points / 2 with an Engineer. Engineer deployments
  free with shared turret limits and one mine; Rogue Caltrops free and rotatable.
  Existing Job effects reused; no new generic trap framework. Legacy battles retain
  old rules. See design/DEFENSE_PREPARATION.md. Validation: 232 backend and 427
  frontend checks plus build pass; 81 focused checks pass after the Caltrops
  eligibility fix. Four prepared Engineer/Fighter smoke fights complete without
  errors/stalls across all layouts. These are smoke checks, not support-class tuning.
  Manual visual review open. Personality proposal below remains parked for review.

- Implemented the last two missions in the 14-mission combat-audit scope:
  Hedgerow Watch (four defense layouts) and Bring the Captive Home (four E-rank
  rescue layouts). Recruitable Goblin kits/voices, legal placement, carry/extraction,
  a visible warning post, no D-cart dispatch rewards in the E rescue. Battle Lab
  exposes each layout. D-cart and higher rescue tiers retained.
- Validation: 194 relevant backend checks pass. Small sample of 32 martial fights
  (solo rescue, paired defense): 31 wins/one loss, zero exceptions/stalls. User
  says not to spend extensive manual effort balancing naturally weaker supports.
  Manual visual/difficulty review remains; auto results are not universal balance.
- Personality audit found only 12 ordinary runtime IDs, no Tsundere/Kuudere.
  Proposed 16 additional profiles for 28 total in player-reference/PERSONALITY_AUDIT.md.
  They are proposals, not runtime changes; existing identities preserved. Separate
  social expression from shared tactical policies. Only four current profiles
  have voice packs; no new generation or authoring-contract changes this turn.
- Next: user's map playtest and personality proposal review; then integrate agreed
  profiles and refresh authoring catalog/brief. No prod push or server restart.

## Previous completed: wordless enemy vocal packs; listening review

- User accepts Goblin quality as sufficient and asks for bandit samples. Bandits
  already use the installed Human packs (72 clips, four personalities × genders).
  Assembled male/female Opportunist attack/hurt/death audition MP3s from existing
  WAVs; no paid regeneration or runtime change. Generator --audition KEY reuses
  clips without needing an API key. Samples are in staging-sfx/enemy-vocals-v1.
- Previously remaining: Hold the Hedgerow Watch and Bring the Captive Home;
  both are now implemented as recorded above. Twelve earlier audited missions
  remain implemented. Manual player review is open, but exhaustive solo-support
  tuning is deprioritized by the user. Noncombat E-rank quests are separate scope.

- User approved the wordless SFX direction and full variations. Installed 144
  Human/Goblin vocals: male/female × Guardian/Strategist/Opportunist/Survivor,
  three attack/hurt/death samples each. Female Goblin has a lighter feminine
  register with a little rasp; original approved female demos retained as fallback.
  Approved male baseline is reused for Guardian variant 1. Exact speaker identity
  is not guaranteed by SFX generation; in-game listening review remains.
- Packs opt in only on audited humanoid encounter units and their captured
  recruits. Voice keys persist in recruit snapshots/battle entry; saved audited
  enemies derive a frontend fallback without identity rerolls. Event timing keeps
  weapon sounds, prevents early death vocals and limits rapid multi-hit overlap.
  Only battle-relevant packs decode in background; map loading never waits on them.
  See art/ENEMY_VOCALS_V1.md and player-reference/VOICE_PROGRESS.md.
  Validation: 25 relevant backend checks, all 424 frontend tests and build pass;
  all 144 exported clips have zero final clipping and peaks at/below -3dBFS.

- User configured ELEVENLABS_VOICES_KEY. Generated male/female Goblin Voice
  Design demos, three automatically returned alternatives per gender; originals,
  prompts and generated preview IDs retained in staging-sfx/goblin-voice-demo-v1.
  Inline primary audio previews delivered; standalone preview.html auditions all six.
- Earlier spoken Voice Design demos are superseded and retained in staging.
  No account voice IDs created; the final clips use the SFX API key. Originals,
  prompts, metrics and feminine comparison MP3 are in staging-sfx/enemy-vocals-v1.
  Runtime audio: frontend/public/assets/sfx/enemy-vocals-v1, with preview.html.
  No production push or process restart. Backend reload is needed for new saved
  voice metadata; existing audited battles have the frontend identity fallback.
- Parting Cut now uses one continuous approach/contact/backward skid when legal;
  counters/displacement retain ordered reactions. Physical dust/scuff replaces the
  cyan retreat art, slash/skid SFX starts at contact, no duplicate walking footsteps.
  Damage, cooldown and retreat legality unchanged. Eleven backend and 27 focused
  frontend checks plus build pass; full frontend suite also passes (415 tests).
  Visual feel still needs player review.
- Parked: single spanning Tripline artwork proposal and dedicated enemy Perks
  section proposal; neither implemented in this pass. General quirks/manual balance
  review remains below. Production untouched; no push or server restart.

## General quirks implemented in dev; manual balance review next

- October 9: implemented 61 generic personal quirks, alongside the 16 selected
  backgrounds. See player-reference/GENERAL_PERKS.md for the readable catalog.
  New rolls/rewards reject opposing pairs and multiple redistribution profiles;
  one HP tier. Existing saves/traits are not rerolled or moved out of active folders.
- Naturally Gifted adds +1 to all six attributes; one-in-a-million opening roll,
  independent of redistribution and luck groups per user correction; it can
  coexist with those traits, but never duplicate itself. Rare/exceptional traits remain eligible at level 1
  and E-rank. Ordinary NPC perkless outcomes remain about 20%; new procedural
  recruits can receive no additional generic quirk. HP/VIT profiles are rarer
  on combat NPCs to preserve ordinary map budgets.
- Implemented per-battle random attribute overlays, damage-only Burn/Poison/Bleed
  resistance, strongest-only status resistance, Ranger bow/crossbow range,
  unarmed per-action budget and positive-reward mission gold. Random stat choices
  are saved on battle units and never change permanent character attributes.
- No production changes, push, server restart or existing-character migration.
  Backend restart is required for fresh encounters when automatic reload is off.
- Validation: 352 backend checks passed (185 perk/encounter/mission tests plus
  167 Monk/Ranger/Mage/Druid/ability/mercenary regressions). Generated reference
  --check and git diff --check pass. Frontend files did not change in this pass.

- User rejected flat Survival/Scavenging/Medicine/Combat Capability perks and
  requested multiple stronger alternatives. Selected origin perks are implemented;
  unselected background alternatives and extra event-based quirk ideas remain proposals.
- Latest naming preference: professions/personal quirks, not activated-skill names.
  Added selected origin rules: separate lumber/quarry/salvage +1 matching-workplace
  production perks (usually one, very rarely two/all three); herb origin ignores
  first incoming Poison stack once per battle; timber origin Fast Builder adds one
  defense deployment allotment. Hourly production and preparation-point meanings
  are implemented interpretations. Profession names and initial rarity rates are
  recorded in player-reference/RECRUIT_PERKS.md; tune with user feedback.
- User selected defeat-created Tripwire, Make an Example, Play Dead, Ricochet,
  one first-ally extra attack per battle, Last One Standing (never solo), and
  Broken Escape. Selected effects are implemented under profession/quirk names.
  Current rules are in RECRUIT_PERKS.md; the options document retains prior names;
  do not substitute the older accuracy-only Follow My Lead for the extra attack.
- Read player-reference/RECRUIT_PERK_OPTIONS.md for 41 alternatives, separated
  by enemy background and worksite origin. Unselected options require review.
- Custom skills/background perks, rank recovery and prisoner encounters are now
  implemented and validated in dev; uncommitted and unpublished. Preserve dirty
  changes. 169 backend checks pass; 432 prisoner cases give 385 wins/zero errors,
  312 older-map Human regressions give 261 wins/zero errors. Twelve prisoner
  layouts pass access checks after opening usable doors. Manual balance review
  remains for support/setup Jobs; two E-rank audits remain (defense/rescue).
- New eight-icon/twelve-effect atlas and nine physical SFX are installed. See
  docs/player-reference/README.md for short references; bespoke humanoid voices
  remain planned. No dev restart or production modification in this pass.
- Accepted recovery: E 1 minute, D 5, C 10, B 30, A 60, S 120.
- Tag Team damage buff applies only to the user; crossed enemies can be Stunned.
  Heel Cut lasts through the target's next activation: each newly reached distance
  adds a Bleed stack and extra tick; backtracking does not repay that distance.
- New perk ideas add no canonical story tags or quest IDs. Character-history
  integration remains a proposal. Production untouched during this discussion.

## Complete: E-rank worksite batch 3

- Timber Across the Creek (two layouts), The Locked Tool Shed and Herbs Behind
  the Wall (four each): all ten reviewed, with authored Goblin specializations.
- Optional peaceful routes/handover/rewards preserved; current timber/limestone
  structures retained. New battles only; production unchanged.
- Opposition totals 48–52 HP / 8–9 ATK; two ordinary or three lighter enemies.
  Recruitment preserves real skills/personality; existing scoped humanoid AI.
- 360 Human/Fairy/Ogre starter-loadout simulations: 313 wins, zero exceptions.
  135 mission/encounter/location/recruitment tests passed.
  Long tool store is hardest; Engineer auto-play remains weak. Manual balance
  acceptance pending. See E_RANK_COMBAT_AUDIT.md for all layouts and caveats.
- Next E-rank batch: Hedgerow Watch and prisoner-linked encounters; retain
  distinct defense/rescue/story objectives rather than convert to simple clears.
- Backend restart required with reload off; existing battles retain snapshots.

## Complete: five-minute dev mission refresh

- Interpreted reset timer as mission-board refresh in the ongoing dev context.
- Dev profiles refresh every 300 seconds; release/standalone retain 1800 seconds.
- Backend expiry/slot and API countdown use the same settings-derived duration.
- 18 onboarding/profile tests pass. Restart dev backend to activate; production
  untouched. Existing claimed missions and character saves are not reset.

## Complete: race-name import in dev

- User authorized consuming seven submitted name files for dev only.
- All 42 races accepted; 5,840 ordinary / 1,008 leader given names and 1,680
  second components. 504 titles/504 epithets stored behind explicit context gates.
- New recruitment and humanoid encounters use race/gender-compatible pools;
  existing identities, animals and seeded stat/loot sequences are preserved.
- Compiled tracked bundle: backend/name_pools/race_names.json; importer/check:
  tools/import_race_names.py. Original drafts preserved; hashes/report retained.
- 58 focused + 135 mission/capture/recruitment backend tests pass, including
  eight new tests covering all race/gender/tier combinations. No frontend changes.
- Production untouched. Restart dev backend when reload is off to see new names
  on newly generated people/battles. No current saved characters are renamed.
- Reference: docs/content/RACE_NAMES_WORKFLOW.md. Story packs remain proposals.

## Complete: dev and production publication

- User authorized pushing current dev and production; preserve production saves.
- Production port 5173 is stopped. Release builder retains credentials, backs up
  SQLite and uses release flags; QA tools/tests/drafts excluded.
- Name uploads remain drafts, not installed runtime content.
- Published main and release code commit 84c2bfd, production version
  0.3.1-prod.20261008.221602. Production prepared but left stopped.
- 71 focused + 370 Job/profile + 178 navigation/mission backend test runs and
  411 frontend tests passed. Isolated release startup/API smoke passed; debug
  labs and force-refresh return 404 even for an admin.
- Verified all 1,517 runtime assets match dev, production credentials unchanged,
  database logical contents equal pre-update backup.
- Backup: fortcamp-release-data/backups/before-prod-update-20261008-221605-014751.db.
  Prior checkout: fortcamp-backups/prod-20261008-221605-014751.
- Validation/publication results recorded in RELEASE_PREPARATION.md.

## Complete: starting race eligibility - included in release

- Previous creator/API allowed 41 races, including Secret Werewolf.
- Approved 14 starting choices enforced by creator and API; full 42-race
  content catalogue and existing saves retained. Five onboarding tests, creator
  test and frontend build pass. Included in October 8 release; restart dev backend
  when reload is off. See design/STARTING_RACE_AUDIT.md.
- User supplied seven race_names JSON files in content/drafts/names;
  subsequent dev import is complete, originals preserved (see checkpoint above).
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

## Complete: larger race-name pools

- All seven uploads validated and compiled for dev; details in active checkpoint.
- Naming brief still covers all 42 races, not only the 14 starting choices.
- Source limitations remain author metadata; no new cultures/quests inferred.
- Production still uses preceding pools until another release is authorized.

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

Mount layering follow-up: generic walking/attack/hit styles gave both bodies
the same raised layer, letting the later DOM boar cover the portrait. Explicit
ordered layers now keep rider above mount during idle, hover and every motion.
Browser playback checks both aligned centers and rider-above-boar layers.
Facing/crop update passes all 437 frontend tests and browser checks; build passes.

Overhead-pose correction: rotate the top-left north-facing overhead boar, not
the side-biased east pose. Isolate its full silhouette with corrected crop
bounds (remove neighboring artifact). Keep existing 96%-cell mount container
and 75% rider; no extra shrink requested. No walking sprites. Death sprite
uses a -90-degree basis correction to share the overhead facing convention.

Boar scale correction: tightening source crops removed transparent padding and
made the animal appear larger. Render its artwork at 80% of the mount container
(10% inset per side), for both living and dead poses; keep rider at 75% standard
size. Hit targets, paired motion, facing and combat mechanics are unchanged.

Boar head/rear clipping root cause: generic `.battle-token img` used cover and
overrode the earlier mount contain rule at equal specificity. Mount image now
uses an explicit scoped `object-fit: contain !important`; size remains unchanged.
Browser fixture loads generic character CSS after mount CSS to reproduce actual
cascade, checking computed contain/no clipping as well as motion/layering.

Final containment/proportion correction: remove the temporary 10%-per-side
art inset now that cover clipping is fixed. Full contained overhead silhouette
uses the original 96%-cell footprint, extending beyond the 75% rider frame.
Keep explicit contain, clean crop, shared motion and ordered layers.

Mounted readability: target reticle stays within the rider frame instead of
covering the animal outline; animal art sits 12% lower beneath the portrait.
This constant art offset does not alter paired token motion or unit coordinates.

Current mounted presentation: boar artwork is centered again (remove downward
offset) and 25% larger than its previous contained image, behind the unchanged
75% rider. Attack facing now persists on the actual mount, so redraws after an
unrelated player action do not revert it to a prior walking direction. Forced
displacement preserves facing. Own walking/attacks still deliberately turn it.
No walking sprites or combat balance changes.
