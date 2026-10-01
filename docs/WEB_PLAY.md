# Browser play and separate dev/release environments

Fortcamp now supports normal browser play through Discord OAuth, alongside the Discord Activity. Both interfaces use the same `(Discord server, Discord user)` save and mission pool in their environment. Servers never share characters, inventory or contracts. Website play does not create a separate copy of the player's save.

After login, choose a server you belong to where this instance's bot is currently installed. Run `/register` with the correct bot in that server first. The picker marks registration status and gives a retryable message if registration is missing. `Change server` reloads the interface before selecting a different session; background requests cannot keep using the previous server's UI. Sign out removes the browser login session and selected game token without deleting game data.

## Set up development once

The existing alpha and trial `.env` files used the same Discord application. Do not run both bots with those same credentials. Alpha's signing secret has been made independent; create a separate development application to finish separating the Discord side.

1. Open [Discord Developer Portal](https://discord.com/developers/applications). Create an application named **Fortcamp Dev**.
2. In **OAuth2 → Redirects**, add exactly `https://dev.fortcampgame.fyi/api/web/callback` and save. Browser login requests only `identify` and `guilds`, not bot installation permission.
3. Put that new application's Client ID, Client Secret and Bot Token into **alpha's `.env`** under `DISCORD_CLIENT_ID`, `DISCORD_CLIENT_SECRET`, `DISCORD_BOT_TOKEN`. Do not edit the existing release's `.env` or paste secrets into chat.
4. Install **Fortcamp Dev** in your test Discord server, enabling the `bot` and `applications.commands` scopes (Developer Portal Installation settings / install link). Use the server installation type. Register with that bot using `/register`. Existing dev saves/registration rows are preserved; a code change does not require registering again.
5. Keep the existing Cloudflare route **dev.fortcampgame.fyi → http://127.0.0.1:5174**. No new tunnel route is needed for the callback.
6. Close the old alpha runner and start **run_dev_discord_windows.bat**. Open **https://dev.fortcampgame.fyi/** in your browser. Choose **Sign in with Discord**, then select your server.

If the dev application should also run the embedded Activity, configure its Activity URL mappings/App Testers using [FRIEND_TRIAL.md](FRIEND_TRIAL.md). Browser play does not need the Activity configuration itself.

`run_dev_windows.bat` remains the local bypass/testing option on port 5174; it does not run a bot or display the real Discord server picker. Use the authenticated dev launcher for website play with Discord accounts.

## Set up the release

1. Open the **original production Discord application**, not Fortcamp Dev. Add exactly `https://play.fortcampgame.fyi/api/web/callback` in **OAuth2 → Redirects**, then save.
2. Prepare the next release from committed alpha code using **create_release_windows.bat**, with a new version such as `0.3.1-trial.2`.
3. The builder takes production credentials from the previously prepared release, or a private alpha `.env.release` if you explicitly supply one. It never automatically copies alpha's development `.env` into production. Credentials and the production signing secret persist independently.
4. Stop the old release runner, keep Cloudflare running, and start **run_release_windows.bat** inside the new release folder. Open **https://play.fortcampgame.fyi/**. Website and Activity players in that environment share their existing saves.

The currently pinned `fortcamp-release-0.3.1-trial.1` was not edited or restarted by this pass. It gains browser play only when switched to a new release containing this code. Preparing a release does not change a running game or overwrite the production save.

## Isolation and persistence

| | Development | Release |
|---|---|---|
| Website | dev.fortcampgame.fyi | play.fortcampgame.fyi |
| Frontend/public port | 5174 | 5173 |
| API port | 8001 | 5173 |
| Saves | alpha/data/fortcamp-dev.db | fortcamp-release-data/fortcamp.db |
| Bot application | Fortcamp Dev | Original Fortcamp |
| Debug controls | Enabled for permitted testers/admins | Disabled by launcher |
| Browser badge | DEV · Test saves | Normal game |

Game JWTs bind to environment, Discord application and canonical database location. Other environments reject them even if signing secrets match; older unscoped tokens must log in once again. Alpha also has its own signing secret. Browser cache keys and host-only cookie names include the namespace. Profile launchers set the appropriate origin independently. Updated launchers check for duplicate live application IDs and stop before launching a conflicting bot. The dev runner also rechecks while running so it can stop its own session if an older release starts with the same app. Separate applications remain required.

Browser account sessions last up to 12 hours and persist in the environment's database through backend restarts/reloads. Cached game sessions restore without another Discord authorization. Renewing login requests `prompt=none` so Discord can skip consent for previously approved scopes. The cookie is HttpOnly, SameSite=Lax, host-only and Secure on HTTPS; its opaque value is stored only as a hash. Discord OAuth access tokens are used during callback and then discarded. Only server IDs/admin flags are retained. Server selection checks current bot installation, current user membership and active game registration before issuing a server-scoped game session.

Newly joined Discord servers may require **Refresh Discord login** to update the membership snapshot. `Refresh list` updates current bot installations and game registrations. Bot connection/API errors show Retry rather than falling back to another environment.

OAuth state is signed, short-lived and tied to a cookie. Redirects use the configured origin; request host input cannot choose a different callback. Server-selection/logout POSTs require that exact Origin. Development's Vite proxy preserves the original public Host and Origin for these checks.

Optional overrides in alpha/release env files: `FORTCAMP_DEV_WEB_ORIGIN` and `FORTCAMP_RELEASE_WEB_ORIGIN`. Defaults already match the two domains above. To test real browser OAuth on localhost, set the dev override to `http://127.0.0.1:5174` and add `http://127.0.0.1:5174/api/web/callback` to the **dev** application's OAuth2 Redirects. Restart the authenticated dev launcher afterward.

Discord requires the authorization and token-exchange redirect URI to match the registered redirect. See [Discord OAuth2 documentation](https://discord.com/developers/docs/topics/oauth2).

## Verification

Automated tests cover OAuth state/cookie validation, expiration, server-list filtering, current-membership checks, registration gating, logout, restart persistence, scoped JWT rejection and credential-safe release preparation. A real Vite proxy test checks Host/Origin forwarding. The isolated browser fixture (`tools/build_web_login_preview.py`, served by `tools/serve_board_preview.mjs`) exercises actual frontend startup, server selection, DEV labeling, selected-token API requests and narrow-screen layouts without live Discord/player data. `tools/web_login_browser_qa.mjs` runs it with a dedicated Chrome debugging session on port 9229.

Actual Discord authorization still requires adding the portal redirect URLs and installing/configuring the separate dev application; those account actions cannot be completed from the local workspace.
