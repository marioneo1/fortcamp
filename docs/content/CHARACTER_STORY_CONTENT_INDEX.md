# Character story content index

Canonical entry point for proposed character voices, personal histories and
one-off story content. Updated October 8, 2026. **Planning only**; no
character-story packs below are active. Race-name content is separately implemented
in dev and does not implement the proposed personal-story system.

## References and ownership

October 9 Boar-Rider follow-up adds persistent perk ID `rider` and innate action
IDs `innate:rider:mount` and rider-owned `innate:rider:boar_charge`; registered in backend/recruit_perks.py and
backend/combat_mounts.py. Captured patrol recruits retain the perk and ordinary
Job starters. No history/dialogue/story/race/quest IDs or repeat scopes changed.
Animal capture remains deferred; see ../design/ANIMAL_MOUNTS.md.

First D-rank batch: Highway Ambush, Bone Patrol and Boar-Rider Patrol retain
their mission IDs/rewards/repeat scope and receive four tactical variations each.
New patrol role labels reuse existing Jobs, skill and personality IDs; no new
hidden histories, dialogue events or personal quest triggers. Recruitment keeps
specialties and normal Job starters. Scouting describes an unaware patrol instead
of a sleeping camp. See ../design/D_RANK_COMBAT_AUDIT.md. The authoring catalog
has no new IDs to register; the proposed character-life system remains separate.

Defense preparation v2 changes Hedgerow's preparation budget/options and reuses
existing Engineer/Rogue skills and pit escape. It adds no Job, personality,
history fact, story trigger or reward ID; allegiance and one-off completion scope
are unchanged. See ../design/DEFENSE_PREPARATION.md for implemented rules.

October 9 personality review: [short audit](../player-reference/PERSONALITY_AUDIT.md)
confirms 12 implemented IDs and proposes 16 additions, including Tsundere,
Kuudere and Dandere. Proposed IDs are not eligible for import/runtime yet; the
existing authoring contract and generated GPT brief still use the current catalog.
No story eligibility, one-off repeat scope, completion history or existing
character identity is changed. Approval, runtime integration and then catalog/brief
regeneration are separate future work; no new voice generation is implied.

Final E-rank combat batch: Hedgerow Watch receives four authored raid layouts;
Bring the Captive Home has four dedicated E-rank escort layouts instead of the
D-cart roster. Mission IDs, allegiance/recruitment promises and completion scope
are retained. New role labels reuse existing Jobs/skill IDs and personality IDs;
no hidden histories, dialogue events or personal-story rewards were added.

October 9 combat implementation: the eight new enemy specialties and approved
background perks are active for newly generated audited dev encounters; see
[enemy kits](../player-reference/ENEMY_SPECIALTIES.md) and
[recruit perks](../player-reference/RECRUIT_PERKS.md). They use existing Jobs,
personalities and mission origins, without adding hidden histories or dialogue
triggers. The newly requested broad generic perk pool remains a proposal.

Recruit background perk design: [selected effects and profession/quirk names](../player-reference/RECRUIT_PERK_OPTIONS.md).
Selected combat and workplace effects are implemented in dev; unselected options
remain proposals. No new history tags or story rewards are introduced by this work.

Implemented starting-race eligibility: [audit](../design/STARTING_RACE_AUDIT.md).
All 42 race IDs remain in authoring/name pools; no tags or acquisition rules
changed. Seven submitted race-name files are validated and integrated in dev;
see the workflow and import report. All originals remain preserved.

E-rank worksite batch 3 adds recruitable Goblin Salvage Guard, Tool Snatcher,
Goblin Forager, Worksite Pilferer/Lookout, Sling Scavenger and Garden/Worksite
Snarer specializations using existing Fighter/Rogue/Ranger skill IDs. These
are combat loadouts, not new Jobs, personality IDs or hidden-history facts.
Peaceful mission routes remain available; no personal-story triggers or repeat
scopes change. See the classes reference and E-rank audit for current kits.

| Reference | Purpose |
| --- | --- |
| [Design proposal](../design/CHARACTER_STORIES_PROPOSAL.md) | Rules, integration points, pacing, novelty, persistence, stages |
| [Short character overview](CHARACTER_LIFE_OVERVIEW.md) | Readable personalities, eligibility, backgrounds, stories and reward directions; keep current |
| [Race names brief](RACE_NAMES_GPT_BRIEF.md) / [workflow](RACE_NAMES_WORKFLOW.md) | Seven-batch request for all 42 races; names-0.1 compiled into dev runtime pools; production unchanged |
| [GPT authoring prompt](CHARACTER_STORY_AUTHORING_PROMPT.md) | Reusable writing instructions and batch requests |
| [Single-file GPT brief](CHARACTER_LIFE_GPT_BRIEF.md) | Upload-ready instructions, two-blueprint pilot and current contract |
| [Authoring workflow](CHARACTER_LIFE_WORKFLOW.md) | One upload, preserved submissions, structural checks, review and approval gates |
| [Current GPT task](CHARACTER_LIFE_CURRENT_REQUEST.md) | Requests pilot revision 3; packaged with revision 2 and its review |
| [Draft v0.2 contract](character-story-contract-v0.2.json) | Current IDs, proposed tags/events, character blueprints and output format |
| [Historical v0.1 contract](character-story-contract-v0.1.json) | Preserved for earlier draft packs; use v0.2 for new work |
| `backend/races.py` | Authoritative race IDs, families and generation restrictions |
| `backend/relationships.py` | Authoritative personalities, existing tastes, memories and conversation behavior |
| `backend/job_loadouts.py` | Authoritative Job IDs and executable skill definitions |
| [Prison recruitment](../design/PRISON_RECRUITMENT.md) | Existing personal agreements, rival/former-command quests and allegiance history |

The contract mirrors IDs for external writers; it does not replace canonical
gameplay catalogues. Proposed traits and predicates do not establish new race
lore or imply runtime support. Existing prisoner rival quests remain their
current system; this proposal must integrate with them deliberately rather than
silently counting or overwriting them as the new personal-rival story.

Mission-context note, October 8: starter rat/wolf counts now vary by layout
(two to four); toll retains the two humans promised by its description. No story
IDs, racial tags or new Jobs were introduced. Dialogue must use observed/bound
context rather than assuming every layout has three animals. See the E-rank audit.

## Pack manifest

| Pack / family | State | Expected output | Repeat policy |
| --- | --- | --- | --- |
| `race_names_001` through `race_names_007` | Prompt ready; files not received/approved/live | Six races per file in drafts/names; gendered/shared given names, second-name components, leader pools and contextual titles/epithets | Reusable pools; preserve existing identities; unique full-name selection requires runtime integration |
| `character_blueprints_pilot_001` | Generated; reviewed, revisions required; not approved/live | [Original GPT draft](drafts/character_blueprints_pilot_001.json), [review](reviews/character_blueprints_pilot_001.md), [focused revision prompt](reviews/character_blueprints_pilot_001_revision_prompt.md) | Source has character-scoped arcs; review recommends player-scoped pilot one-offs; choice not implemented |
| `character_blueprints_pilot_001`, revision 2 | Reviewed; targeted corrections and user story decisions required; not approved/live | [Revision 2 submission](drafts/character_blueprints_pilot_001_revision_2.json), [revision 2 review](reviews/character_blueprints_pilot_001_revision_2.md) | Proposes player-scoped major arcs with preserved keys; character-specific cap allocation remains unresolved |
| `character_blueprints_pilot_001`, revision 3 | Structural checks passed; direction decisions delegated and recorded; concrete trust scene and integration pending; not approved/live | [Revision 3 submission](drafts/character_blueprints_pilot_001_revision_3.json), [review](reviews/character_blueprints_pilot_001_revision_3.md), [decisions](reviews/character_blueprints_pilot_001_design_decisions.md) | One character receives this player-scoped guard story; ordinary traits remain reusable; planned only |
| `character_blueprints_002` | After pilot review | Four additional coherent blueprints | Same budgets; explicit one-off keys |
| `character_path_voices_001` | After blueprint and predicate approval | 40 dialogue alternatives for exact saved stages | Stage/family repetition rules; no new story facts |
| `voice_pilot_001` | Prompt ready; not generated/approved | 12 dialogue entries | Cooldown/novelty controlled, no rewards |
| `voices_002` | Proposed after pilot approval | 48 dialogue entries | Cooldown/novelty controlled, no rewards |
| `old_rival` / `rival_outlines_001` | Four outlines requested by reusable prompt; not generated/approved | Prose variants for one vertical-slice story | Proposed once per player across first-story variants; same-instance retry/defer only |

Add generated batches with file path, schema version, approved ID range,
supported contexts, review status and required runtime capabilities. Do not mark
generated as approved, or approved as implemented. Track retired IDs explicitly.

Keep untouched generated submissions in `drafts/`, their assessments and revision
requests in `reviews/`. Keep prompts/contracts at this directory's root. Approved
content can gain its own versioned location when approval/import tooling exists;
do not move draft stories into runtime assets just because their JSON is valid.
Pilot 001's original file was moved from this root with matching SHA-256 before
and after; its content was not rewritten. Revised submissions should be separate
files, retaining batch/entry IDs and an explicit revision number.

## Mandatory update checklist for future work

When adding a race, personality, Job, quest, history fact, dialogue event or new
capability used by character content:

1. Update its actual canonical system first. Review existing content for changed
   assumptions; new race-family membership is not proof of biology or beliefs.
2. Refresh relevant existing IDs in the authoring contract, update snapshot date
   and its version when semantics change. Update the GPT prompt if writing rules
   or valid fields change. Rebuild the single-file brief with
   `python tools/build_character_life_brief.py` and run its `--check` mode to
   catch catalogue/bundle drift. Retain compatibility for reviewed old packs.
3. Record new tags/events/templates here with status, eligibility and dependencies.
   Unsupported proposals remain outside the allowed runtime catalogue.
4. For each story, record a stable repeat key, scope (`player` or `character`),
   offer limit, retry/defer policy, trigger conditions, target-binding rules,
   outcome attribution, reward references and retirement behavior. A renamed
   variant of the same one-off shares the original repeat key.
5. Check mutual exclusions and known facts. Dialogue must not claim a new quest
   already happened merely because its content was installed.
6. When implemented, add behavior checks for save/load, duplicate events,
   completed one-off exclusion, absent/hidden targets and one-time rewards.
7. Update the design reference/backlog/history with implemented versus deferred
   status. Gameplay capability changes also update COMBAT_CAPABILITY_REFERENCE.

For mission-specific one-offs, scope the trigger to that mission/story context;
do not leak its recognition lines into generic encounters. If once-per-player,
no other character may start a fresh instance after it is offered/completed,
according to its explicit offer policy. A deferred existing instance can remain
in the journal; this is not a new randomized offer. Keep completion/tombstone
records after clearing active flags. Never reset them on refresh, content pack
updates, recruitment, character dismissal or ordinary quest expiry.

Account/save-wide means one player's persistent world, not global completion
shared by all players. Special seasonal resets, save wipes or new campaigns
would require an explicit separate policy; do not infer them from elapsed time.

## v0.2 character-path refinement

Conversations can reveal fixed latent facts, develop open facets and arm saved
mission opportunities. Individual prospective loyalty caps must be disclosed
early, before recruitment/investment; existing prisoner resistance is distinct.
Personality/bond changes need cause and scope. Devotion can be platonic; optional
romance follows the user's male/female pairing direction without blocking
nonromantic core development. Concluded core arcs stop generating major new
personal conflicts while ordinary memories, bonds and progression continue.

Every blueprint needs reward promises, narrative payoff, actual proposed grant,
aftercare/recovery and remembered outcomes. A story is not approved solely because
its JSON parses. Mechanics, loyalty ceilings, permanent perks and new skills
remain unimplemented proposals requiring gameplay review.


## Implemented ordinary radiant event ? October 8

`radiant:foraging_bear`: repeatable per eligible mission entry, one saved 3% roll
per battle; same-map third-party wildlife in Pickpockets/Old Well/Supply Watch.
An existing skirmish may be authored at arrival. No character-history tags,
personal-chain eligibility, new dialogue templates or once-per-player flags.
Runtime contract: [Radiant encounters](../design/RADIANT_ENCOUNTERS.md).
This does not implement the proposed character-life story system above.

## Implemented generic quirk catalogue ? October 9
Runtime IDs and modifiers live in backend/general_perks.py; the generated
player-reference/GENERAL_PERKS.md lists all 61 general quirks. These are combat/
character perks, not hidden history facts, radiant story templates or dialogue
eligibility tags. New random rolls and standalone-perk rewards enforce the shared
compatibility rules. Existing trait/history data is preserved. No story repeat
scope or authoring contract was changed; deferred personal-story grants still
require review against the current runtime catalogue.
