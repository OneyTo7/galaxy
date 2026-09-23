from __future__ import annotations

from app.contexts.user.repository import UserRepoProtocol
from app.contexts.user.schemas import UserDomain
from app.core.exceptions import AuthError, ConflictError, NotFoundError
from app.core.security import create_access_token, hash_password, verify_password


class UserService:
    def __init__(self, repo: UserRepoProtocol) -> None:
        self._repo = repo

    def register(
        self, username: str, password: str, role: str, display_name: str
    ) -> tuple[UserDomain, str]:
        if self._repo.get_by_username(username):
            raise ConflictError("用户名已存在")
        domain = self._repo.add(
            username, hash_password(password), role, display_name
        )
        return domain, create_access_token(str(domain.id))

    def login(self, username: str, password: str) -> tuple[UserDomain, str]:
        domain = self._repo.get_by_username(username)
        if not domain:
            raise AuthError("用户名或密码错误")
        pw_hash = self._repo.get_password_hash(username)
        if not pw_hash or not verify_password(password, pw_hash):
            raise AuthError("用户名或密码错误")
        return domain, create_access_token(str(domain.id))

    def get_me(self, user_id: int) -> UserDomain:
        domain = self._repo.get_by_id(user_id)
        if not domain:
            raise NotFoundError("用户不存在")
        return domain
