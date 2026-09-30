@echo off
cd /d %~dp0
if not exist .venv\Scripts\python.exe (
  echo Run setup_windows.bat first.
  pause
  exit /b 1
)
start "Fortcamp Backend" cmd /k "cd /d %~dp0 && call .venv\Scripts\activate && uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload"
start "Fortcamp Activity Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"
echo Backend: http://127.0.0.1:8000
echo Frontend: http://127.0.0.1:5173
echo For Discord, tunnel port 5173 with cloudflared.
echo.
echo Keep this control window open. Press any key here when you want to stop
echo the backend, frontend, and any Fortcamp tunnel together.
pause >nul
call "%~dp0stop_dev_windows.bat" /quiet
