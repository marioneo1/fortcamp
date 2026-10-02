@echo off
cd /d "%~dp0"
title Fortcamp Development - Web and Discord
.venv\Scripts\python.exe tools\run_profile.py dev-discord
if errorlevel 1 pause
