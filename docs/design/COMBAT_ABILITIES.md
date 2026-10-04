# Combat ability foundation

Implemented in dev, October 4, 2026. The twelve starting Jobs, loadouts, new passives/reactions, summons, forms and zones remain proposed. See STARTING_JOBS_AND_SKILLS_V1.md.

## Player rules

New battles give each technique its own availability. Precision Shot and Arc Bolt become ready at the second following owner activation; Field Care at the third. Other gear techniques retain one use each per battle. No two-gear-active cap. Identical technique IDs are still collected once.

Using a technique commits provisional movement and spends the main action. Misses spend cooldowns/uses. Invalid targets, range, capture incompatibility and Mute rejection do not. Contact discovery during an approach pauses before attacking without spending the technique. Ordinary attacks, capture and Guard keep existing rules.

The picker displays cooldowns/uses and permits selecting another ready technique while one cools down. Switching costs no action. Physical Field Care works while muted; magical techniques do not.

New battles have no universal twenty-round defeat. Existing reinforcements and objectives remain. Auto Resolve pauses unfinished battles after its bounded step budget with an explanation, without inventing defeat or awarding rewards. Continue manually or request more auto turns. More encounter-specific pressure remains to be authored.

## Definitions and persistence

backend/combat_abilities.py owns the validated version-1 vocabulary. Abilities are snapshotted into units; clients submit IDs, never definitions. Equipment supplies source, scaling, elements and procs. No parallel character database or combat engine.

Definitions declare enemy/ally target, explicit elevation rule, range, cooldown/charges and one to four ordered effects. Effects: attack, heal, cleanse, Guard, status. Conditions: earlier attack hit, target has status, HP below fraction. Unknown effects/conditions and invalid numbers are rejected before effects run. Fixed data, not a scripting language.

Later effects observe earlier results and stop on death/unconsciousness. Resolution reuses accuracy, armor, resistances, elements, procs, defeat, animations and records. Statuses reuse control recovery and racial resistance, including poison immunity. Barrier/Mark and new ownership/expiry semantics remain future work.

Owners persist ability_activation, ability_stamp and ability_state keyed by skill ID (uses, ready_at) in existing battle JSON. Cooldown 2 used at activation N is ready at N+2. Real activations tick once; polling/reopening never starts activations or ticks damage. Concealment first sightings remain persistent on view refresh so revealed enemies stay visible.

Saved battles without versioned skills retain legacy shared use and round/action limits; no mid-fight migration. New battles use versioned snapshots automatically. No saves rewritten or production deployed.

## Validation and remaining work

Tests cover JSON reload, repeated views, independent charges, misses, invalid commands, ordered conditions, physical care while muted, lethal termination, poison immunity, capture restrictions, legacy saves and auto/manual consistency. All 45 authored gear techniques validate, including negative damage bonuses. Frontend checks cover selection, timing and legacy fallback.

Removing forced defeat exposed existing auto pathfinding stalls at walls in Locked Tool Shed and the former-command prison encounter. Auto pauses these fights; boundary-aware approach/pathfinding needs follow-up. Do not claim all maps complete automatically.

Next: status ownership/expiry and Barrier/Mark, displacement and bounded reactions; then zones/forms/summons, regular five-slot loadouts and Job UI/AI. Publish all twelve starters together after planned encounter checks.

Validation: 420 backend tests and 183 frontend tests passed; Vite build passed (existing large-chunk warning). Isolated Chrome check confirmed cooldown labels, independent selection and action-button availability without JavaScript errors. No live API/database used for browser review.
