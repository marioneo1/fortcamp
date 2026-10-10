# E-rank combat audit

## October 9: shared body migration

[Current stat rules](SHARED_COMBAT_STATS.md) now govern fresh ordinary humanoids
and recruits. Earlier HP tables below are historical authoring targets; rounded
VIT/racial allocations can differ. Supply/worksite targets were adjusted to keep
the 15% variation budget band. Species kits remain authored; saved battles remain.
All exposed layouts of 14 E plus three D missions are in the
[396-fight smoke audit](SHARED_COMBAT_STATS_AUDIT.md), with no errors/stalls.
Capture parity is tested across all audited humanoid layouts. Support Jobs,
other races and manual playtests remain outside this auto-play evidence.

## October 9: Hedgerow preparation rework

The user replaced the older defenses after the final map batch. Base allotment is
now 12 + 4 per defender; 1-point barriers have no separate count cap, pits cost 2,
and proximity bombs cost 3 / 2 with an Engineer. Equipped Engineer deployments
and Rogue Caltrops are free; machine caps still apply, with one Engineer mine.
See [current rules and validation](DEFENSE_PREPARATION.md). Enemy layouts/HP and
keeper victory conditions are unchanged. The 32 combat samples recorded below
precede this preparation rework and are not a fresh balance claim for the new menu.

## October 9: final defense/rescue batch implemented in dev

All **14 missions in this combat audit scope** now have authored opposition and
variation coverage. This does not mean every noncombat E-rank quest has been audited.

| Mission | Variations | Opposition | What changes |
| --- | --- | --- | --- |
| Hold the Hedgerow Watch | Northern / southern advance, split raid, staggered column | 4 × 24 HP or 5 × 20 HP Goblins | Roles, flanks and grouping; preparation and Keeper Mara protection remain. |
| Bring the Captive Home | Halted wagon, inspection, muddy escort, changing guard | 2 × 28 HP or 3 × 20 HP Goblins | Escort count/roles, wagon and captive positions; carry out or secure the field. |

Those are base encounter HP budgets before rolled general perks. Four/five-raider
defense totals are 96/100 HP; two/three-escort rescue totals are 56/60 HP. More
bodies have lower individual ATK. Enemies use existing Fighter/Rogue/Ranger kits,
specialties, recruitment snapshots and wordless Goblin voice packs, not generic
boss flags or 10–18 HP filler. No new skills or Jobs were introduced.

Defense includes a visible wooden warning post using the current structure art,
an open road, fields and wooded flanks. Keeper and post cells are excluded from
deployment. Its actual win condition remains repel all raiders with the keeper
alive, not an invented timed evacuation countdown. Objective text now says so.

E-rank rescue now has its own `prison_rescue_e` encounter and four generated maps.
The original **D-rank Captive Cart** and higher-rank prisoner rescue definitions
remain unchanged. Dispatch-satchel/cartmaster story prizes do not leak into this
E-rank allegiance mission. Extraction/carrying and field-secured rescue rules are
shared; objective completion looks up IDs rather than assuming three objectives.

Test in Battle Lab: **Hold the Hedgerow Watch** (normally two defenders) and
**Bring the Captive Home** (normally one), Direct map test, then select each layout.
Already-running battles retain their old roster; start a fresh test after loading
the updated backend. No production push or live-save migration in this pass.

Validation: eight-layout connectivity/nonoverlap and carried extraction checks,
recruit kit persistence, repeatable layouts, original D-cart compatibility and
existing battle/mission regressions. Small automated balance sample: 32 fights
using Fighter/Barbarian/Monk/Rogue; solo rescue and paired defense, one seed per
layout/job. **31 wins, one Rogue inspection-rescue loss, zero errors or stalls.**
This is a smoke sample, not a claim of universal win rate. Per user direction,
no extensive manual solo-support equalization; support/setup jobs may be weaker.
Manual difficulty/visual review remains open.

October 9 presentation pass: all currently audited humanoid layouts opt into
Human/Goblin race/gender/personality wordless combat vocals. Three attack, hurt
and death variants per supported identity, preserved through recruitment. Existing
animal sounds stay separate; no encounter stat, count, story or reward changes.
See ../art/ENEMY_VOCALS_V1.md. New voice metadata needs backend reload; saved
audited enemies have a frontend fallback from their existing identity fields.

## October 9 — prisoner batch 4 and recruit backgrounds

All four variants each of Break the Rival Warband (prison_rival_e), End the Old
Command (prison_former_e), and A Promise Proven in Battle (prison_proof_e) now
use two authored recruitable enemies. Opposition is 48–56 total HP; variation
ratios stay within 15%. Placement, actual usable closed doors and current timber
structure art are retained, not replaced by generic open arenas. Access tests
open legal doors before checking reachability; this is not a claim doors are
already open at encounter entry. All twelve variants have nonoverlapping units,
reachable enemy positions and no generic boss inflation. Story gating, objectives,
reward and noncombat route definitions are unchanged.

Kits: Enforcer/Trapper/Skirmisher on rival road; Warden/Bruiser and mixed
support on former command; Bruiser/Warden/Skirmisher/Lookout at proof yard.
See [short enemy reference](../player-reference/ENEMY_SPECIALTIES.md).
Background perks include a no-perk outcome and modest stat tradeoffs; recruit
snapshots preserve their actual learned skills, traits and personality. Normal
Job starters are added as learned options, without rewriting equipped order.

432 fresh Human/Fairy/Ogre starter-loadout auto fights: 385 wins, zero exceptions.
Rival: 132/144; former: 129/144; proof: 124/144. Fighter/Barbarian 36/36 each,
Rogue/Ranger/Monk 35/36 each, Mage 32/36, Cleric 34/36, Summoner 33/36;
Bard/Druid 28/36, Engineer 26/36, Captor 27/36. Support/setup solo auto-play
is weaker and remains a manual-playtest concern, not a reason to change their
identity or claim human-tested balance. Report: data/audits/e-prison-perks-v3.json.
An earlier discarded run exposed missing team metadata on environmental damage;
the hook is fixed with a regression test. Do not cite the invalid v2 run.

Additional regression across all 26 variants of Toll/Pickpockets/Well/Supply and
the three worksites: 312 Human auto fights, 261 wins, zero exceptions. Engineer
8/26 remains especially weak in auto-play; manual construction/positioning should
be reviewed. Report: data/audits/e-background-regression-v1.json. Previous batch
numbers below are historical results before specialty/background additions.

169 backend tests, including recovery, capture starter skills, twelve-map access,
perks and mission routing, pass. Background/general definitions are separate from
slotted skills. New general positive/negative perk expansion is still proposed.
Remaining E-rank audit scope: Hedgerow Watch and Bring the Captive Home. Fresh
dev battles require a backend restart with reload off; existing encounters and
characters are not rerolled. Production untouched; no browser playtest claimed.

## Remaining E-rank inventory, October 8

User reports first-batch encounters feel good; continue three missions at a time.
Final mission catalogue and tactical registry identify the following remaining scope:

| Batch | Missions | Notes |
| --- | --- | --- |
| Completed: ordinary combat | The Goblin Pickpockets; Movement at the Old Well; The Small Supply Watch | Four layouts each; authored recruitable roles, 19-28 HP, 3-5 ATK; see batch 2 below |
| Optional combat at work sites | Timber Across the Creek; The Locked Tool Shed; Herbs Behind the Wall | Goblin opposition; two/four/four layouts; preserve noncombat mission identity and choices |
| Defense | Hold the Hedgerow Watch | Dedicated defense path, not ordinary contract presets |
| Prisoner stories | Break the Rival Warband; End the Old Command; A Promise Proven in Battle; Bring the Captive Home | Keep personal-story conditions/objectives; rescue has a dedicated map path |

Batch-two implementation and validation are recorded below. Ordinary
Pickpockets and Well descriptions explicitly specify two enemies; vary their
roles, gear and arrangement rather than silently contradicting those counts.
Supply Watch has no explicit count, permitting modest count variation.

## Scope and method — batch 1, October 8, 2026

Three missions per batch: Rats in the Storehouse, The Unwanted Toll, Wolves at
the Fence. Compare the actual compiled maps, final mission catalogue and combat
creation path. Do not rebalance all E-rank encounters through one global rookie
override. No changes to production, saves, starter Job kits or rewards.

All three belong to **The Briar Ford Watch** (`frontier_watch`), maintaining local
supplies and safe routes while the watch tracks the Black Banner/Meridian
threads. None of these three directly advances a decision branch or unlocks a
new narrative mission. Their premise is local clearance; preserving provisions
is narrative motivation, not an implemented sack-destruction timer.

## Map/story and opposition decisions

| Contract | Lore and map checks | Revised opposition |
| --- | --- | --- |
| Rats in the Storehouse | Provision shed variants contain grain, barrels, storage chest and delivery tools; the twin-store variant keeps both stores relevant | Two to four rats with count-adjusted HP/ATK; regrouping swarms/Gnawing Weakness; see composition table |
| The Unwanted Toll | Toll-post road variants preserve the road obstruction, gate and withdrawal approach; exactly two opportunists, as the story specifies | Human Fighter enforcer: 28 HP/5 ATK/1 armor/move 3; Human Rogue cutpurse or mixed Road Trapper: 22 HP/4 ATK/0 armor/move 4 |
| Wolves at the Fence | Fenced farm clearing variants contain hay, trough, farm tools and scarecrow; wolves threaten the clearing, not a humanoid military camp | Two to four wolves with count-adjusted HP/ATK; pack-positioning/Bleed traits; see composition table |

Initial deployment now uses an authored cluster or separated formation per layout;
delivery-court rats also use two collision-checked outdoor cells. Buildings,
exits, doors, props and collision definitions are preserved. Four variants per
mission are checked for distinct, clear deployment;
existing location tests check doorway/exit connectivity across generated seeds.
The two bandits are ordinary humanoids, not a chieftain with boss resistance.

The enforcer retains Fighter Driving Strike/Intercept. The repeatable authored
layout gives the second bandit either the standard Rogue kit or the **Road
Trapper** specialization: Cheap Shot, Road Bola and Exploit Weakness. Road Bola
is a ranged 50%-power attack with Hobble for two turns and a three-activation
cooldown. This is an authored mixed kit, not a new starter Job. Unit Details
shows specialization and equipped techniques. Recruitment preserves learned
skills, equipped skills and personality; equipment still follows normal inventory
rules and encounter stat budgets do not become permanent roster stats.

## Baseline problem and racial adjustment

Previously all six beginner combat contracts used two enemies with 10/7 HP,
3 ATK and zero armor, overriding racial rank budgets. This allowed an entire
encounter's opposition to sit below ordinary skill damage thresholds.

At identical starter Fighter attributes/equipment, Human/Fairy/Ogre had
48/25/81 HP respectively. Fairy now has 36 HP; Ogre 69. The original flight,
movement, evasion, initiative and armor differences remain. At VIT 6 before
perks, the same HP formula changes Human/Fairy/Ogre from 48/25/81 to 48/36/69.
This affects newly created battles using these races throughout the game, not
just these three contracts; already saved battle snapshots are not rewritten.

Ogre remains a slow armored bruiser. No one-tile movement floor or loyalty cap
was introduced. These need separate usability/design consideration rather than
silently changing the character-autonomy system.

## Validation record

`tools/audit_beginner_combat.py` creates isolated fresh starter states, uses real
combat creation and existing balanced auto-play, and never reads/writes player
saves. Compare the same seeds/loadouts before and after. Recorded errors count
as errors, never wins. A forty-player-step simulation limit is a harness bound,
not an in-game defeat rule.

The first baseline (one seed, twelve Jobs, Human/Fairy/Ogre, three contracts =
108 runs) gave every ordinary Job except Engineer/Captor 9/9 auto-play wins.
Engineer also exposed an existing generic-handler dispatch error: unsupported
Engineer techniques could reach the generic ability resolver. They now remain
in Engineer's dedicated auto handler. A regression test covers that fallback.

Behavior tests verify species geometry, incapacitated neighbors, forecast/hit
agreement, no pack bonus/proc inheritance on DoTs, actual enemy Driving Strike,
recruitable Job persistence and the narrower racial HP spread. Numerical auto
results and their limitations follow.

Historical pre-swarm auto-play: three seeds x twelve Jobs x three races x three
contracts = **324 runs, 287 wins, zero exceptions**. Results per Job (out of 27):

| Job | Wins | Mean round reached |
| --- | ---: | ---: |
| Fighter | 27 | 8.9 |
| Barbarian | 26 | 8.5 |
| Rogue | 27 | 8.7 |
| Ranger | 26 | 8.2 |
| Mage | 27 | 8.1 |
| Cleric | 26 | 9.9 |
| Monk | 27 | 7.6 |
| Bard | 21 | 10.3 |
| Druid | 22 | 9.5 |
| Engineer | 6 | 22.0 |
| Summoner | 27 | 8.4 |
| Captor | 25 | 10.0 |

These are starter three-skill kits at baseline attributes, not five-slot endgame
builds. Mean round includes losses/step-limited cases and is not mean win time.
Totals by race: Human 95/108, Fairy 92/108, Ogre 100/108. An additional legal
basic-attack-only probe, retaining original gear/stats/loadout but foregoing
techniques, won 25/27 for both Bard and Druid (54 runs). This shows their normal
auto choices matter; it does not prove the remaining losses are solely AI bugs.
Engineer still needs a dedicated auto-behavior/setup pass; do not weaken these
encounters merely until its current AI wins. Manual kiting, positioning,
construction choices and unlocked loadouts are not validated by these runs.

Raw isolated results are in ignored `data/audits/e-batch-1-*.json`; reproduce with
`tools/audit_beginner_combat.py --seeds 3 --races Human Fairy Ogre`. Use
`--jobs bard druid --policy basic` for the alternate probe. No manual browser
playthrough or full race audit is claimed.

Validation: 46 focused encounter/location/loadout/ability tests and 194 broader
DoT/impact/feedback/tactics/capture/recruitment/faction/mission tests pass.
The broader pass also corrected three stale tests from the earlier Resolve
rework: capture equipment retains ordinary Attack, and capture tests must use
Resolve plus the current capture-roll hook rather than HP and an old RNG mock.
Python compilation and whitespace checks pass. That earlier balance pass did not change frontend assets; the following behavior
pass adds presentation using existing painted attack/status assets.

## Next batches / unresolved design

### Encounter composition refinement

User clarified that variations include enemy count, type/role, grouping and
apparent activity, with only small difficulty differences within the same quest
rank. Each of the four layouts now has a deterministic authored opening setup:

| Mission / layout | Opposition | Opening arrangement |
| --- | --- | --- |
| Rats 1, long shed | 3 rats, each 17 HP / 3 ATK | Cluster feeding around interior stores |
| Rats 2, twin stores | 4 smaller rats, each 14 HP / 2 ATK | Separated across both stores |
| Rats 3, rear annex | 2 larger rats, each 25 HP / 4 ATK | Together near the annex |
| Rats 4, delivery court | 4 smaller rats, each 14 HP / 2 ATK | Two inside, two on clear ground outside the east side |
| Toll 1, gated court | Enforcer + Cutpurse | Together blocking the court |
| Toll 2, through-road hall | Enforcer + Trapper | Separated forward blocker and rear control |
| Toll 3, inspection wing | Enforcer + Trapper | Close formation near the wing |
| Toll 4, watch posts | Enforcer + Cutpurse | Covering separate posts |
| Wolves 1, broken rail | 3 wolves, each 22 HP / 4 ATK | Cluster near the fence |
| Wolves 2, offset clearing | 2 tougher wolves, each 31 HP / 5 ATK | Separated positions |
| Wolves 3, twin paddocks | 4 lean wolves, each 17 HP / 3 ATK | Spread across the paddocks |
| Wolves 4, deep pasture | 3 wolves, each 22 HP / 4 ATK | Spread approaches |

Rats retain movement 4/armor 0 and existing swarm/Weakness; wolves retain movement
4/armor 0 and existing pack/Bleed mechanics. Total rat HP stays 50-56 and summed
ATK 8-9; wolf HP 62-68 and summed ATK 10-12. These are initial budget bounds,
not proof of equal difficulty: initiative, AoE, pack pressure and approach timing
matter. No added enemy race, boss, Job, loot multiplier or reinforcement.

Toll description explicitly promises two opportunists, so count stays two and
variety comes from existing roles and formation. Rat/wolf descriptions do not
promise exact counts. Activity is conveyed by starting position, existing map
props and a short opening History line; no new feeding/patrol idle animation or
passive state is claimed. All current species/personality AI remains active.
Outdoor spawn selection checks real collision, bounds and unit occupancy.
New battles receive the changes; saved battles retain their snapshots.

Earlier numerical tables describe the old fixed-count setups. Composition-run
results are recorded separately below; do not cite old win rates as new balance.

Composition validation: **432 runs, 377 auto-play wins, zero exceptions**, matching
the previous overall win total on the same twelve Jobs, three races and four
presets. This aggregate match does not prove equal difficulty per layout.

| Mission | Layout 1 | Layout 2 | Layout 3 | Layout 4 |
| --- | ---: | ---: | ---: | ---: |
| Rats | 30/36 | 32/36 | 35/36 | 33/36 |
| Toll | 32/36 | 31/36 | 34/36 | 29/36 |
| Wolves | 29/36 | 29/36 | 33/36 | 30/36 |

Human 123/144, Fairy 118/144, Ogre 136/144. Engineer 16/36 and Captor 22/36
remain weaker in auto-play; do not confuse their setup/decision limits with
demonstrated unavoidable mission failure. Keep individual layouts under manual
review, particularly toll 4 and wolf openings. No claim of exhaustive RNG,
party/loadout coverage or actual browser playthrough of new compositions.
Raw output: ignored data/audits/e-batch-1-compositions.json.

Validation: 27 encounter/profile/location tests plus 33 Battle Lab/starter/map
tests pass. Coverage includes exact counts, bounded combined HP/ATK, clear unique
deployment, the outdoor/indoor split, deterministic human roles and recruitable
skills. No frontend asset or animation changes; no frontend build required.

October 8 coverage follow-up: all four layouts already receive profile and
deployment checks, but earlier post-swarm combat runs sampled only two layouts
per mission. `tools/audit_beginner_combat.py --all-variants` now explicitly uses
all four Battle Lab presets per mission instead of a random seed sample. It
does not alter encounter mechanics or player saves. Results recorded below
distinguish automated coverage from manual playtesting.

### Explicit all-layout run, after swarm/AI changes

`--all-variants --races Human Fairy Ogre` produced 432 runs: twelve starter Jobs
times three races times three missions times four authored presets. Every
mission/layout has 36 runs. **377 wins, zero exceptions.**

| Mission | Layout 1 | Layout 2 | Layout 3 | Layout 4 |
| --- | ---: | ---: | ---: | ---: |
| Rats in the Storehouse | 31/36 | 33/36 | 34/36 | 36/36 |
| The Unwanted Toll | 28/36 | 31/36 | 30/36 | 29/36 |
| Wolves at the Fence | 28/36 | 35/36 | 32/36 | 30/36 |

By race: Human 123/144, Fairy 120/144, Ogre 134/144. By Job: Fighter/Rogue/Monk
36/36 each; Ranger/Mage 35; Summoner 33; Barbarian/Cleric 32; Bard/Druid 31;
Captor 22; Engineer 18. These totals measure current auto-play, not fair human
difficulty or validated five-skill builds. One preset seed per layout is not
exhaustive RNG, party-composition or humanoid-kit coverage.

Next inspect toll layouts and wolves layout 1, separating geometry/targeting/AI
issues from actual encounter strength; retain Engineer/Captor setup caveats.
Do not weaken enemies just to maximize auto-play wins. No encounter stats changed
in this follow-up. Raw results: ignored data/audits/e-batch-1-all-variants.json.
Fourteen location/profile tests pass; audit tool compiles and whitespace check
passes. Manual playthroughs of all twelve layouts remain unclaimed.

2. Goblin Pickpockets, Movement at the Old Well, Small Supply Watch.
3. E-rank prisoner rival/former/proof contracts, tracing their recruitment links.
4. E-rank prisoner rescue and Hedgerow defense.

Continue in batches of three until geometry/lore/kit/balance checks are reliable;
then consider five. Add new humanoid specializations only when an existing Job
or authored mixed loadout cannot express their role. Animals retain species
abilities. Broader personality planning, additional encounter kits and full race balancing
remain future batches; the scoped behavior pass below is implemented.

## Species and personality behavior pass - October 8

- **Rats:** successful direct bites apply Gnawing Weakness, not Poison. Each
  stack reduces damage dealt by 5% and increases damage received by 5%, capped
  at 30% for each effect regardless of stored stacks. At the affected unit's
  activation end, remove one stack. HP/max HP never change from Weakness.
- Healthy rats attack. Wounded rats seek a compatible nearby rat, approaching
  a legal adjacent cell to merge as their main action. At most **three rats
  total** share one swarm. Current/max HP, ATK and Resolve sum without healing:
  5/8 plus 9/9 becomes 14/17. The absorbed rat leaves initiative without a
  corpse, death proc or extra activation. A swarm retains one normal activation.
- Swarm bites form one combined damage packet with a short lunge per rat;
  each landed attack applies Weakness equal to its rat count. The merge retains
  the donor visually until contact and updates the receiver HP at that point.
  Combining status state does not cleanse the swarm. No splitting is implemented.
- Wolves select a shared pack target and prefer free cardinal flanks, particularly
  opposite a packmate. Existing pack damage and Bleed remain; wolves never merge.
- Wounded bandits below half HP seek safer reachable cells near a healthy ally
  and Guard when withdrawing. Guardian enforcers prioritize threats to wounded
  partners; opportunist cutpurses favor wounded victims; strategist trappers
  use Road Bola before closing when possible. Forced targeting overrides regroup
  and withdrawal. These are bounded heuristics, not simultaneous team planning.
- Sparse personality lines appear in combat bubbles and History: at most one
  per three rounds and once per tactical situation. No generated dialogue/API
  requests. Existing portraits, icons and effect art are reused.

Validation: 152 focused behavior/kit/mission backend tests and 393 frontend tests
pass, as do isolated browser merge/Weakness/dialogue/Unit Details checks and build.
Human starter simulations across two seeds, twelve Jobs and these three maps
completed 72 runs: 61 wins, zero exceptions. Fighter/Rogue/Ranger/Mage/Cleric/Monk/
Summoner won 6/6; Barbarian/Bard 4/6, Druid/Engineer 3/6, Captor 5/6. Results are in
`data/audits/e-batch-1-swarm-ai.json`. Auto-play is a smoke test, not proof of
manual difficulty or all race/loadout balance. Actual iOS Safari and subjective
animation feel still require player testing. Newly created battles receive these
profiles; saved encounters are not rewritten. No production changes.


## Batch 2 - October 8, 2026

Implemented in dev: Goblin Pickpockets, Movement at the Old Well, Small Supply
Watch, all four existing layouts each. Existing structures, exits and props stay;
reviewed purse/cart/branches, well/pump/tub/ruins, grain/barrels/chest/cart dressing
against mission descriptions. Pickpockets and Well keep their stated two enemies.
Supply varies two stronger raiders versus three weaker pilferers. Deployment
alternates clustered/separated formations; no newly animated patrol/looting loops.

| Mission | Layout 1 | Layout 2 | Layout 3 | Layout 4 |
| --- | --- | --- | --- | --- |
| Pickpockets | Cutpurse + Lookout | Cutpurse + Snarer | Snarer + Cutpurse | Lookout + Cutpurse |
| Old Well | Guard + Lookout | Guard + Snarer | Lookout + Guard | Guard + Snarer |
| Supply Watch | Guard + Lookout | 3 Pilferers | Guard + Snarer | 2 Pilferers + light Lookout |

Guards use Fighter Driving Strike/Intercept; cutpurses/pilferers use Rogue Cheap
Shot/Crippling Cut; lookouts use Ranger Mark Quarry/Longshot and a sling; snarers
use Road Bola/Cheap Shot. These are recruitable specializations of existing Jobs,
not additional starter Jobs. Skills/personality survive capture/recruitment.
Guards: 28 HP, 5 ATK, 1 armor, move 3. Goblins: 24 HP, 4 ATK, move 4,
12% evasion. Other ordinary roles: 23 HP, 4 ATK; light roles: 19 HP, 3 ATK.
Total HP varies by at most 15% within each contract; Supply's three-body versions
have 9 total ATK versus 9 for the two-body version. Extra bodies still change
focus fire and target switching, so equal stat budgets are not exact equivalence.
None is a boss. Existing animal AI and first-batch tuning are retained.

All-layout Human/Fairy/Ogre runs: **432 fights, 371 wins, zero exceptions**.
Wins out of 36 per Job: Fighter 36, Barbarian 36, Rogue 32, Ranger 35,
Mage 36, Cleric 30, Monk 36, Bard 28, Druid 25, Engineer 13, Summoner 36,
Captor 28. Human 122/144, Fairy 112/144, Ogre 137/144. Across individual
mission/layout pairs, wins range 26-35/36 and mean duration 6.9-10.8 rounds.
Engineer's automatic setup and Druid's form choices remain limitations; do not
nerf successful Jobs to fit weak auto-play. Human playtesting is still required,
especially Supply's three-body openings and Well's Snarer layouts.

Reproduce: `tools/audit_beginner_combat.py --missions goblin_pickpockets ruined_well
supply_watch --all-variants --races Human Fairy Ogre --output data/audits/e-batch-2.json`.
Run with the checkout virtualenv Python. This default path excludes optional
radiants so normal rank difficulty remains measurable independently.

A 3% entry roll now adds an independent foraging bear to these same maps.
See [Radiant encounters](RADIANT_ENCOUNTERS.md) for saved rolls, ongoing skirmishes,
optional combat and loot rules. Known-seed same-map smoke run: 36 fights,
34 wins, zero exceptions. This is one seed across twelve Human Jobs/three maps,
not a substitute for every radiant/layout combination.

Final focused validation: 38 backend encounter/behavior/location/API/loot tests
passed; 411 frontend tests passed; frontend build passed with the existing large
chunk warning. A broader 128-test run exposed two pre-existing legacy capture
fixtures with obsolete RNG/Resolve assumptions (test_gear_expansion and
test_slot_gear); logged in backlog, production capture code left unchanged.
No manual browser/audio acceptance is claimed.


Runtime follow-up: reported 10/7 HP came from the dev session launched at 21:07
with reload disabled, before the 21:41 profile update. Fresh local construction
of all twelve layouts confirms 24/24 Pickpockets, 28/23 Well (order can reverse),
and 28/23 or 19/19/19 Supply. These compiled maps use current structure materials:
fieldstone for Well, timber for Supply; Pickpockets is an outdoor road with no
building shell. Existing shapes/layouts were retained, not fully rebuilt.

## Batch 3 - October 8, 2026

Implemented in dev: Timber Across the Creek (two bridge layouts), The Locked
Tool Shed and Herbs Behind the Wall (four layouts each). These are optional
guarded work sites: peaceful collection, the guarded-route choice, handover
and existing rewards remain unchanged. No fresh radiant roll is added.

| Mission | Layout 1 | Layout 2 | Layout 3 | Layout 4 |
| --- | --- | --- | --- | --- |
| Timber Creek | Guard + Sling Scavenger | 2 Pilferers + light Lookout | — | — |
| Tool Shed | Guard + Tool Snatcher | Snarer + Sling Scavenger | Guard + Snarer | 2 Pilferers + light Lookout |
| Herb Garden | Guard + Sling Scavenger | Snarer + Forager | 2 Foragers + light Lookout | Snarer + Sling Scavenger |

All are Goblins with move four and 12% evasion; guards have 28 HP/5 ATK/one
armor, ordinary roles 24 HP/4 ATK, light roles 17 HP/3 ATK. Total opposition
HP stays 48–52 and combined ATK 8–9. Three-body layouts trade durability for
numbers. Existing Fighter/Rogue/Ranger and mixed Road Bola kits survive
recruitment. Existing bounded guardian/withdrawal/snare/ranged AI is reused;
no new generic AI framework or starter class.

Lore/geometry review: creek retains repaired crossing routes, logs and planks;
sheds retain tool storage and damaged timber shells; garden retains herb beds,
potting/wash furniture and limestone boundaries. Structures already use the
current material system; no wholesale rebuild needed. All ten layouts have
distinct legal spawn tiles and reachable opposition after opening gates.
No enemy count is promised in the gathering descriptions. Scavenging activity
is indicated by placement and History text, not newly animated work routines.

All-layout starter-loadout Human/Fairy/Ogre simulation: **360 fights, 313 wins,
zero exceptions**. Wins out of 30 per Job: Fighter 30, Barbarian 30, Rogue 30,
Ranger 29, Mage 26, Cleric 28, Monk 30, Bard 25, Druid 24, Engineer 7,
Summoner 30, Captor 24. Human 100/120, Fairy 101/120, Ogre 112/120.
Layout win counts range 24–36/36; mean durations 7.9–10.9 rounds. The long
tool store is the hardest automated case (24/36); prioritize it for manual
testing. Equal stat budgets do not guarantee equivalent doorway geometry or
single-unit auto-play. Engineer auto-construction and Druid form selection
remain limitations, and one sample per race/Job/layout is not a balance proof.

Reproduce using virtualenv Python: `tools/audit_beginner_combat.py --missions
timber_creek tool_shed herbs_wall --all-variants --races Human Fairy Ogre
--output data/audits/e-batch-3.json`. Focused tests cover access, recruitment,
budget limits and peaceful choices; **135 mission/encounter/location/recruitment
tests passed**. No frontend code or assets changed in this batch.
Fresh battles require a backend restart when reload is off. Existing saved
encounters remain unchanged. No production update or human playtest claimed.

## General quirk integration - October 9
Authoring now uses the shared compatible generic pool as an occasional alternative
to a role background. About 20% of new humanoid encounter recruits remain perkless;
rare and exceptional quirks remain possible at E-rank. HP/VIT-changing generic
profiles are in the rare encounter tier, rather than common, to preserve ordinary
mission variation budgets. Animals do not receive this humanoid trait roll.
Captured recruits retain traits; ordinary generated recruits can acquire one
optional compatible quirk. Existing characters and encounters are untouched.
Structural tests continue checking all audited layouts and their actual HP totals.
These checks do not replace manual playtests or claim a new full simulation audit.
