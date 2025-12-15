#!/usr/bin/env bash
set -euo pipefail

cd /app/valorant-coach

if [ -f .env.production ]; then
	set -o allexport
	source .env.production
	set +o allexport
fi

echo "---- START DEBUG STARTUP ----"
echo "PWD: $(pwd)"
echo "USER: $(whoami 2>/dev/null || echo unknown)"
echo "ENV VARS (selected):"
echo "  PORT=${PORT:-8002}"
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
echo "Running: gunicorn valorant-coach.src.app:app --bind 0.0.0.0:${PORT:-8002} --workers 2 --worker-class uvicorn.workers.UvicornWorker"

# Exec gunicorn with the Valorant Coach FastAPI entrypoint
exec gunicorn valorant-coach.src.app:app --bind 0.0.0.0:${PORT:-8002} --workers 2 --worker-class uvicorn.workers.UvicornWorker
