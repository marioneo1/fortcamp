# Combat ability foundation

Implemented in dev, October 4, 2026. Subsequent foundations now cover spaces,
deployments and regular loadouts; see COMBAT_SPACES.md, COMBAT_DEPLOYMENTS.md and
JOB_LOADOUTS.md. Twelve starting Jobs are playable in dev, with six skills each except the expanded Fighter and Barbarian kits; the larger
catalogue remains a draft. See COMBAT_CONTROLS.md for current targeting and UI.

## Player rules

New battles give each technique its own availability. Precision Shot and Arc Bolt become ready at the second following owner activation; Field Care at the third. Other gear techniques retain one use each per battle. No two-gear-active cap. Identical technique IDs are still collected once.

Using a technique commits provisional movement and spends the main action. Misses spend cooldowns/uses. Invalid targets, range, capture incompatibility and Mute rejection do not. Contact discovery during an approach pauses before attacking without spending the technique. Ordinary attacks, capture and Guard keep existing rules.

The picker displays cooldowns/uses and permits selecting another ready technique while one cools down. Switching costs no action. Physical Field Care works while muted; magical techniques do not.

New battles have no universal twenty-round defeat. Existing reinforcements and objectives remain. Auto Resolve pauses unfinished battles after its bounded step budget with an explanation, without inventing defeat or awarding rewards. Continue manually or request more auto turns. More encounter-specific pressure remains to be authored.

## Definitions and persistence

backend/combat_abilities.py owns the validated version-1 vocabulary. Abilities are snapshotted into units; clients submit IDs, never definitions. Equipment supplies source, scaling, elements and procs. No parallel character database or combat engine.

Definitions declare enemy/ally target, explicit elevation rule, range, cooldown/charges and one to four ordered effects. Effects: attack, heal, cleanse, Guard, status, Barrier, Mark and straight push/pull. Conditions: earlier attack hit, target has status, HP below fraction. Unknown effects/conditions and invalid numbers are rejected before effects run. Fixed data, not a scripting language.

Later effects observe earlier results and stop on death/unconsciousness. Resolution reuses accuracy, armor, resistances, elements, procs, defeat, animations and records. Statuses reuse control recovery and racial resistance, including poison immunity. Modern status timing and Barrier/Mark ownership are implemented below.

Owners persist ability_activation, ability_stamp and ability_state keyed by skill ID (uses, ready_at) in existing battle JSON. Cooldown 2 used at activation N is ready at N+2. Real activations tick once; polling/reopening never starts activations or ticks damage. Concealment first sightings remain persistent on view refresh so revealed enemies stay visible.

Saved battles without versioned skills retain legacy shared use and round/action limits; no mid-fight migration. New battles use versioned snapshots automatically. No saves rewritten or production deployed.

## Validation and remaining work

Tests cover JSON reload, repeated views, independent charges, misses, invalid commands, ordered conditions, physical care while muted, lethal termination, poison immunity, capture restrictions, legacy saves and auto/manual consistency. All 46 authored gear techniques validate, including negative damage bonuses. Frontend checks cover selection, timing and legacy fallback.

Removing forced defeat exposed existing auto pathfinding stalls at walls in Locked Tool Shed and the former-command prison encounter. Auto pauses these fights; boundary-aware approach/pathfinding needs follow-up. Do not claim all maps complete automatically.

Next: full twelve-Job starter creation, later unlocks, progression and kit-aware AI.
Publish all twelve starters together after planned encounter checks.

Validation: 420 backend tests and 183 frontend tests passed; Vite build passed (existing large-chunk warning). Isolated Chrome check confirmed cooldown labels, independent selection and action-button availability without JavaScript errors. No live API/database used for browser review.

## Tactical dependency pass - October 4

Implemented in dev. Guild Tower Shield grants Shield Cover (6 Barrier, cooldown 3) and adjacent-ally interception. Duelist Gloves grant a half-strength melee Riposte after a hit. Precision Shot applies an owned Mark; Hook Thrust pulls one tile and Titan Thrust pushes one tile after a successful hit. Existing item IDs, artwork and drop pools stay intact.

Barrier absorbs a finite amount after mitigation. Smaller shields cannot refresh a stronger remaining shield; equal/stronger applications replace rather than add. It expires at the recipient's activation end. Mark provides its owner up to 10 accuracy on the first successful hit each activation; misses preserve it. An owner marks only one target at a time. Reactions cannot consume that bonus.

Poison/Burn tick at activation start. Other timed effects expire at activation end; newly applied effects do not immediately expire on the same activation. Control and Bind cannot be refreshed or switched into another disabling effect while active. Their expiry grants recovery protection. Repeated finish calls and polling do not double-tick durations.

Interception and counters share one reaction per unit activation. Incapacitated, carried, extracted, panicked or otherwise disabled units cannot react. Interception checks adjacency, range and sight and redirects subsequent effects to the actual recipient. Capture bypasses interception/counters. Counters cannot trigger counters; throws and damage ticks do not trigger these reactions. Forced movement resolves before counter range is checked. Returning Hand is supported but not published as new content.

Push/pull follows a straight cardinal path, at most two tiles, without routing around obstacles. Walls, occupied cells and excessive elevation stop it. Boss/chieftain displacement resistance defaults to 25%; authored resistance and Braced can modify it. Previews show destination, resistance, collision and pit risk. Collision damage is optional and zero for the current pilot techniques. Forced movement clears exit readiness and moves a carried body with its carrier.

Authored shallow pits inflict fall damage and Slow; deep pits also require a main-action Climb Out onto a legal adjacent tile. Explicit lethal pits kill and prevent body/gear recovery, including carried bodies. Flying units bypass these falls. Old untyped pits default to shallow; untyped void remains blocked, not secretly lethal. Maps must author recoverable exits and lethal hazards deliberately. No new pit maps were added in this pass.

The battle UI explains remaining Barrier, Mark ownership, reaction availability, displacement resistance and durations. Lost-in-pit bodies are not displayed as recoverable corpse tokens. Equipment descriptions show their reactions.

Validation: full backend regression 432 tests passed, followed by 74 focused tests covering final changes. Frontend suite 185 tests passed; final status tests and Vite build passed (existing large-chunk warning). Isolated actual battle UI check confirmed Barrier, Mark, resistance, reactions and skill previews without JavaScript errors. Live saves and production were untouched.

October 4 spaces dependency: zone/form effects, bounded activation clocks, route entry, reversible Prowler/Bulwark profiles and battle presentation are now implemented as engine vocabulary. No starter kits or gear drops changed. See COMBAT_SPACES.md for limitations; summon/device economy and the Job/loadout rollout are next.

Deployment effects and owner-linked temporary units are implemented;
COMBAT_DEPLOYMENTS.md is authoritative. JOB_LOADOUTS.md now documents opt-in
starter skill grants and loadouts. Full starter creation and dedicated placement
controls remain pending.


### One-use rally bonuses (implemented October 5)

Hold Together demonstrates three ordered effects in one skill. Its two allied
status effects accept a radius of 1-2 and only the guaranteed `rally_power` and
`rally_protection` statuses. They have no activation expiry: consumed separately
by the next normal direct attack (miss included) and next direct hit. Area attack
power covers the whole attack. Both are battle-local and do not stack. Guard
and rally protection provide one 25% reduction together, not two reductions.
Other area statuses remain unsupported; validation rejects them rather than
silently applying incorrect resistance/chance rules. Existing single-target
status effects retain their original behavior.


## October 5: bounded martial extensions

Versioned skills may declare `self_only`, `fury_cost` (1?5) or `fury_gain` (1?2).
Availability reports insufficient Fury; accepted casts spend Fury once alongside
existing independent charges/cooldowns. Healing accepts either an integer
`amount` or `max_hp_percent`, never both. `area_attack` is intentionally narrow:
one self-targeted effect, radius one, attack power percentage and one/two-cell
push. Groundbreaker authors a one-cell push and excludes allies. It reuses the
existing hit, damage, displacement, collision, immunity and death handling.

`combat_martial.py` holds the eight-ability kit's bounded hooks at actual damage,
status application, lethal resolution and owner activation. It is not a general
skill scripting language. Fury/passive state lives in existing battle JSON;
view polling does not advance it. Resolved `martial_effect` events share attack
packets with contact sounds and visual playback; they do not predict damage.

See [Martial Jobs](MARTIAL_JOBS_REWORK.md) for gameplay and migration details.
