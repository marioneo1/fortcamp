# Development runner and uninterrupted playtesting

Run `run_dev_windows.bat` in fortcamp-dev for browser and Discord playtesting. The dev-discord profile retains real authentication, the dev bot, debug tools and isolated dev saves. Browser port is 5174; API port is 8001. Keep the existing Cloudflare route running.

## Default: uninterrupted session

The launcher serves source files with Vite dev on port 5174 and the existing API proxy. It does not build first or use preview mode. Normal mode disables watchers/backend reloading and substitutes a tiny CSS-only module for Vite's `/@vite/client`: styles still load, but there is no live socket, reconnect logic or page-reload instruction. This dev-only adapter is for installed Vite 6.4.3 and is checked by actual server tests. It is not bundled into production.

Restart the launcher to load edited source in steady mode. Optional live editing restores the stock Vite client and watcher. The preceding built-preview experiment was rolled back following reported loading/effect regressions; the distinction is preserved in history rather than retaining two parallel dev paths.

The server remains authoritative for combat. Debug features are controlled by the existing backend configuration, not whether frontend files are bundled. This is still the dev profile; no production credentials, data or rollout are involved.

Optional live-edit mode: set `FORTCAMP_DEV_AUTO_RELOAD=true` in dev `.env`, then restart. This uses Vite's development server and automatic browser updates; Python watches only `backend`, not tools/tests/staging. File changes can reset a play session. Vite's live connection can also reload the page after reconnecting without a source edit. Use default mode for long Battle Lab tests. Remove the setting or set it to false to return to uninterrupted mode.

The reported browser-only refresh had no corresponding crash/restart in the available server log. Development reload/reconnect is a plausible cause, not a proven diagnosis of that particular occurrence. Disabling the reload client removes both source-edit and reconnect-triggered Vite reloads. It does not claim to cure unrelated browser crashes, tunnel failures or user navigation.

## Logs

Combined backend/frontend output remains visible and is timestamped in `data/logs/dev-discord-latest.log`. Local-only dev uses `dev-latest.log`. Before overwriting latest at a new launch, the runner preserves it under a timestamped filename in the same directory. Logs are local and ignored by Git. Python fault handling is enabled for diagnostic output when supported; native termination may still emit no traceback.

Unexpected service exit prints its code, stops only this runner's services and returns failure; the batch window pauses. Ctrl+C is a normal shutdown. The runner does not automatically restart failed services or reload the game. Timestamped logs can distinguish API failure from an ordinary browser reload, but cannot prove the reason for a browser-only event without browser evidence.

Validation: runner/profile tests cover safe production isolation, optional backend reload scope, abnormal service exit and previous-log preservation. A real Vite source-server fixture checks the client has no socket/reload logic, game JavaScript and CSS helpers load, no-store headers apply, and the API proxy still works. Vite reference: https://vite.dev/config/server-options (watch/HMR); installed Vite 6.4.3 client also explicitly reloads after its live socket reconnects.


## Cold presentation assets

Mage sprites are warmed from the battle's equipped skills. Before manual or automatic command playback starts, required returned spell/ground images are loaded and decoded through a shared cache. The pending-command lock remains active, so no enemy/player action races ahead of the delayed impact clock. Missing assets/timeouts resolve after a bounded eight-second wait rather than locking combat forever; normal warmed casts add no network wait. A tiny initial HTML rule hides inactive screens before the main stylesheet arrives. This pass does not preload every map/portrait or claim to eliminate all first-load network latency.


October 6 startup regression: Vite's versioned CSS imports still requested `createHotContext`, even in steady mode. The initial adapter omitted that export and stopped the entire module graph before initialization. The adapter now provides the inert context methods as well as style helpers; no reload connection is opened. Actual source-server tests include versioned CSS requests, context methods and style application. Browser fixture previews use the same adapter instead of the stock client, so full game/CSS imports exercise it too. Restart an already running dev server after this fix because its middleware cached the preceding client source.


## Temporary browser QA profiles

Use the checkout-local `data/browser-qa/profile` for isolated Chrome QA via
`--user-data-dir` with an absolute resolved path. Do not create drive-root profiles.
The data directory is ignored by Git; this is browser cache/preferences, not game saves.
Historical drive-root QA profiles were moved to `data/browser-qa/archived-profiles`
on October 7 after confirming none was in use. Browser QA scripts connect to CDP
port 9229 and local fixtures on port 8766; the scripts do not hardcode a profile path.


### October 7: repeated loading investigation

The running dev-discord session was verified to use Vite source mode, auto_reload=false, with no built-preview switch. The Unit details refinement did not change the launcher, API polling or asset-loading strategy. Read-only asset probes confirmed existing no-store headers; however, Chrome reused an identical decoded image within the same document with no second HTTP response, so no-store alone was not established as the cause of repeated delays. Cache policy remains unchanged. The isolated fixture cannot establish timings in the user's live Discord/browser session.

Inspector redraws now preserve unchanged DOM; see COMBAT_STATUS_PRESENTATION.md. tools/combat_loading_browser_qa.mjs profiles fixture rendering and History; --live-assets optionally performs two read-only image loads from localhost:5174, never authenticated APIs or saves. Restart the normal steady-mode dev launcher to load changed source; no automatic restart was performed during an active user session.
