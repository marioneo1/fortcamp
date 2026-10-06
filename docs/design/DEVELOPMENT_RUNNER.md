# Development runner diagnostics

Run `run_dev_windows.bat` in fortcamp-dev for the combined web/Discord development
session. Its profile is dev-discord; credentials and saves remain isolated from
production. This pass does not modify production launchers or environments.

The runner keeps backend/frontend output visible and writes it to
`data/logs/dev-discord-latest.log`. The local-only dev profile uses
`data/logs/dev-latest.log`. Logs are ignored by Git. The latest file is overwritten
at the next launch; preserve it before restarting if a failure needs investigation.

An unexpected child exit now prints its exit code, stops only the processes owned
by this session and returns a failing exit code. The existing batch file then
pauses, allowing the error to be read. Ctrl+C remains a normal shutdown.

The log preserves Python tracebacks and process exit codes; it cannot recover
output that a native crash or forced termination never emitted. A past unexplained
window closure is not considered diagnosed merely because navigation tests pass.

A simulated failing child test checks retained output and the failing launcher
exit code. Profile isolation tests remain required when editing this runner.
