# Enemy specialties
Current dev implementation, October 9, 2026. These are recruitable variations of
existing Jobs, not extra selectable starter Jobs.

| Specialty | Job | Added technique |
| --- | --- | --- |
| Road / Bandit Trapper | Rogue | Tripline: one three-cell trap; first enemy crossing Hobbles and consumes the entire strip. |
| Road / Bandit Enforcer | Fighter | Shakedown: double weapon damage, two-activation cooldown. |
| Road / Bandit Skirmisher | Rogue | Parting Cut: 125% damage, then retreat one legal tile; no cooldown. |
| Goblin Cutpurse / Tool Snatcher / Forager | Rogue | Ankle Bite: damage and Hobble; stronger beside another ally. |
| Goblin Slinger / Lookout | Ranger | Goliath Shot: 75% Stun chance; target takes 25% more sword damage through its next activation. |
| Goblin Ringleader | Fighter | Tag Team!: swap with an ally, buff only the user, Stun enemies crossed between original positions. |
| Warband Bruiser | Barbarian | Cornered Fury: below half HP with multiple cardinal enemies, single-hit weapon attacks also strike those enemies. |
| Warband Warden | Fighter | Heel Cut: 150% damage and Bleed; moving farther adds stacks and extra Bleed ticks through the target's next activation. |

Tripline/Goliath/Ankle/Tag Team/Heel Cut cooldowns are 4/4/3/4/4 activations.
Road Bola remains a separate half-power HP attack with Hobble, distinct from
Captor's Resolve Bola. Main techniques end the activation; no free main attacks.

Captured recruits retain their learned specialty and receive their normal Job's
starter skills as learned options. Equipped order stays unchanged; normal
five-slot rules apply. They do not immediately unlock all eight progression skills.

Found in Unwanted Toll, Goblin Pickpockets, Old Well, Supply Watch, the three
worksites, and the three prisoner-linked warband missions. Exact roles depend
on each authored layout. Background perks are separate: [Recruit perks](RECRUIT_PERKS.md).

Catalogue: 97 player-Job skills plus nine enemy definitions (eight active,
one passive) = 106. No new selectable Job or personality ID.
