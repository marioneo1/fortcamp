# Windows launchers and tools

Audit date: September 30, 2026. This is a source/path/dependency audit, not a claim that every interactive workflow was launched. Starting/stopping live servers, opening both portrait editors, modifying portraits, enabling a public tunnel, and installing dependencies were deliberately not executed for this audit.

## Everyday use

| Launcher | Purpose | Audit result |
| --- | --- | --- |
| `run_dev_windows.bat` | Start backend and frontend; its control window stops Fortcamp when you press a key | Targets exist. Quoted working directory, explicit venv Python, npm preflight and frontend working directory corrected. New launcher has not been used to restart the user's current game. |
| `stop_dev_windows.bat` | Stop Fortcamp's titled backend, frontend and tunnel windows | Matches titles assigned by the launchers; deliberately not executed against the running game. It does not stop unrelated manually started processes or a background Windows tunnel service. |
| `start_tunnel_windows.bat` | Run configured Cloudflare Tunnel, or a temporary tunnel if none is configured | cloudflared is installed. Named/token modes read .env; no secret was displayed. Connectivity depends on Cloudflare route/DNS and a live frontend. Does not start the game. |

## Occasional setup and content tools

| Launcher | Purpose | Audit result |
| --- | --- | --- |
| `setup_windows.bat` | Create venv and install Python/frontend dependencies | Python launcher and npm available; requirements and frontend package files exist. Quoted root path corrected. Installer not rerun; existing environment preserved. |
| `run_champion_portrait_manager_windows.bat` | Open Champion portrait editor | pythonw and target script exist; tkinter and Pillow import successfully; source compiles. GUI not opened during audit. |
| `run_portrait_pool_importer_windows.bat` | Open generic-race portrait pool importer | Same GUI dependencies and source checks pass. GUI not opened during audit. |
| `fix_champion_batch_crops_windows.bat` | Back up and repair one 4x4 Champion sheet | Target exists; its `--batch` CLI was verified with `--help`. No crop changes made. This is not the generic 5x4 importer. |
| `setup_tailscale_funnel_windows.bat` | Optional alternative public hosting setup | tailscale is installed; targets frontend port 5173. Kept as an optional alternative, not needed for the current Cloudflare domain. Not run. |

The music-only batch shortcut was removed as redundant. Use **Sound settings -> Music library** in the game or open `staging-music/LISTEN.html` directly. No new launcher is required for each music pack.

## Maintainer commands

- `tools/generate_music_candidates.py --process-only`: reprocess the saved guild originals, without paid requests.
- `tools/generate_music_candidates.py --pack locations --process-only`: reprocess saved base/combat originals, without paid requests.
- `tools/build_music_library.py`: rebuild the local and hosted listening page without generation.
- Omitting `--process-only` from a generation command may purchase missing tracks. Existing originals are reused; uncertain requests block automatic paid retries.

Use the project venv Python for these commands. Tool code is tracked in Git; generated assets, player data and secrets remain separate. Update this inventory when adding, retiring or changing a launcher. Do not claim operational verification based only on a file existing.
