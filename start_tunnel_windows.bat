@echo off
setlocal
title Fortcamp Tunnel
set "FORTCAMP_TUNNEL_TOKEN="
set "FORTCAMP_TUNNEL_NAME="
if exist "%~dp0.env" for /f "usebackq tokens=1,* delims==" %%A in ("%~dp0.env") do (
  if /I "%%A"=="FORTCAMP_TUNNEL_TOKEN" set "FORTCAMP_TUNNEL_TOKEN=%%B"
  if /I "%%A"=="FORTCAMP_TUNNEL_NAME" set "FORTCAMP_TUNNEL_NAME=%%B"
)
if defined FORTCAMP_TUNNEL_TOKEN (
  echo Starting the configured persistent Fortcamp tunnel.
  set "TUNNEL_TOKEN=%FORTCAMP_TUNNEL_TOKEN%"
  cloudflared tunnel --no-autoupdate run
  goto :done
)
if defined FORTCAMP_TUNNEL_NAME (
  echo Starting named tunnel %FORTCAMP_TUNNEL_NAME%.
  cloudflared tunnel --no-autoupdate run "%FORTCAMP_TUNNEL_NAME%"
  goto :done
)
echo No persistent tunnel is configured. Starting a temporary Quick Tunnel.
cloudflared tunnel --url http://127.0.0.1:5173
:done
pause
