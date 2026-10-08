# Summons and Engineer devices

Current Engineer rules: [Engineer rework](ENGINEER_REWORK_REVIEW.md), October 7.
Its new Job machines use active slots and construction, independent firing cycles,
mounting and hazards. The shared-budget prototype below still describes legacy gear
deployments, not the current Engineer Job. Summoner: [Summoner review](SUMMONER_REWORK_REVIEW.md).

Engine dependency implemented in dev, October 4, 2026. JOB_LOADOUTS.md now covers
opt-in Engineer/Summoner skill grants; full starter creation remains pending.
No existing gear, vendor or drop pool has been
changed to grant deployments. Profiles below are tested trial values, not final
Job progression balance.

## Deployment and resources

The versioned ability vocabulary accepts one grouped `deploy` effect. It uses
the owner's main action and the ability's independent cooldown/charges. A cast
targets self and selects legal adjacent ground in deterministic north/east/south/
west order. Empty-tile placement UI is still pending. All required cells are
checked before spending anything; pairs deploy together or not at all.

These initial units each occupy one combat cell. Walls, solid props, occupied
cells including hidden enemies, inappropriate water/pits and traversal prohibit
placement. Multi-cell moving constructs require further geometry work; do not
publish them by only enlarging a sprite.

| Profile | Policy | Trial HP / armor | Output | Resource |
|---|---|---|---|---|
| Scrap Turret | Stationary automatic | 16 / 1 | 6 attack, ballistic range 4 | 2 Components |
| Guard Automaton | Commanded | 24 / 2 | 7 melee attack, movement 2 | 3 Components |
| Bonded Wolf | Commanded | 18 / 0 | 7 melee attack, movement 3 | 1 capacity |
| Wisp pair | Automatic | 8 / 0 each | 3 magic attack each, range 3, flying movement 2 | 2 capacity per pair |
| Stone Bulwark | Commanded | 30 / 3 | 4 melee attack, movement 1 | 2 capacity |
| Grove Sprite | Automatic support | 10 / 0 | Up to 3 healing, range 2, movement 2 | 1 capacity |
| Astral Guardian | Commanded, once per encounter | 32 / 2 | 9 melee attack, movement 2 | 2 capacity |

Components are encounter resources: default three, spent permanently for the
encounter. Dismissal/destruction never refunds them. Reclaimer and gear bonuses
remain future authored mechanics. Summon capacity defaults to two simultaneous
points and is released when deployments disappear. A surviving wisp still
reserves the pair's two points; dismissing a member releases the whole pair.
Ability cooldowns and once-per-encounter deployment history are independent
of capacity and cannot be reset by dismissal/redeployment. Defaults are not Job
locks; future gear can author capacity/resources/budgets explicitly.

## Actions and clocks

Deployments receive no initiative slot and cannot attack during the activation
that created them. Their status clock and movement reset occur once at their
owner's next activation start. Polling, reconnects and unit selection do not
advance clocks. JSON preserves costs, deployment identity, fired cycles and
owner activation stamps.

Commanded movement uses the entity's own finite movement budget. It is provisional
until the owner commands an attack or finishes the turn; switching between owner
and entity cannot renew it. Commands use the owner's main action, not a free
additional full turn. The current context menu exposes movement, attack and
dismissal, with costs; a dedicated selection/command panel remains UI work.

Autonomous output occurs at owner activation end. Eligible entities share a
default budget of six raw attack/healing points (not six damage after mitigation).
Output is divided across eligible entities, spent on attempts including misses,
and bounded even when there are multiple turrets or wisps. Policies prefer
visible in-range targets, then nearest reachable targets. They use existing
movement, sight, accuracy, armor, reactions, damage, healing and status rules.
Grove healing cannot revive, farm overhealing, or heal through Burn.

Manual Calibration currently uses the context-menu Operate Turret command from
an adjacent owner. It spends the owner's main action and the same automatic
output budget; the turret does not fire again automatically that cycle. This
foundation supports owned operation only, not allied strangers operating devices.

Dead, unconscious, carried or extracted owners dismiss their deployments.
An owner unable to act suspends output. Mute blocks magical summon commands and
automatic magical output; physical turret output/operation remains available.
Disabled entities cannot attack. Hidden personality-aware tactical scoring is
still pending; the initial automatic policy is explicit nearest/in-range targeting.

## Records, prisoners and rewards

Summon attacks credit actual damage/defeats to the owner once. Equipment effects
are not inherited by cloning a character; each profile has its own basic attack.
Temporary victims provide no mission kill credit, corpses, loot or prisoners.
Destroyed entities disappear instead of becoming carryable bodies. Reward/prison
services also reject temporary entities defensively. Real mission objectives and
ordinary enemies retain their existing victory and reward rules.

## Presentation and artwork decision

Mobile summons/automatons use the same portrait circle system as other units.
Use existing movement/impact animations; do not require a separate animation
sprite sheet for every summoned creature. Dedicated portraits are still pending.

Stationary turrets/devices may use map sprites. Future image packs should include
idle/base, firing preparation where useful, firing pose, projectiles and destroyed
forms, with stable anchor/scale/orientation so transitions do not jump. Projectiles
are separate effects, not terrain tiles. No new projectile animation is claimed
in this dependency pass.

A 4x4 painted summon/device atlas was generated using the approved overhead
furniture sheet as style reference. It remains staging/reference only after the
mobile-unit presentation decision. It is not installed as mobile unit art.
See docs/art/SUMMON_DEVICE_ART.md for source, prompt and ordered contents.

New artwork must be generated as coherent equal-cell image packs, with the same
lighting/perspective and complete separated silhouettes. Keep terrain separate
from props/entities. Crop using actual source dimensions, inspect cell boundaries,
and retain originals/manifests. Generation requests do not guarantee exact pixel
dimensions or perfect spacing; extraction must be checked.

## Remaining work

Dedicated ground placement/command UI, repair/reclaim/release skills, summon
techniques, personality-aware AI scoring, equipment expansions and integration
with the full twelve-Job creation/loadout catalogue. Champion kits stay deferred.
Current template values need solo E-rank, paired D-rank, objective and resistance
balance checks after the starter kits become playable.

## Starter integration, October 4

Engineer and Summoner are now creator choices with matching poor kits. Regular
Job loadouts use the existing deployment rules. Auto can command a ready owned
unit using legal movement and the owner's action, without extra initiative turns.
All twelve Jobs have a solo Storehouse completion smoke check; this does not
replace encounter balance or personality-aware kit AI. Dedicated placement,
repair/reclaim/release controls and final art remain deferred.
