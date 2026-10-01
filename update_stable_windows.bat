@echo off
cd /d "%~dp0"
title Fortcamp Prepare Trial Release
.venv\Scripts\python.exe tools\prepare_trial_release.py
pause
