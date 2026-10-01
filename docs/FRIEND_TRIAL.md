# Development and release copies

The current workspace stays the development copy on Git branch `main`. The friend trial is an independent Git clone on branch `release`, connected to the same GitHub repository. It has its own `.env`, virtual environment, source, built frontend, generic/Champion portraits, and frontend art/audio assets. No junctions or shared code directories are used.

## Folders

- Development: `E:/Other Games/Fortcamp/fortcamp-alpha-0.3.1/fortcamp-alpha-0.3.1`
- First release: `E:/Other Games/Fortcamp/fortcamp-release-0.3.1-trial.1`
- Production progress and uploaded portraits: `E:/Other Games/Fortcamp/fortcamp-release-data`

The production data folder stays in place when you create a newer version. Preparing or starting a new release never replaces an existing production database. Development saves remain inside the dev copy and cannot affect friends. The original internal `.fortcamp-releases` snapshots are legacy and preserved; launch the sibling copy instead.

| | Release copy | Development copy |
|---|---|---|
| Start in its folder | `run_release_windows.bat` | `run_dev_windows.bat` |
| Browser/public port | 5173 | 5174, local only |
| API | Same server on 5173 | 8001 |
| Save | `../fortcamp-release-data/fortcamp.db` | `data/fortcamp-dev.db` |
| Uploaded portraits | `../fortcamp-release-data/portraits/` | `data/dev_portraits/` |
| Git branch | `release` | `main` |
| Source reload | Off | On |
| Debug/auth bypass | Both off | Both on, launcher overrides |
| Bot | On | Off |
| Mission time scale | 1.0 | 0.05 |

## Start the friend trial

1. Stop the older Fortcamp backend **and** Vite frontend. Do not leave the old backend's Discord bot running alongside the release. Leave the persistent Cloudflare tunnel running.
2. Open `E:/Other Games/Fortcamp/fortcamp-release-0.3.1-trial.1` and double-click **run_release_windows.bat**. Keep this single control window open; Ctrl+C stops the server it launched. Port conflicts are reported rather than killing unrelated processes.
3. Keep Cloudflare's `play.fortcampgame.fyi` route pointed at **http://127.0.0.1:5173**. Keep the existing Discord URL mapping. There is no Vite development server needed for the release.
4. In the [Discord Developer Portal](https://discord.com/developers/applications), select the existing Fortcamp application. Under **Installation**, enable **Guild Install**, with **bot** and **applications.commands**. Copy the installation link and have your friend install it in the server as an owner or member with Manage Server permission. Grant View Channel, Send Messages and Embed Links in the announcement channel. [Official installation guide](https://github.com/discord/discord-api-docs/blob/main/developers/quick-start/getting-started.mdx).
5. For an unverified Activity, go to **App Testers**, add your friend's Discord username, and have them accept the email invitation. In their Discord desktop **User Settings > Advanced**, enable **Application Test Mode**, paste the Application ID from the developer portal's **General Information**, and activate it. Discord documents unverified testing in servers with **fewer than 25 members**, so approximately 20 members fits. Add each additional tester who needs access. [Official tester instructions](https://support-dev.discord.com/hc/en-us/articles/21204493235991-How-Can-Users-Discover-and-Play-My-Activity).
6. A server manager runs **/fortcamp_setup** in the desired announcement channel. Each player runs **/register** in this server, then launches Fortcamp from a voice channel's Activity launcher. Each server has its own saves and registrations.

Only registered people scale mission generation, not all server members. Registration works before creating a character. **/unregister does not delete progress**: it pauses new contract access and excludes the person from future pool sizing; **/register** restores their existing save. Already generated public missions are not removed when somebody unregisters.

## Environment files

The release has its own local `.env` copied during creation, with safe production defaults. Its launcher also forces `DEV_BYPASS_AUTH=false`, `GAME_DEBUG_MODE=false`, `MISSION_TIME_SCALE=1.0`, `BOT_ENABLED=true`, and an empty `DISCORD_TEST_GUILD_ID` so commands sync to all installed servers. Discord credentials, the session secret and tunnel settings were copied without being printed or committed. These local files stay excluded from GitHub.

The dev launcher forces local debug/auth bypass on and the bot off, regardless of inherited settings. Changing dev settings after release creation does not alter the release's `.env`. If you rotate a Discord credential later, update each copy that needs it.

## Continue developing

Open the original development folder and run **run_dev_windows.bat**, then use **http://127.0.0.1:5174** in your browser. Edit and test here. Commit/push development work to **main**. Leave the release folder alone while friends play: it has separate packages and code, so source edits, installs, builds, and dev restarts cannot modify its running game.

This browser-based dev mode uses local test identities. To test development inside Discord while the trial remains live, create a separate Discord development application and dev hostname/URL mapping later; do not point the production app at dev or expose the auth-bypass dev port publicly.

## Publish a tested update

1. Finish testing in dev and commit all source changes. Update `requirements.lock.txt` deliberately if Python packages change; test the pinned versions. Generated runtime media stays local, but the release builder copies it.
2. In the **dev** folder, run **create_release_windows.bat** and enter a new version, for example **0.3.1-trial.2**.
3. The builder fast-forwards GitHub's `release` branch to the tested commit, creates a separate `fortcamp-release-0.3.1-trial.2` clone, installs its own pinned Python packages, builds/copies the frontend and media, and publishes tag **v0.3.1-trial.2**. It never force-pushes, overwrites an existing version folder/tag, or replaces production progress. Running friends remain on the old copy.
4. When players are between battles, Ctrl+C in the old release control window. Run **run_release_windows.bat** in the new folder. It uses the same production data folder and public port, so saves, uploaded photos, Cloudflare and Discord URLs stay unchanged.
5. Keep the previous release folder for rollback. Switching code back may not be safe after incompatible future database migrations; back up the production save before such upgrades. Do not blindly pull source inside a running release: launch checks reject a commit that no longer matches its prepared assets.

Both copies are Git repositories linked to `https://github.com/marioneo1/fortcamp.git`. A version tag identifies exactly which source a release contains. The release branch can advance when another release is prepared; the old local clone does not update automatically.

## Reset and backups

Grimm's original save and 168 owned contracts were reset with a consistent SQLite backup. Shared contracts and guild configuration were preserved. The initial production data was bootstrapped from that reset save. Backups and private runtime data are excluded from GitHub.

Future targeted resets: stop the release and run `tools/reset_player.py --database "E:/Other Games/Fortcamp/fortcamp-release-data/fortcamp.db" --guild SERVER_ID --user USER_ID` using that copy's Python environment. The reset keeps a backup and preserves other players and shared missions. Unregistering is not this reset operation.
