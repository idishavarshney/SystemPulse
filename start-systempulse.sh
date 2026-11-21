#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

if ! command -v python3 >/dev/null 2>&1; then
  echo "Python 3 was not found. Install Python 3.9+ and try again."
  exit 1
fi

if [[ ! -x ".venv/bin/python" ]]; then
  echo "Creating Python virtual environment..."
  python3 -m venv .venv
fi

echo "Installing or checking dependencies..."
.venv/bin/python -m pip install -r requirements.txt

echo
echo "SystemPulse is starting. Keep this terminal open."
echo "Local health check: http://127.0.0.1:5000/api/health"
echo "Dashboard: https://systempulse-mocha.vercel.app"
echo

exec .venv/bin/python app.py
