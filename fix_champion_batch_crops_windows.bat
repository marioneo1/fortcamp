@echo off
setlocal
cd /d "%~dp0"
set /p FORTCAMP_BATCH=Enter the three-digit Champion batch number (example: 011): 
if "%FORTCAMP_BATCH%"=="" exit /b 1
".venv\Scripts\python.exe" "tools\fix_champion_batch_crops.py" --batch "%FORTCAMP_BATCH%"
if errorlevel 1 (
  echo.
  echo Repair failed. Original portraits were restored from the backup.
) else (
  echo.
  echo Repair and validation completed successfully.
)
pause
