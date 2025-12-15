from datetime import datetime, timedelta
import uuid

import pytest
from fastapi import HTTPException
from jose import jwt

from src.auth import (
    ALGORITHM,
    SECRET_KEY,
    create_access_token,
    decode_access_token,
    require_active_user,
)


def test_decode_access_token_requires_subject() -> None:
    token = jwt.encode(
        {"exp": datetime.utcnow() + timedelta(minutes=5)},
        SECRET_KEY,
        algorithm=ALGORITHM,
    )
    with pytest.raises(HTTPException) as exc:
        decode_access_token(token)
    assert exc.value.status_code == 401


def test_require_active_user_raises_when_unknown_user(app) -> None:
    token = create_access_token({"sub": f"ghost-{uuid.uuid4().hex[:6]}"})
    with pytest.raises(HTTPException) as exc:
        require_active_user(token)
    assert exc.value.status_code == 401
