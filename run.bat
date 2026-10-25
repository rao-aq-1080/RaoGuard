@echo off
setlocal
cd /d "%~dp0"

where py >nul 2>nul
if %errorlevel%==0 (
  set PY=py -3
) else (
  set PY=python
)

if not exist ".venv\Scripts\python.exe" (
  echo Creating virtual environment...
  %PY% -m venv .venv
  if errorlevel 1 (
    echo Python 3.12+ was not found. Install it from https://www.python.org/downloads/
    echo Tick "Add python.exe to PATH" during setup, then run this file again.
    pause
    exit /b 1
  )
)

call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if not exist ".env" copy ".env.example" ".env" >nul

set PYTHONPATH=%cd%
echo.
echo RaoGuard is starting. Leave this window open.
echo Browser: http://127.0.0.1:8000
echo.
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
pause
