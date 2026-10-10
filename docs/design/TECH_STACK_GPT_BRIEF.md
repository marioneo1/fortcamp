# Fortcamp technical context for GPT

Verified against the development checkout on October 9, 2026. This is a code-based
snapshot, not a promise that every dependency or proposed feature is in active use.
Update when dependencies, architecture, deployment or tooling change.

Copy the following into GPT:

---

We are developing **Fortcamp**, a fantasy settlement/character-collection game
with ranked missions and turn-based tactical grid combat. It runs as a Discord
Activity and in a regular browser. Please tailor proposals to this existing stack
and engine, rather than assuming a new game framework.

**Platform and languages**
- Windows development, PowerShell/batch launchers, Git/GitHub.
- Python 3.12.3 in a project `.venv`.
- Node.js 24.15.0, npm, JavaScript ES modules, HTML and CSS.
- Current application package/API version: 0.3.1; this is evolving development.

**Frontend**
- Vanilla JavaScript with custom DOM rendering and modular helpers. No React,
  Vue, Angular or TypeScript application framework.
- Vite 6.4.3 for development and production bundling.
- Discord Embedded App SDK (`@discord/embedded-app-sdk`, package range ^2.5.0).
- Main game UI/combat orchestration in `frontend/src/main.js`; feature modules
  handle playback, targeting, effects, HUD, inspection, camera, etc.
- Map terrain, props, portraits, status icons and UI primarily use HTML/CSS and
  CSS Grid. Motion uses CSS and the browser Web Animations API. This is not a
  Unity/Unreal/Godot game, and the entire battlefield is not a 3D scene.
- PixiJS 7.4.3 modular packages and `@pixi/particle-emitter` 5.0.10 provide WebGL
  particle/atmosphere effects, with fallback handling.
- Vendored Effekseer 1.70e JS/WASM integration exists for selected effects,
  including a campfire trial sharing Pixi's WebGL context; not every spell uses it.
- Lighting uses shared SVG color-matrix filters, selective CSS silhouette
  shadows and bounded glow layers. Normal missions save arrival phase/time;
  light drifts within that phase and accounts for time away. No physical 3D
  roof/window occlusion or full phase cycling during normal missions yet.
- Custom draggable/resizable battle HUD, unit inspection, targeting previews,
  placement flows and mobile adaptations. iPhone Safari matters alongside desktop.

**Backend and storage**
- FastAPI 0.141.1, Uvicorn 0.53.0, Pydantic 2.13.5.
- SQLAlchemy 2.0.54 async ORM, aiosqlite 0.22.1. Windows dev/release profiles
  currently use separate SQLite databases.
- PostgreSQL support is available through asyncpg; Docker Compose supplies an
  optional PostgreSQL 17 service. Do not assume PostgreSQL is the live database.
- Player states and parts of mission/battle state are JSON in database records;
  there are also relational tables for missions, registrations, guilds and login.
- HTTPX 0.28.1 for outgoing HTTP; python-dotenv for environment configuration;
  Pillow 12.3.0 for asset-processing tools.
- `backend/main.py` exposes JSON HTTP APIs; `services.py` coordinates persistence;
  combat lives in `combat.py` and focused modules for Jobs, statuses, AI, hazards,
  movement, deployments, capture, stats and presentation.
- Backend is authoritative: it validates commands, resolves damage/statuses/AI
  and returns battle state plus animation/sound events. Frontend plays the event
  timeline; it must not expose future deaths/debuffs before their visual event.
- Browser uses HTTP requests and periodic polling (main dynamic refresh about
  every 5 seconds), not a WebSocket-based real-time combat server.

**Discord/authentication/hosting**
- discord.py 2.7.1 bot and Discord OAuth; Embedded SDK integration for Activity.
- PyJWT 2.14.0 application sessions with environment/database namespace isolation.
- Regular-browser login also supported. Credentials stay in environment files.
- Cloudflare Tunnel exposes the locally hosted application.
- Dev: separate `fortcamp-dev` checkout, API localhost:8001, Vite localhost:5174,
  public `dev.fortcampgame.fyi`.
- Production: separate prepared release folder/runtime data, localhost:5173,
  public `play.fortcampgame.fyi`; FastAPI serves built frontend files and API.
- Production does not depend on the Vite development server or HMR. Release
  tooling excludes testing tools/credentials and disables debug/auth bypass.
- Default dev mode disables automatic browser/backend reload for uninterrupted
  playtesting; restart runner for source edits. Optional live-edit mode exists.

**Game systems already available**
- Twelve base Jobs: Fighter, Barbarian, Monk, Rogue, Ranger, Mage, Bard, Cleric,
  Druid, Summoner, Engineer and Captor; equipped loadouts and enemy specialties.
- Main actions, Quick Actions, activation-based cooldowns, movement previews and
  committed movement, range/line-of-sight, physical/magical damage, accuracy,
  crits, resistances, hard control, DoTs, buffs/debuffs and forced movement.
- Placed hazards/zones, destructible terrain, doors, defensive preparation,
  autonomous summons with orders, machinery/construction, mounted boars,
  HP/Resolve capture, prisoners/recruitment and perks.
- Authored mission maps and variations, E-rank audits and initial D-rank audits,
  same-map radiant encounters, character personalities and content/name pools.
- Character-life/radiant personal quest authoring has documented proposals;
  do not assume all story blueprints, rebirth or proposed mechanics are live.

**Art/audio and tools**
- Local generated raster portraits, top-down terrain/props, icons, sprite sheets,
  atlases, textures and animation frames. Reuse established visual styles.
- Prefer bulk image sheets/packs over wasteful single-image generation, preserve
  source atlases/manifests and use careful crops. Animal forms often swap portraits
  rather than replacing characters with full animated animal units.
- ElevenLabs-generated sound effects and wordless combat vocals; consistent
  race/gender/personality voices with multiple attack/hurt/death variants.
- Browser Web Audio plus music/audio playback, event-timed SFX and volume settings.
- Image/audio generation is an authoring workflow, not required during gameplay.
- Battle Lab: isolated temporary combat tests, missions/variations, party/loadout
  setup, seed/restart, radiant overrides and Lighting controls. Portrait Lab and
  Wall Kit Lab are separate specialist tools under Developer Tools. Labs are dev-only.

**Testing/documentation/constraints**
- Python unittest and Node's built-in `node:test`; Vite production build checks.
- Isolated Chrome/CDP browser QA with local fixtures; native Safari still needs
  device review. No assumption of a Playwright-based test framework.
- `docs/INDEX.md` is the reference map; `docs/WORK_STATE.md` preserves active and
  parked work; `FEATURE_BACKLOG.md` tracks outstanding work.
- `docs/design/COMBAT_CAPABILITY_REFERENCE.md` and `CLASSES_AT_A_GLANCE.md` track
  implemented combat/Jobs. `docs/player-reference/` contains short readable guides.
- Generated art/audio, staging assets, databases, build outputs and credentials
  are largely excluded from Git and need separate backups/transfers.
- Recommend the smallest compatible change. Distinguish implementation from
  proposals, explain consequential behavior changes, preserve dev/prod isolation,
  and do not replace combat/loading/framework architecture without discussion.
- In-battle descriptions should usually be one clear sentence, two at most.
  Detailed calculations belong in unit inspection/reference views.
- Treat this brief as context; the current repository and canonical docs are the
  source of truth when writing implementation-specific instructions.

---
