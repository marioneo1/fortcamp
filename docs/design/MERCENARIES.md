# Mercenaries — implemented alpha/dev pass

October 2 capture/starter update: [Capture and starting roles](CAPTURE_AND_STARTING_ROLES.md) is authoritative for dedicated capture weapons, removal of ordinary blunt/unarmed Subdue and six coherent starting kits. References below to old nonlethal weapon permissions are historical; XP/levels remain proposed.


Each player has four persistent hiring contacts. Open a Private Contract, assign at least one available member of your own crew, and select **Hire mercenaries**. Select a contact to fill an empty party or optional bodyguard slot. Payment happens when the expedition starts, not when browsing or assigning. Public contracts must first be saved to Private Contracts.

Names, portraits, equipment, rank, personality, and trust persist in the player's save. Existing contacts never reroll on refresh or restart. A missing contact is replaced the next time the hiring board is opened. Early contacts are Human fighters, scouts, adepts, medics, or builders; further racial and named mercenary content is future work. There is no background death lottery.

## Price and progression

| Contact rank | Base fee on E contract | Permanent service | Initial betrayal chance |
| --- | ---: | ---: | ---: |
| E | 10 gold | 100 gold | 6% |
| D | 16 gold | 180 gold | 8% |
| C | 28 gold | 360 gold | 10% |
| B | 48 gold | 750 gold | 12% |
| A | 80 gold | 1,600 gold | 14% |
| S | 130 gold | 3,200 gold | 16% |

Hiring fees also scale with the accepted contract rank: E x1, D x1.5, C x2.2, B x3.2, A x4.5 and S x6.5. Apply the existing trust discount, then round to whole gold. An E contact therefore costs 10/15/22/32/45/65 gold across E through S contracts before trust. Browsing a different rank changes quotes without rerolling contacts. Preview and acceptance use the same calculation; the server reads the actual mission template rank at acceptance, independently of the browser quote. Existing permanent-service prices and betrayal rules are unchanged. Current planner browser QA verifies rank-priced hires and bodyguards.

Successful/critical-success contracts give +2 trust; failed contracts give +1 for loyal surviving hires. Turncoats gain none. Permanent recruitment requires 30 trust, an available contact, and the buyout fee. That is approximately fifteen successful contracts with the same contact. Recruitment keeps the identity and weapon, and starts loyalty at 75 plus half trust, capped at 95. Ordinary character relationships then apply.

Fees fall by 0.5% per trust point up to 40 trust, for a maximum 20% discount; fees never fall below 3 gold. Betrayal risk decreases linearly toward zero at 100 trust. One collective roll uses the average hired risk, plus up to two percentage points per extra hire. That surcharge scales down with the group's lowest trust, and total risk caps at 25%. When several hires betray, a 15% secondary roll lets exactly one remain loyal; a loyal holdout only exists alongside opposing turncoats.

The hiring board initially retains affordable E contacts. Replacements can roll up to the player's unlocked mission rank. Rank increases attributes and proficiency modestly, not to boss-level strength. Stronger mercenaries are substantially more expensive to buy. Completed-job relationship and fees, rather than a free early recruit or a removed party requirement, pace the workaround.

Each temporary hire, including a bodyguard, applies **−1 to mission and dialogue checks**, capped at −4. This compares against an equivalent permanent crew. Tactical combat remains decided by actions and objectives; there is no artificial combat damage penalty. Loaned weapons cannot be transferred or sold and are removed after the contract. Hires remain busy until completion and do not remove the permanent-solo +10 free-for-all claim bonus.

## Betrayal and contract continuation

Betrayal is a separate road encounter before the original expedition. The actual hired characters, weapons, and portraits become opponents; any holdout stays with the player. Defeat/subdue them or escape. Surviving resumes the original roll, choices, or tactical mission without awarding a second contract payout. Turncoats are removed from the expedition and the roll is recalculated for remaining participants. The originally reserved contract survives even if this leaves fewer than its initial required party size. A complete party defeat is still a critical failure.

The original scene and battle setup are retained. A turncoat's death removes the contact; subdual causes a 30-minute recovery cooldown. Known hired swords are not duplicated as generic prisoners. This first pass does not yet carry every injury/consumable from the pre-contract skirmish into the original encounter; richer multi-encounter attrition belongs in the adventure system.

## Rare battlefield appearances

At most one incident roll occurs per contract in suitable road/camp encounters, the goblin warcamp/cart/signal maps, or the Hedgerow defense. Courtrooms, confined ruins, and unrelated magical interiors do not roll it. Only available contacts from the player's board qualify.

- **1% corpse:** a known mercenary lies near the enemy position, on a reachable unoccupied tile. The contact is removed immediately.
- **0.25% friendly arrival:** a contact enters from a reachable map approach and fights automatically beside the party. Surviving assistance gives +2 trust.
- **0.25% hostile arrival:** a contact attacks both the party and local enemies. They block victory until killed or subdued. Escaping while they remain a threat causes failure; losing the party causes critical failure.

Arrival cells avoid occupied tiles, blocking props, and unreachable ground, with separation from the party and enemies. If no suitable cell exists, the incident is skipped. A central battlefield message explains the situation and can be dismissed without spending a turn. Deaths are recorded after each combat command, so a dead contact is removed before the mission ends. Extracting a living mercenary does not incorrectly count as death.

## Event and starter pacing changes

Natural regional boards previously rolled at 30% each half-hour with consecutive events permitted. The new threshold is 12%, with a quiet board required after a candidate event roll. Across 10,000 deterministic board slots, events occupy roughly 10.5% of boards; natural events cannot be consecutive. Debug-forced events still bypass this rule. Existing boards are not rewritten mid-cycle.

New characters receive a low-grade kit based on their chosen starter perk: Guard gets Chipped Sword + Splintered Shield; Scout gets Frayed Bow; Fire Magic gets Cracked Wand; Engineer gets Worn Mallet; Field Medic gets Knotted Staff. Each keeps Worn Jacket and Work Boots. A magic/combat proficiency supplies a compatible fallback when no listed perk applies. Existing equipment is unchanged. The character creator previews the kit; the current creation flow chooses a perk/proficiency, not a separate mandatory class. Starter icons reuse existing local art; dedicated worn-gear art remains optional.

## Verification

Backend behavioral tests cover persistence/refill, private ownership, idle crew, slot validation, affordability, busy contacts, coordination penalties, solo allowance, trust/buyout, group betrayal/holdout frequency, settlement, death versus extraction, valid rare spawns, blocked victory, matching starter ranges, event frequency, and database-backed preview → claim → completion/betrayal continuation. Browser QA exercises the actual planner, multiple hires/bodyguards, selection refresh, prices, and central encounter notice. All QA fixtures use isolated saves/databases. Multiplayer soak testing and subjective price/encounter balance remain follow-ups.

Final checks: 255 backend tests, 96 frontend tests, frontend production build, and the isolated browser planner/arrival QA passed. `tools/build_mercenary_preview.py` builds that local-only fixture and `tools/mercenary_browser_qa.mjs` checks it against the existing preview server and a headless Chrome debugging session; they are development tools, not game launchers.
