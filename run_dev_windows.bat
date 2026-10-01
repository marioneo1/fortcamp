@echo off
cd /d "%~dp0"
title Fortcamp Isolated Development
.venv\Scripts\python.exe tools\run_profile.py dev
if errorlevel 1 pause
