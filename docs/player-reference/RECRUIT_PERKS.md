# Recruit perks — current dev rules
Implemented October 9, 2026, for newly created audited encounters. Existing
characters/battles are not rerolled. Production has not been updated.

Perks describe a background or quirk, persist after recruitment, and appear in
Traits without taking a skill slot. Some enemies have no perks.

| Perk | What it does |
| --- | --- |
| Rider | Can ride allied mounts for their bonuses and techniques. Boars grant +1 movement, 25% protection and Boar Charge; mount loss risks damage with Stun or Hobble. |
| Cunning Trapper | On defeat, leaves one legal 1x3 tripwire containing the fallen tile. Prefers excluding the killer; skips impossible placements. First enemy contact snaps it. Survives the owner's defeat for up to three rounds. |
| Intimidating | First kill each battle makes enemies within two cells of the victim deal 15% less damage through their next activation. |
| Sly Survivor | Once per battle, surviving damage at or below 25% HP makes AI prefer other legal targets until the character acts. Does not grant invulnerability or actual unconsciousness. |
| Resourceful Slinger | Once per activation, a landed ranged weapon shot against metal armor/machinery can ricochet at half weapon power into a second enemy within two cells with clear sight. |
| Opportunistic Leader | Once per battle, an ally attacking the leader's current target gets one additional legal Basic Attack. Current target is the enemy most recently attacked by the leader. No recursive extra attacks or spent ally activation. |
| Defiant | Once per battle, becoming the last conscious ordinary teammate after an ally falls grants a 20% max-HP Barrier for two activations. Solo missions, summons and protected NPCs do not manufacture the trigger. |
| Relentless Pursuer | Once per activation, hitting an enemy who used a movement skill since your previous activation adds Hobble. Ordinary walking does not qualify. |
| Lumberjack | +1 wood/hour worked while assigned to a lumber mill. |
| Quarry Worker | +1 stone/hour worked while assigned to a quarry. |
| Salvager | +1 scrap/hour worked while assigned to a salvage yard. |
| Poison Tolerant | Ignores one incoming Poison stack once per battle, not a whole multi-stack application or damage tick. |
| Fast Builder | +1 defense preparation point per deployed character with the perk; no extra party member or turret slot. |
| Strong-Armed | +2 STR, -1 AGI. |
| Nimble | +2 AGI, -1 STR. |
| Bookish | +2 INT, -1 STR. |
| Steady-Handed | +2 DEX, -1 AGI. |

Generation uses its own deterministic random stream, independent of stat/loot
rolls. There is a 20% no-perk roll. Among the rest, 20% choose a general stat
tradeoff instead of their role perk. Tool shed/well/supply origins additionally
choose matching production professions: 99% one, 0.9% two, 0.1% all three
(conditioned on the nonzero-perk roll). Herb origin adds Poison Tolerant;
timber origin adds Fast Builder. These initial probabilities are tuning choices.

Once-per-battle usage survives battle saves; Traits descriptions mark spent
effects. Production bonuses require an actual matching assignment, not an idle
unassigned player doing general camp work. General stat traits affect enemy
combat stats and recruited character calculations without modifying base
attributes. The larger new positive/negative pool is still only proposed:
[General perk audit](GENERAL_PERK_AUDIT.md).


## General quirks expansion
61 additional quirks are now implemented: [catalog and conflict rules](GENERAL_PERKS.md).
The zero-perk gate remains about 20% for authored NPCs. The old four-profile
alternative can now roll a compatible general quirk, with HP-changing profiles
kept rare on combat NPCs. Profession rolls retain their prior rates.
Existing characters are never rerolled. General traits do not consume skill slots.
