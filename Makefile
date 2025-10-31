.PHONY: venv run coach-test test

VENV_DIR := .venv

venv:
	python3 -m venv $(VENV_DIR)
	. $(VENV_DIR)/bin/activate && pip install --upgrade pip && pip install -r requirements.txt && pip install -r valorant-coach/requirements.txt

run:
	cd valorant-coach && UVICORN_PORT=8000; . ../.venv/bin/activate && uvicorn src.app:app --reload

coach-test:
	cd valorant-coach && . ../.venv/bin/activate && PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONPATH=. pytest -q -p pytest_asyncio.plugin -c /dev/null --rootdir=. tests/test_api.py

test: coach-test
