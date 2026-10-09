# Encounter audit workflow

Use batches of three contracts; consider five only after several reliable passes.
Canonical results: [E-rank audit](E_RANK_COMBAT_AUDIT.md). Preserve accepted starter
Jobs and saved battles; changes apply to newly created encounters.

1. Read final mission descriptions, chain links/objectives and compiled maps;
   inventory every authored layout. Check structures, doors, exits, dressing,
   plausible enemy activity, stated species/counts and mission-specific rules.
2. Define each layout's composition/formation and modest shared rank budget.
   Prefer existing humanoid Jobs or logged mixed specializations; animals use
   species traits. Preserve capture/recruitment skills, personality and race.
3. Check legal spawns, footprints/props, entry/exit connectivity, line of sight,
   role ranges, hazards and melee access. Never fix balance by breaking story.
4. Compare HP/ATK/armor/movement/evasion/INT/STR identities and real damage rules.
   Avoid globally rewriting races to solve a single encounter; document scoped
   overrides and unresolved global race issues.
5. Run focused behavior/mission/geometry/capture tests. Run all layouts x twelve
   Jobs x Human/Fairy/Ogre with the isolated balance tool; compare counts,
   duration and exceptions. Simulation measures current AI, not human limits.
6. Check optional events separately, including saved rolls, same-map third parties,
   objectives, reward recovery, friendly fire, statuses and sequential playback.
7. Reuse assets; when needed generate one packed 5x4 sheet, inspect safe crops,
   add stable manifests and fill genuine equipment gaps. Preserve sources/prompts.
   Check sounds at animation contact, hurt and death; human listening is separate.
8. Record results and limits in audit/capability/content/art references, backlog,
   history and WORK_STATE. Give the player exact missions/layouts to test. Keep
   future proposals separate and never publish to prod without authorization.

## Verify what the player is actually running

The dev runner can disable backend code reload. Local simulations and a frontend
build do not update a running Python process. Compare launch time with changed
backend files and verify newly created battles in the current server when possible.
Explicitly report a required restart; browser refresh alone is insufficient.
Existing saved battle snapshots retain their original stats. Never silently rewrite
live fights to make them resemble newly authored encounters.
