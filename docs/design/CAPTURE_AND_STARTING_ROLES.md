# Capture weapons, starting roles and level direction

Updated October 4, 2026. Capture weapons and all twelve starting Jobs are
implemented in dev. Job practice unlocks skills without automatic stat growth;
character levels and advanced Jobs remain proposals. See JOB_LOADOUTS.md.

## Starting Jobs - implemented

Job means combat class. Work proficiencies are separate and no longer selectable
as starter Jobs. Each new character receives three equipped Job skills, an
automatic Basic proficiency and matching poor-quality equipment. Race is separate.
Choosing a Job is permanent for now; gear and equipped skills can change the build.

| Job | Basic proficiency | Weapon kit | Starting attribute focus |
|---|---|---|---|
| Fighter | Combat | Chipped Sword + Splintered Shield | STR |
| Barbarian | Combat | Nicked Axe | STR |
| Rogue | Combat | Pitted Dagger | DEX |
| Ranger | Combat | Frayed Bow | DEX |
| Mage | Magic | Cracked Wand | INT |
| Cleric | Magic | Tarnished Prayer Rod | INT |
| Monk | Combat | Frayed Handwraps | DEX |
| Bard | Magic | Battered Song Focus | INT |
| Druid | Magic | Weathered Grove Staff | INT; forms alter melee options |
| Engineer | Building | Worn Mallet + Bent Tool Kit | STR personal attacks |
| Summoner | Magic | Faded Calling Focus | INT |
| Captor | Combat | Frayed Capture Net | Balanced STR/DEX/INT |

Every Job also receives Worn Jacket and Work Boots. Weapons are Common, power
0-1. The vendor offers all starter kits for 4-6 gold per item, above resale value.
New kit icons reuse existing artwork pending a coherent art pack.

Legacy Fighter/Ranger/Mage/Captor/Engineer traits remain. New Jobs rely on actual
skills rather than invented placeholder traits. Medicine training and Field Care
remain available on existing characters; Medic is no longer a creation choice.
Existing characters are not re-equipped or silently assigned a Job. Internal
legacy callers remain compatible; the public creation API requires a known Job
and defaults to Fighter when omitted.

## Capture — implemented

A capture weapon replaces the weapon's damaging basic attack with **Subdue [A]**. There is one action button; the client sends `subdue`, and the server rejects `attack` for capture weapons. Attack previews are absent. Ordinary weapons cannot choose Subdue. Each attempt consumes a main action, but not the once-per-battle technique use. You can try again on another activation while the battle continues.

Failure does no damage and applies no enchantment or on-hit effect. Success immediately leaves an active target unconscious and alive. Capture receives a subdue in the service record but no damage or kill credit, and produces no death/blood animation. Recovering the captive still follows normal carrying, extraction, battlefield recovery and prison rules. Capture is not recruitment; boss allegiance agreements still gate using a powerful prisoner as a permanent crewmate.

The preview uses the same probability as the check, including a proposed move into range. Polling and repositioning do not roll capture. Attacking with a capture weapon cannot damage walls or gates. Separately selected offensive gear techniques and thrown payloads remain damaging actions; auto battle uses capture rather than those techniques when carrying a capture weapon.

Current balance:

- Effective capture rating = lowest of STR/DEX/INT + 35% of the difference between their average and lowest stat. Gear and proficiency attribute bonuses apply. One huge STR stat is much less effective than balanced training.
- Stat contribution = `16 × ln(1 + rating / 8)` percentage points. This gives diminishing returns without discarding further improvement.
- Missing HP adds up to 36 points. Stun, Sleep, ambush Sleep or Freeze adds 10; Bind or Paralyze adds 6. Control bonuses do not stack.
- Half the target's evasion and 60% of its armor reduce the chance. Guard reduces it by another 8 points. Bosses have a 20-point resistance penalty.
- Normal targets currently range from 2–95%; bosses from 2–60%. These are capture bounds, not changes to critical-success probabilities.
- Ballistic capture tools use existing uphill/downhill accuracy modifiers. Magic binding tools explicitly use line of effect and are blocked by Mute; they do not silently inherit physical projectile elevation bonuses. Blind and Fear reduce capture chance.
- An ambush attempt uses the sleeping-target bonus, then wakes the whole camp even if the attempt fails.
- Captor perk adds 3 points. Padded Capture Gloves add 3 equipment points and carrying STR; they never enable capture with an ordinary weapon. Strongest equipment capture bonus applies, capped at 6.

Wounding or controlling a boss before attempting capture is the intended team strategy. An undamaged boss facing a frayed starter net is deliberately difficult. Exact probabilities are shown in the battle; subjective pacing still needs friend-trial feedback.

## Equipment progression — implemented

| Item | Rarity | Range / rule | Base capture points | Source |
|---|---|---|---:|---|
| Frayed Capture Net | Common | 1 / melee | 8 | Captor starter; E+ general cache |
| Patrol Capture Net | Common | 2 / ballistic | 16 | E+ general cache |
| Weighted Capture Net | Uncommon | 3 / ballistic | 20 | D+ general/Goblin caches |
| Warden's Mancatcher | Rare | 2 / melee | 24 | C+ general cache |
| Runebinding Focus | Rare | 3 / line of effect | 23 | C+ general/Arcane caches |
| Prototype Stun Rod | Epic | 2 / melee | 28 | B+ general/Starfall caches |
| Magistrate's Binding Seal | Legendary | 3 / line of effect | 31 | A+ general cache |
| Warhost Master Mesh | Rare | 3 / ballistic | 26 | Goblin Warcamp: 3%, +2 points for critical success |
| Starless Containment Lens | Mythic | 4 / line of effect | 35 | The Door Between Dead Stars, legitimate chain continuation: 2%, +2 points for critical success |

Cache membership is not a guaranteed drop: cache discovery and rarity checks still apply. The two exclusives never enter ordinary caches. Existing Goblin Net Bow, Hunter's Bola and Mooncord Sling are now dedicated capture weapons with base qualities 20/18/25 and ranges 3/2/4; their old damaging capture techniques are retired.

Ordinary clubs, hammers, mallets, staffs and previously nonlethal gear strikes now deal ordinary damage. **Blackwatch Cudgel** retains the stable item ID `watchmans_cudgel`: it scales with STR, may kill, and has a 5% chance on a killing direct cudgel blow to leave the victim unconscious instead. Nonlethal capture, damage over time and unrelated gear spells do not roll this effect. Chieftain's Chain Grips now grants Chain Brace, a support technique that guards an ally and removes Bind, rather than bypassing the capture-weapon requirement.

Active older battles migrate obsolete permissions and restraint weapons without resetting HP, positions, identities or encounter difficulty. New battles have effective STR/DEX/INT saved for capture. Older battles without those attributes use their recorded STR/INT and a neutral DEX of 4; exact stat snapshots resume with the next battle.

## Levels and classes — proposal only

Keep levels as experience and specialization, not a second large source of automatic attributes. No automatic HP, damage or STR/DEX/INT growth is recommended. Weapons, races, earned perks and choices should continue to determine how a character plays.

Suggested first pacing trial: 12/24/42/70/110/170 experience for E/D/C/B/A/S success, +20% for critical success, reduced experience for failures, and no experience from debug-forced victories. Award once at final settlement, including participating bodyguards; repeated decisions, capture attempts and battle polls must not award XP. Keep early missions useful with a reduced rather than zero XP floor for veterans.

A modest increasing XP cost can support high levels without exponential stat inflation. Begin testing the first level after roughly four or five E contracts; tune later milestones using actual pool sizes and completion times before committing a save migration. Unlock a limited set of meaningful specialization choices such as capture preparation, field medicine, movement or front-line defense. Do not give unlimited stacking stat points or permanently bind players to their initial role. Respecialization needs an explicit rule before the first permanent tree ships.

Enemy levels, when implemented, must be assigned by encounter/rank and boss identity. Never copy the player's level. Level difference should make only a small bounded contribution to capture chance; wounded HP, setup and gear should matter more. Captured bosses retain their identity and encounter level, while existing prisoner recruitment gates prevent an immediate power shortcut.

Deferred: XP persistence and UI, specialization tree implementation, respecialization, class refinements beyond starting roles, level contribution to capture, dedicated capture/starter icons, enemy captor encounter design and multiplayer balance telemetry.

## Validation

296 backend tests, 100 frontend tests and a production frontend build passed. An isolated actual-browser fixture verified the Capture action/chance, no duplicate Subdue button, six role choices, matching kit/training previews, locked included training and a narrow layout. No production deployment, save wipe or live player API calls were performed.
