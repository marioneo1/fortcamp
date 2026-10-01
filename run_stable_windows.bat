@echo off
cd /d "%~dp0"
if exist .fortcamp-release.json (
  call run_release_windows.bat
) else (
  echo This is the development copy. Run run_release_windows.bat in the sibling release folder.
  pause
)
