# Jobs and character loadouts

Implemented Engineer rework: [Engineer review](ENGINEER_REWORK_REVIEW.md) documents
eight actives, construction/slots instead of Components, mounting, Overclock,
mines/Dynamite and idempotent migration. Starter has three active choices; normal
five-slot limits remain. Existing battle snapshots retain their saved kit.

Implemented Summoner rework: [Summoner review](SUMMONER_REWORK_REVIEW.md) records
eight choices, three starter actives, unlocks at 2/5/9/12/16 successes, autonomous
creatures, innate orders/Reclaim, chosen placement, lifecycle cooldowns and legacy
ID migration. Five character slots still apply. With Engineer's rework the catalogue has 95 skills
across twelve Jobs; older counts below describe earlier passes.

Implemented Mage rework: [Mage review](MAGE_REWORK_REVIEW.md) records three starter actives, eight choices, practice unlocks at 2/5/9/12/16, elemental interactions, delayed casts, chosen weapon enchantments and compatibility migration. The current catalogue is 85 executable definitions across twelve Jobs.

Implemented Ranger rework: [Ranger rework review](RANGER_REWORK_REVIEW.md) records eight skills, three starting actives, practice unlocks at 2/5/9/12/16, owner-specific Mark, ranged/Poison builds and loadout migration.

Implemented Monk rework: [Monk rework review](MONK_REWORK_REVIEW.md) records eight choices, a complete starter combo, owner-turn readiness, technique damage/proc budgets, Sweeping Dash and save migration. Initial tuning still needs gameplay comparison.

Implemented in dev, October 4, 2026. The twelve starting Jobs, matching poor-quality equipment and first skill unlocks
are playable. The larger catalogue in STARTING_JOBS_AND_SKILLS_V1.md remains a draft.

## What is playable

Roster → Skills provides a Job preview, five equipped slots, learned-skill cards,
search, passive descriptions, Save loadout and Discard changes. Unsaved choices
survive ordinary roster refreshes and stay scoped to the player/server/save.

Regular characters can deliberately choose one of twelve initial toolboxes:
Fighter, Barbarian, Rogue, Ranger, Mage, Cleric, Monk, Bard, Druid, Engineer,
Summoner and Captor. Most start with two supported actives and one passive; Monk starts with three actives forming its complete combo; Rogue starts with Cheap Shot, Crippling Cut and Exploit Weakness; Ranger starts with Mark Quarry, Longshot and Poison Attack; Mage starts with Chain Lightning, Fireball and Typhoon. Most Jobs unlock three further skills after 2, 5 and 9 successful contracts. Expanded Fighter, Barbarian, Monk, Rogue, Ranger and Mage pools bring the current catalogue to 85 executable definitions across twelve Jobs. The 96-skill draft is not fully implemented. Several
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

## October 5 Fighter refinement

Fighter Cover is now Chain Snare (damage, square reach 3, pull up to 2, halve
movement for 2 activations). Break Formation is Earthbreaker (leap 3, square
impact radius 2, inner push 2 / outer push 1, cooldown 5). Hold Together
clears Fear from all allies within 2 cells of the caster; no Barrier. Stable
loadout IDs and unlock thresholds are retained; active snapshots are not migrated.
See FIGHTER_COMBAT_REVIEW.md for exact legality, collision and auto-play rules.

## October 5: Fighter power and wave contact

Driving Strike now uses 150% attack power and stuns surviving solid-collision
participants for one activation. Chain Snare adds nonstacking 30% armor loss for
two target activations. Earthbreaker uses 200% attack power, with per-target
contact markers following the expanding wave after landing. Existing cooldowns
and defensive rules remain. See [Fighter review](FIGHTER_COMBAT_REVIEW.md) for
exact rules, balance proposals and validation. Fresh battles use these changes;
existing snapshots and production are unchanged.


## October 5: Fighter additions and Barbarian Fury rework

The catalogue now contains 77 definitions: Fighter has nine, Barbarian eight,
and the other ten Jobs have six each. Five equipped slots still include both
actives and passives; learned skills remain available for later loadout changes.
Fighter adds Brace at 12 successes, Second Wind at 16 and Victory Strike at 20.
Barbarian adds Bloodthirst at 12 and Unstoppable at 16. Earlier unlocks still use
2, 5 and 9 successes. The roster displays each Job's actual thresholds.

Barbarian's innate Fury is part of the Job, not a sixth equipped passive.
Old Barbarian learned/equipped IDs migrate to the corresponding new kit IDs
when character data is initialized. Previously earned practice also unlocks
these additions; existing battles retain their saved snapshots.

See [Martial Jobs](MARTIAL_JOBS_REWORK.md) for exact effects, costs, clocks,
visual/audio presentation, migration and testing limits.


Combat display order is independent of learned/equipped IDs. The character's
`combat_skill_order` contains display preferences only and may be saved while on
a mission; it never replaces a battle snapshot or permits equipping a new skill
mid-combat. Unknown or retired display IDs are ignored when composing the bar,
while newly available skills append. Slotted passives appear in the bar, not the
innate/equipment Traits panel. See COMBAT_CONTROLS.md for drag/Arrange behavior.

## Rogue rework (implemented in dev)

Eight choices, three starter actives, unlocks at 2/5/9/12/16 successful contracts. Slotted Trap Expert costs one of five slots. Multiple independently cooled Quick Actions precede one main attack; normal walking locks after the first Quick Action, while legal mobility techniques remain usable. Old Rogue choices/order migrate without losing practice; current saved battles retain snapshots. See ROGUE_REWORK_REVIEW.md for exact geometry, stack/cooldown rules and limitations. Battle Lab's 16-success tier exposes the whole pool.

## Cleric rework (implemented in dev)

Eight choices; starter Mend, Rest and Holy Light; other skills unlock at 2/5/9/12/16 successful contracts. Traditional restoration uses finite battle charges recovered by continuous vulnerable Rest. Slotted Battle Priest changes healing into self-only cooldown skills. Legacy choices map without losing practice or automatically enabling Battle Priest. See CLERIC_REWORK_REVIEW.md for formulas, timing, UI, migration and AI limits.

## Druid rework (implemented in dev)

Eight choices; starter Prowler, Rejuvenation and Bramble Wall; remaining unlocks
at 2/5/9/12/16 successes. Persistent quick-action forms share HP and allow one
change per activation, preserving legal movement before the change. Animal
forms cannot cast nature spells. Shared-health Bramble terrain and regenerative
support reuse existing combat clocks; two slotted specialization passives remain
within the five-slot limit. Legacy choices migrate without losing practice.
See DRUID_REWORK_REVIEW.md for exact mechanics, AI scope and balance risks.
