from fastapi import APIRouter, Depends, HTTPException, status

from app.contexts.user.deps import get_user_service
from app.contexts.user.schemas import LoginIn, RegisterIn, TokenOut, UserOut
from app.contexts.user.service import UserService
from app.core.deps import get_current_user_id
from app.core.exceptions import AuthError, ConflictError, NotFoundError

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=TokenOut, status_code=status.HTTP_201_CREATED)
async def register(
    req: RegisterIn, svc: UserService = Depends(get_user_service)
) -> TokenOut:
    try:
        _domain, token = svc.register(req.username, req.password, req.role, req.display_name)
    except ConflictError as e:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=e.message)
    return TokenOut(access_token=token)


@router.post("/login", response_model=TokenOut)
async def login(req: LoginIn, svc: UserService = Depends(get_user_service)) -> TokenOut:
    try:
        _domain, token = svc.login(req.username, req.password)
    except AuthError as e:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail=e.message)
    return TokenOut(access_token=token)


@router.get("/me", response_model=UserOut)
async def me(
    user_id: str = Depends(get_current_user_id),
    svc: UserService = Depends(get_user_service),
) -> UserOut:
    try:
        domain = svc.get_me(int(user_id))
    except NotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=e.message)
    return UserOut(
        id=domain.id,
        username=domain.username,
        role=domain.role,
        display_name=domain.display_name,
    )
