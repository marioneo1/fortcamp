@echo off
setlocal
cd /d "%~dp0"
title Fortcamp Create Release Copy
set /p "FORTCAMP_NEW_VERSION=New trial version, for example 0.3.1-trial.2: "
if not defined FORTCAMP_NEW_VERSION exit /b 1
.venv\Scripts\python.exe tools\prepare_release_copy.py --version "%FORTCAMP_NEW_VERSION%"
pause
