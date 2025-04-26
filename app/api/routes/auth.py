# app/api/routes/auth.py

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from repositories.user import UserRepository

from services.crud.user_service import UserService
from schemas.token import Token
from db.sessions import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.user import UserCreate, UserRead
from exceptions.user import (
    UserAlreadyExistsError,
    InvalidUserDataError,
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
    try:
        token = await svc.authenticate(form_data.username, form_data.password)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"access_token": token, "token_type": "bearer"}


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
    except UserAlreadyExistsError as e:
        logger.warning(str(e))
        raise HTTPException(status_code=409, detail=e.message)
    except InvalidUserDataError as e:
        logger.warning(str(e))
        raise HTTPException(status_code=422, detail=e.message)
