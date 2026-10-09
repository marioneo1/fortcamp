# Fortcamp development notes

At session start and whenever the user pivots, read `docs/WORK_STATE.md` alongside
`docs/INDEX.md`. Update the checkpoint with the active task, parked work, accepted
decisions and next steps; a topic change does not cancel unfinished work. Follow
links to canonical references before changing a resumed feature.

Use docs/INDEX.md to find the active design and implemented-system references before changing a feature. FEATURE_BACKLOG.md tracks outstanding work; docs/history/MISSION_REFINEMENT_PHASE.md records completed passes.

Keep temporary browser QA profiles inside this checkout at `data/browser-qa/profile` (ignored by Git). Never create QA profiles at the root of a drive. Use an isolated browser profile, never the user's normal browser profile; stop only processes started for the current QA session.

For gameplay, UI, API or tooling changes, update the matching system document and FEATURE_BACKLOG.md in the same pass. Clearly distinguish implemented behavior, proposals and deferred work. Record validation and material limitations. Keep public UI claims aligned with code. Do not claim effects, dialogue knowledge or historical statistics that are not implemented.

Preserve dev/release isolation. Do not copy alpha credentials into a release, modify release saves or publish secrets. Use the existing release builder. Keep portraits, identity, tastes and personality stable across restarts. Test behavior rather than mirroring implementation.

In-game help should describe player-facing rules in plain English; keep internal details and secret conditions out. Add canonical documents to docs/INDEX.md and define unfamiliar gameplay terms there or in the relevant system doc.

When changing combat mechanics, enemy kits, racial combat profiles, or encounter balance, update `docs/design/COMBAT_CAPABILITY_REFERENCE.md` and the relevant audit/rework document in the same pass. Record implemented rules separately from proposals and deferred AI/personality work. Keep `docs/design/CLASSES_AT_A_GLANCE.md` synchronized when adding or changing classes, enemy specializations or species kits; retain its short player-readable format.

When adding or changing races, Jobs, personalities, quests, character-history facts or dialogue events, review `docs/design/CHARACTER_STORIES_PROPOSAL.md` and update `docs/content/CHARACTER_STORY_CONTENT_INDEX.md` plus the applicable authoring contract/catalogue in the same pass. Keep existing IDs synchronized with their canonical code definitions; mark unimplemented tags/events/templates as proposals. Record story repeat scope explicitly, including once-per-player stories; preserve retired IDs and completion history rather than recycling them. New content must not silently make a completed one-off quest eligible again.

After changing the current character-life authoring prompt or contract, regenerate `docs/content/CHARACTER_LIFE_GPT_BRIEF.md` with `tools/build_character_life_brief.py` and run `--check`. Character blueprints must distinguish fixed/revealed facts from developed/transformed facets, explain early loyalty conflicts before investment, respect personal-chain budgets and core closure, and match reward promises to actual proposed grants. These requirements describe the planned system; do not claim they are runtime features until implemented.
