# Jobs and character loadouts

Implemented in dev, October 4, 2026. This is the loadout dependency pass, not the
full starting-Job/progression release described in STARTING_JOBS_AND_SKILLS_V1.md.

## What is playable

Roster → Skills provides a Job preview, five equipped slots, learned-skill cards,
search, passive descriptions, Save loadout and Discard changes. Unsaved choices
survive ordinary roster refreshes and stay scoped to the player/server/save.

Regular characters can deliberately choose one of twelve initial toolboxes:
Fighter, Barbarian, Rogue, Ranger, Mage, Cleric, Monk, Bard, Druid, Engineer,
Summoner and Captor. Each currently knows two supported actives and one passive.
These 36 definitions are executable catalogue entries, not the 96 proposed
skills from the design draft. Several starter passives intentionally overlap;
complete differentiated Job catalogues are still pending.

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
summon attacks keep the established owner-linked costs. Advanced kit-specific AI
and deployment placement controls are pending. No new overhead unit art was
generated; portrait circles remain the mobile-unit presentation.

## Still pending

- Replace the six-role character creator with all twelve starting Jobs together,
  remove proficiency/Medic starter choices and supply matching low-quality kits.
- Later learned skills, unlock pacing, Job progression and further build choices.
- More mechanically distinct passives and conditional/resource kits.
- Dedicated summon/device controls, authored portraits and device state packs.
- Champion fixed kits; no Champion combat power is derived from collection rank.

No generic Job-switch/respec, XP curve, advanced Jobs or arbitrary skill scripts
were added. The Job choice in this dependency pass should not be presented as a
finished starting-character rollout.

## Files and validation

Catalogue/validation: `backend/job_loadouts.py`. Save API:
`POST /api/characters/{id}/loadout` (`job_id`, `skill_ids`). Definitions exposed
under `/api/content` → `job_loadouts`; character fields live in existing player
JSON, requiring no parallel skill database. Roster: `job-loadout-ui.js`.

Validation: 230 related backend tests, 188 frontend tests, production frontend
build, and isolated Chrome checks of actual battle/roster rendering. Checked
slot removal and persistence through roster rerender, technique grouping and
passive inspection. QA used temporary fixtures, not player saves. Existing Vite
large-chunk warning remains. Development only; no production deployment.
