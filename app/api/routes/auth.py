# app/api/routes/auth.py

import logging

from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordRequestForm

from exceptions.route import PermissionDeniedError
from repositories.user import UserRepository

from services.crud.user_service import UserService
from schemas.token import Token
from db.sessions import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.user import UserCreate, UserRead
from exceptions.user import (
    UserAlreadyExistsError,
    InvalidUserDataError,
    AuthenticationError,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/users/auth", tags=["Auth"])


def get_user_service(session: AsyncSession = Depends(get_session)) -> UserService:
    """Dependency for user service."""
    return UserService(UserRepository(session))


@router.post("/token", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    svc: UserService = Depends(get_user_service),
):
    """
    Login endpoint.
    Returns JWT for authenticated users.
    """
    try:
        token = await svc.authenticate(email=form_data.username, password=form_data.password)
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.warning(str(e))
        raise HTTPException(status_code=500, detail=str(e))

    return token


@router.post("/telegram-login", response_model=Token)
async def telegram_login(
    telegram_id: int = Body(..., embed=True),
    svc: UserService = Depends(get_user_service),
):
    """
    Telegram login endpoint.
    Returns JWT for Telegram users.
    """
    try:
        token = await svc.telegram_auth(telegram_id)
    except UserAlreadyExistsError as e:
        logger.warning(str(e))
        raise HTTPException(status_code=409, detail=e.message)
    except InvalidUserDataError as e:
        logger.warning(str(e))
        raise HTTPException(status_code=422, detail=e.message)
    return token


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(
    user_in: UserCreate,
    svc: UserService = Depends(get_user_service),
):
    """
    Create a new user with e-mail or telegram_id.
    Raises:
        UserAlreadyExistsError: If user already exists.
        InvalidUserDataError: If user data is invalid.
    """
    try:
        return await svc.register(user_in)
    except PermissionDeniedError as e:
        logger.warning(str(e))
        raise HTTPException(status_code=403, detail=e.message)
    except UserAlreadyExistsError as e:
        logger.warning(str(e))
        raise HTTPException(status_code=409, detail=e.message)
    except InvalidUserDataError as e:
        logger.warning(str(e))
        raise HTTPException(status_code=422, detail=e.message)
