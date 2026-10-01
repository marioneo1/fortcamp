# Running the friend trial

The trial and development share credentials in `.env`, but run different code and databases. Artwork is copied into each trial release. Editing source or portraits in the workspace cannot change an already prepared trial release.

| | Friend trial | Development |
|---|---|---|
| Start | `run_stable_windows.bat` | `run_dev_windows.bat` |
| Browser port | 5173 (existing Cloudflare route) | 5174 (local only) |
| API | Same server on 5173 | 8001 |
| Save | `data/fortcamp-stable.db` | `data/fortcamp-dev.db` |
| User-uploaded portraits | `data/stable_portraits/` | `data/dev_portraits/` |
| Code | Pinned release, no reload | Workspace with automatic reload |
| Debug/auth bypass | Both off | Both on |
| Bot | On | Off (no competing commands/announcements) |
| Mission time scale | 1.0 | 0.05 |

## First switch

1. Close the older Fortcamp backend/frontend runner so port 5173 is free. Leave your persistent Cloudflare tunnel running.
2. Double-click `run_stable_windows.bat`. The prepared release serves the built game and API together on 5173. Leave its single control window open; Ctrl+C stops its own server.
3. Keep `play.fortcampgame.fyi` routed to `http://127.0.0.1:5173`. No Cloudflare/Discord URL changes are needed for this switch.
4. In the Discord Developer Portal, select the existing Fortcamp app. Open **Installation**, enable **Guild Install**, and include **bot** and **applications.commands** in its default installation settings. Copy its installation link and have a server owner or manager install it in your friend's server. Grant View Channel, Send Messages, and Embed Links for its announcements. [Discord installation guide](https://github.com/discord/discord-api-docs/blob/main/developers/quick-start/getting-started.mdx).
5. For an unverified Activity, add your friend under **App Testers** and have them accept the email invitation. In Discord desktop **Settings > Advanced**, enable **Application Test Mode**, paste the application's ID from Developer Portal **General Information**, and activate it. Discord documents unverified Activity testing in servers with **fewer than 25 members**, so the approximately 20-member server fits that limit. [Discord's testing instructions](https://support-dev.discord.com/hc/en-us/articles/21204493235991-How-Can-Users-Discover-and-Play-My-Activity).
6. Each participating player runs **`/register`** in that server before opening the Activity. A server manager runs **`/fortcamp_setup`** in the channel where pool announcements should go. Launch the Activity from that server's voice channel; saves and registrations are server-specific.

You do not need privileged member-list access or to register all 20 members. Only opted-in registrations scale mission generation. New registrations can add missions to the existing pool; unregistering reduces future pool sizes without removing missions someone already sees or owns.

## Settings

The trial launcher forces `DEV_BYPASS_AUTH=false`, `GAME_DEBUG_MODE=false`, `MISSION_TIME_SCALE=1.0`, `BOT_ENABLED=true`, and an empty `DISCORD_TEST_GUILD_ID` so guild commands sync in all installed servers. Your `.env` now has the first three safe defaults and the test-guild restriction cleared. Keep the configured Discord credentials, session secret, tunnel settings and public hostname. Do not manually share this file.

`/unregister` pauses participation and new contract claims. It **does not delete characters, equipment, gold, prisoners, or progress**; existing timed expeditions can still resolve. `/register` restores access to the same save. Older saves receive a registration once during migration; inactive registrations are never reactivated by a restart. Full deletion is a separate local administrator action with a database backup.

## Developing and updating

Run `run_dev_windows.bat` alongside the trial and open `http://127.0.0.1:5174`. Its fresh local save and disabled bot cannot affect your friends. Use the trial Activity in Discord; testing a dev build inside Discord later requires a separate Discord app/URL mapping, rather than redirecting the trial hostname.

When a change has been checked and committed, run **`update_stable_windows.bat`**. It builds and copies a new version into `.fortcamp-releases/` and updates the pointer for the **next** stable start. Running players stay on their existing release until you stop and restart `run_stable_windows.bat`. Choose a quiet time between battles. The stable save is never replaced on an update. The release records its Git commit; previous release folders are retained for rollback. Code and media are pinned; Python dependencies still use this workspace's virtual environment, so avoid upgrading dependencies during a live trial without testing.

Player-uploaded portraits live outside the release and survive updates alongside the save. Generic and Champion portrait pools are copied into each release so editing those source assets during development does not change the running trial.

## Reset recorded for this pass

Grimm's original save and 168 owned contracts were removed after a consistent SQLite backup. Shared contracts and guild configuration were preserved. The initial stable database starts from that reset save; the dev database starts separately. Backups are under `data/backups/` and are excluded from GitHub.

Future targeted resets use `tools/reset_player.py --database data/fortcamp-stable.db --guild SERVER_ID --user USER_ID`. Stop the trial first. This resets only that server/player's save, registration and owned mission rows; it keeps a backup and other players' data.
