@echo off
setlocal
cd /d "%~dp0"
title Fortcamp Update Production
.venv\Scripts\python.exe tools\prepare_release_copy.py --prod
pause
