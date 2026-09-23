from __future__ import annotations

from sqlalchemy.orm import Session

from app.contexts.user.models import User
from app.contexts.user.schemas import UserDomain


class UserRepoProtocol:
    def get_by_username(self, username: str) -> UserDomain | None: ...
    def get_password_hash(self, username: str) -> str | None: ...
    def add(
        self, username: str, password_hash: str, role: str, display_name: str
    ) -> UserDomain: ...
    def get_by_id(self, user_id: int) -> UserDomain | None: ...


class SQLAlchemyUserRepo(UserRepoProtocol):
    def __init__(self, db: Session) -> None:
        self._db = db

    @staticmethod
    def _to_domain(u: User) -> UserDomain:
        return UserDomain(u.id, u.username, u.role, u.display_name)

    def get_by_username(self, username: str) -> UserDomain | None:
        u = self._db.query(User).filter(User.username == username).first()
        return self._to_domain(u) if u else None

    def get_password_hash(self, username: str) -> str | None:
        u = self._db.query(User).filter(User.username == username).first()
        return u.password_hash if u else None

    def add(
        self, username: str, password_hash: str, role: str, display_name: str
    ) -> UserDomain:
        u = User(
            username=username,
            password_hash=password_hash,
            role=role,
            display_name=display_name,
        )
        self._db.add(u)
        self._db.commit()
        self._db.refresh(u)
        return self._to_domain(u)

    def get_by_id(self, user_id: int) -> UserDomain | None:
        u = self._db.get(User, user_id)
        return self._to_domain(u) if u else None
