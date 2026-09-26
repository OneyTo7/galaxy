from __future__ import annotations

from dataclasses import dataclass

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.core.security import decode_token

oauth2 = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


@dataclass(frozen=True)
class CurrentUser:
    id: int
    role: str


def get_current_user(token: str = Depends(oauth2)) -> CurrentUser:
    payload = decode_token(token)
    if not payload or not payload.get("sub"):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="invalid token")
    return CurrentUser(id=int(payload["sub"]), role=payload.get("role", ""))


def require_teacher(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    if user.role != "teacher":
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="需要教师权限")
    return user
