@echo off
setlocal
taskkill /FI "WINDOWTITLE eq Fortcamp Backend*" /T /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq Fortcamp Activity Frontend*" /T /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq Fortcamp Tunnel*" /T /F >nul 2>&1
echo Fortcamp backend, frontend, and tunnel stopped.
if /I not "%~1"=="/quiet" pause
