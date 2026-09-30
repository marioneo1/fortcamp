@echo off
setlocal
title Fortcamp Tailscale Funnel Setup
where tailscale >nul 2>&1
if errorlevel 1 (
  echo Tailscale was not found. Install it and sign in before running this setup.
  pause
  exit /b 1
)
echo Configuring a persistent public HTTPS Funnel for Fortcamp...
echo Tailscale may open a one-time approval page the first time Funnel is enabled.
tailscale funnel --bg 5173
if errorlevel 1 (
  echo.
  echo Funnel setup failed. Check that Tailscale is connected and Funnel is enabled for your tailnet.
  pause
  exit /b 1
)
echo.
echo Fortcamp Funnel status:
tailscale funnel status
echo.
echo Copy the hostname shown above into Discord Developer Portal:
echo Activities ^> URL Mappings ^> / ^> Target
echo Do not include https:// or the final slash.
echo.
echo This Funnel runs in the background and resumes automatically. You do not
echo need to run this setup whenever Fortcamp starts.
pause
