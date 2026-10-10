# Character progression: where we are

**October 9 update: implemented in dev.** Ordinary players and humanoid enemies
now share 12 + 4×VIT HP and 2 + half the weapon scaling attribute + power/training
Attack. Adventurer Rank scales allocations once; bonuses apply afterward. New
captures preserve allocations, race, perks and rank, with equipment changes still
affecting combat stats. Existing battles/save data were not rewritten.

396 automated E/D fights and capture-parity checks cover the audited layouts.
Restart dev, refresh and start a fresh battle to test. Nothing was pushed to prod.

**Still pending:** personal rank promotion, Growth Grade, rebirth/respec, growth
rewards, weapon overhaul and racial innate HP/Attack differences.
[Current rules and limits](../design/SHARED_COMBAT_STATS.md).
