# Effekseer combat trial

Finite, modest blood splash on lethal defeat and moving blue projectile for basic magic attacks and magic-rule skills. Nonlethal takedowns do not spray blood. Slimefolk tint the splash teal; mechanical enemies use warm sparks; deathless enemies use muted dust. Existing impact/death sounds accompany the timeline; no new ElevenLabs calls or gore audio.

Sources: docs/art/effekseer/blood.efkproj, spell.efkproj and their procedural textures. Rebuild with `.venv/Scripts/python.exe tools/build_effekseer_combat.py` after the existing portable Effekseer 1.70e editor is installed. Compiled files live under frontend/public/assets/effekseer/combat-v1. Release preparation copies public assets. Campfire remains separate.

Uses the [official WebGL context/handle API](https://github.com/effekseer/EffekseerForWebGL). One transparent map canvas aligns to map coordinates and scales with zoom. It preloads on opening battle, bounds instances/events, stops at idle and pauses on close/hidden pages. Reduced motion suppresses effects. Asset/WebGL failure uses a small CSS flash and reports fallback in diagnostics. These cosmetic effects do not change damage, elements or rolls.

This is a two-effect trial, not a full elemental library. Magic has a common blue projectile; per-weapon/element visuals can follow. Blood is brief and stylized, without anatomical detail. A temporary copy of the pre-hit token flashes and fades before revealing the existing corpse marker. Persistent corpse markers remain separate. Review appearance in the real browser/Discord layout before expanding.

For an isolated preview without database requests: run `tools/build_relationship_combat_preview.py` with venv Python, start `node tools/serve_board_preview.mjs`, then open `http://127.0.0.1:8766/staging-ui/combat-relationships/preview.html`. It contains synthetic characters and mocked API responses. `tools/relationship_combat_browser_qa.mjs` exercises this fixture through a local QA Chrome on port 9229.
