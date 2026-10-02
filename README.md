# Fortcamp

Fortcamp is a Discord Activity fantasy settlement game with shared ranked contracts, owner-only Private Contracts, character collections, and tactical grid encounters. Some missions resolve through rolls; others offer decisions, fights, rescues, or defense objectives. This repository tracks the evolving alpha rather than a finished release.

## Run on Windows

1. Run `setup_windows.bat` to install dependencies.
2. Copy `.env.example` to `.env` and configure your Discord application and hosting values.
3. Run `run_dev_windows.bat`. The frontend uses port 5173 and the backend uses port 8000.
4. For Discord hosting, configure the application's URL mapping and your Cloudflare route, then use `start_tunnel_windows.bat` if a tunnel service is not already running.

See [Windows tools](WINDOWS_TOOLS.md) for launcher purposes and limitations. Keep credentials in `.env`.

## Current development

Read the [documentation index](DOCUMENTATION.md), [feature backlog](FEATURE_BACKLOG.md), and [gameplay vision](GAMEPLAY_VISION.md). The backlog distinguishes implemented foundations from future design. The [implementation log](docs/history/MISSION_REFINEMENT_PHASE.md) records content and validation passes.

Music includes guild rotation, base themes, and scenario playlists with fades. Sound settings control Master, Music, Interface & Mission Sounds, and Battle Effects. Local assets are required to hear the soundtrack.

## Assets and player data

Generated portraits, terrain, UI artwork, sound effects, music, player databases, build outputs, and secrets are intentionally excluded from Git. A clone contains the code and tools, but does not include the complete local art/audio library or saved game. Back up those folders separately; Git does not protect them. Preserve original sources and asset manifests when transferring the game to another machine.

## Validation

Run frontend tests with `node --test src/*.test.js` from `frontend`, and build with `npm run build`. Python tests live under `tests`; use the project virtual environment. Do not run paid generation tools without reviewing their options and authorization.

Public code repository: [marioneo1/fortcamp](https://github.com/marioneo1/fortcamp).


Documentation: [system map and glossary](docs/INDEX.md), [current backlog](FEATURE_BACKLOG.md), [relationships](docs/design/CHARACTER_RELATIONSHIPS.md).
