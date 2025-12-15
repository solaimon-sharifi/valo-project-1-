from __future__ import annotations

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from fastapi import HTTPException, status
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.getenv("VC_SECRET_KEY", "valorant-coach-secret")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
USERS_FILE = DATA_DIR / "users.json"
DATA_DIR.mkdir(parents=True, exist_ok=True)

if not USERS_FILE.exists():
    USERS_FILE.write_text("{}")


def _read_users() -> dict[str, Any]:
    try:
        return json.loads(USERS_FILE.read_text())
    except json.JSONDecodeError:
        return {}


def _write_users(data: dict[str, Any]) -> None:
    USERS_FILE.write_text(json.dumps(data, indent=2))


class User(BaseModel):
    username: str


class UserInDB(User):
    hashed_password: str


class TokenData(BaseModel):
    username: str | None = None


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def get_user(username: str) -> UserInDB | None:
    data = _read_users()
    entry = data.get(username)
    if not entry:
        return None
    return UserInDB(username=username, hashed_password=entry["hashed_password"])


def save_user(user: UserInDB) -> None:
    data = _read_users()
    data[user.username] = {"hashed_password": user.hashed_password}
    _write_users(data)


def authenticate_user(username: str, password: str) -> UserInDB | None:
    user = get_user(username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
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
