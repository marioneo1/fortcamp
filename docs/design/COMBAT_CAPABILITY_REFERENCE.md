# Combat capability reference

Ordinary rats/wolves/bears/boars cannot operate doors: blocked pursuit attacks
destructible door HP and consumes the normal action. Destruction still ends the
animal's activation; next activation resumes pursuit. Open doors require no
special animal behavior. Druid forms/humanoids retain normal door operation.

Door operation: free once per unit activation, including humanoid enemies; preserves
unspent normal movement/main action. Door use commits the preview's terrain cost,
so movement cannot refill from the doorway. AI may continue pursuit/attack/flee afterward.
Other objective interactions keep their action costs. See COMBAT_CONTROLS.md.
Authored bandit AI no longer stops on free door operation. Pursuit may
approach/open/continue in one activation, retaining its remaining movement budget
and the one-door-per-activation limit.

October 9 mounted shockwaves: Earthbreaker/Groundbreaker damage rider and mount
independently but move a surviving linked pair once per cast. Lethal separate
routes play independently before collapse/fall. Corpse representation records
whether the animal died mounted. See ANIMAL_MOUNTS.md for presentation details.

October 9 real boar mounts: persistent Rider perk, innate Mount/Dismount, separate
HP/targets, +1 movement, 25% reduction to both bodies. Mount loss: 25% hard
(half mount max HP + Stun), 50% rough (quarter + Hobble), 25% safe; one-turn control. Mounted boar shares movement/hazards and status timing,
skips its autonomous turn; fresh Boar-Rider Patrol layouts use real animals.
See [Animal mounts](ANIMAL_MOUNTS.md); animal capture/other species deferred.


Tripline presentation refinement October 9: one painted rope spans its complete
1×3 footprint, with two endpoints, no extra boundary outline and no atlas-edge
artifact. Orientation and single-use crossing behavior remain. Approved female
Human attacks and Goblin attacks/hurt/death are installed. One final voice tester;
superseded auditions archived. Gameplay and event timing remain unchanged.
See art/ENEMY_SPECIALTIES_V1.md and art/ENEMY_VOCALS_V1.md via the documentation index.

October 9 shared-stat migration: ordinary HP uses 12 + 4×VIT; weapon Attack uses
2 + half its scaling attribute + power/training, with existing race/gear/perks.
Adventurer E–S scales allocations once at 1.0/1.3/1.6/1.9/2.2/2.5; bonuses
apply afterward, not another multiplier on completed combat values. Fresh
humanoids are rebuilt around encounter targets; captures persist raw allocations
and rank. Saved battles/legacy recruits are not inferred or unscaled. Species,
summons, machinery and form exceptions remain explicit. See [current rules](SHARED_COMBAT_STATS.md),
[D audit](D_RANK_COMBAT_AUDIT.md) and [396-fight audit](SHARED_COMBAT_STATS_AUDIT.md).

Defense preparation v2 replaces the spike/snare/platform menu with uncapped
point-funded barriers, enemy trap pits, proximity explosives and free equipped
Engineer/Rogue deployments sharing their normal caps. Existing pit Climb Out,
machine ownership, caltrop zones and explosion/displacement pipelines are reused.
See [current defense rules](DEFENSE_PREPARATION.md); legacy saved defenses remain compatible.

October 9 final E-rank batch: `frontier_watch_defense` and `prison_rescue_e`
have four reproducible Battle Lab layouts each, authored Goblin kits and
recruit/voice identity. Defense preserves preparation/keeper objectives; E-rank
rescue shares carry/extraction rules without inheriting the D-cart difficulty or
dispatch prizes. The original D-cart and higher-tier rescue contracts are intact.
See [E-rank audit](E_RANK_COMBAT_AUDIT.md) for budgets and validation scope.

Audited Human/Goblin enemies now have opt-in wordless attack/hurt/death vocals
by race, gender and personality (three variations each). Captured identities
persist on recruits. Shared event timing preserves weapon impacts and prevents
early death sounds; this changes presentation, not combat balance. See
[vocal implementation](../art/ENEMY_VOCALS_V1.md) and [short progress](../player-reference/VOICE_PROGRESS.md).

October 9 dev extension: nine recruitable enemy definitions (Road Bola plus
Tripline, Shakedown, Parting Cut, Ankle Bite, Goliath Shot, Tag Team, Cornered Fury,
Heel Cut). See [short kit reference](../player-reference/ENEMY_SPECIALTIES.md).
Captures retain specialties and learn normal Job starters; equipped slots stay
unchanged. [Recruit backgrounds](../player-reference/RECRUIT_PERKS.md) add bounded
event-driven effects, matching-workplace production, first-stack Poison rejection,
defense preparation and modest attribute tradeoffs. Wider general traits remain
proposals. Perks persist across recruitment and do not occupy skill slots.

Maintained alongside combat changes. This is an index of implemented tools for
encounter design, not a list of promises or a second skill catalogue. Exact skill
definitions live in `backend/job_loadouts.py`; individual rework documents record
their design rationale. Update this reference and the relevant audit when adding
or changing a mechanic.

## Characters, Jobs and enemy kits

- Explicit unit-targeted techniques and Subdue execute their validated approach
  and selected action on one click. Invalid targets cannot substitute basic Attack.
  Ground/self and dedicated placement/command flows retain their own controls;
  [targeting audit](SKILL_TARGETING_AUDIT.md) lists the reviewed base-Job routes.

- Doorways expose one centered control usable from either operating side. Nearby
  approaches preview server-supplied movement immediately; distant doorway intent
  routes toward the closest reachable side. A door-icon click also opens/closes
  on arrival using the normal main action; plain floor navigation does not.
  Interrupted/insufficient movement never bypasses occupancy or turn validation.

- Regular characters equip five total active/passive skills. Learned cross-Job
  skills can be equipped; no new starter Job is needed for an enemy specialization.
- Fighter: displacement/collision, interception, protection, fear removal,
  limited healing and kill sustain.
- Barbarian: enemy-damage Fury, Fury-priced control without normal cooldowns,
  low-health scaling, kill healing and temporary death prevention.
- Monk: three-stage techniques, multi-hit attacks, vulnerability, defensive
  follow-up, mobility and reliable finishing through Perfect Rhythm.
- Rogue: cardinal surrounding, debuff-count burst, multiple Quick Actions before
  one main action, chosen teleport destination, trap strips and thrown techniques.
- Ranger: owner-specific Quarry, distance damage, crits, independent multi-hit
  shots, Poison buildup/cashout and stationary range bonuses.
- Mage: Wet/Fire/Lightning/Freeze interactions, delayed zones/channeling,
  displacement, friendly-fire area spells and chosen weapon enchantments.
- Bard: planted Songs, two-Bard-activation performance lifetime, lingering
  benefits, NO LINGER Accelerando/Peace, commands and forced targeting.
- Cleric: finite healing charges, vulnerable Rest recovery, placed restoration,
  mixed holy/weapon damage, Blind and self-only Battle Priest transformation.
- Druid: once-per-activation form switching, shared character HP, global Bleed
  amplification, fragile Rat, regeneration and shared-HP reactive Bramble Wall.
- Summoner: owner-linked autonomous units, persistent high-level orders, chosen
  placement, replacement cooldowns, swaps, sacrifice and one-use Overload.
- Engineer: blocking/attackable construction, stationary autonomous machinery,
  mounting, Overclock, scuttling, mines, delayed Dynamite and Rapid Assembly.
- Captor: separate HP/Resolve, Attack alongside Subdue, isolation, Hobble/Disarm,
  dragging, Hold Resolve ticks/repeated capture rolls and unconscious prisoners.

Capturable humanoids may use these Jobs and authored learned/equipped loadouts.
`recruitable_snapshot` preserves the kit through prisoner recruitment. Roster
HP/attack are then calculated normally from attributes and equipment; encounter
budgets are not permanent recruit stats. Captures do not grant free duplicate gear.
Animals use species traits, not humanoid Jobs.

## Damage, movement and statuses

- STR/DEX/INT weapon scaling follows the equipped weapon; VIT contributes HP and
  flat armor; AGI contributes initiative and can increase movement. Weapon magic
  and elemental resistance use the existing damage pipeline.
- Armor subtracts a flat amount; Armor Fracture reduces effective armor by 30%.
  A displayed armor value is not a percentage damage reduction.
- Evasion affects accuracy by delivery type; guaranteed-hit effects bypass it.
  Physical/magical/elemental defenses and status application resistance are
  separate concepts. Do not infer immunity solely from a creature's appearance.
- Hard-control application respects selective resistance/immunity. Boss control
  durations may be shortened; this does not mean blanket immunity to all debuffs.
- Normal movement uses the final committed path from START; previews are free.
  Real forced-movement paths trigger eligible hazards. Collision, walls, pits,
  occupied cells, flying and terrain cost all have existing resolvers.
- Burn: 2% max HP per stack; Bleed: 5% per stack; Poison: 10% total per tick,
  with duration stacks. Target-end damage removes one stack. Burn ground entry
  adds a stack and triggers its current damage without consuming it.
- Caltrops add Bleed/Hobble on placement occupants and real entry. Scorched
  overlap never creates a double fire entry trigger. Mines can interrupt movement.
- Existing control vocabulary includes Stun, Freeze, Paralysis, Sleep, Bind,
  Hobble, Disarm, Fear, Blind and Mute. Use existing effects before inventing a
  parallel status. See [DoT rules](COMBAT_DOTS.md) and the Job rework documents.

## First E-rank species and humanoid profiles — October 8

Implemented in `backend/combat_encounter_profiles.py`, only for the three audited
contracts. Neither profile depends on the player's roster strength.

| Enemy | Implemented contribution | Counterplay |
| --- | --- | --- |
| Store rat | Gnawing Weakness on landed bite; wounded rats merge up to three bodies with summed HP/ATK | Finish wounded rats before regrouping; separate or disable partners |
| Fence wolf | 25% Bleed on landed bite; +20% bite power per other wolf cardinally beside the victim, maximum +40% | Protect flanks, use fences/chokes and displace the pack |
| Human Road Enforcer | Fighter: Driving Strike and Intercept | Avoid collision lanes; separate the two bandits |
| Human Road Cutpurse / Road Trapper | Seed chooses normal Rogue kit or Cheap Shot/Road Bola/Exploit Weakness mixed kit | Deny flanks, avoid Bola approach; inspect techniques in Unit Details |

Pack neighbors must be conscious, present and not hard-disabled; intervening
blocking wall boundaries prevent their contribution. Previews and actual direct
damage share the same bonus. Damage-over-time does not inherit bite bonuses or
roll the bite's on-hit proc again. Rats merge as a main action, without healing or extra turns; wolves never merge.

Fairy combat HP now uses 0.75x base; Ogre uses 1.35x base +4. Other racial
modifiers remain: Fairy flight/+2 movement/20 evasion/+5 initiative; Ogre -1
movement/-12 evasion/+1 armor. This is a targeted adjustment, not a finished
review of every race. Current player movement floor is two; no one-cell Ogre or
racial loyalty cap was added.

## Deferred work and review boundaries

- Swarm splitting and additional species behaviors are not implemented.
- Broader race review: racial skills, attributes, selective magical/status
  defenses and all other species must be measured in later encounter batches.
- Broader personality planning outside the scoped rat/wolf/toll-bandit heuristics.
  Other encounters retain their existing behavior.
- Player autonomy/loyalty naming and any Ogre-specific cap require separate
  design. Race currently does not force a loyalty ceiling.
- Starter auto-play is a smoke benchmark, not proof that every player build or
  every race can solo every map. Manual tactics and stronger/unlocked loadouts
  are separate tests. Keep scenario seeds and results in the audit record.

## Authored encounter AI and status vocabulary

Beginner encounters also have authored per-layout compositions: rats/wolves
vary between two and four bodies with adjusted HP/ATK, clustered/separated
openings and two outdoor scavengers in the delivery-court rat variant. Toll
retains the two humans promised by its description, varying Cutpurse/Trapper
roles and formation. Existing species AI is unchanged; opening activity is
position/props plus a short History line, not a new idle AI state. See the
E-rank audit composition table and validation limits.

`combat_encounter_ai.py` implements scoped rat regroup/merge, wolf shared-target
cardinal flanking and toll-bandit withdrawal/guardian/opportunist/strategist
behavior. Existing paths, wall checks, control restrictions and forced targeting
remain authoritative. Safer destination selection avoids known fire/Caltrops;
this is not an optimal hazard-aware path planner. Dialogue is authored, throttled
and local. See the E-rank audit for limits and validation.

**Gnawing Weakness:** each stack means -5% damage dealt/+5% damage received,
with each percentage capped at 30%; one stack expires per target activation.
Each rat in a swarm contributes one application on a landed direct bite. DoT
packets never reapply bites. **Rat Swarm:** one to three original rats sharing
summed current/max HP, ATK and Resolve, one turn and one combined attack packet.
UI shows swarm size and effect details; merge and bite playback remain sequential.

**Road Bola** (`npc:bandit:road_bola`): recruitable Road Trapper technique,
range three, 50% physical attack power, Hobble for two turns on hit, cooldown
three activations. It uses existing net art and does not create another starter
Job. Normal and mixed bandit variants both retain skills/personality on capture.


## E-rank batch 2 and independent wildlife

Goblin Pickpockets, Old Well and Supply Watch now use four authored compositions
each with recruitable Fighter/Rogue/Ranger and mixed Snarer roles. Scoped Goblin
mobility/evasion remains distinct. See the E-rank audit for budgets and testing.
Same-map foraging bear: saved 3% entry roll, hostile to both sides, excluded from
required contract clearance, optional recovered pelt/5% claws. Existing targeting
and corpse pipeline retained. Details: [Radiant encounters](RADIANT_ENCOUNTERS.md).
20 new field items use ordinary stat/scaling rules, including DEX/STR knuckles;
no new generic on-hit multiplier or Job redesign.

## E-rank worksite batch 3

Timber Across the Creek (two layouts), The Locked Tool Shed and Herbs Behind
the Wall (four layouts each) now use scoped Goblin Fighter/Rogue/Ranger kits.
Two ordinary scavengers or three lighter scavengers guard the optional route;
peaceful collection and postcombat handover remain unchanged. Guard 28 HP/5 ATK,
ordinary 24 HP/4 ATK, light 17 HP/3 ATK; all move four and have 12% evasion.
Existing Driving Strike/Intercept, Cheap Shot/Crippling Cut, Mark Quarry/Longshot
and mixed Road Bola/Cheap Shot are retained on recruitment. No new skill IDs,
global racial changes, personal-story eligibility or new radiant events.
See the E-rank audit for layout rosters, simulations and limitations.

## Generic personal quirks - October 9
61 runtime definitions in backend/general_perks.py supplement the 16 selected
backgrounds. Central conflict groups enforce one constitution tier, one
redistribution profile and no opposing stat/resistance pairs on new rolls/grants.
Rarity has no level/rank gate; Naturally Gifted has a 0.0001% opening roll and
+1 to STR/DEX/AGI/VIT/INT/LUK. It is an independent bonus, compatible with
redistribution and luck traits; duplicate copies are blocked. NPC HP/VIT profiles
are rare to keep ordinary encounters near their authored budgets.
Combat integrates permanent attribute/stat modifiers, a seeded temporary
battle-start attribute overlay, Ranger bow/crossbow range, per-action unarmed
flat damage, displacement resistance, status-application resistance, damage-only
DoT resistance and final all-source mitigation. Existing control resistance
uses the maximum, not addition. DoT traits do not prevent application. Precomputed
Monk hit budgets apply perk mitigation once. Enterprising awards +1 per actual
party bearer only when mission settlement awards positive gold. No rerolls of
existing saves; no new skills, classes, stories or racial rebalance.
Readable generated catalog: ../player-reference/GENERAL_PERKS.md.
Validation: 352 backend tests pass, including perk conflict/rate boundaries,
save-stable rolls, actual DoT damage, shared unarmed budgets, single application
of precomputed Monk mitigation, recruitment and existing map budgets. Reference
generator --check passes; manual balancing of rare combinations remains.

## October 9 follow-up: rider-owned Boar Charge

Rider now describes allied mounts, with species bonuses/techniques. Only boars
are currently available. Mounting a boar adds `innate:rider:boar_charge` to the
rider without consuming an equipped slot; dismount or mount loss removes it.
Boar Charge uses a main action, three-activation cooldown and a clear cardinal
line. Starting target distance 1/2/3/4 gives 1.25/1.5/1.75/2.0 times rider attack
power, stopping adjacent. Only a landed four-cell hit attempts one-turn Stun;
normal Stun resistance applies. Approach hazards resolve on both bodies and
can stop the charge. This is dedicated skill movement, not a normal movement
refill. Existing walking/strike presentation is reused. AI chooses a legal
straight charge before its ordinary attack; no new animal AI framework.
Targeted mount/D-rank checks cover tiers, shared movement, blockers, miss,
immunity, dismount, save/fall outcomes and hazard interruption.
