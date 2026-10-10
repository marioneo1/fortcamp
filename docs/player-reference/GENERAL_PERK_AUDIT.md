# General perk audit
Historical design review, October 9, 2026. The implemented pool and final rules
are in [General quirks](GENERAL_PERKS.md); that catalog supersedes pending
values/scope below. Patient, Light Sleeper, Fidgety, Easily Winded, Tender-Hearted,
Cold-Blooded and Reliable remain event-based proposals, not runtime traits.
Approved recruit backgrounds are in RECRUIT_PERKS.md.

Names describe the person rather than an activated skill. Each exact modifier
must appear in its tooltip. MS means movement allowance; it is not initiative.
These traits can occur on zero-perk or mixed-perk recruit distributions later,
but do not make zero-perk recruits impossible or attach everything to everyone.

## User-supplied effects and recommended names
| Trait | Effect |
| --- | --- |
| Hearty / Robust / Stout | +5 / +7 / +10 maximum HP, respectively. |
| Sure-Footed | +5 evasion. |
| Resilient | 1% less incoming damage from all sources. |
| Lucky | +1 LUK. |
| Light-Footed | +1 movement. |
| Far-Sighted | +1 ranged attack range; eligible scope still needs agreement. |
| Heavy-Fisted | +3 fixed additional unarmed damage; multi-hit budget needs agreement. |
| Restless | 75% Sleep resistance. |
| Thick-Skulled | 75% Stun resistance. |
| Adaptable | +1 randomly selected attribute for this battle, rolled once at battle start. |
| Enterprising | +1 gold from a completed mission that already awards gold. |
| Frail / Sickly / Delicate | -5 / -7 / -10 maximum HP, respectively. |
| Wiry | -2 STR, +1 AGI. |
| Clumsy | -5 evasion. |
| Thin-Skinned | 1% more incoming damage from all sources. |
| Unlucky | -1 LUK. |
| Heavy-Footed | -1 movement, with normal mobile-unit allowance at least one. |
| Short-Sighted | -1 ranged attack range; eligible scope still needs agreement. |
| Distracted | -1 randomly selected attribute for this battle, rolled once at battle start. |

## Code-informed decisions to make
- HP: choose only one positive/negative constitution tier per character; keep
  maximum HP at least one. Avoid assigning -10 HP to a tiny animal automatically.
- Evasion: +5 is an evasion-stat increase, not five percentage points of dodge
  against every attack. Current penalties use 100% of evasion for ballistic,
  60% for melee, 30% for magic. Guaranteed hits still bypass ordinary evasion.
- Damage reduction: 1% is very small at E-rank damage values because damage is
  integer-rounded. Keep the proposed value if wanted, but do not advertise a
  guaranteed one-damage saving on every hit. Apply after normal damage modifiers.
- Movement: preserve genuine zero-movement states (Root/Bind, mounted machines,
  building, Bard Songs, stationary objects). The minimum-one rule only prevents
  this negative trait from taking a mobile character below one.
- Range: recommend affecting ordinary bow/crossbow weapon range and skills that
  inherit it, not spell areas or explicit fixed-range techniques. This is a
  recommendation; user said ranged classes, and Fortcamp permits weapons across
  Jobs, so do not silently broaden the eligibility rule.
- Unarmed: +3 after technique multipliers, with one shared extra-damage budget per
  multi-hit action recommended. Otherwise four punches gain +12 while one gains
  +3. Keep Rat Form's fixed-one-damage rule. Per-hit versus per-action is pending.
- Resistance: 75% means an application chance is reduced by 75%; a 100% Stun
  becomes 25%, a 50% Stun becomes about 12.5% before existing integer rounding.
  Recommend use strongest applicable resistance instead of summing to immunity.
- Random attributes: choose STR/DEX/AGI/VIT/INT/LUK once with a battle seed, save
  the chosen stat, update derived combat stats once, never change permanent
  character attributes or reroll on refresh/reload/form changes.
- Gold: award once on actual mission settlement to eligible participating
  characters, only if that mission awards gold. Do not trigger on kill loot,
  previews, replayed settlement or failed missions with no gold reward.
- Opposed pairs: avoid trivial cancellation such as Lucky + Unlucky on the same
  initial recruit. Do not block meaningful unrelated mixed strengths/weaknesses.
  Rarity probabilities and generic-pool generation remain unapproved.

## Additional options based on those ideas
These are optional alternatives, not approved effects.
| Trait | Proposed tradeoff or quirk |
| --- | --- |
| Broad-Shouldered | +1 STR, +1 VIT, -1 AGI. |
| Keen-Eyed | +1 DEX, +5 accuracy, -1 STR. |
| Scholarly | +2 INT, -1 VIT. |
| Athletic | +1 movement, -5 evasion. |
| Patient | +5 ranged accuracy after remaining stationary; moving removes it. |
| Impulsive | +2 initiative, -5 accuracy. |
| Cautious | +5 evasion, -2 initiative. |
| Hardy | 25% Burn damage resistance, without preventing Burn application. |
| Iron-Stomached | 25% Poison damage resistance, without preventing Poison application. |
| Light Sleeper | Sleep lasts one fewer activation, minimum one; separate from resisting it. |
| Stubborn | 25% displacement resistance, -1 AGI. |
| Fidgety | +1 AGI, -5 ranged accuracy when stationary. |
| Easily Winded | -1 movement after taking direct damage until the next activation. |
| Tender-Hearted | Better Resolve damage, weaker lethal damage; exact values pending. |
| Cold-Blooded | Better lethal damage, weaker Resolve damage; exact values pending. |
| Reliable | Once per battle, ignore an accuracy penalty from Fear; does not grant a guaranteed hit. |
| Superstitious | +1 LUK, -1 INT. |
| Meticulous | +1 DEX, -1 AGI. |

Recommend first adding clear HP tiers, Lucky/Unlucky and four small attribute
tradeoffs, then movement/range and control-resistance traits with manual balance
checks. Large trait count is useful variety, not a reason to stack many on one
character. No new history tags, quest triggers or canonical runtime IDs yet.
