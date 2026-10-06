# Development runner and uninterrupted playtesting

Run `run_dev_windows.bat` in fortcamp-dev for browser and Discord playtesting. The dev-discord profile retains real authentication, the dev bot, debug tools and isolated dev saves. Browser port is 5174; API port is 8001. Keep the existing Cloudflare route running.

## Default: uninterrupted session

The launcher builds current browser files before starting the services, then serves that build with Vite preview and the existing API proxy. There is no Vite reload client in this browser build and no automatic backend source reloader. Source/art edits during play do not instruct the browser to refresh. Restart the launcher to build/load changed code. A failed build stops startup and retains its output; it does not silently serve an older build.

The server remains authoritative for combat. Debug features are controlled by the existing backend configuration, not whether frontend files are bundled. This is still the dev profile; no production credentials, data or rollout are involved.

Optional live-edit mode: set `FORTCAMP_DEV_AUTO_RELOAD=true` in dev `.env`, then restart. This uses Vite's development server and automatic browser updates; Python watches only `backend`, not tools/tests/staging. File changes can reset a play session. Vite's live connection can also reload the page after reconnecting without a source edit. Use default mode for long Battle Lab tests. Remove the setting or set it to false to return to uninterrupted mode.

The reported browser-only refresh had no corresponding crash/restart in the available server log. Development reload/reconnect is a plausible cause, not a proven diagnosis of that particular occurrence. Disabling the reload client removes both source-edit and reconnect-triggered Vite reloads. It does not claim to cure unrelated browser crashes, tunnel failures or user navigation.

## Logs

Combined backend/frontend output remains visible and is timestamped in `data/logs/dev-discord-latest.log`. Local-only dev uses `dev-latest.log`. Before overwriting latest at a new launch, the runner preserves it under a timestamped filename in the same directory. Logs are local and ignored by Git. Python fault handling is enabled for diagnostic output when supported; native termination may still emit no traceback.

Unexpected service exit prints its code, stops only this runner's services and returns failure; the batch window pauses. Ctrl+C is a normal shutdown. The runner does not automatically restart failed services or reload the game. Timestamped logs can distinguish API failure from an ordinary browser reload, but cannot prove the reason for a browser-only event without browser evidence.

Validation: runner/profile tests cover safe production isolation, optional backend reload scope, failed-build output, abnormal service exit and previous-log preservation. A real Vite preview fixture checks served HTML has no reload client, game JavaScript loads, and the API proxy still works. Vite reference: https://vite.dev/config/server-options (watch/HMR); installed Vite 6.4.3 client also explicitly reloads after its live socket reconnects.
