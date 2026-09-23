from fastapi import Depends
from sqlalchemy.orm import Session

from app.contexts.user.repository import SQLAlchemyUserRepo
from app.contexts.user.service import UserService
from app.core.database import get_db


def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(repo=SQLAlchemyUserRepo(db))
