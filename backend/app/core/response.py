from __future__ import annotations

from typing import Generic, Optional, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    code: int = 0
    message: str = "ok"
    data: Optional[T] = None


def ok(data: object = None, message: str = "ok") -> dict:
    return {"code": 0, "message": message, "data": data}


def err(code: int, message: str) -> dict:
    return {"code": code, "message": message, "data": None}
