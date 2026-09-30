@echo off
setlocal
cd /d %~dp0
if not exist .env copy .env.example .env
if not exist .venv (
  py -3 -m venv .venv
)
call .venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
pushd frontend
call npm install
popd
echo.
echo Setup complete. Edit .env with your Discord credentials, then run run_dev_windows.bat
pause
