from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

Base = declarative_base()
_engine: Engine | None = None
_SessionLocal: sessionmaker | None = None

DEFAULT_DB_URL = os.getenv(
    "DATABASE_URL",
    f"sqlite:///{Path(__file__).resolve().parents[1] / 'valorant_coach.db'}",
)


def configure_database(database_url: Optional[str] = None) -> None:
    """Initialize the SQLAlchemy engine and session for the application."""

    global _engine, _SessionLocal
    target_url = database_url or os.getenv("DATABASE_URL") or DEFAULT_DB_URL
    connect_args = (
        {"check_same_thread": False} if target_url.startswith("sqlite") else {}
    )
    engine = create_engine(target_url, connect_args=connect_args, future=True)
    SessionFactory = sessionmaker(
        autocommit=False, autoflush=False, bind=engine, future=True
    )
    _engine = engine
    _SessionLocal = SessionFactory


def get_engine() -> Engine:
    if _engine is None:
        configure_database()
    assert _engine is not None
    return _engine


def get_session() -> Session:
    if _SessionLocal is None:
        configure_database()
    assert _SessionLocal is not None
    return _SessionLocal()


def init_db() -> None:
    from . import models_db  # noqa: F401  (ensure models registered)

    Base.metadata.create_all(bind=get_engine())
