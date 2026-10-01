# Gear and loot design

Implemented September 30, 2026. The live catalogue has 108 items; this pass adds 28. `backend/gear_expansion.py` contains the additions and cache assignments, `backend/mission_loot.py` controls mixed cache rolls, and `backend/combat.py` applies actual abilities and enchantments.

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

An equipment skill replaces the current single special-action slot, once per battle, using the normal action cost. A weapon skill takes priority over a skill from another equipped slot. Every new skill declares range, STR/DEX/INT scaling, armor piercing, damage adjustment, nonlethal behavior and elevation rules. Both manual and auto battle honor those fields. This is not yet a multi-spell hotbar.

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

## Names and remaining scope

**Proficiencies** are Basic → Skilled → Expert → Master training tracks. **Perks** are distinctive traits, backgrounds, racial traits and equipment-granted properties. Internal saved `perks` track fields and existing endpoints remain compatible to preserve progress.

The equipment browser is under Roster → Equipment. It pages item types, stacks duplicates, searches names/elements/abilities, filters by slot/rarity, sorts, identifies owners and supports named transfers and quick unequip. On-mission equipment stays locked; injured characters can change gear. Comparisons show attribute/weapon-power differences, not a misleading universal gear score. Granted effects are expandable. A dedicated shared armory, loadouts, multi-skill selection, consumable actions and deeper capture/branch-specific pools remain future passes.
