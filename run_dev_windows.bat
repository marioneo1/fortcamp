@echo off
setlocal
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe (
  echo Run setup_windows.bat first.
  pause
  exit /b 1
)
where npm.cmd >nul 2>&1
if errorlevel 1 (
  echo Node.js / npm is missing. Install Node.js before starting Fortcamp.
  pause
  exit /b 1
)
start "Fortcamp Backend" cmd /k ".venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload"
start "Fortcamp Activity Frontend" /D "%~dp0frontend" cmd /k "npm.cmd run dev"
echo Backend: http://127.0.0.1:8000
echo Frontend: http://127.0.0.1:5173
echo For Discord, tunnel port 5173 with cloudflared.
echo.
echo Keep this control window open. Press any key here when you want to stop
echo the backend, frontend, and any Fortcamp tunnel together.
pause >nul
call "%~dp0stop_dev_windows.bat" /quiet
