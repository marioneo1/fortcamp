# Same-map radiant encounters

Implemented in dev, October 8, 2026. This is a small encounter event, separate
from the proposed character-life/personal-quest system.

`radiant:foraging_bear`: 3% seeded entry roll in `goblin_pickpockets`,
`ruined_well`, `supply_watch`. Roll and outcome are stored on the battle, including
misses; reconnect/reload does not reroll. Repeatable on later contracts, not a
once-per-player story. No separate battle or mission instance is created.

The bear is present before the arrival notice. An open, prop-free tile at least
six Manhattan cells from the party is chosen. Prefer a legal cardinal tile beside
a local raider, without a wall between them. Both start wounded (bear -6 HP,
raider -4 HP, never below 1), representing a fight that began before arrival.
These are authored starting wounds, not skipped current-turn attacks/deaths.
If no skirmish tile exists, use a clear roaming position; if no valid position
exists at all, omit the event. The notice describes the actual situation and
pauses initiative until acknowledged. It does not offer a separate-instance fight.

The bear attacks both sides and locals can attack it. An amber token border and
Independent Wildlife label distinguish it. Internally it remains an enemy-side
combatant for existing targeting/corpse compatibility, with hostile-to-all metadata;
this does not make it allied to raiders. It cannot Intercept for them or count as
a Cheap Shot ally. Its presence is excluded from the required clear objective
and clean-completion check. Players may avoid it, exploit the distraction, or
fight it; winning the base contract allows departure with normal recovered spoils.
Continuing after that victory allows hunting the bear. Living wildlife gives no
loot and cannot silently be awarded as a kill.

Foraging bear: 34 max HP, 5 ATK, 1 armor, move 2, melee claws; reused existing
bear portrait. Recovered slain bears give Thick Bear Pelt (+2 VIT/-1 AGI), plus
an independent 5% Bear Claws roll. Bear Claws: DEX knuckles, power 2, +1 DEX;
weapon power benefits Monk techniques without adding an exponential on-hit proc.
Neither trophy appears in ordinary loot pools. Pit-lost/unrecovered bodies yield
nothing. Standard capture/carry/recovery rules remain authoritative.

Nine ElevenLabs sounds: three attacks, three hurt cries, three death cries.
Attack voices accompany existing claw/flesh contacts; hurt requires real direct
damage and death follows resolved defeat events, never final-state guessing.
See [Field gear and bear audio](../art/FIELD_GEAR_V1.md).

Validation: saved notice/one acknowledgment, placement, opposing hostility,
optional objective, loot recovery, actual 5% boundary through completion,
recruitable profiles and equipment tests. Human listening/visual review pending.
Known test seed `74` triggers the encounter on all three eligible contracts:
`tools/audit_beginner_combat.py --missions goblin_pickpockets ruined_well supply_watch
--radiant-seed 74 --output data/audits/e-batch-2-bear.json` (virtualenv Python).
Future events should record IDs, eligibility, repeat scope, saved state, objective
impact and actual rewards here; do not imply personal-story flags are implemented.
