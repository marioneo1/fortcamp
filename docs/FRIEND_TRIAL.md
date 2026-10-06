# Development and production

## Folders and launchers

| Folder | Purpose | Launcher |
| --- | --- | --- |
| `E:/Other Games/Fortcamp/fortcamp-dev` | Editable development code, branch `main`, isolated development saves | `run_dev_windows.bat` |
| `E:/Other Games/Fortcamp/fortcamp-prod` | Prepared production code and built assets, branch `release` | `run_prod_windows.bat` |
| `E:/Other Games/Fortcamp/fortcamp-release-data` | Production database, uploaded portraits, and database backups | None; keep this folder |
| `E:/Other Games/Fortcamp/fortcamp-backups` | Prior production copies and rename/environment recovery files | Rollback only |
| `E:/Other Games/Fortcamp/fortcamp-reference` | Preserved Fork of Chains reference source and old hosting notes | None |

Production data is shared by successive production builds, not by development. `fortcamp-release-data/fortcamp.db` stores all servers using the production instance. Saves, registrations and guild settings are separated by Discord server ID and user ID inside that database. It is not a separate server, executable, or a development save. Do not delete or move it for ordinary updates. Development uses `fortcamp-dev/data/fortcamp-dev.db` and its own uploaded portrait folder.

The former nested alpha workspace is now `fortcamp-dev`. The previous versioned trial copy is preserved under `fortcamp-backups`. Names do not change Cloudflare routes, Discord application IDs, server registration, or production save locations. Dev's moved database has a new canonical path; a cached dev login may need refreshing once, but progress and registration are preserved.

## Run with friends

1. Keep the persistent Cloudflare tunnel running. Its `play.fortcampgame.fyi` route stays on **HTTP 127.0.0.1:5173**.
2. Double-click **run_prod_windows.bat** inside `fortcamp-prod`. One control window owns the server; Ctrl+C stops it. Do not start an older production copy too.
3. Open **https://play.fortcampgame.fyi/**, sign in with Discord, and select the friend's server.
4. If the production bot is already installed and configured in that server, nothing needs reinstalling. A server manager runs **/fortcamp_setup** in the announcement channel if it has not been configured. New players run **/register** once in that server. Existing players keep their registrations through updates and restarts.
5. If the bot is not installed, use the original production application's installation link from [Discord Developer Portal](https://discord.com/developers/applications), with Guild Install, `bot` and `applications.commands`. The installer needs Manage Server permission. The announcement channel needs View Channel, Send Messages and Embed Links for the bot.

Browser play does not require embedded Activity tester configuration. For embedded Activity testing, preserve the application's existing URL mapping, App Tester access and Application Test Mode. See [browser play](WEB_PLAY.md) for OAuth and development-app details. The production OAuth redirect remains **https://play.fortcampgame.fyi/api/web/callback**.

Only registered players scale new mission pools. `/unregister` pauses participation and preserves progress; it does not delete the player's account or character. Each server requires its own registration.

## Develop safely

Run **run_dev_windows.bat** in `fortcamp-dev`, then use **https://dev.fortcampgame.fyi/** or the dev Discord Activity. This single dev launcher runs the bot and real Discord login for both interfaces, with debug tools enabled and separate dev saves. Frontend port is 5174; backend port is 8001. Keep the dev Cloudflare route running. Source edits and dev builds cannot change the prepared production copy.

The currently configured dev and prod environments still use the same Discord application. Do not run the authenticated dev launcher while production is running until a separate development application has been configured. The launcher checks this. A production copy refuses dev launch profiles to prevent accidentally testing against the wrong folder.

Production launch forces **GAME_DEBUG_MODE=false**, **DEV_BYPASS_AUTH=false**, **BOT_ENABLED=true**, **MISSION_TIME_SCALE=1.0**, and global command registration. Its private `.env`, signing secret and OAuth configuration are preserved from production; dev credentials are never automatically copied. Keep secrets and generated runtime media out of GitHub.

## Update the same production folder

1. Finish tests in `fortcamp-dev` and commit the source changes.
2. Stop production with Ctrl+C in its control window. Keep Cloudflare running.
3. Double-click **update_prod_windows.bat** inside `fortcamp-dev`.
4. When preparation finishes, double-click **run_prod_windows.bat** inside the same `fortcamp-prod` folder.

The updater refuses to replace a running server, saves a consistent SQLite backup under `fortcamp-release-data/backups`, archives the old production folder under `fortcamp-backups`, and prepares the tested commit in the fixed `fortcamp-prod` location. It installs independent packages, builds/copies frontend media and portraits, preserves production credentials, and never replaces an existing production save. If preparation fails, it retains the failed build for inspection and restores the preceding production folder. It publishes a version tag and fast-forwards GitHub's `release` branch without force-pushing.

The old `create_release_windows.bat` is replaced by `update_prod_windows.bat`. The command-line builder can still make a separately versioned clone with `--version`, but normal updates use `--prod`. Do not blindly pull source into production: startup validates the source commit against its prepared assets.

## Backup and reset

Updating production does not wipe characters, existing contracts, registrations, or uploaded portraits. Prior production copies and database backups remain local and excluded from GitHub. Rollback after future incompatible data migrations may require the matching database backup; do not restore an older database over live progress casually.

Targeted resets remain an explicit operation using `tools/reset_player.py --database "E:/Other Games/Fortcamp/fortcamp-release-data/fortcamp.db" --guild SERVER_ID --user USER_ID` while production is stopped. Do not use resets or unregistering to perform an ordinary code update.

## October 2 deployment

The current production preparation includes the tested mercenaries, quieter regional events, matching starter kits, camp/roster/inventory workspaces, and item sales. See [mercenary rules](design/MERCENARIES.md). Save isolation, production flags, rollback-on-build-failure and launcher guards are tested; actual Discord installation and server permissions remain account-specific.


## Launcher cleanup ? October 2

There is one game launcher in each folder: run_dev_windows.bat for authenticated browser and Discord development, run_prod_windows.bat for production. The former separate Discord shortcut is removed. Stop either session with Ctrl+C in its control window; the obsolete stop_dev_windows.bat was removed because it targeted the old three-window setup and could also stop the shared tunnel. Keep Cloudflare running independently.

Release preparation excludes dev-only launch/update shortcuts from the production checkout using Git sparse checkout. This keeps the pinned production source clean and its integrity check intact. The currently installed production copy received only that launcher cleanup; it was not upgraded or restarted. Developer-only unauthenticated local diagnostics remain available through `.venv\Scripts\python.exe tools\run_profile.py dev`; this is an internal option, not a second everyday launcher.


## October 3: production update packaging

Release updates now include shared portrait framing defaults alongside portrait assets, exclude the obsolete macOS/Linux dev shortcut, and require clean tracked source while leaving unrelated untracked notes alone. Production launch continues to force debug and authentication bypass off; production credentials, player saves and uploads stay separate. The standalone portrait tagging tool remains separate from game runtime metadata.

Validation: 142 frontend checks passed. Full backend run passed 355/356; the remaining special-Goblin portrait test depended on an optional uninstalled male art pool. Isolated that test with both special pools supplied explicitly; production fallback behavior remains unchanged.


October 6 dev testing update: the normal dev launcher serves source browser files without automatic refresh or a startup build; restart it to load code changes. Debug tools, Discord/web authentication, ports and dev saves remain the same. Optional live-edit mode and preserved session logs: [Development runner](design/DEVELOPMENT_RUNNER.md).
