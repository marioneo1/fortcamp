@echo off
cd /d "%~dp0"
echo Release updates now use independent sibling folders.
call create_release_windows.bat
