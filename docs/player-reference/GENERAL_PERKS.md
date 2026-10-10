# General character quirks
Implemented in dev, October 9, 2026. These are innate perks, not skill slots.

**61 new quirks.** Characters get variety, not the whole list; existing characters are not rerolled.

## Rules
- No Lucky + Unlucky, opposing movement/range/evasion/accuracy traits, or conflicting resistance tiers.
- Only one HP tier and one stat-redistribution profile, including existing Strong-Armed/Nimble/Bookish/Steady-Handed and random-stat traits. Naturally Gifted is a separate bonus and may coexist with those traits and Lucky/Unlucky.
- Unrelated strengths and weaknesses may coexist. Existing saved traits are preserved; new rolls and trait rewards reject conflicts.
- Low level and low mission rank never exclude rare perks.
- Naturally Gifted: **one-in-a-million opening roll**. It gives +1 to all six attributes and does not occupy a redistribution or luck tier; duplicate copies are still blocked.
- Ordinary generated recruits have a 40% chance of no additional general quirk; their existing archetype traits remain. Generic-roll tiers: 52% common, 7.5% uncommon, 0.5% rare, 0.0001% exceptional. An incompatible/empty tier adds nothing.
- Audited combat NPCs retain roughly 20% completely perkless outcomes. Usually they receive their role background; 20% of remaining ordinary outcomes try a general quirk, falling back to the existing small stat profiles. The exceptional opening roll can bypass the perkless outcome.
- HP/VIT-changing general traits use the rare tier on authored combat NPCs to protect ordinary map difficulty. They remain possible at E-rank. Existing background/profession rolls remain separate.

## Catalog
| Quirk | Effect | Rarity |
| --- | --- | --- |
| Hearty | +5 maximum HP. | Common |
| Robust | +7 maximum HP. | Uncommon |
| Stout | +10 maximum HP. | Rare |
| Frail | -5 maximum HP. | Common |
| Sickly | -7 maximum HP. | Uncommon |
| Delicate | -10 maximum HP. | Rare |
| Sure-Footed | +5 evasion. | Common |
| Clumsy | -5 evasion. | Common |
| Light-Footed | +1 normal movement; mobile units retain at least one tile. | Uncommon |
| Heavy-Footed | -1 normal movement; mobile units retain at least one tile. | Uncommon |
| Resilient | 1% less damage received from all sources. | Common |
| Thin-Skinned | 1% more damage received from all sources. | Common |
| Quick-Witted | +2 initiative. | Common |
| Slow to React | -2 initiative. | Common |
| Accurate | +5 accuracy. | Common |
| Inattentive | -5 accuracy. | Common |
| Heavy-Fisted | +3 unarmed damage per attack action, shared across its hits; does not affect Rat Form. | Uncommon |
| Weak-Fisted | -1 unarmed damage per attack action, shared across its hits; does not affect Rat Form. | Uncommon |
| Far-Sighted | +1 bow/crossbow weapon range for Rangers; fixed-range techniques are unchanged. | Uncommon |
| Short-Sighted | -1 bow/crossbow weapon range for Rangers; fixed-range techniques are unchanged. | Uncommon |
| Enterprising | +1 gold when a mission you participate in awards gold. | Common |
| Lucky | +1 LUK. | Common |
| Unlucky | -1 LUK. | Common |
| Wiry | -2 STR, +1 AGI. | Common |
| Broad-Shouldered | +1 STR, +1 VIT, -1 AGI. | Common |
| Keen-Eyed | +1 DEX, -1 STR; +5 accuracy. | Common |
| Scholarly | +2 INT, -1 VIT. | Common |
| Superstitious | +1 LUK, -1 INT. | Common |
| Meticulous | +1 DEX, -1 AGI. | Common |
| Brawny | +2 STR, -1 INT. | Common |
| Resolute | +2 VIT, -1 DEX. | Common |
| Quick-Fingered | +2 DEX, -1 VIT. | Common |
| Fleet | +2 AGI, -1 VIT. | Common |
| Frail Scholar | +2 INT, -2 VIT. | Common |
| Practical | +1 VIT, +1 STR, -1 INT. | Common |
| Athletic | +1 move, -5 evasion. | Common |
| Impulsive | +2 initiative, -5 accuracy. | Common |
| Cautious | +5 evasion, -2 initiative. | Common |
| Hardy | 25% less Burn damage; does not prevent its application. | Uncommon |
| Heat-Hardened | 50% less Burn damage; does not prevent its application. | Rare |
| Heat-Sensitive | 25% more Burn damage; does not prevent its application. | Uncommon |
| Iron-Stomached | 25% less Poison damage; does not prevent its application. | Uncommon |
| Toxin-Hardened | 50% less Poison damage; does not prevent its application. | Rare |
| Sensitive Stomach | 25% more Poison damage; does not prevent its application. | Uncommon |
| Thick-Blooded | 25% less Bleed damage; does not prevent its application. | Uncommon |
| Quick-Clotting | 50% less Bleed damage; does not prevent its application. | Rare |
| Bleeds Easily | 25% more Bleed damage; does not prevent its application. | Uncommon |
| Alert | 25% Sleep application resistance; uses the strongest applicable resistance. | Uncommon |
| Wakeful | 50% Sleep application resistance; uses the strongest applicable resistance. | Uncommon |
| Restless | 75% Sleep application resistance; uses the strongest applicable resistance. | Rare |
| Tough | 25% Stun application resistance; uses the strongest applicable resistance. | Uncommon |
| Unflinching | 50% Stun application resistance; uses the strongest applicable resistance. | Uncommon |
| Steadfast | 75% Stun application resistance; uses the strongest applicable resistance. | Rare |
| Brave | 25% Fear application resistance; uses the strongest applicable resistance. | Uncommon |
| Fearless | 75% Fear application resistance; uses the strongest applicable resistance. | Rare |
| Slippery | 25% Bind application resistance; uses the strongest applicable resistance. | Uncommon |
| Escape Artist | 50% Bind application resistance; uses the strongest applicable resistance. | Uncommon |
| Stubborn | 25% displacement resistance; −1 AGI. | Uncommon |
| Adaptable | +1 random attribute for each battle; rolled once, never changes permanent attributes. | Uncommon |
| Distracted | −1 random attribute for each battle; rolled once, attributes remain at least one. | Common |
| Naturally Gifted | +1 STR, DEX, AGI, VIT, INT and LUK. | Exceptional |

## Reading the numbers
- Evasion is a stat: +5 does not mean five extra dodge points against every attack. Ballistic/melee/magic use different evasion weights; guaranteed hits remain guaranteed.
- One-percent damage changes can round away on small hits. Damage resistance reduces the calculated hit/tick; it does not change status stacks or duration. Existing mitigation combines normally.
- Sleep/Stun and other application resistance uses the strongest applicable value. DoT-damage resistance is separate and never makes Poison/Bleed/Burn application fail.
- Heavy-Fisted shares its +3 budget across a multi-hit action, rather than adding +3 to each hit. It affects melee unarmed damage, not magic or Rat Form.
- A battle-start random stat uses the battle seed and stays in the saved unit; refreshes do not reroll it. Permanent character attributes stay unchanged.
- Ranger range quirks affect bow/crossbow weapon range, not fixed spell/technique ranges or AoE size. Movement penalties never undo real movement locks.
- Enterprising gives +1 gold per participating bearer on a mission settlement with a positive gold reward; no bonus for a zero-gold mission.

Source: `backend/general_perks.py`. Regenerate with `tools/build_general_perk_reference.py`; `--check` detects drift.
Selected profession/role perks: [Recruit perks](RECRUIT_PERKS.md).
