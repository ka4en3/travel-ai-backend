# app/api/routes/user.py

from typing import List
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from db.sessions import get_session
from schemas.user import UserCreate, UserRead, UserShort
from services.crud.user_service import UserService
from repositories.user import UserRepository
from exceptions.user import (
    UserAlreadyExistsError,
    UserNotFoundError,
    InvalidUserDataError,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/users", tags=["Users"])


def get_user_service(session: AsyncSession = Depends(get_session)) -> UserService:
    """Dependency for user service."""
    return UserService(UserRepository(session))


@router.get("/", response_model=List[UserShort])
async def list_users(service: UserService = Depends(get_user_service)):
    """
    Get a list of all users.
    """
    return await service.list_users()


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(user_in: UserCreate, service: UserService = Depends(get_user_service)):
    """
    Create a new user from Telegram ID.
    Raises:
        UserAlreadyExistsError: If user already exists.
        InvalidUserDataError: If user data is invalid.
    """
    try:
        return await service.create_user(user_in)
    except UserAlreadyExistsError as e:
        logger.warning(str(e))
        raise HTTPException(status_code=409, detail=e.message)
    except InvalidUserDataError as e:
        logger.warning(str(e))
        raise HTTPException(status_code=422, detail=e.message)


@router.get("/{telegram_id}", response_model=UserRead)
async def get_user_by_telegram_id(
    telegram_id: int,
    service: UserService = Depends(get_user_service),
):
    """
    Get full user details by Telegram ID.
    Raises:
        UserNotFoundError: If user not found.
    """
    try:
        return await service.get_user_by_telegram_id(telegram_id)
    except UserNotFoundError as e:
        logger.warning(str(e))
        raise HTTPException(status_code=404, detail=e.message)


@router.delete("/{telegram_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(telegram_id: int, service: UserService = Depends(get_user_service)):
    """
    Delete a user by Telegram ID.
    Raises:
        UserNotFoundError: If user not found.
    """
    try:
        await service.delete_user_by_telegram_id(telegram_id)
    except UserNotFoundError as e:
        logger.warning(str(e))
        raise HTTPException(status_code=404, detail=e.message)
