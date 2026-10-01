@echo off
cd /d "%~dp0"
title Fortcamp Friend Trial
.venv\Scripts\python.exe tools\run_profile.py stable
if errorlevel 1 pause
