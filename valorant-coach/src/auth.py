from __future__ import annotations

import os
from datetime import datetime, timedelta
from typing import Any

from fastapi import HTTPException, status
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from .db import get_session
from .models_db import User as DBUser

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
SECRET_KEY = os.getenv("VC_SECRET_KEY", "valorant-coach-secret")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


class User(BaseModel):
    username: str
    persona: str | None = None
    favorite_map: str | None = None
    favorite_weapon: str | None = None
    favorite_agent: str | None = None
    win_rate: float | None = None
    kd_ratio: float | None = None
    first_duel_rate: float | None = None
    notes: str | None = None


class UserInDB(User):
    hashed_password: str


class TokenData(BaseModel):
    username: str | None = None


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def _build_user_from_db(entry: DBUser) -> UserInDB:
    return UserInDB(
        username=entry.username,
        hashed_password=entry.hashed_password,
        persona=entry.persona,
        favorite_map=entry.favorite_map,
        favorite_weapon=entry.favorite_weapon,
        favorite_agent=entry.favorite_agent,
        win_rate=entry.win_rate,
        kd_ratio=entry.kd_ratio,
        first_duel_rate=entry.first_duel_rate,
        notes=entry.notes,
    )


def get_user(username: str) -> UserInDB | None:
    session = get_session()
    try:
        entry = session.query(DBUser).filter(DBUser.username == username).first()
        return _build_user_from_db(entry) if entry else None
    finally:
        session.close()


def save_user(user: UserInDB) -> DBUser:
    session = get_session()
    try:
        db_user = DBUser(
            username=user.username,
            hashed_password=user.hashed_password,
            persona=user.persona or "Analyst",
            favorite_agent=user.favorite_agent or "Sova",
            favorite_weapon=user.favorite_weapon or "Vandal",
            favorite_map=user.favorite_map or "Ascent",
        )
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
        return db_user
    finally:
        session.close()


def authenticate_user(username: str, password: str) -> UserInDB | None:
    user = get_user(username)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


def create_access_token(
    data: dict[str, Any], expires_delta: timedelta | None = None
) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire, "sub": data.get("sub")})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> TokenData:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str | None = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
            )
        return TokenData(username=username)
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        ) from exc


def require_active_user(token: str) -> UserInDB:
    token_data = decode_access_token(token)
    user = get_user(token_data.username or "")
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return user
