import os
import sys
from pathlib import Path

import pytest

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src import db as db_module


@pytest.fixture(scope="session", autouse=True)
def test_database(tmp_path_factory):
    db_dir = tmp_path_factory.mktemp("db")
    db_path = db_dir / "valorant_test.db"
    db_url = f"sqlite:///{db_path}"
    previous = os.environ.get("DATABASE_URL")
    os.environ["DATABASE_URL"] = db_url
    db_module.configure_database(db_url)
    db_module.init_db()
    yield
    if previous is None:
        os.environ.pop("DATABASE_URL", None)
    else:
        os.environ["DATABASE_URL"] = previous


@pytest.fixture(scope="session")
def app(test_database):
    from src.app import app as valorant_app

    return valorant_app
