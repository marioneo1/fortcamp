# Gear and loot design

Updated October 1, 2026. The live catalogue has 180 items. The September pass added 28 tactical items; this pass adds 56 equipment pieces to a live baseline of 124. `backend/gear_expansion.py` and `backend/gear_progression.py` contain additions and placements, `backend/mission_loot.py` controls mixed cache rolls, and `backend/combat.py` applies actual abilities and enchantments. See [the complete catalogue audit](ITEM_CATALOGUE_AUDIT.md) for counts, individual effects and drop sources.

## Drop sequence

A successful mission first makes its authored reward checks and independent exclusive checks. General/event cache attempts then roll whether anything is found, roll a rank-appropriate rarity, and choose a weighted item within that rarity. The first event-cache attempt uses its themed pool; other mixed attempts favor the contract/faction pool 60% of the time. Explicit mission pools take precedence over broader faction pools. Exclusives are removed from every ordinary pool.

Rarity weights below are relative weights, not the probability of receiving an item. A cache can fail before rarity is rolled. If a pool has no items of a tier, available tiers are renormalized. Rank minimums apply separately.

| Rank | Common | Uncommon | Rare | Epic | Legendary | Mythic |
|---|---:|---:|---:|---:|---:|---:|
| E | 80 | 20 | — | — | — | — |
| D | 60 | 32 | 8 | — | — | — |
| C | 42 | 38 | 18 | 2 | — | — |
| B | 25 | 35 | 32 | 8 | — | — |
| A | 15 | 25 | 40 | 17 | 3 | — |
| S | 5 | 15 | 40 | 28 | 10 | 2 |

Missed caches only pay fallback gold when that contract actually pays gold. Failure/critical failure retain their existing restricted rewards. Event keepsakes, perks and recruits have independent checks; participation never guarantees special equipment.

## Tactical gear

Ordinary gear now includes a capture cudgel, apprentice wand, armor-piercing Hooked Spear, nonlethal Weighted Sling, fire-enchanted Coalbrand Sabre, poison-focused Venomthorn Bow, lightning Stormglass Rod, and legendary Mercykeeper's Maul. Five events each add a Common, Uncommon and Rare weapon to their existing higher-tier pool.

All equipped techniques are available in a selector beside the battle Skill action. The weapon technique is the initial choice; skills from offhand, gloves or accessories remain selectable. All choices share one use per battle and the normal action cost. Every new skill declares range, STR/DEX/INT scaling, armor piercing, damage adjustment, nonlethal behavior and elevation rules. Selection updates authoritative target/approach previews; the server validates the equipped technique ID and remaining charge. Auto battle chooses an in-range technique and respects nonlethal rescue objectives. This is not an unlimited spell hotbar.

Fire/Ice/Holy match existing Burn/Freeze/Radiant racial affinities. Matching elemental resistance reduces damage 25%; weakness increases it 25%. Lightning and Void affect matching affinities when present. Magic damage also follows existing magic-resistance rules. A magic skill explicitly ignores elevation; a magical bow still uses ballistic rules. Enchantments do not amplify nonlethal takedowns.

Burn/Poison effects occur only after a successful lethal hit that leaves the target active. They last two target activations, deal 4% maximum HP per activation (minimum 2, maximum 5), bypass armor/guard, and refresh rather than stack. A separate deterministic proc stream preserves accuracy rolls. Repeated views cannot tick an effect twice. Water still extinguishes Burn. Poison-resistant races are immune to Poison; Burn resistance halves its proc chance, and vulnerability adds 15 percentage points. Other named statuses are not claimed as newly implemented here.

## Longer-chain relics

| Final contract | Relic | Tactical identity |
|---|---|---|
| Court of the Empty Crown | Empty Crown's Verdict | Guard perk and armor-piercing melee verdict |
| The Procession's Empty Hearse | Processional Last Light | Holy spells, Exorcist and distant ward-breaking skill |
| The Meridian Engine | Meridian Arc Driver | Lightning bolts, precision perk and long ballistic skill |
| The Shepherd of Titans | Shepherd's Gentle Hand | Beast Bond and powerful nonlethal restraint |
| The Door Between Dead Stars | Starless Door Key | Short normal reach, distant INT-scaled void spell |

Each has a separate 14% discovery check on success and 22% on critical success. The check requires follow-up provenance; opening a raw final template does not qualify. These items are neither ordinary cache drops nor guaranteed progression rewards. Existing chain entry/continuation probabilities and rank gates also apply. They are rare equipment discoveries, not globally unique Champion-style ownership records; multiple copies remain possible through distinct completed chains.

## October slot/build expansion

Added 6 head, 6 body, 6 hands, 8 legs, 6 feet, 8 offhand, 8 accessories and 8 weapons. Plain early equipment remains useful and inexpensive in power; higher tiers offer conditional or positional choices rather than uniformly larger attributes. Six existing items also receive utility: Gravity Boots, Tower Shield, Ironcap Buckler, Saint's Censer, Bell of Last Rites and Starfall Core.

Numeric equipment rules use the strongest equipped bonus, with caps: carrying STR +6, throwing range +1 (total range at most 5), structure damage +3, Guard recovery +4 HP, wounded-target direct damage +2 and boss direct damage +2. Carrying STR does not improve ordinary attacks or thrown damage. Guard recovery costs the action normally; it cannot revive unconscious units. Regeneration perks keep their existing shared +4 HP/round cap and duplicate perk IDs do not stack.

Water/rubble gear reduces the relevant terrain cost to 1 while preserving elevation movement costs, impassable cliffs and pits. Opening Guard protects against the first direct hit or expires at the next round. Capture Gloves unlock melee Subdue regardless of weapon. Equipment resistances join racial resistances without stacking; elemental mitigation and Poison/Burn proc protection retain existing rules.

Survival safeguards leave the wearer at 1 HP on one lethal attack, thrown impact or damaging status tick per battle. Multiple equipped safeguards share that one use; nonlethal capture bypasses them. They are not an escape or resurrection guarantee.

The pass adds 18 restricted discoveries: six E-rank revisiting incentives, four other authored mission finds, five nonweapon chain rewards, two live-capture-only rewards and a Starfall tomb relic. Each has an independent rate listed in the audit. The new chain pieces roll 4% on success / 6% critical success in addition to the existing 14% / 22% weapon relic checks. The Starfall pendant rolls 2% / 4%. Killing the chieftain/cartmaster removes the new capture-exclusive opportunity. Ordinary/faction/event caches exclude all 43 mission-exclusive items.

Nonexclusive new equipment enters mixed general caches and suitable Goblin, Procession, Arcane, Beast Tide and Starfall caches. New Common/Uncommon pieces begin at E; Rare at C, Epic at B, Legendary at A, Mythic at S. Existing tables retain their authored rank exceptions. Rare low-rank jackpots use separate checks, so they remain worth seeking later without flooding higher-rank pools.

## Names and remaining scope

**Proficiencies** are Basic → Skilled → Expert → Master training tracks. **Perks** are distinctive traits, backgrounds, racial traits and equipment-granted properties. Internal saved `perks` track fields and existing endpoints remain compatible to preserve progress.

The equipment browser is under Roster → Equipment. It pages item types, stacks duplicates, searches names/elements/abilities, filters by slot/rarity, sorts, identifies owners and supports named transfers and quick unequip. On-mission equipment stays locked; injured characters can change gear. Comparisons show attribute/weapon-power differences, not a universal gear score. Granted effects include the actual bounded equipment rules. A dedicated shared armory, loadouts, consumable actions and further branch-specific pools remain future passes.

## Equipment and briefing QoL (2026-10-01)

Spare gear stats, abilities and perks start expanded. Hide gear details is separate from Hide equipped gear and persists per player/server in browser storage. Equipped slots have Gear effects disclosures and a hover summary on the name. Attributes, CON and the mission DPS rating explain their actual formulas on hover or keyboard focus. Perk help uses a viewport-clamped panel rather than inheriting the rounded tag layout.

Contract summaries conceal undisclosed exclusive item names and drop percentages, replacing duplicate spoilers with equipment discovery hints. An item explicitly named in the description/objective, or authored in disclosed_rewards, stays named as a possible recovery. Paid rewards and ordinary reward categories remain visible; no actual loot rolls were changed. All three briefing views use the same server-filtered preview.

Equipped gear effects are now always shown directly in each filled slot. They cannot be collapsed or hidden. The saved Hide spare gear details setting applies only to inventory cards. Hover summaries remain available on equipped names.

## Inventory UI and resale (October 1, 2026, dev)

Character Equipment excludes non-wearable items; party Inventory has all gear, manuals and materials with search/categories/rarity and stacked duplicates. Only unequipped instances can be sold, after quantity/total-gold confirmation. Backend rarity prices and faction purchase-price caps are described in ../design/CAMP_INTERFACE.md. No buyback or automatic material-use action is implemented.
