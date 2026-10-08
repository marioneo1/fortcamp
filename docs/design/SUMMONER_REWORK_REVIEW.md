# Summoner — implemented in dev, October 7, 2026

Summoner creates autonomous board presence. The player chooses initial placement,
orders and investment; creatures never receive manual initiative turns. Existing
temporary-unit ownership, legal movement, combat accuracy, defenses, conditions,
forced movement, terrain entry events and owner-linked clocks are extended.
Legacy gear deployments retain their policies and budget. The subsequent Engineer
rework uses construction/active machinery slots instead; see ENGINEER_REWORK_REVIEW.md.

## Actions, slots and progression

Five character skill slots still include passives. Eight Job choices:

| Skill | Unlock | Action / cooldown | Behavior |
|---|---|---|---|
| Bound Companion | Starter | Main; replacement 5 | Choose Fire, Earth or Grass; one companion, no capacity. |
| Transposition | Starter | Quick / 3 | Swap caster + creature or two owned creatures, at any distance. |
| Life Pact | Starter | Main / 2 | Spend ceil(25% caster max HP); heal an injured owned creature by that amount. Cannot leave caster below 1 HP. |
| Wisp Swarm | 2 successes | Main; replacement 6 | Place three separate flying, 1-HP ranged Wisps. One capacity per surviving Wisp. |
| Spirit Projection | 5 successes | Main / 6 | Enemy within 3 and sight; one INT-based hit per owned creature within 2. |
| Sacrifice | 9 successes | Main / 3 | Select 3x3 within 3 and sight; owned creatures there die and each explodes within one cell. |
| Overload | 12 successes | Main / none | Triple creature ATK and max HP, preserving HP percentage; dies at caster's third following activation start. Once per creature lifetime. |
| Rapid Conjuration | 16 successes | Slotted passive | Bound Companion and Wisp Swarm become Quick Actions. |

Normal attacks/main skills end the activation. Multiple legal Quick Actions may
precede the main action. Rapid Swarm → Projection and Rapid Swarm → Sacrifice are
supported. Reclaim is innate, always Quick, and replaces the corresponding active
summon skill. Replacement cooldown begins only after the last member is gone;
it never runs while that group remains active.

Placement is on distinct legal empty cells in the two-cell square around the
caster, with clear sight. Ground companions avoid water and pits; Wisps use the
existing flying rules. Wisp placement is atomic: select three cells, confirm once,
or cancel without a cost. Partial selection does not create units or spend actions.

Transposition commits provisional movement and applies arrival hazards. It ends
normal walking for this activation, while leaving the main action available. This
explicit rule prevents swapping from resetting the movement origin/budget. No
temporary mutation of real coordinates is used to test destination legality.

## Autonomous activation and commands

New creatures first act after the owner's **next** activation, then after each
owner activation. Each acts at most once per owner clock, including when a living
owner loses its action to control. They have independent attacks, movement and
signature cooldowns; they do not share the old six-damage automatic budget.
Movement and attack events use the normal serialized combat playback, including
hazards along the entire committed route. No client-side damage simulation.

Summon Orders is an innate numbered skill-bar tile, available for one creature
or all. It opens the centered command popup, can be reordered with other skills,
and uses neither an equipped skill slot nor an action. With no active summons it
is visibly unavailable:

| Order | Behavior |
|---|---|
| Hold Position | Route toward the selected cell; stay there and attack in range. Seek nearby legal ground when occupied/blocked. |
| Focus Target | Prefer the chosen visible living enemy, pursue when practical; attack legal nearby alternatives when necessary. |
| Follow Summoner | Seek positions within two cells of the owner and attack opportunistically. |
| Protect Ally | Bound Companion only. Select any living ally, including the Summoner; seek positions within two cells. Grass heals/supports that ally; Earth and Fire prioritize enemies able to attack them, then nearby threats. Does not intercept attacks. |
| Stand Down | Stay still and Guard; no aggressive action. |
| Clear Order | Return to default autonomous behavior. |

Orders persist and cost no skill slot or action. Each portrait has a readable order
effect; right-click details expose the creature's innate profile. Routing uses
bounded board searches and normal occupancy, not recursive retries. Closed doors
and unreachable targets may leave a creature holding nearby; creatures do not
operate doors. No claim of globally optimal positioning or coordinated planning.

Protect Ally with All summons selected affects only the Bound Companion and
leaves Wisp orders intact. Individual Wisps do not show this command. The selected
companion cannot protect itself. Invalid/enemy/departed targets are rejected before
orders change. If the protected ally later becomes unavailable, the companion
supports its Summoner until that ally is available again or the order changes.
Clear Order restores normal autonomous behavior. Grass keeps the existing Life
Offering amount, HP cost, healing restrictions and cooldown; no extra healing
charge, action or player-controlled summon turn is introduced.

## Creature profiles

General stats inherit approximately half their owner's raw combat stats at cast
time. They do not copy the owner's skill pool or gear triggers. Changes to the
owner afterward do not repeatedly compound creature stats.

* **Fire:** full INT as ranged attack power. Hits apply Burn and Scorch the tile.
  Fire Wall places three cells for three creature turns, cooldown 3. Each entry
  adds/triggers Burn and deals an additional half-INT fire hit. Allies are affected.
  AI uses the wall when a legal strip contains at least two visible enemies.
* **Earth:** full owner max HP, half ATK, one movement, 25% less direct damage.
  Basic hits independently roll 25% Push and 25% one-turn Stun. Hurl Boulder has
  range 3, 1.25x ATK, 75% one-turn Stun, cooldown 3. Normal resistance applies.
* **Grass:** full owner max HP and INT; half other stats. Its melee spirit attack
  uses inherited INT as attack power, with normal accuracy and defenses; there
  is no fixed one-damage override. This also allows Overload to improve its attack.
  Life Offering costs ceil(25% own max HP), heals its Protect Ally target
  (otherwise the Summoner) for twice that amount,
  cannot kill itself, cooldown 2. AI avoids waste and Burn-blocked healing.
  Nature Burst is a non-damaging 3x3 push centered on the supported ally, with
  cooldown 3; adjacent allies can also be pushed. AI requires more nearby enemies
  than allies before using it. Centered on the supported ally is a deliberate simple V1
  heuristic, rather than a player-controlled ground spell.
* **Wisp:** 1 HP, flying, range 3, 40% owner INT as magical attack power. Normal
  accuracy, armor and other defenses still apply. Each occupies a real tile.

Fire Wall uses existing entry processing and hazard warnings, including forced
movement and one legitimate trigger per entered cell. Overlapping Fire Walls do
not multiply a single entry. Fire Wall is a separate hazard from Scorched ground;
it can coexist with Scorch, whose duplicate patches remain deduplicated.

Projection uses the caster's magical damage and separate hit/defense resolution
for each contribution. Its preview shows the all-hits total, not a guarantee.
Sacrifice overlaps hit independently, including caster/allies and other summons
outside the sacrifice area. Walls block explosions; living victims receive Blind
for three target turns subject to normal resistance. Reapplication refreshes;
it does not multiply Blind duration. Destruction/reclaim releases capacity and
starts replacement cooldowns; defeated owners dismiss their creatures.

## Presentation and migration

One generated 4x4 atlas supplies four portrait-circle faces, eight square skill
icons and four transparent effects. Six ElevenLabs clips provide conjure, swap,
projection, sacrifice, overload and pact cues. Existing fire surfaces and normal
projectile/contact playback are reused. Assets warm when a Summoner battle opens.
Overload has an aura and an owner-turn countdown. Companion choices explain their
different contributions; spell descriptions state costs and lifecycle rules.

Older Summoner learned/equipped/order IDs migrate idempotently: wolf/bulwark →
companion, wisps → swarm, sprite → pact, manifestation → projection, footwork →
Rapid Conjuration. Practice and identities remain stable. Existing battle snapshots
with old deployment definitions continue using the legacy path; start a fresh
Battle Lab encounter to test the new kit.

## Validation and remaining work

Automated checks cover ownership, eight-skill catalogue, migration, atomic
placement, capacity, cooldown lifecycle, Quick/main sequences, shared turn timing,
movement events, orders, HP costs, Overload, four-contribution Projection, allied
Sacrifice damage, Fire Wall route warnings, owner defeat and read-only views.
Browser checks exercise placement/confirmation, portraits, group orders, Reclaim,
Transposition, Projection and cancellation against isolated fixtures without saves.
Protect Ally checks cover Summoner/other-ally healing, invalid targets, group
scope, fallback/Clear Order, threat priority, routing and ally-centered bursts.

Personality-aware caster/enemy AI remains deferred. Current owner auto-play
conservatively summons, uses valuable Projection and heals badly injured companions;
it does not plan Sacrifice/Overload/Transposition combinations. Creature AI is
heuristic, not a tactical planner. Live numerical and aesthetic playtesting remain
necessary, particularly Earth control, body-blocking, Fire Wall + Scorch, and
four-body Projection/Sacrifice. Generated SFX have technical checks, not human
listening approval. No production deployment or save reset is part of this pass.

October 7 follow-up: dismissed summon bodies remain visible through the resolved
enemy playback and disappear at their defeat/dissolve event, including a summon
created and killed in one response. Temporary presentation bodies do not restore
gameplay HP, occupancy or targetability. Reclaim, Sacrifice, Overload expiry and
owner-defeat cleanup use the same departure presentation. Newly conjured Grass
companions receive the updated inheritance; existing saved battle stats are not
retroactively rewritten.

## October 7 placement usability refinement

Battle skill and popup help now use one concise sentence; detailed skill definitions remain available as `detailed_description` for a future reference menu. Placement/order windows drag by their header and remember their viewport position separately from Engineer. E confirms; C/Escape/right-click cancel; footer keys match command keycaps. Companion/Wisp placement uses the X cursor outside legal cells. No changes to summon AI, command costs, capacity or lifecycle.
