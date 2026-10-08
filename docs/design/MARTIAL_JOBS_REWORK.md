# Fighter additions and Barbarian Fury

Implemented in dev, October 5, 2026. Production and player saves are unchanged.

## Fighter

| Skill | Effect | Cost / cooldown | Unlock |
| --- | --- | --- | --- |
| Brace | Self: 25% less incoming damage, including damage over time, for three owner turns | Main action; 5 owner turns | 12 successes |
| Second Wind | Self: heal 50% maximum HP, capped at full HP | Main action; once per battle | 16 |
| Victory Strike | 150% attack power; a lethal kill heals 10% maximum HP | Main action; 2 owner turns | 20 |

Percent attack power is applied before normal armor and other damage rules;
it does not promise that much final damage. Percentage healing uses maximum HP.
Brace reduces damage rather than multiplying the armor stat. Existing Fighter
skills and their timing remain available.

## Barbarian

Innate Fury starts at zero each new battle and has five segments. Enemy damage
that reaches HP grants one Fury. Fully absorbed, self-inflicted and friendly
damage grant none. Enemy damage over time can grant one; Bloodfury's extra point
requires a direct hit and uses HP after that hit. The innate rule consumes no
equipped slot. Fury remains in the persisted battle, never in the roster.

| Skill | Effect | Cost / cooldown | Unlock |
| --- | --- | --- | --- |
| Reckless Blow | 200% attack; gain one Fury even on miss; take 20% more damage until next owner turn | Main action; 2 turns | Starter |
| Skullbreaker | 125% attack; a hit stuns for two target activations | 2 Fury; main action; no cooldown | Starter |
| Bloodfury | Direct enemy hits leaving you at 50% HP or less grant two Fury | Passive slot | Starter |
| Bloodied Strength | Attack rises linearly with missing HP, from no bonus at full HP to +50% at 1 HP | Passive slot | 2 successes |
| Groundbreaker | 200% attack against enemies in all eight neighboring cells; push one cell | 4 Fury; main action; no cooldown | 5 |
| Too Angry to Fall | First lethal damage leaves 1 HP; subsequent lethal damage cannot kill until your next turn | Passive slot; once per battle | 9 |
| Bloodthirst | Each lethal kill heals 20% maximum HP; multiple kills in the triggering turn each heal | Passive slot; 3 owner-turn cooldown | 12 |
| Unstoppable | Automatically spend one Fury to remove one harmful status, prioritizing disabling control | Passive slot; 3 owner-turn cooldown | 16 |

Regular characters still equip five active/passive skills in total. This makes
the full kit a choice, not eight permanent bonuses. Equipment abilities remain
outside these slots. Victory Strike's two-turn cooldown and Unstoppable's one-Fury
price are explicit initial tuning choices where the request left a cost open.
The requested “3s” cooldown uses three owner turns in this turn-based game.

## Timing and counterplay

Cooldown N used on owner activation K is ready at K+N. Polls, view refreshes and
reopening the battle do not tick cooldowns, Fury or healing. Bloodthirst's same-turn
window lasts for the owner's activation; owner-attributed kills in that window
can each heal, including other supported damage sources. It does not repeatedly
reset its cooldown for later kills. Temporary summons award no kill healing.

Death defiance ends at the next owner activation without killing the Barbarian.
Healing can save them; another lethal hit afterward can kill them. Nonlethal
capture still incapacitates them. Falling out of the map into a lethal pit remains
an environmental defeat. Unstoppable does not remove Reckless Blow's deliberate
exposure, pit entrapment or encounter-wide scripted sleep. With no Fury it cannot
cleanse; one cleanse does not remove every debuff. Boss control recovery, racial
immunity and displacement resistance still apply.

Groundbreaker respects walls/closed gates through existing line-of-sight rules.
Allies take no primary Groundbreaker hit, but existing collision physics still
apply when a pushed enemy hits a person, including an ally. Dead enemies can
still be displaced and collide; corpses do not receive stun. Armor, barriers,
misses and position therefore remain answers to the burst/control kit.

## Persistence and performance

New units snapshot the Job and kit. Six retired Barbarian IDs migrate in learned
and equipped lists: shove→reckless_blow, expose→skullbreaker,
anchored→bloodfury, hide→bloodied_strength, drive→groundbreaker,
stand→too_angry_to_fall. Order and the five-slot choice are preserved. Practice
already earned grants newly eligible skills. Existing fights keep their saved
definitions; restart Battle Lab to use the new kit. No database-wide rewrite.

Hooks run on actual damage/status changes and owner turns. Fury does not need a
timer, background task or separate database. Effects use short resolved sprite
events; aura breathing is CSS and honors reduced motion. Auto-battle can use the
new self-centered area attack, normal offensive abilities and self-care. Its
existing heuristic is not a full Fury/burst planning AI.

## Presentation and validation

Five Fury pips appear below the token, with numbered meters in the acting card
and hover inspection. Brace and defiance have attached painted auras; restoration,
physical contact and Groundbreaker use short alpha-sprite phases and dry physical
sounds. The effects share resolved contact packets; enemy playback waits for them.
See [Art and audio](../art/MARTIAL_JOBS_V1.md) for reproducible import and limits.

Automated checks cover hostile/friendly/absorbed damage, Fury saturation and cost,
threshold attack scaling, exposure, cooldowns, lethal survival, nonlethal capture,
multi-kill healing, status cleanse, wall occlusion, self targets, percentage healing,
JSON persistence, repeated views and idempotent migration. Browser fixture checks
verify the actual battle renderer loads the new icons and Fury meters. Subjective
audio approval and live playtest balance remain open.
