# Starting Jobs and Skills — V1 design draft

Status: proposed, October 4, 2026. This is a design specification for discussion,
not implemented behavior. The agreed direction is twelve starting Jobs, five
regular-character skill slots, all equipped gear abilities accessible without
consuming those slots, and Champion kits deferred. Individual abilities and
balance values below remain proposals.

Current runtime still has six starting roles and equipment-driven techniques.
The [ability foundation](COMBAT_ABILITIES.md) is now implemented in dev. The
twelve Jobs and proposed 96 skills are not playable yet.
See CAPTURE_AND_STARTING_ROLES.md for live behavior. Do not present this draft
as playable content. No advanced Jobs, Champion kits or final XP curve here.

## Boundaries and progression

- Job means combat class. Medicine, construction and other work proficiencies
  remain separate; remove Medic/proficiency selection from the future starter UI.
  Cleric is a combat Job, not a renamed medicine proficiency.
- All twelve Jobs become available together when this starting system launches.
  Each must have a viable solo opening and matching poor-quality equipment.
- Each Job has eight initial learnable skills: two active starters, one passive
  starter, five later unlocks. All three starters begin equipped; capacity is five.
- Active and selectable passive skills consume the same character slots.
  Race, permanent story traits, proficiency and universal actions do not.
- Basic weapon Attack or capture-only Subdue, Move, Guard, Interact, Exit and
  End Turn remain separate. No free lethal attack for capture weapons.
- Newly recruited regulars receive a stable appropriate Job and a usable starter
  loadout. Existing people need a deliberate migration; do not reroll identities,
  silently overwrite equipment or assume every medic-trait holder is a Cleric.
- Unlock opportunities should be spread across early/middle progression, with
  no permanent branch lock. Select skills from the known catalogue. Respec the
  loadout freely while idle; snapshot it for a deployed expedition.
- Do not set final XP thresholds until mission frequency and early recruitment
  are tested. No automatic large attribute inflation with Job levels.
- Champion popularity/acquisition rank does not determine combat strength.
  Champion authoring is deferred; eventual kits may contain 5–10 total abilities.

## Common timing and limits

Every active below uses the main action unless an exception explicitly says
otherwise. It commits provisional movement. Availability is per ability, not the
legacy shared special_used flag. Ordinary actions end the activation.

Initial cooldown bands, subject to testing:

- Routine setup/mobility: ready again at the second following owner activation.
- Strong control, area effects and protection: third following owner activation.
- Major summons: explicit deployment/charge limits instead of indefinite refresh.

UI should say “Ready in 2 of your turns.” Refresh happens once at owner activation
start; polling, action-mode changes and movement previews never advance timers.
Durations name the affected unit's activation or the creator's next activation,
not an ambiguous mixture of rounds and turns.

One ordinary reaction allowance per unit, refreshed at its activation start.
Interception and counters share it. Reaction attacks cannot trigger more reaction
attacks; one incoming attack cannot bounce between multiple interceptors.
Triggered healing/damage requires effective results, not attempted casts.

Offensive hit-based effects require a hit. Support effects normally require no
accuracy roll, but still validate target, range, sight and immunities. Magic
explicitly declares sight, elevation and component rules. No default “all magic
ignores everything” rule.

Short movement effects respect occupancy, walls, terrain and traversal. They
consume remaining movement unless an ability explicitly grants bounded extra
movement. Never reset movement_origin to award a new full movement budget.
Post-action movement, where granted, is one Move-or-Finish opportunity with no
second attack. Previewing movement cannot trigger zones, stacks or reactions.

V1 adds Mark, finite Barrier, short displacement, bounded reactions, small zones,
selected local counters and summons. Reuse existing conditions and attack math.
Apply explicit caps/refresh/source rules to Poison, Fury and Combo; no unlimited
percentage-HP damage, recursive conditions or arbitrary skill scripts.

## Starter equipment

All receive existing Worn Jacket and Work Boots. Reuse stable starter item IDs
where suitable. Proposed additions are common, poor quality, in the same baseline
power band as Chipped Sword/Frayed Bow/Cracked Wand. Sell matching starter gear
through the basic vendor when implemented. Skills must not require a rare drop
to make a starting Job function.

| Job | Weapon/offhand proposal | Attribute direction, not a stat lock |
|---|---|---|
| Fighter | Chipped Sword + Splintered Shield (existing) | STR/VIT; AGI for positioning |
| Barbarian | Nicked Axe (new) | STR/VIT; durability matters |
| Rogue | Pitted Dagger (new; explicitly DEX-scaled) | DEX/AGI |
| Ranger | Frayed Bow (existing) | DEX/AGI |
| Mage | Cracked Wand (existing) | INT; secondary choice depends on build |
| Cleric | Tarnished Prayer Rod (new; INT-based, modest ranged basic) | INT/VIT |
| Monk | Frayed Handwraps (new; DEX-based melee weapon) | DEX/AGI; STR displacement alternative |
| Bard | Battered Song Focus (new; modest INT-based ranged basic) | INT/AGI |
| Druid | Weathered Grove Staff (new; INT-based modest ranged basic) | INT; VIT/AGI shape choices |
| Engineer | Worn Mallet + Bent Tool Kit (existing weapon/new offhand) | INT for devices; STR for personal weapon |
| Summoner | Faded Calling Focus (new; INT-based modest ranged basic) | INT; defensive secondary |
| Captor | Frayed Capture Net (existing) | Balanced STR/DEX/INT |

Job identity does not lock every weapon. Individual abilities state equipment
requirements. A capture weapon cannot perform a damaging weapon technique;
other gear abilities retain explicit compatibility. Actual symbols/art and new
weapon-category integration are implementation work, not created by this memo.

## Skill catalogues

S = unlocked/equipped starter. A = active. P = selectable passive, including
automatic reactions. Other five skills are later unlocks; ordering is not a
final level requirement. Small/short/modest values require numerical tuning.

### Fighter — techniques, protection and chosen engagements

| Skill | Type | Behavior |
|---|---|---|
| Shield Bash | S/A | Shield required. Attack adjacent target; on hit push one tile. Blocked by solid terrain applies Vulnerable, not an extra full attack. |
| Measured Advance | S/A | Move a short valid route and make a reduced weapon strike; remaining movement pays the route. Useful against an enemy just beyond basic reach. |
| Firm Footing | S/P | Gain modest protection until next activation after ending without committed movement. Does not stack repeatedly through previews. |
| Intercept | P/reaction | Redirect one direct attack aimed at an adjacent ally to self when in reach/sight. Respects hostility and uses reaction allowance. |
| Riposte | P/reaction | After surviving a melee hit, make one reduced basic strike against the attacker if still in range. Cannot chain. |
| Duel Challenge | A | Mark one enemy. Own attacks benefit when the marked enemy lacks adjacent allies; new challenge replaces own previous mark. No forced target obedience. |
| Tactical Order | A | Give a nearby willing ally a small legal reposition, not another attack or full turn. |
| Break Formation | A | Weapon strike; on hit pull the target one tile toward a valid adjacent space. Stable targets resist; cannot pull through a wall. |

Builds: counter protector (Intercept/Riposte/Firm Footing + two actives); duelist
(Challenge/Advance/Bash + chosen passives); field commander (Order/Formation/
Intercept). Reaction competition and proximity provide costs. Multiple threats
and separation punish protection; grouped opponents undermine dueling.

### Barbarian — exposure, Fury and disruption

| Skill | Type | Behavior |
|---|---|---|
| Driving Blow | S/A | Forceful weapon attack that pushes one tile on hit. Requires a damaging melee weapon. |
| Reckless Rush | S/A | Approach and attack; gain Vulnerable until next activation as the explicit price. Route uses remaining movement. |
| Battle Fury | S/P | Meaningful enemy damage taken generates Fury, capped at three. Tiny repeated ticks cannot farm it; unspent Fury decays after inactivity. |
| Fury Sweep | A | Spend Fury on a small adjacent area attack. Preview affected allies; no hitting through walls. |
| Refuse to Yield | A | Spend Fury for a temporary Barrier and remove Fear. Cannot revive or clear every condition. |
| Demolisher | P | Better structural damage and reduced recoil from blocked displacement; not universal armor penetration. |
| Blood Momentum | P | One small movement opportunity after a direct defeat, at most once per activation. Reaction defeats do not grant a fresh turn. |
| Intimidating Roar | A | Short-area Fear check against visible enemies. Bosses/mindless enemies follow explicit resistance rules. |

Fury abilities without Battle Fury equipped can generate a single Fury through
their authored risky setup (Rush); no unusable mandatory-passive dependency.
No ally damage/self-harm farm. Berserker accepts danger; breaker trades raw focus
damage for displacement/structure control. Kiting, control and denied targets
interrupt the plan.

### Rogue — access, openings and sabotage

| Skill | Type | Behavior |
|---|---|---|
| Dirty Trick | S/A | Adjacent target: modest weapon strike with a short Blind application on hit; resistance shown. |
| Slip Away | S/A | Short retreating movement; gain temporary evasion. No invisibility or traversal through bodies/walls. |
| Opportunist | S/P | Modest bonus against enemies already suffering Bind or Vulnerable. Multiple eligible conditions do not multiply it. |
| Expose Weakness | A | Apply Vulnerable to an accessible target; no damage burst stapled on. |
| Target Access | A | Short approach to an enemy with no adjacent allies; validates an accessible destination. Does not teleport through terrain. |
| Sabotage | A | Disrupt an adjacent device/alarm or damage a structure; requires authored object support, not any arbitrary quest bypass. |
| Clean Getaway | P | Once per activation, direct defeat grants bounded post-action movement; no second strike. |
| Cut the Signal | A | Short-duration Mute attempt against a nearby target; physical commands/machines require their own disruption tags. |

Assassin specializes in access/Exposure/Getaway; saboteur in Trick/Signal/Sabotage.
Protected targets, resistance and blocked escape routes are real weaknesses.
Do not imply a fully implemented player-stealth system in this first catalogue.

### Ranger — lines of fire, pursuit and preparation

| Skill | Type | Behavior |
|---|---|---|
| Pinning Shot | S/A | Ranged weapon attack; on hit applies short Slow. Does not automatically immobilize. |
| Hunter's Mark | S/A | Mark a visible target; own first hit each activation gains a bounded accuracy benefit. One own mark at a time. |
| Steady Aim | S/P | Accuracy improves when firing without committed movement. Target's cover/sight still applies. |
| Toxic Shot | A | Attack applies one Poison stack on hit, maximum three. Damage/refresh rules bounded; immunity visible. |
| Venom Extraction | A | Weapon strike; on hit consumes own applied Poison stacks for payoff. Other characters' stacks are not stolen. |
| Running Shot | A | Reduced ranged strike grants a short retreating movement opportunity; movement is the benefit. |
| Snare Placement | A | Place one visible temporary trap on a valid nearby ground tile. Entry binds briefly; controlled enemies receive recovery protection. |
| Clear Lane | P | A modest advantage when no unit or obstacle intervenes. Does not grant sight through walls. |

Marksman favors firing lanes and stationary aim; hunter spends actions on Poison
and movement. Traps expire and consume setup time. Cleansing, resistance, close
pressure and moving objectives counter these builds.

### Mage — temporary spaces, elements and wards

| Skill | Type | Behavior |
|---|---|---|
| Ember Patch | S/A | Place a small visible temporary zone; entry/start can apply bounded Burn. Once per target activation, not per preview/step spam. |
| Force Pulse | S/A | Short ranged magical hit pushes one tile on hit. Declares sight/elevation rules. |
| Arcane Ward | S/P | Modest magic mitigation, not broad physical immunity. Shares documented modifier stacking limits. |
| Frost Line | A | Small line spell with Slow; walls truncate the line. No room-wide stun. |
| Ward Ally | A | Finite Barrier for self or nearby ally; expiry and non-additive refresh stated. |
| Kindle | A | Exploit an already Burning target for a bounded payoff while consuming Burn. |
| Binding Circle | A | Small zone; first qualifying entry attempts brief Bind, with control-recovery rules. |
| Elemental Discipline | P | Improve duration/reliability of a selected element at the cost of selecting this passive; not all elemental effects at once. |

Controller uses Pulse/zones; elemental attacker uses setup/consumption; warder
spends actions protecting. Areas should not be safely stackable into unlimited
damage tiles. Friendly effects/harms must be explicit, visible and balanced.

### Cleric — restoration, wards and offensive rites

| Skill | Type | Behavior |
|---|---|---|
| Mend | S/A | Restore bounded HP to self/conscious ally, no revival. Main action and cooldown make it different from endless free regeneration. |
| Rebuke | S/A | Modest magical attack; on hit applies Vulnerable to an appropriate supernatural enemy. Normal targets still take the modest attack. |
| Care into Courage | S/P | Effective healing of an injured ally/self grants a small personal Barrier once per activation. Overhealing grants nothing. |
| Purify | A | Remove a stated small set of harmful statuses; not a cure-all. |
| Protective Rite | A | Give self/ally a finite Barrier. No stacking multiple casters into infinite absorption. |
| Consecrated Ground | A | Small temporary zone provides bounded Regeneration at eligible activation starts; Burn suppresses it. |
| Judgment | A | Consume own applied Vulnerable for a single-target payoff. Existing unrelated Vulnerable sources cannot double-trigger. |
| Shared Resolve | P | Effective healing of an ally below a threshold shortens Mend's cooldown once per activation, never making it free/repeatable in that turn. |

Battle healer remains capable of fighting solo. Warder uses prevention, exorcist
condition-specific offense. Healing and support consume offensive opportunities;
separation, burst and dangerous zones challenge these builds.

### Monk — positioning and short sequences

| Skill | Type | Behavior |
|---|---|---|
| Opening Palm | S/A | Modest melee strike; on hit adds one Combo, capped at three. |
| Flowing Step | S/A | Short legal movement with brief evasion; consume remaining movement rather than duplicating the budget. |
| Centered Breath | S/P | Ending with no attack grants one Combo, once per activation. Combo expires after sustained inactivity. |
| Driving Palm | A | Spend Combo on a hit-dependent push. Resistance affects displacement. |
| Nerve Strike | A | Spend Combo to attempt brief Mute/disruption of the specified action type. Not universal disable against every creature. |
| Stone Stance | A | Spend Combo on Barrier and displacement resistance until next activation. |
| Returning Hand | P/reaction | Reduced counter after an adjacent miss; shares reaction allowance and cannot cause chains. |
| Linked Strikes | A | Two reduced hits using existing attack math, spending Combo. Consumes one action, not two turns; on-hit proc budget prevents doubling every enchantment for free. |

Opening Palm generates Combo even without Breath equipped. Combo has no general
resource-restoration gear loophole. Disruptor, evasive counterfighter and combo
attacker trade setup and skill slots; control, armor and separation interrupt them.

### Bard — sustained performances and tactical coordination

| Skill | Type | Behavior |
|---|---|---|
| Marching Verse | S/A | Start a short performance granting bounded movement to self/nearby allies at activation start. Re-entering range does not refresh a full budget. |
| Discordant Note | S/A | Modest magical hit with a short accuracy penalty/Blind on hit. |
| Keep the Beat | S/P | Staying near a supported ally modestly extends performance duration, with a fixed maximum. Solo still uses the base performance. |
| Steady Chorus | A | Replace current performance with temporary defensive support for self/nearby allies. |
| Rallying Call | A | Remove Fear from nearby allies/self; ordinary morale Panic has explicit eligibility, not an unconditional story-objective bypass. |
| Coordinated Step | A | Reposition one nearby willing ally a short legal distance; no extra main action. |
| Cutting Refrain | A | Consume current performance to apply Vulnerable to a visible opponent. Sacrifices ongoing team benefit. |
| Echo of Effort | P | First effective support action while performing improves next basic attack modestly; cannot stockpile through repeated casts. |

Only one own performance runs at a time. Identical buffs refresh/take strongest
rather than add indefinitely. Support is evaluated at clear activation events,
not expensive continuous recalculation or exploitable tile toggles. Disruptors,
separation and forced movement counter conductor builds.

### Druid — forms first, nature support second

| Skill | Type | Behavior |
|---|---|---|
| Briar Snare | S/A | Visible target receives a short Bind attempt, with resistance and recovery protection. |
| Wild Shape: Prowler | S/A | Enter a short mobile melee form. Fixed bounded attack profile and traversal rules; no HP refill, free flying or race rewrite. |
| Rooted Recovery | S/P | Ending still on suitable living ground grants a modest bounded recovery. Terrain requirement shown; not immortal sustain. |
| Wild Shape: Bulwark | A | Replace current form with durability/displacement resistance, reduced mobility. |
| Grove Remedy | A | Modest heal and removal of Poison for self/ally; no resurrection. |
| Thornbed | A | Temporary visible zone punishes eligible movement with bounded damage; standing still is an available answer. |
| Call Grove Sprite | A | Small autonomous support summon with shared summon economy. No additional unrestricted healer turn. |
| Adaptation | P | First form change in an activation removes Slow; switching forms repeatedly grants no additional benefit. |

One form at a time. Transformations keep absolute HP subject to temporary max-HP
rules; entering/leaving a form never creates healing. Equipment remains owned;
form-incompatible weapon abilities are disabled with explanation, compatible
passives persist once. Nature controller versus shapeshifter are genuine choices.

### Engineer — machinery, maintenance and routes

| Skill | Type | Behavior |
|---|---|---|
| Deploy Scrap Turret | S/A | Spend encounter Components to place a small stationary autonomous turret on a valid tile. It fires after future owner activations, not immediately on deployment. |
| Field Repair | S/A | Restore bounded HP to an owned construct in reach; no resurrecting destroyed devices. |
| Efficient Assembly | S/P | One extra encounter Component. No ability to dismantle and rebuild for infinite components or new shots. |
| Deploy Guard Automaton | A | More expensive mobile commanded construct. No independent full main action plus owner main action. |
| Manual Calibration | A | Operate a nearby compatible turret for a selected shot. Uses operator action and replaces, not adds to, that turret's automatic shot for the cycle. |
| Tripwire | A | Temporary trap with a small placement count/cooldown; entry applies short Slow/Bind under recovery rules. |
| Breaching Work | A | Target a nearby destructible structure for efficient damage; no generic key/quest-lock bypass. |
| Reclaimer | P | Recover a bounded portion of Components from own destroyed/dismantled devices, capped by original cost and once per device. |

Starter numerical trial: three encounter Components, turret costs two, automaton
costs three. These are temporary combat resources, not permanent wood/scrap/gold.
Efficient Assembly/Reclaimer and later gear can expand options. No costs are final.
Mechanisms retain damage, cooldown and resource identity when moved; replacing a
device cannot refresh exhausted shots. Engineer retains ordinary mallet attacks
and a repair/setup plan, not a mandatory construction proficiency choice.

### Summoner — bonded presence and temporary manifestations

| Skill | Type | Behavior |
|---|---|---|
| Call Companion | S/A | Summon a modest commanded companion using capacity. Starts available in its deployment state, but cannot immediately add a free second attack. |
| Bond Mend | S/A | Heal an owned summon or self for a modest amount. No free summon resurrection. |
| Bonded Endurance | S/P | Own summons receive a small durability benefit; does not transfer player HP multipliers repeatedly. |
| Call Wisps | A | Summon a pair of fragile autonomous entities sharing a bounded automatic attack budget. Useful routes, not two unrestricted turns. |
| Call Bulwark | A | More expensive durable commanded summon; limited offense, good obstruction/protection. |
| Direct the Bond | A | Use owner's main action for a summon-specific technique at its position. Unit requirements/range still apply. |
| Manifestation | A | Once-per-encounter major temporary summon; consumes capacity and takes time/action to deploy. No instant deployment strike. |
| Release the Bond | A | Dismiss an owned summon for a finite Barrier on self/ally. Sacrifices presence and does not reset summoning cooldowns. |

Starter capacity trial: two points; companion costs one, wisp pair costs two,
bulwark/major manifestation two. Capacity restricts simultaneous presence,
cooldowns/charges restrict replacement. Gear can author extra capacity. Do not
make Job capacity an arbitrary universal cap on all equipment entities.

### Captor — isolation, restraint and live extraction

| Skill | Type | Behavior |
|---|---|---|
| Entangle | S/A | Capture tool required. Brief Bind attempt against a nearby enemy; no lethal damage or automatic unconsciousness. |
| Draw Aside | S/A | Capture tool required. Pull a reachable target one tile toward a valid space; explicit resistance check. No pulling through walls. |
| Patient Restraint | S/P | A small bounded capture benefit against an isolated target with no adjacent allies. Does not remove boss resistance. |
| Pursuit Line | A | Short movement toward an isolated enemy; capture attempt remains a separate action. |
| Wide Net | A | Short-area Slow attempts against enemies; ordinary enemies not automatically all captured or immobilized. |
| Secure Binding | A | Consume an existing own Bind to improve one Subdue attempt. Failure removes that setup; never awards a prisoner on binding alone. |
| Close Escort | P | Lower carrying penalty for a living unconscious person, not unlimited weight or free remote extraction. |
| Defensive Restraint | P/reaction | After surviving a nearby attack, attempt short Slow against that attacker. Shares reaction allowance; no free Subdue check. |

Isolator (Draw Aside/Pursuit/Patient/Secure) creates a duel-like capture opening;
controller (Entangle/Wide Net/Reaction) suppresses threats while allies act. Solo
Captors can end enemy opposition by Subdue, but must not be forced into a starter
objective requiring structural destruction with their net. Preserving capture
restrictions means early missions need suitable alternate interactions/hirelings,
not secretly awarding every Captor a lethal net attack.

## Restraint, resistance and pits

- Restrained means conscious and on the map, with specific actions restricted.
  Bound units can still use allowed attacks/support. It is not unconsciousness,
  recruitment, a prisoner reward or automatically a defeated enemy.
- Subdue uses the existing balanced STR/DEX/INT capture check; success yields an
  unconscious unit. Extraction/secured-field recovery then determines prisoners.
- Repeated Bind needs recovery protection or diminishing reliability; currently
  the runtime CONTROL set does not include Bind. Implementation must handle this
  rather than claiming the existing stun protection already solves it.
- Defensive resistance can be a movement reduction, Braced state or conditional
  footing. A full immunity must be visible. Recheck resistance after interception
  or any actual target change. No blanket unexplained boss immunity.
- Shallow pits cause damage/disadvantage; deep recoverable pits need a route or
  escape action; lethal/bottomless hazards explicitly cause defeat. Define unit
  flight interactions and defeat/loot consequences before authoring lethal maps.
- Previews show destinations, resistance chances, collisions and pit outcomes.
  Blocked displacement is not always collision damage; the ability states it.
- Push/pull use legal short segments. Do not accidentally apply normal walking
  rules to permit a victim to walk around the obstacle they were pushed toward.

## Summon and device action rules

Action policy is authored per entity, not hardcoded by Job.

1. Autonomous entities follow a visible policy (nearest visible enemy, protect
   owner, or marked target). They do not consult concealed information.
2. Commanded entities move during the owner's activation and spend the owner's
   main action to attack/use their technique. The owner's personal movement
   remains separate, but movement must commit before a consequential command.
3. Autonomous attacks initially use a shared small output budget per owner
   activation. A wisp pair splits its authored output; it does not multiply full
   companion turns. Exact outputs vary by entity and must be measured.
4. Manual turret operation replaces its automatic firing opportunity, not both.
5. Newly deployed entities cannot attack for free immediately. Their timing,
   cooldowns and consumed budgets persist in battle state.
6. A player's direct units may reposition without free attack resets. Movement
   budgets never renew from switching between owner and summon.
7. Devices have footprints, HP, blocking rules and targetability. Placement checks
   forbid walls, occupied cells and inappropriate pits/water. Do not copy editor
   placement-only collision into combat pathfinding.
8. Automatic entities get no extra unrestricted initiative slots. Decide summon
   movement/attacks at explicit owner-linked events; status ticks occur once.
9. Incapacitating/extracting the owner stops autonomous attacks. A short existing
   effect may remain where explicitly authored, but it cannot fight indefinitely
   while its owner is dead or outside the map.
10. Summons are temporary, not roster recruits, capturable prisoners, loot farms,
    or sources of mission kill rewards/XP. Attribute credit to their owner without
    double counting the summon and owner. Equipment effects inherit only through
    explicitly allowed channels.
11. Commands, maintenance and dismissal use the same validated APIs for manual
    play, auto-battle and independent personality-driven turns. Owner personality
    influences broad decisions; entity policy governs its automatic targeting.
12. Once-per-encounter deployment is appropriate for major constructs, not every
    summon. Persist limits through reconnect/reload and encounter continuation.

This is extra board presence with measured output and costs, not a ban on strong
summoning gear. Some gear may explicitly break baseline limits; the rule must
still be authored, finite and testable.

## UI and AI

Creation shows Job and race as separate choices, a starter kit, the three starter
skills and brief build directions. Do not expose proficiency selection as combat
class selection. All twelve approved Jobs are available; existing Medic starts
need a migration plan with preserved medicine knowledge.

Combat groups Basic, Character, Equipment and Context actions. All equipped gear
actives remain accessible; favorites only pin shortcuts, never restrict access.
Use compact icons/names, remembered expansion, search for large lists, source
labels and cooldown/charge/disabled explanations. Passives/reactions have their
own inspectable effects panel. Show total resolved summon capacity/Components.

Selecting a controllable summon shows its current legal move/command options and
the cost to its owner. Clicking the owner returns to personal actions. Automatic
turrets show range, target policy and next firing opportunity. Preview area harm,
displacement, occupied routes, pit risk and generated board presence.

AI evaluates objective progress, prevention, setup, damage, useful control and
exposure, using the same legal actions as players. Hidden personality adjusts
risk/target priority; it is not skill eligibility or an excuse for broken kits.
Give constructs readable policies. Bound candidate tile/zone enumeration; no
multi-turn exhaustive search across every entity. Test auto and manual outcomes.

## Encounter pacing and rollout

Remove the universal twenty-round gameplay loss when implementing this system.
Use authored reinforcements, escaping targets, rituals, fire and objective damage
where appropriate. A sustain build can win a patient fight and lose a time-sensitive
one. Technical auto-resolution limits should pause/return unfinished state, not
invent a universal gameplay failure.

Implement in dependency order but publish all twelve Jobs together:

1. Activation timing, snapshots and ability validation.
2. Status ownership/expiry, Barrier/Mark, effects/conditions, displacement and reactions.
3. Small zones, form rules and owner-linked summon/device economy.
4. Loadouts, full gear action access, creation/combat UI and AI evaluation.
5. All starter kits; later skill catalogues tested through distinct builds.
6. Tune XP/unlock pace and existing encounter budgets; Champions later.

Release checks must include every Job in solo E-rank play, a two-character D-rank
party, capture and rescue, structures/doors, timed defense, resistant enemies,
concealment, pits and long sustain fights. Verify gear/summon combinations, reload,
repeat commands, status timing, control recovery, owner defeat and no duplicate
reward credit. Require each build to make different tactical choices, not merely
win by a different damage coefficient.

The original proposal was based on read-only inspection. Its first dependency
pass is now implemented and tested; COMBAT_ABILITIES.md documents live scope.
