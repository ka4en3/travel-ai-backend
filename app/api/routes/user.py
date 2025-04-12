# app/api/routes/user.py

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from db.sessions import get_session
from repositories.user import UserRepository
from schemas.user import (
    UserCreate,
    UserRead,
    UserShort,
)

router = APIRouter(prefix="/users", tags=["Users"])
logger = logging.getLogger(__name__)


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_in: UserCreate,
    session: AsyncSession = Depends(get_session),
):
    """
    Create a new user from Telegram data.
    """
    repo = UserRepository(session)
    existing = await repo.get_by_telegram_id(user_in.telegram_id)
    if existing:
        logger.info("User already exists: telegram_id=%s", user_in.telegram_id)
        raise HTTPException(status_code=409, detail="User already exists")
    user = await repo.create(user_in)
    logger.info("Created user with id=%s", user.id)
    return user


@router.get("/{telegram_id}", response_model=UserRead)
async def get_user_by_telegram_id(
    telegram_id: int,
    session: AsyncSession = Depends(get_session),
):
    """
    Get full user details by Telegram ID.
    """
    repo = UserRepository(session)
    user = await repo.get_by_telegram_id(telegram_id)
    if not user:
        logger.warning("User not found: telegram_id=%s", telegram_id)
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/", response_model=list[UserShort])
async def get_all_users(
    session: AsyncSession = Depends(get_session),
):
    """
    Return a short list of all users.
    """
    repo = UserRepository(session)
    users = await repo.get_all()
    logger.info("Retrieved %d users", len(users))
    return users


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    session: AsyncSession = Depends(get_session),
):
    """
    Delete a user by ID.
    """
    repo = UserRepository(session)
    deleted = await repo.delete(user_id)
    if not deleted:
        logger.warning("User not found or already deleted: id=%s", user_id)
        raise HTTPException(status_code=404, detail="User not found")
    logger.info("Deleted user with id=%s", user_id)
