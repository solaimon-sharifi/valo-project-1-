#!/usr/bin/env bash
set -euo pipefail

echo "---- START DEBUG STARTUP ----"
echo "PWD: $(pwd)"
echo "USER: $(whoami 2>/dev/null || echo unknown)"
echo "ENV VARS (selected):"
echo "  PORT=${PORT:-<not set>}"
echo "  PATH=$PATH"
echo "---- LIST /app ----"
ls -la /app || true
echo "---- LIST /app/static/images ----"
ls -la /app/static/images || true
echo "---- PYTHON VERSION ----"
python --version 2>&1 || python3 --version 2>&1 || true
echo "---- PIP FREEZE (first 50 lines) ----"
pip freeze 2>/dev/null | sed -n '1,50p' || true

echo "---- ATTEMPTING TO START GUNICORN ----"
echo "Running: gunicorn app:app --bind 0.0.0.0:${PORT:-5000} --workers 2"

# Exec gunicorn so it becomes PID 1 and logs flow to stdout/stderr
exec gunicorn app:app --bind 0.0.0.0:${PORT:-5000} --workers 2
