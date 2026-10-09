# Character story content index

Canonical entry point for proposed character voices, personal histories and
one-off story content. Updated October 8, 2026. **Planning only**; no content
packs below are active, and no importer is implemented.

## References and ownership

Implemented starting-race eligibility: [audit](../design/STARTING_RACE_AUDIT.md).
All 42 race IDs remain in authoring/name pools; no tags or acquisition rules
changed. Seven submitted race-name files await validation and integration.

| Reference | Purpose |
| --- | --- |
| [Design proposal](../design/CHARACTER_STORIES_PROPOSAL.md) | Rules, integration points, pacing, novelty, persistence, stages |
| [Short character overview](CHARACTER_LIFE_OVERVIEW.md) | Readable personalities, eligibility, backgrounds, stories and reward directions; keep current |
| [Race names brief](RACE_NAMES_GPT_BRIEF.md) / [workflow](RACE_NAMES_WORKFLOW.md) | Single-upload seven-batch request for all 42 races; separate names-0.1 authoring format; not installed |
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
