@echo off
setlocal
cd /d "%~dp0"
title SystemPulse Local Monitor

where py >nul 2>nul
if errorlevel 1 (
  echo Python launcher was not found. Install Python 3.9+ from https://www.python.org/downloads/
  echo During installation, enable "Add Python to PATH".
  pause
  exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
  echo Creating Python virtual environment...
  py -3 -m venv .venv
  if errorlevel 1 goto :error
)

echo Installing or checking dependencies...
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto :error

echo.
echo SystemPulse is starting. Keep this window open.
echo Local health check: http://127.0.0.1:5000/api/health
echo Dashboard: https://systempulse-mocha.vercel.app
echo.
".venv\Scripts\python.exe" app.py
if errorlevel 1 goto :error
exit /b 0

:error
echo.
echo SystemPulse could not start. Check the error shown above.
pause
exit /b 1
