from dataclasses import dataclass

from pydantic import BaseModel, Field


class RegisterIn(BaseModel):
    username: str = Field(min_length=3, max_length=64)
    password: str = Field(min_length=6)
    role: str = Field(default="student", pattern="^(student|teacher|admin)$")
    display_name: str = ""


class LoginIn(BaseModel):
    username: str
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: int
    username: str
    role: str
    display_name: str


@dataclass(frozen=True)
class UserDomain:
    id: int
    username: str
    role: str
    display_name: str
