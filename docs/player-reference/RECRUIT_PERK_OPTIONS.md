# Recruit perk options

Historical brainstorm. Approved effects are now implemented in dev; see
[current recruit perks](RECRUIT_PERKS.md). The newest generic pool remains proposed
in [General perk audit](GENERAL_PERK_AUDIT.md). Earlier names below are superseded.

Design review, October 9, 2026. Seven effects selected below; naming and exact
behavior still under audit. No runtime perk implementation in this naming pass.
These replace the rejected flat Survival/Scavenging/Medicine/Combat Capability
bonuses. Numbers and trigger limits need balance review before implementation.

## Selected effects and naming audit

### Latest naming direction and origin choices

User wants perk names to describe professions or personal quirks rather than
sound like activated techniques. The earlier names below are superseded naming
proposals; selected combat effects remain unchanged.

| Background | New recommended name | Meaning |
| --- | --- | --- |
| Road Trapper | Cunning Trapper | Leaves the defeat-triggered tripwire. |
| Bandit Enforcer | Intimidating | Killing an enemy intimidates nearby opponents. |
| Road Skirmisher | Sly Survivor | Uses the selected Play Dead behavior. |
| Goblin Slinger | Resourceful Slinger | Uses the selected ricochet behavior. |
| Goblin Ringleader | Opportunistic Leader | Grants the first ally attacking the current target an extra attack once per battle. |
| Warband Bruiser | Defiant | Uses Last One Standing; never triggers in solo missions. |
| Warband Warden | Relentless Pursuer | Uses the selected Broken Escape behavior. |
| Lumber mill worker | Lumberjack | +1 wood production when assigned to a lumber mill. |
| Quarry worker | Quarry Worker | +1 stone production when assigned to a quarry. |
| Salvage worker | Salvager | +1 scrap production when assigned to a salvage yard. |
| Herb garden recruit | Poison Tolerant | Ignores the first incoming Poison stack once per battle. |
| Timber creek recruit | Fast Builder | +1 defense-quest deployment allotment. |

Production perks are separate and apply only at the matching assigned workplace;
they do not grant all-resource bonuses or general capability points. Most NPCs
receive one of the three; having two or all three is possible but very rare.
Exact rarity probabilities have not been approved. Current production is hourly;
interpret +1 as one extra resource per hour worked, pending final implementation.
Do not add farm/herb-production perks or apply the bonus to unassigned camp work
without extending this design explicitly.

Poison Tolerant replaces the earlier Bitter Remedy cleanse proposal. It rejects
one stack application, not a damage tick or the entire multi-stack application:
incoming Poison x3 becomes x2 on its first use. Poison already present is not
cleansed, and subsequent applications proceed normally.

Fast Builder uses existing defense preparation budget as the proposed allotment
interpretation: +1 preparation point, not one extra party member or an Engineer
turret slot. Current defense objects have different point costs, so this does not
guarantee a free additional object of every type. Confirm terminology before coding.
No runtime perks or saved character names changed by this design update.

Road Trapper is an existing Rogue specialization, not a separate selectable Job
and not a perk. Keep that specialization name; give its perk a distinct name.
Current runtime names/IDs were searched: the seven recommended names below have
no exact matches in backend/frontend sources. Existing generic Trapper perk is
separate and still provides its legacy Survival capability bonus.

| Background | Recommended perk name | Alternatives | Selected effect |
| --- | --- | --- | --- |
| Road Trapper | Last Snare | Parting Gift; Final Tripwire | On defeat, leave one legal 1x3 tripwire at the fallen unit's location; prefer a placement excluding the killer, accept one hitting enemies if necessary, and skip if no legal strip exists. |
| Bandit Enforcer / Road Enforcer | Make an Example | Grim Example; Brutal Reputation | First kill each battle intimidates nearby enemies, reducing their outgoing damage; exact strength/radius/duration pending. |
| Road Skirmisher / Cutpurse | Feign Death | Play Dead; Death's Ruse | Once per battle, surviving a hit below 25% HP makes enemies deprioritize the user until they act; no actual unconsciousness or invulnerability. |
| Goblin Slinger | Ricochet | Bank Shot; Skipshot | A weapon hit against metal armor or machinery sends a weaker projectile into a nearby second enemy; exact weapon scope and trigger budget pending. |
| Goblin Ringleader | Press the Advantage | Follow Through; Seize the Opening | Once per battle, the first ally attacking the user's current target gets an extra attack against that same target. |
| Warband Bruiser | Last One Standing | Unbroken; Defiant Survivor | Once per battle, allies falling grants a temporary damage barrier; never triggers in a solo mission. Earlier 'last nearby ally' wording needs reconciliation with whole-party survivor intent. |
| Warband Warden | Cut Short | Broken Escape; Escape Punisher | First hit against an enemy who used a movement skill since the user's previous activation adds Hobble. |

Names are recommendations, not approved runtime renames. No new story tags or
quest IDs. Retain Road Trapper; normalize Bandit/Road Enforcer wording separately
if requested rather than renaming existing saved specializations silently.

Behavior points to settle before implementation:
- Last Snare needs a deterministic horizontal/vertical candidate search. Recommend
  genuine defeat only, not successful capture/reclaim; legal strip must include the
  fallen unit's cell, and failed placement must not create a partial strip.
- Press the Advantage should grant one extra Basic Attack, not repeat an expensive
  skill. Check target survival, range and line of sight before the bonus hit; never
  recurse into another extra attack. This is a recommendation, not a user decision.
- Feign Death changes AI priority and does not prevent deliberate attacks or AoE.
- Last One Standing must require an actual ally-loss event, not mere battle entry
  alone. Recommend counting original deployed companions rather than disposable
  summons so summon sacrifice cannot manufacture the trigger.

## Earlier alternatives (not selected unless listed above)

A background perk should carry across Jobs: a captured road bandit can become a
Mage and still have an identifiable history. Specialty skills remain separate.
Recommend one meaningful origin perk per recruit, selected from alternatives,
rather than granting every option below. Do not gate ordinary starter skills.
Strong options may need once-per-battle limits; extra attacks must not recursively
trigger reactions or other extra attacks. Movement must use legal destinations.

## Road Trapper
- **Slack in the Line:** The first enemy who escapes one of your traps leaves a visible trail for two activations, even after hiding.
- **Caught Red-Handed:** Your first hit against an enemy who triggered your trap since your last activation Disarms them.
- **Leave a Way Out:** Walking over your own trap disarms and retrieves it; an unused retrieved trap refunds part of its cooldown.
- **Tethered Prey:** A trapped enemy cannot teleport or leap until their next activation; ordinary movement remains legal.

## Road Enforcer
- **Pay the Toll:** Once per activation, an adjacent enemy voluntarily walking away takes a light weapon hit.
- **No Weapons at the Gate:** Your first hit against an enemy carrying loot Disarms them.
- **Collector's Due:** Defeating an enemy carrying stolen goods preserves that loot even if fire or an explosion destroys their body.
- **Make an Example:** Your first kill each battle briefly reduces nearby enemies' outgoing damage through Intimidation.

## Road Skirmisher
- **Through the Gap:** Once per activation, move through one enemy-occupied cell if the empty cell beyond is legal.
- **Slippery Exit:** Your first retreat skill each battle also removes Hobble.
- **False Opening:** Once per battle, an adjacent enemy who misses you becomes vulnerable to your next direct hit.
- **Borrowed Cover:** After retreating behind an ally, that ally's occupied cell provides cover against ranged weapon attacks through it until you move.

## Goblin Scrapper
- **Underfoot:** You can pass through allied occupied cells, but must finish on an empty legal tile.
- **Dogpile:** Your first hit each activation against an enemy already hit by an ally that round adds Hobble.
- **Too Small to Hold:** Once per battle, a successful enemy pull moves you to a legal tile beside the puller instead of causing occupied-unit collision.
- **Scrounger's Grip:** Once per battle, pick up an adjacent ground item as a Quick Action.

## Goblin Slinger
- **Bank Shot:** Once per activation, hitting metal armor or a machine sends a weaker stone into a nearby second enemy.
- **Broken Windows:** Ranged attacks can break eligible fragile props, opening a firing line without damaging the occupant.
- **Pocket Gravel:** Your first missed ranged attack each activation still briefly reduces the target's accuracy.
- **Duck and Load:** Ending your activation beside solid cover protects you against the next ranged weapon hit; moving removes it.

## Goblin Ringleader
- **You First:** Your first ally swap each battle clears that ally's Hobble.
- **Follow My Lead:** The first ally attacking a target you hit that round gains an accuracy bonus.
- **Nobody Left Behind:** Once per battle, retreating to extraction lets one adjacent downed ally come with you without first picking them up.
- **Pass the Blame:** Once per battle, after an ally hits an enemy targeting you, that enemy's forced-target restriction against you ends; it does not force them to attack the ally.

## Warband Bruiser
- **Dig In:** Voluntarily ending your activation without moving grants displacement resistance until you move again.
- **Break Their Shelter:** Direct hits against destructible cover deal extra object damage, without extra damage to units.
- **Stand Over Them:** Standing beside a downed ally prevents enemies from carrying that ally away while you remain conscious.
- **Last Fighter Standing:** Once per battle, the last nearby conscious ally falling gives you a temporary damage barrier.

## Warband Warden
- **Prisoner Handler:** Carrying a captured unconscious prisoner has a smaller movement penalty; ordinary downed units and corpses receive no benefit.
- **Search the Captive:** Successfully capturing a humanoid reveals and secures an extra carried item if they actually have one.
- **Keep Them Close:** Once per activation, pulling a Hobbled target adjacent to you also Disarms them.
- **Know Their Tricks:** Your first hit against an enemy who used a movement skill since your previous activation applies Hobble.

## Worksite / mission-origin alternatives
These are alternatives to combat-background perks, not automatic additional perks.

### Tool shed / salvage sites
- **Field Patch:** Once per battle, restore one HP to an adjacent owned machine as a Quick Action.
- **Salvage Before Sparks:** Reclaiming an undamaged deployment returns a small part of its build investment; destroyed machines do not qualify.
- **Pry It Loose:** Open an eligible stuck nonmagical door without destroying it, preserving cover and whatever is behind it.

### Herb garden
- **Bitter Remedy:** Once per battle, remove Poison from an adjacent ally, but briefly reduce their outgoing damage.
- **Poultice:** Before battle, protect one ally from their first Burn or Bleed damage tick; stacks remain.
- **Seeds in the Seam:** Once per battle, your first destruction of a wooden prop leaves a small patch of difficult terrain.

### Timber creek
- **Sure Footing:** The first slippery-ground movement penalty each activation is ignored; damage hazards still apply.
- **Make a Crossing:** Once per battle, an eligible fallen wooden prop can become a temporary one-cell bridge.
- **Clear the Way:** Destroying wooden cover does not leave movement-blocking debris.

## Recommended first shortlist
Underfoot, Pay the Toll, Slippery Exit, Bank Shot, Prisoner Handler, Field Patch,
Bitter Remedy and Stand Over Them. They express history through noticeable rules.

Implementation cautions: stealth trails, inventory-preserving destruction,
cover interception, improvised bridges and temporary targeting exceptions need
specific new hooks. They are design options, not claims that these systems exist.
Background tags, hidden histories and character-story rewards remain proposals
under ../design/CHARACTER_STORIES_PROPOSAL.md. No new canonical tags or quest IDs
are introduced by this option list.
