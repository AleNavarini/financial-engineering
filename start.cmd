@echo off
REM One-click launcher for the Financial Engineering API.
REM Runs run.ps1 with the execution policy bypassed for this session only.

setlocal
cd /d "%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0run.ps1"
exit /b %errorlevel%
