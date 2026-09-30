@echo off
set "FORTCAMP_MUSIC_PREVIEW=%~dp0staging-music\guild-board-candidates-v1\LISTEN.html"
if not exist "%FORTCAMP_MUSIC_PREVIEW%" (
  echo Music candidates are not ready yet. Ask for the generation status.
  pause
  exit /b 1
)
start "" "%FORTCAMP_MUSIC_PREVIEW%"
