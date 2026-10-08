# Production preparation - October 7, 2026

The authorized release includes the current combat Job work and uses the existing independent release builder. Dev source is pushed to origin/main; the builder fast-forwards origin/release and creates an immutable version tag and separate fortcamp-prod checkout. Production credentials stay private and are preserved from the previous production copy.

Production runs the bundled frontend through Uvicorn on port 5173, with real authentication, GAME_DEBUG_MODE=false, DEV_BYPASS_AUTH=false, normal mission timing and separate fortcamp-release-data storage. No Vite dev server or live reload runs in production. Battle Lab, Portrait Lab, Wall Lab and debug actions are guarded/hidden. Source tests, browser QA fixtures, temporary scripts and development launchers are excluded from the production working tree; backend guarded debug modules remain part of pinned source.

Release initialization no longer seeds a missing production save or uploaded portraits from dev. It creates empty SQLite storage and an empty uploads directory, retaining existing production data on ordinary updates. Shared portrait pools, champion art, framing defaults and runtime combat assets are shipped as game content.

For this launch the user explicitly authorized a full production gameplay reset. The stopped production SQLite database must receive a consistent backup; uploaded player portraits are archived with it before clearing active data. Dev saves and authored shared art remain unchanged. All production gameplay rows, missions, registrations and old player uploads are cleared. Backup paths and the release version are reported after execution. First startup creates the current schema normally.

Validation includes release-profile/initialization tests, combat Job tests, frontend tests/build and an isolated production-config startup/API smoke check with no Discord bot or live saves. Release controls and initial empty storage are verified before final handoff. Balance/aesthetic limitations documented per Job still apply; this preparation does not declare them resolved.

Release builder correction: asset copying overlays the committed public asset directories rather than failing when Git already supplied the destination. A failed preparation restores the previous production checkout; live saves are reset only after preparation and isolated validation succeed.

Dependency check: patched transitive source-map-js from 1.2.1 to 1.2.2 for GHSA-68fv-2mgg-jv7q. npm reports zero vulnerabilities after the lockfile update; all 379 frontend tests pass.

Final checkout audit also excludes performance QA, preview servers and portrait-authoring launchers/tools, alongside browser QA and source test files. Production keeps its runtime and tunnel/setup launchers.
