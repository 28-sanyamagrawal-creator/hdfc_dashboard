#!/bin/bash
# Double-click this file on a Mac (first time: right-click > Open) to start the dashboard.
cd "$(dirname "$0")"

if ! command -v python3 >/dev/null 2>&1; then
  echo "Python 3 is not installed. Download it from https://www.python.org/downloads/ and run this again."
  read -p "Press Enter to close..."
  exit 1
fi

if [ ! -d ".venv" ]; then
  echo "Creating a virtual environment (first run only)..."
  python3 -m venv .venv
fi

source .venv/bin/activate
echo "Installing / checking libraries..."
python -m pip install --upgrade pip --quiet
python -m pip install -r requirements.txt --quiet

echo "Starting the dashboard... it will open in your browser. Press Ctrl + C here to stop it."
python -m streamlit run app.py
