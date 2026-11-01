@echo off
REM Double-click this file on Windows to start the dashboard.
cd /d "%~dp0"

where python >nul 2>nul
if errorlevel 1 (
  echo Python is not installed. Download it from https://www.python.org/downloads/ and tick "Add python.exe to PATH".
  pause
  exit /b 1
)

if not exist ".venv" (
  echo Creating a virtual environment ^(first run only^)...
  python -m venv .venv
)

call .venv\Scripts\activate.bat
echo Installing / checking libraries...
python -m pip install --upgrade pip --quiet
python -m pip install -r requirements.txt --quiet

echo Starting the dashboard... it will open in your browser. Press Ctrl + C here to stop it.
python -m streamlit run app.py
pause
