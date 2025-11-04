.PHONY: venv run run-bg stop coach-test test

VENV_DIR := .venv
UVICORN_PORT ?= 8000

venv:
	python3 -m venv $(VENV_DIR)
	. $(VENV_DIR)/bin/activate && pip install --upgrade pip && pip install -r valorant-coach/requirements.txt

# Run in foreground (use UVICORN_PORT to override):
run:
	cd valorant-coach && . ../.venv/bin/activate && ../.venv/bin/uvicorn src.app:app --reload --port $(UVICORN_PORT)

# Run in background and record PID to .valorant-coach.pid
run-bg:
	@echo "Starting valorant-coach on port $(UVICORN_PORT) ..."
	cd valorant-coach && ../.venv/bin/uvicorn src.app:app --reload --port $(UVICORN_PORT) > ../valorant-coach.log 2>&1 & echo $$! > ../.valorant-coach.pid
	@echo "PID written to .valorant-coach.pid"

# Stop background server started by run-bg
stop:
	@if [ -f .valorant-coach.pid ]; then \
		PID=`cat .valorant-coach.pid`; \
		echo "Stopping PID $$PID"; \
		kill $$PID || true; \
		rm -f .valorant-coach.pid; \
		echo "Stopped."; \
	else \
		echo "No .valorant-coach.pid found."; \
	fi

coach-test:
	cd valorant-coach && . ../.venv/bin/activate && PYTHONPATH=. pytest -q -c /dev/null

test: coach-test
