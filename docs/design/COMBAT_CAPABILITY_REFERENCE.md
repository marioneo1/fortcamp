# Combat capability reference

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
