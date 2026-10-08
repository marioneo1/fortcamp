# Fortcamp development notes

Use docs/INDEX.md to find the active design and implemented-system references before changing a feature. FEATURE_BACKLOG.md tracks outstanding work; docs/history/MISSION_REFINEMENT_PHASE.md records completed passes.

Keep temporary browser QA profiles inside this checkout at `data/browser-qa/profile` (ignored by Git). Never create QA profiles at the root of a drive. Use an isolated browser profile, never the user's normal browser profile; stop only processes started for the current QA session.

For gameplay, UI, API or tooling changes, update the matching system document and FEATURE_BACKLOG.md in the same pass. Clearly distinguish implemented behavior, proposals and deferred work. Record validation and material limitations. Keep public UI claims aligned with code. Do not claim effects, dialogue knowledge or historical statistics that are not implemented.

Preserve dev/release isolation. Do not copy alpha credentials into a release, modify release saves or publish secrets. Use the existing release builder. Keep portraits, identity, tastes and personality stable across restarts. Test behavior rather than mirroring implementation.

In-game help should describe player-facing rules in plain English; keep internal details and secret conditions out. Add canonical documents to docs/INDEX.md and define unfamiliar gameplay terms there or in the relevant system doc.
