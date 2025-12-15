from __future__ import annotations

from sqlalchemy import Column, DateTime, Float, Integer, String, Text, func

from .db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(32), unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    persona = Column(String(32), default="Analyst")
    favorite_agent = Column(String(32), default="Sova")
    favorite_weapon = Column(String(32), default="Vandal")
    favorite_map = Column(String(32), default="Ascent")
    win_rate = Column(Float, default=0.56)
    kd_ratio = Column(Float, default=1.05)
    first_duel_rate = Column(Float, default=0.47)
    notes = Column(Text, default="Dashboard data stored in PostgreSQL")
    last_login = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
