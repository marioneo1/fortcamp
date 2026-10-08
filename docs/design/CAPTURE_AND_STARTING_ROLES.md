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

## Capture - implemented, revised October 7

Capture equipment now provides separate lethal **Attack [A]** and **Subdue [N]**. Subdue damages a separate Resolve pool, never HP; at zero Resolve successful contact attempts capture. Armor is replaced by INT/AGI Resolve mitigation, and wounds no longer determine capture chance. Captor adds isolation, drag and Hold techniques. Hold deals 0.75x Resolve damage per tick and repeatedly attempts capture when ready. Captured enemies are unconscious/carryable and automatically recovered at map completion.

[Captor and Resolve](CAPTOR_REWORK_REVIEW.md) is the canonical source for current formulas, probability, eight skills, migration, AI limits and timing. It supersedes the previous HP-based Subdue/capture formula. Equipment quality/range and progression below remain in effect.

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
