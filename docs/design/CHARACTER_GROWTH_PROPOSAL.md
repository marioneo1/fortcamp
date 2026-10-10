# Character growth, rank and rebirth — discussion

October 9, 2026. **Shared stat migration implemented; growth/rebirth remain proposals.**
[Current formulas and limits](SHARED_COMBAT_STATS.md) supersede the historical
calculations below. Manual D map playtests remain parked.

## Chosen shared baseline — October 9

User delegated the fixed-base choice after reviewing the trials. Choose:

- HP before racial/perk adjustments: **12 + 4 × effective VIT**.
- Ordinary weapon Attack: **2 + floor(effective scaling attribute / 2) + weapon power + eligible combat training**.
- Apply Adventurer Rank once to allocated attributes, then add attribute bonuses
  from gear/perks and derive stats. Do not multiply the fixed bases, flat weapon
  power or the completed HP/Attack output again.
- Use the same ordinary body formulas for players and recruitable enemies;
  recruitment retains the body, rank, race and perks rather than switching formulas.
  Equipment removal/replacement may still legitimately change derived stats.
- Preserve explicit special-unit rules (e.g. 1-HP Wisps, 2-HP Sentries, Rat-form
  damage rules). A shared character formula is not a replacement for those mechanics.

An unmodified Human with VIT 6 / STR 6 has 36 HP / 5 unarmed Attack at E,
44 / 6 at D and 72 / 9 at S, before training/gear. Previous E values were 48 / 8.
With no fixed bases, the same E body would have 24 HP / 3 Attack: a much larger
starter reduction. That stat sensitivity was calculated, not combat-tested.

Reason: 12/2 retains a modest baseline for low-investment attributes, makes
allocation more influential than 24/5, and approximates current light-enemy
strength more closely. The controlled sample won 64/72 fights versus 56/72 for
shared 24/5 and 69/72 for live. This is a defensible starting design choice,
not proof of universal balance. Lower-base fights averaged 8.7 rounds versus
7.0 live; enemy Armor and gear need coherent reconstruction before migration.

This choice supersedes earlier "candidate/unapproved bases" language below.
The shared formulas, fresh enemy reconstruction and stat explanations are now
implemented together. Existing saved battles were not rewritten.
Other progression values (growth rolls/cost curve, rebirth requirements) remain
proposals unless separately confirmed.

## Deferred race pass: racial base HP and Attack

User requests that some races may have higher innate HP and/or higher base
Attack for meaningful variety. The selected 12/2 values are the neutral baseline,
not a requirement that every race have identical innate contributions.

Review racial flat HP/Attack bonuses or explicit racial base overrides during
the later race audit. Exact values and additive-versus-multiplier handling are
undecided; do not implement or assign bonuses now. Existing racial HP modifiers
remain part of the migration reference, not silently removed or compounded with
new bonuses. Use the same racial rules for player, enemy and recruited bodies,
and show each racial contribution in stat calculations. Balance against mobility,
armor, evasion, resistances and other racial strengths rather than making every
race strictly stronger. Fixed racial bonuses must not be scaled twice by rank.

## Historical pre-migration behavior and comparison

This section records the original investigation; use SHARED_COMBAT_STATS.md
for implemented rules. Comparison/trial evidence is preserved.

- Creator: six attributes begin at 4, plus 12 freely assigned points. Full
  allowance totals 36. One +1 costs one point; decreases refund one. Current
  UI range is 1–10. Unspent creator allowance is not a persistent growth ledger;
  backend clamps individual attributes, without enforcing this total budget.
- Player combat HP: `(24 + effective VIT × 4) × race HP factor`, rounded,
  then racial flat HP / perk HP with minimum rules.
- Ordinary weapon attack: `5 + scaling attribute // 2 + weapon power + combat
  training`. Armor begins with `VIT // 3 + racial Armor`, plus gear/perks/Job.
  Ordinary physical damage subtracts Armor; it is not a universal percent DR.
  Magical/status damage and other mitigation have their own existing rules.
- The roster `combat_metrics` DPS expression also differs from battle Attack:
  it uses the full scaling attribute, weapon power and half the combat capability.
  It must not be presented as the same value/formula when adding rank explanations.
  Prefer a shared canonical combat-stat calculation for roster and battlefield.
- Enemies currently have authored HP/attack/Armor budgets, alongside attributes.
  They do **not** all derive those combat values through the player formulas.
  Recruitment preserves authored attributes/specialties where a snapshot exists;
  allied combat recomputes HP/attack through player rules. Generic captives use
  a separate fallback attribute profile. Encounter-only boss HP is not a body grade.
- Existing D rank policy scales HP/attack/Armor and attributes independently from
  E-relative baselines. This is not yet a persistent personal adventurer-rank
  progression system. Guild mission access, Job practice and captive source rank
  are separate existing concepts.
- Audited D snapshots contain already-scaled attributes; their battle metadata
  records pre-rank attributes. A future migration must separate these before
  applying personal rank. Do not multiply already-ranked captured attributes again.

Read-only samples, without new mechanics:

| Character | Encounter HP / ATK | Stored attribute total | Pre-rank total | Allied HP / ATK after recruitment, before supplied gear |
| --- | --- | --- | --- | --- |
| E Human Road Enforcer | 28 / 5 | 28 | 28 | 44 / 9 |
| E Human Road Cutpurse | 22 / 4 | 27 | 27 | 40 / 8 |
| E Goblin Cutpurse | 24 / 4 | 27 | 27 | 28 / 8 |
| D Human Bandit Enforcer | 36 / 6 | 37 | 28 | 52 / 10 |
| D Goblin Boar Vanguard | 36 / 7 | 40 | 30 | 36 / 10 |

These are particular seeded samples; perks/gear change actual results. The
intended player creator allowance is 36 even when the player leaves points unused.
Do not infer a player's permanent allowance solely from their spent attributes.

## Recommended separation

1. **Adventurer Rank**: personal combat advancement, E→S. Proposed 1.0→2.5
   multiplier. Separate from guild mission eligibility and Job name/practice.
2. **Growth Grade**: the body's available allocation budget, excluding rank,
   equipment, temporary statuses and perk attribute bonuses.
3. **Job**: equipped techniques and class mechanics; not another numeric rank.

Two visible badges: `Adventurer D · Growth F--`. A trained character with a weak
body is valid; a talented but inexperienced character is also valid. Do not grade
potential from current HP, gear or a boss phase. Races retain their mechanical
identity without making every race require a different point-buy system.

Store base allocated attributes, total earned budget, unspent points and rank
separately. Ordinary respec refunds the earned budget; it must not erase body
advancement or turn gear/perk bonuses into permanently spendable points.
Preserve stable identity, specialty skills, memories/personality and loyalty.

## Illustrative budgets, not finalized balance

| Growth | Threshold budget |
| --- | --- |
| F--- | 21 |
| F-- | 26 |
| F | 31 |
| E | 36 |
| D | 41 |
| C | 46 |
| B | 51 |
| A | 56 |
| S | 61 |

The exact budget remains authoritative. An existing 28-point recruit would be
Growth F-- with 28 points, not rounded down to 26. A 30-point Vanguard before
rank also falls in F--. A reset cannot silently give it the player’s 36 points.
Below 24 total, six attributes at 4 are impossible; existing minimum 1 permits
redistribution, so 4 is a default distribution, not a mandatory floor.

Prefer fixed +5 advancement for the prototype, clamped at the shared final
ceiling. A 27-point recruit needs seven such advances to reach 61; a 36-point
player needs five; a 21-point recruit needs eight. Existing off-threshold budgets
must retain their legitimate points. Growth grade is a band, not six separate
variables for minus signs. Display one simple F badge on compact hover, with the
subgrade/point total in Details if repeated minus signs become noisy.

At 61 points, the current six-stat maximum of 10 is insufficient (capacity 60).
Attribute ceilings must be reviewed before approving these numbers. A rising
ceiling can preserve specialization; alternatively a new escalating cost curve
could be designed, but none exists now. Do not pretend +5 means less than five
attribute increases under current rules. Start with linear allocation for clarity.

## Rebirth and reset recommendations

- Normal redistribution: repeatable camp hall service, gold/medicine/food and
  recovery time. No in-combat respec. A rare item can waive some service costs
  for exceptional use; it should not be the only way to correct a build.
- Growth advancement/rebirth: separate, rarer service with personal advancement
  requirements and a meaningful milestone/trial. Guild progression unlocks the
  facility; it should not let an untouched new recruit instantly become max growth
  just because the player reached S. Costs/time/requisites are not finalized.
- Consider cheaper F→E rehabilitation so a beloved early recruit does not need
  seven full S-rank prestige loops merely to become viable. True E→S growth can
  require progressively harder milestones. This is a recommendation, not approval.
- Rebirth reallocates the body budget, with a choice to keep the current build
  and spend only new points. It need not remove Adventurer Rank or Job skills;
  repeatedly restarting ordinary rank would require an explicitly approved loop.
- Avoid permanent random +3…+7 gains. Five rolls range from +15 to +35: a
  20-point difference, over half the original 36-point allowance. +4…+6 still
  creates a 10-point difference across five upgrades. That can undermine loyalty
  to an unlucky favorite and encourage replacing/re-rolling characters.
- Variation is better supplied by existing perks, races, distribution and history.
  Naturally Gifted already supplies rare all-attribute bonuses separately from
  allocation. Prefer a shared reachable ceiling to automatic player +6/+7 gains;
  a unique player perk can express specialness without making companions obsolete.

## Critical formula decision before implementation

Do not multiply STR/VIT by rank, feed them into HP/attack and multiply that output
again. For a neutral unmodified Human at VIT 6, base HP is 48. D output-only
scaling gives about 62 HP; ranking VIT to 8 and then scaling HP gives about 73.

Two coherent options:
- Rank attributes once, then derive combat stats. Simplest shared stat model,
  but HP/attack will not rise by exactly 30% because their formulas include bases,
  equipment, integer division and thresholds.
- Derive from unranked attributes, then scale designated combat outputs once.
  Preserves the intended exact rank progression; allocated attributes remain
  the body/build values. Separate effective attributes for checks must never feed
  a second rank factor into those outputs. Recommended if 1.3× HP/attack is essential.

Unifying enemies with player formulas while keeping all existing numbers is
not possible through grading alone. Human VIT 5 currently implies 44 HP, not
28; even minimum VIT 1 implies 28 HP, above some authored 19–22 HP bodies.
Attack also has a minimum base above some light enemy budgets. Choices:
- Retain explicit encounter profiles for opposition for now; Growth grades apply
  to actual recruit attributes. Honest, least disruptive, but not full parity.
- Migrate in controlled mission batches to one shared formula, adjusting real
  attributes/equipment/legitimate conditions and revalidating fights. Best long-term
  consistency; cannot promise exact current outputs under unchanged formulas.
- Temporary explicit legacy modifiers can preserve numbers during migration,
  but must be visible/auditable and eventually reviewed, not disguised as Growth.

No gameplay refactor, budget assignment, rank labels or boss grades is authorized
in this brainstorming pass. Boss grading needs an actual base-attribute/profile
audit; large encounter HP alone cannot justify Growth D/C/etc.

## Proposed UI

Compact pointer-following hover: name, Job and two unobtrusive rank/growth badges,
combat summaries and truncated effects. Keep it noninteractive; do not reintroduce
nested calculation tooltips, scrollbars or heavy rendering that caused stutters.

Right-click Unit Details: fixed-size card, six-attribute compact grid, allocation
budget and Adventurer/Growth badges. Hover a stat to show base, source bonuses,
rank factor, temporary modifiers and final value. Distinguish ATK from predicted
damage against a particular target. Show physical flat Armor separately from
percentage reduction/resistance. Enemy legacy adjustments must be explicit.

Roster: base allocated attributes, gear/perk bonuses and total separately;
Growth budget and rank effects must agree with battle Details. Use existing
badge/button styling; no image generation is needed for letter-grade labels.

## Next decisions

Agree on shared formula versus retained encounter budgets, where rank multiplies,
fixed versus random growth, attribute ceilings, respec access, and personal
rebirth requirements. Then audit representative player/E recruit/D recruit/boss
profiles and draft the migration before implementing progression or UI.

## Follow-up discussion: accepted direction and open choices

User confirms below-E catch-up and preserving Adventurer Rank through rebirth.
User favors +4–6 random growth, without a lifetime-gain tally, as a tentative
direction; recognizes variation as desirable and expects S characters to compete.
User prefers scaling attributes once before deriving combat values, but remains
open to output scaling. No implementation requested. These supersede the earlier
fixed +5 recommendation where they conflict; numbers/costs remain discussion.

With +4–6 growth, five E→S upgrades yield 56–66 budget from a 36-point start,
averaging 61 if each result is equally likely. This is a 10-point extreme spread;
the 2.5× rank multiplier does not erase relative disparity. Do not give rolled
points a hard 61 ceiling if persistent S variation is intended. Growth Grade must
describe the achieved advancement stage, rather than require an exact threshold
budget; otherwise an unlucky S-stage character could be incorrectly labeled A.
Generated initial grades can still use reference budgets. Hiding the cumulative
gain tally does not make rolls unknowable: allocations/respec reveal the budget.
Keep current allocation/unspent points understandable; omit the historical tally.
Roll and persist once per successful advancement, never on opening a menu,
restarting, reallocating or cancelling a preview. No random system added yet.

Recommended cost curve to explore (not runtime): one point per increase through
10, two per increase from 11–15, three above 15. Example: 9→10 costs 1,
10→11 costs 2, 15→16 costs 3. This keeps every currently legal creator allocation
at its existing cost, while making extreme specialization more expensive later.
Costs apply to unranked allocated attributes only; 2.5× effective attributes do
not create a larger respec bill. Perks/gear remain nonrefundable sources.
Compare this curve with linear costs using endgame sample builds before approval;
ceilings, budget bands and how many raw increases a growth roll buys remain open.

Attribute-first rank scaling is reasonable for the desired tank/DPS distinction:
rank increases the attribute contributions; fixed HP/attack bases and flat weapon
power are not also multiplied. A neutral VIT 6 body has 48 HP at E and 84 HP at
S (VIT 15), whereas whole-output scaling gives 120 HP. STR 6 unarmed, ignoring
training, gives 8 attack at E / 12 at S under integer flooring (STR 15), versus
20 with whole-output scaling. These are illustrations, not a balance verdict.
Output scaling still respects distribution; neither option alone creates roles.
Role strength also depends on gear, armor, resistances, cooldowns and skills.
Normalize enemy/player calculations in controlled batches before replacing the
authored encounter profiles; preserve current E/D fights until that is approved.

### Guild advancement as currently implemented

Guild rank is account/camp mission access, not personal stat advancement.
Building the Guild Hall unlocks D. Runtime hall construction cost is wood 30,
stone 12, scrap 8 (progression overrides old source defaults).
Successive upgrades spend resources to unlock the next mission rank; no victory
quota/promotion trial and no automatic personal attribute bonus currently apply.

| Unlock | Wood | Scrap | Stone | Medicine |
| --- | --- | --- | --- | --- |
| C | 30 | 25 | 30 | 0 |
| B | 55 | 50 | 45 | 5 |
| A | 90 | 90 | 75 | 12 |
| S | 150 | 160 | 120 | 25 |

Recommended distinction: Guild Rank unlocks missions/facilities; Adventurer Rank
belongs to each character; Growth Grade belongs to the body. Promotion tests are
an optional future idea, not existing behavior or an agreed change.

### Weapons/items: parked future audit

User requests build-defining equipment, class restrictions and clear recommended
attributes in equipment/creation UI. Weapon power already contributes to the
ordinary attack pool used by many weapon techniques; generic on-hit statuses
exist. Coverage is not uniform: individual spells/skills use other calculations,
and some multi-hit techniques limit generic procs to one attack/volley budget.
Do not claim every weapon proc currently runs on every successful skill hit.

Future direction: classify attacks as weapon hits, spells, terrain/status damage
and so on; weapon effects explicitly state which events trigger them. Preserve
intentional per-hit Burn/enchants while distinguishing expensive reactions once
per attack/activation. Avoid recursive proc loops; separate physical and elemental
damage components so resistance applies correctly. Weapon fire rider damage
should not multiply accidentally with every skill multiplier unless specified.

Suggested item progression: commons reliable stats or a modest handling effect;
uncommons one clear interaction; rares/uniques a build-defining mechanic with
explicit trigger rules. Examples under discussion: weapon-hit Fire/Burn,
slower attack with greater armor piercing, shield/barrier interactions, critical
or conditional effects, and tradeoffs rather than universal best-in-slot power.
User wants exciting mechanics before aggressive nerfs; no new items/effects yet.

Prefer hard requirements where the equipment/skill needs them (bows, shields,
mounting constraints) and class proficiencies/compatibility for other choices.
Review strict class whitelists carefully: Captor equipment on other Jobs is an
explicit existing design promise; blanket restrictions must not break it.
Equip requirements, scaling and recommendations must be distinct labels.
Proposed UI examples: “Requires STR 8”; “Scales with DEX”; “Recommended for Ranger.”
At creation: short Job-relevant stat recommendations, without auto-locking builds.

Next: agree on attribute-first versus output-first rank, linear versus graduated
allocation costs, and +4–6 advancement semantics; simulate tank/DPS/hybrid builds.
Then plan formula migration and the separate equipment audit. No gameplay/UI
changes in this discussion.

### Confirmed migration/equipment decisions

User confirms cross-Job capture equipment must remain available. Bows, shields
and particular techniques require compatible gear; future skill definitions should
declare compatibility explicitly. Equipment UI distinguishes Requires, Scales with,
and Recommended for; recommendations are not equip restrictions.

Growth Grade represents the advancement stage completed, not a rigid cutoff
in attribute totals. Initial enemy grade assignment is a reconstruction task:
choose coherent Adventurer Rank, Growth stage and allocation, then racial traits,
perks and equipment, to approximate the enemies' previous overall combat strength.
User clarifies "somewhat the same," rather than exact preservation of every HP/
attack value. Retain current role identity and encounter difficulty as reference;
do not use current encounter HP as a direct Growth-grade conversion.

The requested offline next step is now complete: see
[Growth comparison](CHARACTER_GROWTH_COMPARISON.md), generated by
tools/compare_character_growth.py. It checks 13 current E/D profiles using their
unranked snapshots and 24 endgame body examples. The lower fixed-base option is
an experiment, not an accepted formula. Shared-base selection and real combat
trials still precede runtime reconstruction, Growth assignment and migration.

Follow-up combat trial now complete: [Shared-stat trial](CHARACTER_GROWTH_TRIAL.md)
and its per-fight CSV. 216 isolated fights, all four layouts of Toll/Highway/Bone,
six starter Jobs, two Human allies; zero errors/stalls. Current formulas win
69/72, shared current bases 56/72, lower shared bases 64/72. Average rounds:
7.0 / 8.4 / 8.7 respectively. Recommend the lower 12 HP / 2 Attack bases as the
next reconstruction candidate, not an approved runtime replacement. These are
fixed formula bases, not total HP/Attack. Attribute-derived contributions and
flat gear/training remain additional sources.

All lower-base losses are Ranger auto-play; do not retune that Job from this
sample. The trial preserves player gear/perk contributions and enemy perk
attributes/HP, but removes authored enemy Armor overrides and invents no enemy
weapon/training bonus. Actual enemy builds/equipment still require reconstruction.
It also introduces proposed personal D rank in both shared arms; live players
currently have no such rank bonus. Wider-race/manual review precedes migration.

Before runtime migration, produce representative before/after profiles showing
HP, attack, armor, relevant attributes and any gear/perk effects. Compare effective
durability, skill damage and action economy rather than merely matching attribute
sums. Document unavoidable differences under the chosen shared formulas; do not
hide unexplained encounter multipliers to force exact matches. No blanket changes
to existing battles or grading assignments are authorized in this discussion.
