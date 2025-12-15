import pytest

from src import db as db_module


@pytest.mark.usefixtures("app")
def test_get_engine_configures_when_missing() -> None:
    old_engine = db_module._engine
    old_session = db_module._SessionLocal
    db_module._engine = None
    db_module._SessionLocal = None
    try:
        engine = db_module.get_engine()
        assert engine is not None
        engine.dispose()
    finally:
        db_module._engine = old_engine
        db_module._SessionLocal = old_session


@pytest.mark.usefixtures("app")
def test_get_session_configures_when_missing() -> None:
    old_engine = db_module._engine
    old_session = db_module._SessionLocal
    db_module._engine = None
    db_module._SessionLocal = None
    try:
        session = db_module.get_session()
        assert session is not None
        session.close()
    finally:
        db_module._engine = old_engine
        db_module._SessionLocal = old_session
