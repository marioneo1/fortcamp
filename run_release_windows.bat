@echo off
cd /d "%~dp0"
title Fortcamp Release
.venv\Scripts\python.exe tools\run_profile.py release
if errorlevel 1 pause
