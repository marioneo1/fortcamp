@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\pythonw.exe" (
  echo Fortcamp's virtual environment is missing. Run setup_windows.bat first.
  pause
  exit /b 1
)

start "" ".venv\Scripts\pythonw.exe" "tools\portrait_pool_importer.py"
exit /b 0
