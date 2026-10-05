# Jobs and character loadouts

Implemented in dev, October 4, 2026. The twelve starting Jobs, matching poor-quality equipment and first skill unlocks
are playable. The larger catalogue in STARTING_JOBS_AND_SKILLS_V1.md remains a draft.

## What is playable

Roster → Skills provides a Job preview, five equipped slots, learned-skill cards,
search, passive descriptions, Save loadout and Discard changes. Unsaved choices
survive ordinary roster refreshes and stay scoped to the player/server/save.

Regular characters can deliberately choose one of twelve initial toolboxes:
Fighter, Barbarian, Rogue, Ranger, Mage, Cleric, Monk, Bard, Druid, Engineer,
Summoner and Captor. Each starts with two supported actives and one passive. Three further skills
unlock after 2, 5 and 9 successful contracts, giving 72 executable definitions
across the twelve Jobs. The 96-skill draft is not fully implemented. Several
passives overlap; deeper conditional kits and differentiation remain pending.

New characters choose their Job in the creator, with matching starter gear and
three equipped skills. Medic and work proficiencies are no longer starter choices.
Existing regular characters without a Job may choose one in Roster.
Choosing a Job is permanent for now, stated before saving. Existing characters
are not silently classified. Choosing does not replace their weapons, traits,
appearance, identity, proficiencies or attributes. Champions, Celestials and
temporary hired mercenaries are excluded from this regular-character tool.

Actives and selectable passives share **five slots**. Learned IDs and equipped
IDs are separate character fields. Empty loadouts are allowed; basic actions
still work. Unknown/unlearned IDs, duplicates and more than five entries are
rejected atomically. Skill capacity bonuses are deferred, not accepted from clients.

Characters must be idle and unassigned to save. The authenticated endpoint uses
the existing player lock/database transaction. It only finds characters in that
player's state. Battle creation copies active definitions, passive effects and
reactions into the existing persisted battle JSON. Later roster edits do not
change saved battles. Existing battles retain their previous snapshots.

## Combat and presentation

Character actives use the versioned ordered-effect interpreter. Cooldowns are
per skill and advance on owner activations. Passives contribute actual armor,
evasion, displacement resistance or the existing Intercept/Riposte reaction.
Shared reaction limits still apply even when equipment grants another reaction.

The battle selector groups Character skills and Equipment and proficiency. All
equipped equipment techniques remain available without consuming character slots
or imposing a two-active cap. Passive explanations are inspectable separately.
Physical medicine proficiency retains Field Care for compatibility; no work
proficiency is erased or automatically converted to Cleric.

Auto support now distinguishes healing, cleansing, protection, self forms and
deployment. It summons only with visible enemies, resources and legal adjacent
space; it does not repeatedly transform an already transformed owner. Device and
summon attacks keep the established owner-linked costs. Commanded-unit auto attacks spend the owner action and use legal movement;
advanced kit-specific AI and deployment placement controls are pending. No new overhead unit art was
generated; portrait circles remain the mobile-unit presentation.

## Still pending

- Remaining skills from the draft and further build choices beyond six per Job.
- Experience/levels, advanced Jobs and explicit respecialization rules.
- More mechanically distinct passives and conditional/resource kits.
- Dedicated summon/device controls, authored portraits and device state packs.
- Champion fixed kits; no Champion combat power is derived from collection rank.

No generic Job-switch/respec, XP curve, advanced Jobs or arbitrary skill scripts
were added. This is the first starter rollout, not a completed progression or balance pass.

## Files and validation

Catalogue/validation: `backend/job_loadouts.py`. Save API:
`POST /api/characters/{id}/loadout` (`job_id`, `skill_ids`). Definitions exposed
under `/api/content` → `job_loadouts`; character fields live in existing player
JSON, requiring no parallel skill database. Roster: `job-loadout-ui.js`.

Validation: 124 related backend starter, progression, capture, deployment,
legacy-save and loadout tests; 189 frontend tests and the frontend build pass. Isolated Chrome
checks verified twelve creator choices, matching kits, three starter cards, six
learnable cards and swapping a later skill while retaining five slots. Actual
solo Storehouse encounters complete for every Job without closed-door stalls;
completion is not a guarantee of victory. Captor is a harder solo combat start.
Existing Vite large-chunk warning remains. Development only; no deployment.

## Successful-contract practice

Job practice is one point per success or critical success, regardless of rank.
Failure, critical failure and debug battles award none. Participants receive
credit; bodyguards do so only when the mission actually included combat. Newly
learned skills appear in the result and Roster, but are never automatically
equipped. Attributes, gear and the five-slot capacity do not grow automatically.
Existing completed missions are not retroactively credited.

Awards occur at final settlement in the existing mission transaction. A bounded
list of 32 recent contract receipts additionally prevents immediate duplicate
credits; it is not a replacement for transaction idempotence. Job fields remain
in the existing player JSON. Older saves keep their equipment and identity.

Captor Binding Line lasts two target activations, giving a follow-up opportunity;
Sure Grip provides 25 knockback resistance and four capture percentage points
when equipped. Creature objectives no longer inherit chieftain capture resistance.
Basic auto support can heal or apply regeneration; it does not yet plan complex
Captor setup sequences. Closed operable gates are opened during auto pursuit.
